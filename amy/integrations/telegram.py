"""
Telegram Bot Integration for Amy

This is a THIN integration layer. All AI logic is in amy.core.amy.
"""

import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from amy.config import TELEGRAM_BOT_TOKEN, TELEGRAM_LOG_FILE, APP_NAME
from amy.core.factory import create_amy_runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(TELEGRAM_LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Validate configuration
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize Amy Runner
runner = None

async def init_runner():
    """Initialize the global runner instance."""
    global runner
    if runner is None:
        runner = await create_amy_runner()



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = """
🤖 **Amy Commands:**

/help - Show this help message
/memory - Show memory statistics

💡 **Features:**
• Memory across conversations
• Context-aware responses
"""
    await update.message.reply_text(help_text)


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show memory statistics."""
    # Limitation: With raw Runner, accessing stats requires direct DB access not exposed on Runner.
    # This command is temporarily disabled in strict ADK mode or needs DB access.
    await update.message.reply_text("Memory stats unavailable in strict ADK mode.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages with streaming support."""
    if not update.message or not update.message.text:
        return
    
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    session_id = f"telegram_{user_id}"
    if runner is None:
        await init_runner()

    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    session_id = f"telegram_{user_id}"
    message_text = update.message.text
    
    logger.info(f"[Telegram] {update.effective_user.username}: {message_text[:50]}...")
    
    # Send typing action to show user we are processing
    from telegram.constants import ChatAction
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    # We will create the message object only when we have the first chunk of text
    placeholder = None
    
    full_response = ""
    last_update_time = time.time()
    
    try:
        # Ensure session exists (Required for ADK persistence with FKs)
        # We try to get it, if not found (None), we create it.
        try:
            session = await runner.session_service.get_session(APP_NAME, user_id, session_id)
            if not session:
                logger.info(f"Creating new session: {session_id}")
                await runner.session_service.create_session(APP_NAME, user_id, session_id)
        except Exception as e:
            logger.warning(f"Session check failed (will try to proceed): {e}")

        # Create Content object for ADK
        from google.genai.types import Content, Part
        message = Content(parts=[Part(text=message_text)])

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            # Yield to event loop to allow other tasks (like pings) to process
            await asyncio.sleep(0)

            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, 'thought', False): # Skip thoughts
                        continue
                    if part.text:
                        full_response += part.text
            
                        # Brain-informed buffering: Update if we have a sentence ending or enough time passed
                        current_time = time.time()
                        should_update = False
                        
                        # 1. Time-based trigger (2 seconds for safety)
                        if current_time - last_update_time > 2.0:
                            should_update = True
                            
                        # 2. Heuristic: Update on sentence endings if at least 1.0s passed
                        elif current_time - last_update_time > 1.0:
                            if any(punct in part.text for punct in {'. ', '! ', '? ', '\n'}):
                                should_update = True

                        if should_update and full_response.strip():
                            try:
                                if placeholder is None:
                                    # First Chunk: Reply to user
                                    placeholder = await update.message.reply_text(full_response + " ▌")
                                else:
                                    # Subsequent Chunks: Edit message
                                    await context.bot.edit_message_text(
                                        chat_id=chat_id,
                                        message_id=placeholder.message_id,
                                        text=full_response + " ▌" # Add a typing cursor
                                    )
                                last_update_time = current_time
                                
                                # Renewal of typing status (it expires after 5s)
                                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                            except Exception as e:
                                # Ignore "Message is not modified" errors from Telegram
                                if "Message is not modified" not in str(e):
                                    logger.debug(f"Telegram edit error: {e}")

        # Final update to remove the cursor and ensure full text is sent
        try:
            if full_response:
                if placeholder:
                    await placeholder.edit_text(full_response)
                else:
                    # If we never sent a message (short response < update interval?), send now
                    await update.message.reply_text(full_response)
            else:
                if placeholder:
                    await placeholder.edit_text("I'm sorry, I couldn't generate a response.")
                else:
                    await update.message.reply_text("I'm sorry, I couldn't generate a response.")
        except Exception as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Final Telegram update failed: {e}")
            
    except Exception as e:
        # Check for specific Google API errors if possible, usually they come as google.api_core.exceptions
        error_str = str(e)
        if "429" in error_str or "ResourceExhausted" in error_str:
            logger.error(f"Google API Quota Exceeded: {e}")
            notification = "I'm currently overloaded (Quota Exceeded). Please try again in a minute."
        elif "503" in error_str or "ServiceUnavailable" in error_str:
            logger.error(f"Google API Service Unavailable: {e}")
            notification = "My brain is having trouble connecting to Google. Please try again later."
        else:
            logger.error(f"Error during streaming: {e}")
            notification = "Sorry, an unexpected error occurred."

        try:
            if placeholder:
                await placeholder.edit_text(notification)
            else:
                await update.message.reply_text(notification)
        except Exception:
            pass


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Error: {context.error}")
    if update and hasattr(update, 'effective_message') and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred. Please try again."
        )


def main():
    """Start the Telegram bot."""
    logger.info("Starting Amy Telegram Bot...")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memory", memory_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
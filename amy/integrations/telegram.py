"""
Telegram Bot Integration for Amy

This is a THIN integration layer. All AI logic is in amy.core.amy.
"""

import logging
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from amy.config import TELEGRAM_BOT_TOKEN, TELEGRAM_LOG_FILE
from amy.core.amy import get_brain

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

# Initialize Amy
amy = get_brain()


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
    user_id = str(update.effective_user.id)
    session_id = f"telegram_{user_id}"
    
    # Updated to await async stats
    stats = await amy.get_memory_stats(session_id)
    
    response = f"🧠 Memory Statistics:\n\n"
    response += f"💬 Messages: {stats['message_count']}\n"
    response += f"📚 History: {'Yes' if stats['has_history'] else 'No'}\n"
    
    await update.message.reply_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages with streaming support."""
    if not update.message or not update.message.text:
        return
    
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    session_id = f"telegram_{user_id}"
    message = update.message.text
    
    logger.info(f"[Telegram] {update.effective_user.username}: {message[:50]}...")
    
    # Initial placeholder message
    placeholder = await update.message.reply_text("Thinking...")
    
    full_response = ""
    last_update_time = time.time()
    
    try:
        async for chunk in amy.chat_stream(
            session_id=session_id,
            message=message,
            user_id=user_id,
            platform="telegram"
        ):
            full_response += chunk
            
            # Brain-informed buffering: Update if we have a sentence ending or enough time passed
            current_time = time.time()
            should_update = False
            
            # 1. Time-based trigger (2 seconds for safety)
            if current_time - last_update_time > 2.0:
                should_update = True
                
            # 2. Heuristic: Update on sentence endings if at least 1.0s passed
            elif current_time - last_update_time > 1.0:
                if any(punct in chunk for punct in {'. ', '! ', '? ', '\n'}):
                    should_update = True

            if should_update:
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=placeholder.message_id,
                        text=full_response + " ▌" # Add a typing cursor for smoother feel
                    )
                    last_update_time = current_time
                except Exception as e:
                    # Ignore "Message is not modified" errors from Telegram
                    if "Message is not modified" not in str(e):
                        logger.debug(f"Telegram edit error: {e}")

        # Final update to remove the cursor and ensure full text is sent
        try:
            if full_response:
                await placeholder.edit_text(full_response)
            else:
                await placeholder.edit_text("I'm sorry, I couldn't generate a response.")
        except Exception as e:
            if "Message is not modified" not in str(e):
                logger.error(f"Final Telegram update failed: {e}")
            
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
        try:
            await placeholder.edit_text("Sorry, an error occurred while generating a response.")
        except:
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
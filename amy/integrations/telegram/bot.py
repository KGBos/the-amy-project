import os
import time
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Import configuration
from amy.config import (
    GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, DEFAULT_MODEL,
    DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_TOP_K, DEFAULT_MAX_OUTPUT_TOKENS,
    TELEGRAM_LOG_FILE, SYSTEM_PROMPT
)

# Import the NEW memory system
from amy.features.memory.conversation_db import ConversationDB
from amy.features.memory.ltm import LTM
from amy.features.sensory.audio_transcription import AudioTranscriber

# Load environment variables
load_dotenv()

# Configure Gemini/Google Generative AI
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is required")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model with tools
model = genai.GenerativeModel(DEFAULT_MODEL)

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

# Initialize bot
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize NEW persistent storage
conversation_db = ConversationDB()
ltm = LTM()

# Initialize audio transcriber for voice messages
audio_transcriber = AudioTranscriber("base")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = """
🤖 **Amy Bot Commands:**

/help - Show this help message
/memory - Show memory statistics
/debug - Show current prompt structure and memory state

💡 **Features:**
• Text and voice message support
• Memory across conversations
• Context-aware responses
• Fact learning and recall

🛑 Press Ctrl+C to stop the bot
"""
    await update.message.reply_text(help_text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user about issues."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Format traceback for logging
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    logger.error(f"Traceback:\n{tb_string}")
    
    # Notify user if possible
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "Sorry, an error occurred while processing your request. Please try again."
            )
        except Exception:
            # If we can't notify the user, just log it
            logger.error("Failed to notify user about the error")


async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show memory statistics."""
    try:
        user_id = str(update.effective_user.id)
        session_id = f"telegram_{user_id}"
        
        # Get stats from ConversationDB
        message_count = conversation_db.get_message_count(session_id)
        has_history = conversation_db.has_previous_conversations(user_id)
        
        response = f"🧠 Memory Statistics:\n\n"
        response += f"� Messages in session: {message_count}\n"
        response += f"📚 Has conversation history: {'Yes' if has_history else 'No'}\n"
        response += f"🗄️ Database: instance/amy.db\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        await update.message.reply_text("Sorry, I couldn't retrieve memory statistics.")

async def debug_prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current prompt structure."""
    try:
        user_id = str(update.effective_user.id)
        session_id = f"telegram_{user_id}"
        
        # Get current context
        recent_context = conversation_db.get_context_for_session(session_id, limit=5)
        ltm_context = ltm.build_context_from_query("debug", user_id=user_id)
        
        debug_info = f"🔍 DEBUG INFO:\n\n"
        debug_info += f"📊 System Prompt: {len(SYSTEM_PROMPT)} chars\n"
        debug_info += f"💬 Recent Context: {len(recent_context)} chars\n"
        debug_info += f"🧠 LTM Context: {len(ltm_context) if ltm_context else 0} chars\n\n"
        debug_info += f"📋 SYSTEM PROMPT:\n{SYSTEM_PROMPT}\n\n"
        debug_info += f"💬 RECENT CONTEXT:\n{recent_context or '(empty)'}\n\n"
        debug_info += f"🧠 LTM CONTEXT:\n{ltm_context or '(empty)'}"
        
        # Split if too long
        if len(debug_info) > 4000:
            await update.message.reply_text(debug_info[:4000] + "...(truncated)")
        else:
            await update.message.reply_text(debug_info)
            
    except Exception as e:
        logger.error(f"Error in debug: {e}")
        await update.message.reply_text("Sorry, debug failed.")


async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages by transcribing them and processing as text."""
    if not update.message or not update.message.voice or update.message.from_user is None or update.message.from_user.is_bot:
        logger.info("Ignoring non-voice message or message from bot.")
        return

    chat_id = str(update.message.chat_id)
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or 'unknown'
    
    # Create session ID for this conversation
    session_id = f"telegram_{chat_id}"
    
    # Log the voice message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"--- VOICE MESSAGE ({timestamp}) ---")
    logger.info(f"User ID: {user_id}, Username: {username}, Chat ID: {chat_id}")
    logger.info(f"Voice message received")
    
    try:
        # Download the voice file
        voice_file = await context.bot.get_file(update.message.voice.file_id)
        voice_path = f"instance/voice_{chat_id}_{timestamp.replace(':', '-')}.ogg"
        
        # Download the file
        await voice_file.download_to_drive(voice_path)
        logger.info(f"Voice file downloaded to: {voice_path}")
        
        # Transcribe the voice message
        transcribed_text = audio_transcriber.transcribe_audio(voice_path)
        
        if transcribed_text:
            logger.info(f"Transcribed voice message: {transcribed_text}")
            
            # Process the transcribed text through memory system
            memory_manager.process_message(
                session_id=session_id,
                platform="telegram",
                role="user",
                content=transcribed_text,
                user_id=user_id,
                username=username
            )
            
            # Build context for Amy's response
            mem_context = memory_manager.get_context_for_query(session_id, transcribed_text)
            
            # Build the full prompt with context using AmyPromptBuilder
            full_prompt = AmyPromptBuilder.build_full_prompt(
                user_message=transcribed_text,
                context=mem_context
            )
            
            # Log the context being used
            logger.info(f"--- CONTEXT FOR AMY ---")
            logger.info(f"Context length: {len(mem_context)} characters")
            if mem_context:
                logger.info(f"Context: {mem_context[:200]}...")
            
            # Log the COMPLETE PROMPT that Amy sees
            logger.info("=" * 80)
            logger.info("🎯 COMPLETE PROMPT SENT TO AMY")
            logger.info("=" * 80)
            logger.info(f"SYSTEM PROMPT:")
            logger.info(f"{AmyPromptBuilder.get_system_prompt()}")
            logger.info("")
            if mem_context:
                logger.info(f"CONTEXT:")
                logger.info(f"{mem_context}")
                logger.info("")
            logger.info(f"USER MESSAGE:")
            logger.info(f"{transcribed_text}")
            logger.info("")
            logger.info(f"FULL PROMPT LENGTH: {len(full_prompt)} characters")
            logger.info("=" * 80)
            
            # Generate response using Google Generative AI
            try:
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=1024,
                    )
                )
                
                # Check if response was blocked by safety filters
                if response.candidates and response.candidates[0].finish_reason == 2:
                    amy_response = "I apologize, but I'm unable to respond to that message due to content safety filters. Could you please rephrase your message?"
                elif response.text:
                    amy_response = response.text
                else:
                    amy_response = "I'm sorry, I encountered an issue generating a response. Please try again."
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                amy_response = "I'm having trouble connecting to my thinking system. Please try again in a moment."
            
            # Process Amy's response through memory system
            memory_manager.process_message(
                session_id=session_id,
                platform="telegram",
                role="model",
                content=amy_response,
                user_id=user_id,
                username=username
            )
            
            # Log the response
            logger.info(f"--- AMY RESPONSE ({timestamp}) ---")
            logger.info(f"Response: {amy_response}")
            
            # Send response back to Telegram
            await update.message.reply_text(amy_response)
            
        else:
            await update.message.reply_text("I'm sorry, I couldn't transcribe your voice message. Could you please try sending it as text instead?")
            
        # Clean up the voice file
        try:
            os.remove(voice_path)
            logger.info(f"Cleaned up voice file: {voice_path}")
        except Exception as e:
            logger.warning(f"Could not clean up voice file {voice_path}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your voice message. Please try sending it as text instead.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages - SIMPLIFIED with ConversationDB."""
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    message_text = update.message.text
    session_id = f"telegram_{user_id}"
    
    # Log incoming message
    logger.info(f"--- USER MESSAGE ---")
    logger.info(f"User: {username} ({user_id})")
    logger.info(f"Message: {message_text}")
    
    # 1. Store user message FIRST (persistent)
    conversation_db.add_message(
        session_id=session_id,
        role="user",
        content=message_text,
        user_id=user_id,
        platform="telegram"
    )
    
    # 2. Build context from recent conversation
    recent_context = conversation_db.get_context_for_session(
        session_id, 
        limit=10, 
        max_chars=2000
    )
    
    # 3. Get relevant facts from LTM (semantic search)
    ltm_context = ltm.build_context_from_query(message_text, user_id=user_id)
    
    # 4. Build the prompt
    prompt_parts = [SYSTEM_PROMPT]
    
    if recent_context:
        prompt_parts.append(f"\n{recent_context}")
    
    if ltm_context:
        prompt_parts.append(f"\n{ltm_context}")
    
    prompt_parts.append(f"\nUser: {message_text}")
    prompt_parts.append("Amy:")
    
    full_prompt = "\n".join(prompt_parts)
    
    logger.info(f"--- PROMPT ({len(full_prompt)} chars) ---")
    logger.debug(f"Context: {recent_context[:200] if recent_context else 'None'}...")
    
    # 5. Generate response
    try:
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=1024,
            )
        )
        
        if response.candidates and response.candidates[0].finish_reason == 2:
            amy_response = "I can't respond to that due to content safety. Please rephrase."
        elif response.text:
            amy_response = response.text
        else:
            amy_response = "I'm sorry, I couldn't generate a response."
            
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        amy_response = "I'm having trouble thinking right now. Please try again."
    
    # 6. Store Amy's response (persistent)
    conversation_db.add_message(
        session_id=session_id,
        role="assistant",
        content=amy_response,
        user_id=user_id,
        platform="telegram"
    )
    
    # 7. Extract and store facts from conversation (async background)
    # Simple heuristic: if user said "my name is" or "I like", extract fact
    lower_msg = message_text.lower()
    if any(p in lower_msg for p in ['my name is', 'i am called', 'call me']):
        ltm.store_fact(message_text, "personal_info", user_id)
    elif any(p in lower_msg for p in ['i like', 'i love', 'i prefer', 'my favorite']):
        ltm.store_fact(message_text, "preference", user_id)
    
    logger.info(f"--- AMY RESPONSE ---")
    logger.info(f"Response: {amy_response[:200]}...")
    
    # 8. Send response
    await update.message.reply_text(amy_response)


def main():
    """Start the bot."""
    logger.info("Starting Amy Telegram Bot with Memory System...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memory", memory_stats_command))
    application.add_handler(CommandHandler("debug", debug_prompt_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Add global error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
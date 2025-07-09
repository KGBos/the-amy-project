import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Import the memory system
from app.features.memory import MemoryManager
from app.features.sensory.audio_transcription import AudioTranscriber

# Load environment variables
load_dotenv()

# Configure Gemini/Google Generative AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is required")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-flash')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instance/amy_telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize memory manager
memory_manager = MemoryManager()

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

async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show memory statistics."""
    try:
        stats = memory_manager.get_memory_stats()
        
        # Format the stats
        stm_sessions = stats['stm']['active_sessions']
        ltm_facts = stats['ltm']['fact_types']
        episodic_sessions = stats['episodic'].get('total_sessions', 0)
        
        response = f"🧠 Memory Statistics:\n\n"
        response += f"📝 STM Active Sessions: {stm_sessions}\n"
        response += f"🧩 EpTM Total Sessions: {episodic_sessions}\n"
        response += f"🧠 LTM Facts by Type:\n"
        
        for fact_type, count in ltm_facts.items():
            response += f"  • {fact_type}: {count}\n"
            
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        await update.message.reply_text("Sorry, I couldn't retrieve memory statistics right now.")

async def debug_prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the current prompt structure and memory state."""
    try:
        user_id = str(update.effective_user.id)
        session_id = f"telegram_{user_id}"
        
        # Get detailed memory state
        memory_state = memory_manager.get_detailed_memory_state(session_id, user_id)
        
        # Get current context
        context = memory_manager.get_context_for_query(session_id, "debug", user_id)
        
        # Build the system prompt
        system_prompt = "You are Amy, a helpful and friendly AI assistant with memory. You can remember past conversations and learn about users over time. Respond directly to the user's message in a conversational way, using context from previous conversations when relevant."
        
        # Build the full prompt
        if context:
            full_prompt = f"{system_prompt}\n\n{context}\n\nUser: debug\nAmy:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: debug\nAmy:"
        
        # Format the debug info
        debug_info = f"🔍 PROMPT DEBUG INFO:\n\n"
        debug_info += f"📊 System Prompt Length: {len(system_prompt)} chars\n"
        debug_info += f"🧠 Context Length: {len(context)} chars\n"
        debug_info += f"📝 Total Prompt Length: {len(full_prompt)} chars\n\n"
        
        # Add memory state
        debug_info += f"🧠 MEMORY STATE:\n"
        debug_info += f"• STM Messages in Session: {memory_state['stm']['messages_in_session']}\n"
        debug_info += f"• EpTM Messages in Session: {memory_state['episodic']['messages_in_session']}\n"
        debug_info += f"• LTM Total Facts: {memory_state['ltm']['total_facts']}\n"
        debug_info += f"• User Session Count: {memory_state['user_session']['session_count']}\n"
        debug_info += f"• Is New User: {memory_state['user_session']['is_new_user']}\n\n"
        
        debug_info += f"📋 SYSTEM PROMPT:\n{system_prompt}\n\n"
        
        if context:
            debug_info += f"🧠 CONTEXT:\n{context}\n\n"
        else:
            debug_info += f"🧠 CONTEXT: (empty)\n\n"
            
        debug_info += f"👤 USER MESSAGE: debug\n\n"
        debug_info += f"🎯 FULL PROMPT:\n{full_prompt}"
        
        # Split into chunks if too long
        if len(debug_info) > 4000:
            chunks = [debug_info[i:i+4000] for i in range(0, len(debug_info), 4000)]
            for i, chunk in enumerate(chunks):
                await update.message.reply_text(f"Debug Info (Part {i+1}/{len(chunks)}):\n{chunk}")
        else:
            await update.message.reply_text(debug_info)
            
    except Exception as e:
        logger.error(f"Error in debug prompt command: {e}")
        await update.message.reply_text("Sorry, I couldn't generate debug info right now.")

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
            context = memory_manager.get_context_for_query(session_id, transcribed_text)
            
            # Create the conversation prompt with context
            system_prompt = "You are Amy, a helpful and friendly AI assistant with memory. You can remember past conversations and learn about users over time. Respond directly to the user's message in a conversational way, using context from previous conversations when relevant."
            
            # Build the full prompt with context
            if context:
                full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {transcribed_text}\nAmy:"
            else:
                full_prompt = f"{system_prompt}\n\nUser: {transcribed_text}\nAmy:"
            
            # Log the context being used
            logger.info(f"--- CONTEXT FOR AMY ---")
            logger.info(f"Context length: {len(context)} characters")
            if context:
                logger.info(f"Context: {context[:200]}...")
            
            # Log the COMPLETE PROMPT that Amy sees
            logger.info("=" * 80)
            logger.info("🎯 COMPLETE PROMPT SENT TO AMY")
            logger.info("=" * 80)
            logger.info(f"SYSTEM PROMPT:")
            logger.info(f"{system_prompt}")
            logger.info("")
            if context:
                logger.info(f"CONTEXT:")
                logger.info(f"{context}")
                logger.info("")
            logger.info(f"USER MESSAGE:")
            logger.info(f"{transcribed_text}")
            logger.info("")
            logger.info(f"FULL PROMPT LENGTH: {len(full_prompt)} characters")
            logger.info("=" * 80)
            
            # Generate response using Google Generative AI
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
    """Handle incoming messages."""
    if not update.message or not update.message.text:
        return
        
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    message_text = update.message.text
    session_id = f"telegram_{user_id}"
    
    # Log the incoming message
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"--- USER MESSAGE ({timestamp}) ---")
    logger.info(f"User ID: {user_id}, Username: {username}, Chat ID: {chat_id}")
    logger.info(f"Message: {message_text}")
    
    # Check if this is a new user/session and record it
    is_new_user = memory_manager.is_new_user(user_id, session_id)
    if is_new_user:
        logger.info(f"New user/session detected: {user_id}")
        memory_manager.record_user_session(user_id, session_id)
    
    # Load user-specific memory if this is a new conversation
    if not memory_manager.stm.get_context(session_id):
        logger.info(f"New conversation detected for user {user_id}, loading user-specific memory...")
        memory_manager._load_previous_conversations_for_user(user_id)
    
    # Process the message through memory systems
    memory_manager.process_message(
        session_id=session_id,
        platform="telegram",
        role="user",
        content=message_text,
        user_id=user_id,
        username=username
    )
    
    # Build context for the response
    context = memory_manager.get_context_for_query(session_id, message_text, user_id)
    
    # Create the conversation prompt with context
    system_prompt = "You are Amy, a helpful and friendly AI assistant with memory. You can remember past conversations and learn about users over time. Respond directly to the user's message in a conversational way, using context from previous conversations when relevant."
    
    # Add greeting context for new users
    if is_new_user:
        greeting = memory_manager.get_greeting(user_id, session_id)
        system_prompt += f"\n\nNote: This appears to be a new user. If they say 'hi' or similar greetings, respond with: '{greeting}'"
    
    # Build the full prompt with context
    if context:
        full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {message_text}\nAmy:"
    else:
        full_prompt = f"{system_prompt}\n\nUser: {message_text}\nAmy:"
    
    # Log the context being sent to Amy
    logger.info("--- CONTEXT FOR AMY ---")
    logger.info(f"Context length: {len(context)} characters")
    logger.info(f"Context: {context}")
    
    # Log the COMPLETE PROMPT that Amy sees
    logger.info("=" * 80)
    logger.info("🎯 COMPLETE PROMPT SENT TO AMY")
    logger.info("=" * 80)
    logger.info(f"SYSTEM PROMPT:")
    logger.info(f"{system_prompt}")
    logger.info("")
    if context:
        logger.info(f"CONTEXT:")
        logger.info(f"{context}")
        logger.info("")
    logger.info(f"USER MESSAGE:")
    logger.info(f"{message_text}")
    logger.info("")
    logger.info(f"FULL PROMPT LENGTH: {len(full_prompt)} characters")
    logger.info("=" * 80)
    
    # Generate response using Google Generative AI
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
    
    # Process Amy's response through memory systems
    memory_manager.process_message(
        session_id=session_id,
        platform="telegram",
        role="model",
        content=amy_response,
        user_id=user_id,
        username=username
    )
    
    # Log Amy's response
    logger.info(f"--- AMY RESPONSE ({timestamp}) ---")
    logger.info(f"Response: {amy_response}")
    
    # Send the response
    await update.message.reply_text(amy_response)

def main():
    """Start the bot."""
    logger.info("Starting Amy Telegram Bot with Memory System...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memory", memory_stats_command))
    application.add_handler(CommandHandler("debug", debug_prompt_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Start polling
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
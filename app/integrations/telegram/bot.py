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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    if update.message:
        welcome_message = "Hi! I'm Amy, your AI assistant with memory. I'll remember our conversations and learn about you over time. How can I help you today?"
        await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    if update.message:
        help_message = "I'm Amy, your AI assistant with memory! I can:\n• Remember our conversations\n• Learn about your preferences\n• Build context from past chats\n• Help you with various tasks\n\nJust send me a message and I'll respond with full context awareness!"
        await update.message.reply_text(help_message)

async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /memory command to show memory statistics."""
    if update.message:
        try:
            stats = memory_manager.get_memory_stats()
            stats_message = f"🧠 **Memory Statistics:**\n\n"
            stats_message += f"• Active sessions: {stats['stm']['active_sessions']}\n"
            stats_message += f"• Total conversations: {stats['mtm']['total_sessions']}\n"
            stats_message += f"• Facts stored: {sum(stats['ltm']['fact_types'].values())}\n\n"
            
            if stats['ltm']['fact_types']:
                stats_message += "**Fact Types:**\n"
                for fact_type, count in stats['ltm']['fact_types'].items():
                    stats_message += f"• {fact_type}: {count}\n"
            
            await update.message.reply_text(stats_message)
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            await update.message.reply_text("Sorry, I couldn't retrieve memory statistics right now.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a text message and pass it to Amy using the memory system."""
    if not update.message or not update.message.text or update.message.from_user is None or update.message.from_user.is_bot:
        logger.info("Ignoring non-text message or message from bot.")
        return

    user_message = update.message.text
    chat_id = str(update.message.chat_id)
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or 'unknown'
    
    # Create session ID for this conversation
    session_id = f"telegram_{chat_id}"
    
    # Log the user message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"--- USER MESSAGE ({timestamp}) ---")
    logger.info(f"User ID: {user_id}, Username: {username}, Chat ID: {chat_id}")
    logger.info(f"Message: {user_message}")
    
    try:
        # Process user message through memory system
        memory_manager.process_message(
            session_id=session_id,
            platform="telegram",
            role="user",
            content=user_message,
            user_id=user_id,
            username=username
        )
        
        # Build context for Amy's response
        context = memory_manager.get_context_for_query(session_id, user_message)
        
        # Create the conversation prompt with context
        system_prompt = "You are Amy, a helpful and friendly AI assistant with memory. You can remember past conversations and learn about users over time. Respond directly to the user's message in a conversational way, using context from previous conversations when relevant."
        
        # Build the full prompt with context
        if context:
            full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {user_message}\nAmy:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAmy:"
        
        # Log the context being used
        logger.info(f"--- CONTEXT FOR AMY ---")
        logger.info(f"Context length: {len(context)} characters")
        if context:
            logger.info(f"Context: {context[:200]}...")
        
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
        
        amy_response = response.text
        
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
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your message. Please try again.")

def main():
    """Start the bot."""
    logger.info("Starting Amy Telegram Bot with Memory System...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("memory", memory_stats_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
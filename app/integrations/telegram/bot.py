import os
import sys

# Add the project root to the Python path to resolve import issues
# The project root is 3 levels up from the current file's directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv, find_dotenv
import time
import random

# Import ADK components
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import Session as AdkSession # Alias to avoid conflict with telegram.Session

# Import Content from google.genai.types
from google.genai.types import Content

# Import Amy's root_agent directly
from app.core.amy_agent.agent import root_agent

def setup_logging():
    """Configures the logging for the application."""
    # Basic logging configuration
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # --- File Handler for General Logs ---
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    general_log_file = os.path.join(project_root, 'amy_telegram_bot.log')
    file_handler = logging.FileHandler(general_log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger.addHandler(file_handler)

    # --- Custom Handler for LLM Requests ---
    llm_log_file = os.path.join(project_root, 'llm_request_log.txt')
    
    class LLMRequestFileHandler(logging.Handler):
        def __init__(self, filename):
            super().__init__()
            self.filename = filename

        def emit(self, record):
            if record.name == 'google_adk.google.adk.models.google_llm' and 'LLM Request:' in record.msg:
                try:
                    with open(self.filename, 'a', encoding='utf-8') as f:
                        f.write(f"\n--- LLM Request ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
                        f.write(record.getMessage() + "\n")
                        f.write("---------------------------------------\n")
                except Exception as e:
                    # Use a different logger to avoid recursion if the root logger has issues
                    logging.getLogger(__name__).error(f"Failed to write LLM request to file: {e}")

    llm_request_handler = LLMRequestFileHandler(llm_log_file)
    root_logger.addHandler(llm_request_handler)

    # Set google.adk logging to a less verbose level unless debugging
    logging.getLogger('google.adk').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# --- Constants and Initial Setup ---
# Load environment variables from the .env file in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

logger = setup_logging()

# --- Telegram Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info("start command received.")
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I am Amy, your personal AI assistant. How can I help you today?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info("help command received.")
    await update.message.reply_text("I am Amy. You can chat with me by sending text messages.")

async def get_adk_response(runner: Runner, session_service: DatabaseSessionService, user_id: str, username: str, session_id: str, message: str) -> str:
    """
    Manages the ADK session and retrieves the agent's response.
    """
    try:
        logger.info(f"Getting ADK response for session: {session_id}")
        
        # Get or create session
        session = await session_service.get_session(
            app_name="amy_agent", user_id="telegram_user", session_id=session_id
        )
        if not session:
            logger.info(f"Creating new ADK session: {session_id}")
            await session_service.create_session(
                app_name="amy_agent", user_id="telegram_user", session_id=session_id
            )
        else:
            logger.info(f"Resuming ADK session: {session_id}")

        # Prepare content for the ADK agent
        adk_content = Content(parts=[{"text": message}])
        
        # Log the user message details
        log_user_message(user_id, username, session_id, message, adk_content)

        # Run the ADK agent
        response_text = ""
        async for event in runner.run_async(
            user_id="telegram_user",
            session_id=session_id,
            new_message=adk_content,
        ):
            logger.debug(f"ADK event received: {event}")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
        
        logger.info(f"Final ADK response: '{response_text}'")
        return response_text
        
    except Exception as e:
        logger.error(f"Error during ADK agent run: {e}", exc_info=True)
        return "Sorry, I encountered an error while processing your request."

def log_user_message(user_id: str, username: str, session_id: str, message: str, adk_content: Content):
    """Logs the user's message to the LLM request log file."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        llm_log_file = os.path.join(project_root, 'llm_request_log.txt')
        with open(llm_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n--- USER MESSAGE ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
            f.write(f"User ID: {user_id}, Username: {username}, Session ID: {session_id}\n")
            f.write(f"Message: {message}\n")
            f.write(f"Content object: {adk_content}\n")
            f.write("---------------------------------------\n")
    except Exception as e:
        logger.error(f"Failed to write user message to llm_request_log.txt: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a text message and pass it to Amy's ADK agent."""
    if not update.message or not update.message.text or update.message.from_user is None or update.message.from_user.is_bot:
        logger.info("Ignoring non-text message or message from bot.")
        return

    user_message = update.message.text
    chat_id = str(update.message.chat_id)
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or 'unknown'
    
    # Use persistent session ID based on chat_id to maintain conversation memory
    persistent_session_id = f"telegram_chat_{chat_id}"

    logger.info(f"Received message from user={username}({user_id}) in chat={chat_id}. Using session_id={persistent_session_id}")

    try:
        runner: Runner = context.bot_data["runner"]
        session_service: DatabaseSessionService = context.bot_data["session_service"]
    except KeyError:
        logger.error("Runner or SessionService not found in bot_data. Bot is not initialized correctly.", exc_info=True)
        await update.message.reply_text("Sorry, the bot is not properly initialized. Please contact the administrator.")
        return

    response_text = await get_adk_response(runner, session_service, user_id, username, persistent_session_id, user_message)

    if response_text:
        await update.message.reply_text(response_text)
    else:
        logger.warning("Amy didn't provide a response. Sending fallback message.")
        await update.message.reply_text("Amy didn't provide a response.")

def setup_adk() -> tuple[DatabaseSessionService, Runner]:
    """Initializes and returns the ADK Session Service and Runner."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, "instance", "amy_memory.db")
    db_url = f"sqlite:///{db_path}"
    
    logger.info(f"Initializing DatabaseSessionService with db_url: {db_url}")
    session_service = DatabaseSessionService(db_url=db_url)

    logger.info("Creating ADK Runner instance.")
    adk_runner = Runner(
        app_name="amy_agent",
        agent=root_agent,
        session_service=session_service,
    )
    return session_service, adk_runner

def setup_telegram_app(token: str, session_service: DatabaseSessionService, adk_runner: Runner) -> Application:
    """Builds and configures the Telegram Application."""
    logger.info("Building Telegram Application.")
    application = Application.builder().token(token).build()

    # Store ADK components in bot_data for access in handlers
    application.bot_data["runner"] = adk_runner
    application.bot_data["session_service"] = session_service
    logger.info("ADK Runner and SessionService stored in application.bot_data.")

    # Register command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Telegram handlers registered.")
    
    return application

def main() -> None:
    """Start the bot."""
    logger.info("Starting bot...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables. Please set it in the .env file.")
        return
    logger.info("TELEGRAM_BOT_TOKEN found.")

    # Set up ADK and Telegram application
    session_service, adk_runner = setup_adk()
    application = setup_telegram_app(token, session_service, adk_runner)

    # Start polling
    logger.info("Telegram bot started. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
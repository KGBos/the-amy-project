import os
import logging
import sys
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

# Load environment variables from .env file
load_dotenv(dotenv_path=find_dotenv('app/.env'))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add file handler for general logs (alongside LLM request log)
GENERAL_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'amy_telegram_bot.log')
file_handler = logging.FileHandler(GENERAL_LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)

# Set google.adk logging to DEBUG for detailed output (might not be fully effective)
logging.getLogger('google.adk').setLevel(logging.DEBUG)

# --- Custom LLM Request Logger ---
LLM_REQUEST_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'llm_request_log.txt')

class LLMRequestFileHandler(logging.Handler):
    def emit(self, record):
        if record.name == 'google_adk.google.adk.models.google_llm' and 'LLM Request:' in record.msg:
            try:
                with open(LLM_REQUEST_LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"\n--- LLM Request ({record.asctime}) ---\n")
                    f.write(record.msg + "\n")
                    f.write("---------------------------------------\n")
            except Exception as e:
                logger.error(f"Failed to write LLM request to file: {e}")

llm_request_file_handler = LLMRequestFileHandler()
logging.getLogger().addHandler(llm_request_file_handler)
# --- End Custom LLM Request Logger ---

# Define a few command handlers.
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle a text message and pass it to Amy's ADK agent."""
    logger.info("handle_message: Function started.")
    print(f"RAW UPDATE OBJECT: {update}", file=sys.stderr) # Direct print to stderr

    # Ensure it's a text message and not from a bot
    if not update.message or not update.message.text or update.message.from_user is None or update.message.from_user.is_bot:
        logger.info("handle_message: Ignoring non-text message or message from bot.")
        return

    user_message = update.message.text
    # Use a unique session_id for each conversation to avoid restoring old state
    chat_id = str(update.message.chat_id)
    unique_session_id = f"{chat_id}-{int(time.time())}-{random.randint(1000,9999)}"
    user_id = update.message.from_user.id if update.message.from_user else 'unknown'
    username = update.message.from_user.username if update.message.from_user else 'unknown'
    logger.info(f"handle_message: Received message from user_id={user_id}, username={username}, chat_id={chat_id}: '{user_message}'")

    try:
        runner: Runner = context.bot_data["runner"]
        session_service: DatabaseSessionService = context.bot_data["session_service"]
        logger.info("handle_message: Runner and SessionService instances retrieved from bot_data.")
    except KeyError:
        logger.error("handle_message: Runner or SessionService not found in bot_data. This indicates a setup issue.", exc_info=True)
        await update.message.reply_text("Sorry, the bot is not properly initialized. Please contact the administrator.")
        return

    try:
        # Get or create session
        session = await session_service.get_session(
            app_name="amy_agent", user_id="telegram_user", session_id=unique_session_id
        )
        if not session:
            logger.info(f"handle_message: Session {unique_session_id} not found. Creating new session.")
            session = await session_service.create_session(
                app_name="amy_agent", user_id="telegram_user", session_id=unique_session_id
            )
        else:
            logger.info(f"handle_message: Session {unique_session_id} found. Resuming conversation.")

        # Create content object for ADK agent directly using google.genai.types.Content
        adk_content = Content(parts=[{"text": user_message}])
        logger.info(f"handle_message: Content object prepared for ADK: {adk_content}") # Log the content object
        logger.info(f"handle_message: SENDING TO LLM: {adk_content}")

        # Log the actual user message to llm_request_log.txt
        try:
            with open(LLM_REQUEST_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n--- USER MESSAGE ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---\n")
                f.write(f"User ID: {user_id}, Username: {username}, Session ID: {unique_session_id}\n")
                f.write(f"Message: {user_message}\n")
                f.write(f"Content object: {adk_content}\n")
                f.write("---------------------------------------\n")
        except Exception as e:
            logger.error(f"Failed to write user message to llm_request_log.txt: {e}")

        response_text = ""
        logger.info(f"handle_message: Calling runner.run_async for session {chat_id} with new_message: {adk_content}") # Updated log message
        async for event in runner.run_async(
            user_id="telegram_user", # A generic user ID for Telegram
            session_id=unique_session_id,
            new_message=adk_content,
        ):
            logger.debug(f"handle_message: Received event from ADK: {event}")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
                        logger.debug(f"handle_message: Appended text part: '{part.text}'")

        logger.info(f"handle_message: LLM RESPONSE: '{response_text}'")

        if response_text:
            logger.info(f"handle_message: Sending response to Telegram: '{response_text}'")
            await update.message.reply_text(response_text)
        else:
            logger.warning("handle_message: Amy didn't provide a response. Sending fallback message.")
            await update.message.reply_text("Amy didn't provide a response.")

    except Exception as e:
        logger.error(f"handle_message: Unhandled exception during ADK agent run: {e}", exc_info=True)
        await update.message.reply_text("Sorry, I encountered an error while processing your request.")

def main() -> None:
    """Start the bot."""
    logger.info("main: Function started.")
    # Get the bot token from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("main: TELEGRAM_BOT_TOKEN not found in .env file. Please set it.")
        return
    logger.info("main: TELEGRAM_BOT_TOKEN found.")

    # Set up DatabaseSessionService
    db_url = "sqlite:///./app/amy_memory.db"
    logger.info(f"main: Initializing DatabaseSessionService with db_url: {db_url}")
    session_service = DatabaseSessionService(db_url=db_url)

    # Create the Runner instance
    logger.info("main: Creating Runner instance.")
    adk_runner = Runner(
        app_name="amy_agent",
        agent=root_agent,
        session_service=session_service,
    )
    logger.info("main: Runner instance created.")

    # Create the Application and pass it your bot's token.
    logger.info("main: Building Telegram Application.")
    application = Application.builder().token(token).build()
    logger.info("main: Telegram Application built.")

    # Store the runner and session_service in bot_data so they can be accessed by handlers
    application.bot_data["runner"] = adk_runner
    application.bot_data["session_service"] = session_service # Store session_service
    logger.info("main: Runner and SessionService stored in application.bot_data.")

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # On non-command messages - pass to Amy's agent
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("main: Message handlers added.")
    logger.info("Telegram bot started. Press Ctrl-C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
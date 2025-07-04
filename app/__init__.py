import logging

from google.adk.app import AdkApp
from google.adk.sessions import DatabaseSessionService

from .amy_agent.agent import root_agent

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Initializing AdkApp and Session Service Builder")

def session_service_builder():
    logger.info("session_service_builder called.")
    db_url = "sqlite:///./amy_memory.db"
    logger.info(f"Using database URL: {db_url}")
    return DatabaseSessionService(db_url=db_url)

adk_app = AdkApp(root_agent=root_agent, session_service_builder=session_service_builder)
logger.info("AdkApp instance created.")
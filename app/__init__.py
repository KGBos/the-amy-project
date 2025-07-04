import logging

# Configure logging for __init__.py
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("app/__init__.py: Starting initialization")

from .core.amy_agent.agent import root_agent
logger.info("app/__init__.py: root_agent imported.")

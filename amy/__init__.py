import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("amy/__init__.py: Starting initialization")

# New simplified memory system
from .features.memory import ConversationDB, LTM
logger.info("amy/__init__.py: Memory system imported.")

import logging

# Configure logging for __init__.py
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("app/__init__.py: Starting initialization")

# Memory system imports
from .features.memory import MemoryManager, ShortTermMemory, LongTermMemory, EpisodicMemory
logger.info("app/__init__.py: Memory system imported.")

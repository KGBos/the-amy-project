"""
Amy - AI Assistant with Memory
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Core exports
from .core.amy import Amy, get_brain
from .memory import ConversationDB, LTM

__all__ = [
    'Amy',
    'get_brain',
    'ConversationDB',
    'LTM',
]

logger.info("Amy initialized")

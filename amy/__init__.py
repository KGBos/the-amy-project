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
from .core.factory import create_amy_runner
from .memory import ConversationDB, LTM

__all__ = [
    'create_amy_runner',
    'ConversationDB',
    'LTM',
]

logger.info("Amy initialized")

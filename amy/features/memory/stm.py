"""
Short-Term Memory (STM) for Amy
Handles immediate conversation context and recent message history
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ShortTermMemory:
    """
    Short-Term Memory system for immediate conversation context.
    Stores recent messages in memory for fast access.
    """
    
    def __init__(self, max_messages: int = 20):
        """
        Initialize STM with configurable message limit.
        
        Args:
            max_messages: Maximum number of messages to keep in memory
        """
        self.max_messages = max_messages
        self.conversations: Dict[str, List[dict]] = {}
        
    def add_message(self, session_id: str, role: str, content: str, timestamp: Optional[datetime] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Unique identifier for the conversation session
            role: 'user' or 'model' (Amy)
            content: The message content
            timestamp: When the message was sent (defaults to now)
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            
        message = {
            'role': role,
            'content': content,
            'timestamp': timestamp or datetime.now()
        }
        
        self.conversations[session_id].append(message)
        
        # Keep only the most recent messages
        if len(self.conversations[session_id]) > self.max_messages:
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages:]
            
        logger.debug(f"Added message to STM for session {session_id}: {role}: {content[:50]}...")
        
    def get_context(self, session_id: str) -> List[dict]:
        """
        Get the conversation context for a session.
        
        Args:
            session_id: The session to get context for
            
        Returns:
            List of recent messages in the conversation
        """
        return self.conversations.get(session_id, [])
        
    def clear_session(self, session_id: str) -> None:
        """
        Clear the conversation history for a session.
        
        Args:
            session_id: The session to clear
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared STM for session {session_id}")
            
    def get_all_sessions(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List of session IDs with active conversations
        """
        return list(self.conversations.keys()) 
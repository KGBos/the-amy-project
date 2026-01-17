"""
User Session Manager for Amy
Tracks user sessions and provides appropriate greetings
"""

import logging

logger = logging.getLogger(__name__)


class UserSessionManager:
    """
    Manages user sessions and provides appropriate greetings.
    """
    
    def __init__(self):
        self.user_sessions = {}  # Track user session history
    
    def is_new_user(self, user_id: str, session_id: str) -> bool:
        """
        Check if this is a new user or new session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if new user/session, False if returning user
        """
        # Check if we've seen this user before
        if user_id not in self.user_sessions:
            return True  # New user
        
        # Check if this is a new session for existing user
        if session_id not in self.user_sessions[user_id]:
            return True  # Existing user, but new session
        
        return False  # Existing user and existing session
    
    def get_greeting(self, user_id: str, session_id: str) -> str:
        """
        Get appropriate greeting based on user history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Appropriate greeting message
        """
        if self.is_new_user(user_id, session_id):
            return "Hi! I'm Amy, your AI assistant. How can I help you today?"
        else:
            return "Hi again! How can I help you today?"
    
    def record_session(self, user_id: str, session_id: str):
        """
        Record that a user has started a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        
        self.user_sessions[user_id].add(session_id)
    
    def get_user_session_count(self, user_id: str) -> int:
        """
        Get the number of sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of sessions for this user
        """
        return len(self.user_sessions.get(user_id, set()))

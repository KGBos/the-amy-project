"""
Memory Manager for Amy
Orchestrates STM, EpTM, and LTM systems and provides unified interface
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import os
import json
import sqlite3

from .stm import ShortTermMemory
from .ltm import LTM as LongTermMemory
from .episodic import EpisodicMemory
from .session_manager import UserSessionManager
from .context_builder import SmartContextBuilder

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Unified memory manager that coordinates STM, EpTM, and LTM systems.
    Provides a single interface for all memory operations.
    """
    
    def __init__(self, db_path: str = "instance/amy_memory.db", vector_db_path: str = "instance/vector_db"):
        """
        Initialize the memory manager with memory systems.
        
        Args:
            db_path: Path to the SQLite database for EpTM
            vector_db_path: Path to the vector database for LTM
        """
        self.db_path = db_path
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory(vector_db_path)
        self.episodic = EpisodicMemory(db_path)
        self.context_builder = SmartContextBuilder(max_length=500)
        self.user_session_manager = UserSessionManager()
        
        # Load previous conversations and extract facts
        self._load_previous_conversations()
        
    def _load_previous_conversations(self) -> None:
        """
        Load previous conversations from database and extract facts for LTM.
        This ensures Amy remembers information across sessions.
        """
        if not os.path.exists(self.db_path):
            logger.info("No existing database found. Starting with fresh memory.")
            return
            
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Get all messages from previous conversations
                cursor.execute("""
                    SELECT m.content, m.role, m.timestamp, c.session_id, c.user_id, c.username
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    ORDER BY m.timestamp
                """)
                
                messages = cursor.fetchall()
            
            if not messages:
                logger.info("No previous conversations found in database.")
                return
                
            logger.info(f"Loading {len(messages)} previous messages into memory...")
            
            # Extract facts from previous conversations
            conversation_messages = []
            for content, role, timestamp, session_id, user_id, username in messages:
                conversation_messages.append({
                    'role': role,
                    'content': content,
                    'timestamp': timestamp,
                    'session_id': session_id,
                    'user_id': user_id,
                    'username': username
                })
                
                # Process in batches to avoid overwhelming the system
                if len(conversation_messages) >= 50:
                    self._extract_facts_from_batch(conversation_messages)
                    conversation_messages = []
            
            # Process remaining messages
            if conversation_messages:
                self._extract_facts_from_batch(conversation_messages)
                
            logger.info("Finished loading previous conversations into LTM.")
            
        except Exception as e:
            logger.error(f"Error loading previous conversations: {e}")
            
    def _load_previous_conversations_for_user(self, user_id: str) -> None:
        """
        Load previous conversations from database for a specific user and extract facts for LTM.
        This ensures Amy remembers information across sessions for the specific user.
        
        Args:
            user_id: The user ID to load conversations for
        """
        if not os.path.exists(self.db_path):
            logger.info("No existing database found. Starting with fresh memory.")
            return
            
        try:
            with sqlite3.connect(self.db_path, timeout=30.0) as conn:
                cursor = conn.cursor()
                
                # Get messages from previous conversations for this specific user
                cursor.execute("""
                    SELECT m.content, m.role, m.timestamp, c.session_id, c.user_id, c.username
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ?
                    ORDER BY m.timestamp
                """, (user_id,))
                
                messages = cursor.fetchall()
            
            if not messages:
                logger.info(f"No previous conversations found for user {user_id}.")
                return
                
            logger.info(f"Loading {len(messages)} previous messages for user {user_id} into memory...")
            
            # Extract facts from previous conversations
            conversation_messages = []
            for content, role, timestamp, session_id, user_id, username in messages:
                conversation_messages.append({
                    'role': role,
                    'content': content,
                    'timestamp': timestamp,
                    'session_id': session_id,
                    'user_id': user_id,
                    'username': username
                })
                
                # Process in batches to avoid overwhelming the system
                if len(conversation_messages) >= 50:
                    self._extract_facts_from_batch(conversation_messages)
                    conversation_messages = []
            
            # Process remaining messages
            if conversation_messages:
                self._extract_facts_from_batch(conversation_messages)
                
            logger.info(f"Finished loading previous conversations for user {user_id} into LTM.")
            
        except Exception as e:
            logger.error(f"Error loading previous conversations for user {user_id}: {e}")
        
    def _extract_facts_from_batch(self, messages: List[Dict]) -> None:
        """
        Extract facts from a batch of messages and store them in LTM.
        
        Args:
            messages: List of message dictionaries
        """
        try:
            facts = self.ltm.extract_facts_from_conversation(messages)
            for fact_content, fact_type in facts:
                try:
                    self.ltm.store_fact(fact_content, fact_type)
                except Exception as e:
                    logger.warning(f"Failed to store fact '{fact_content[:50]}...' of type '{fact_type}': {e}")
        except Exception as e:
            logger.error(f"Error extracting facts from batch: {e}")
        
    def process_message(self, session_id: str, platform: str, role: str, content: str, 
                       user_id: Optional[str] = None, username: Optional[str] = None) -> None:
        """
        Process a message through all memory systems.
        
        Args:
            session_id: Unique session identifier
            platform: Platform name (telegram, web, etc.)
            role: 'user' or 'model'
            content: Message content
            user_id: User identifier
            username: Username
        """
        timestamp = datetime.now()
        
        # Add to STM (immediate context)
        self.stm.add_message(session_id, role, content, timestamp)
        
        # Add to EpTM (conversation storage)
        self.episodic.add_message(session_id, role, content, timestamp)
        
        # Create session in EpTM only if this is the first message in the session
        if user_id and platform and len(self.stm.get_context(session_id)) == 1:
            self.episodic.create_session(session_id, user_id, platform)
        
        # Extract facts for LTM (if user message)
        if role == 'user':
            facts = self.ltm.extract_facts_from_conversation([{'role': role, 'content': content}])
            for fact_content, fact_type in facts:
                try:
                    self.ltm.store_fact(fact_content, fact_type, user_id)
                except Exception as e:
                    logger.warning(f"Failed to process fact '{fact_content}' of type '{fact_type}': {e}")
                
        logger.info(f"Processed message through memory systems: {session_id} - {role}")
        
    def get_context_for_query(self, session_id: str, query: str, user_id: Optional[str] = None) -> str:
        """
        Build smart context for a query with length limits and relevance scoring.
        
        Args:
            session_id: Current session ID
            query: The user's query
            user_id: User ID for filtering LTM search results
            
        Returns:
            Smart, truncated context string (max 500 characters)
        """
        # Get STM context (recent conversation)
        stm_context = self.stm.get_context(session_id)
        
        # Get EpTM context (conversation summary)
        episodic_context = self.episodic.get_context(session_id, query)
        
        # Get LTM context (relevant facts) - filter by user_id
        ltm_context = self.ltm.build_context_from_query(query, user_id)
        
        # Build smart context with limits (includes episodic context if space allows)
        context = self.context_builder.build_context(stm_context, ltm_context, query, episodic_context)
        
        # Log context length for monitoring
        logger.info(f"Built context: {len(context)} characters")
        
        return context
        
    def search_conversations(self, query: str) -> List[Dict]:
        """
        Search all conversations across platforms.
        
        Args:
            query: Search term
            
        Returns:
            List of matching conversations
        """
        return self.episodic.search_conversations(query)
        
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all conversation sessions.
        
        Returns:
            List of session information
        """
        return self.episodic.get_all_sessions()
        
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """
        Get all messages for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages
        """
        return self.episodic.get_session_messages(session_id)
        
    def clear_session(self, session_id: str) -> None:
        """
        Clear a session from STM (EpTM and LTM are permanent).
        
        Args:
            session_id: Session to clear
        """
        self.stm.clear_session(session_id)
        logger.info(f"Cleared STM for session {session_id}")
        
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all memory systems.
        
        Returns:
            Dictionary with memory statistics
        """
        episodic_stats = self.episodic.get_session_stats()
        
        stats = {
            'stm': {
                'active_sessions': len(self.stm.get_all_sessions())
            },
            'episodic': episodic_stats,
            'ltm': {
                'fact_types': self._get_ltm_fact_types()
            }
        }
        
        return stats
        
    def _get_ltm_fact_types(self) -> Dict[str, int]:
        """
        Get count of facts by type in LTM.
        
        Returns:
            Dictionary of fact types and counts
        """
        fact_types = {}
        
        if os.path.exists(self.ltm.vector_db_path):
            for filename in os.listdir(self.ltm.vector_db_path):
                if filename.endswith('.json'):
                    fact_file = os.path.join(self.ltm.vector_db_path, filename)
                    try:
                        with open(fact_file, 'r') as f:
                            fact_data = json.load(f)
                            fact_type = fact_data.get('type', 'unknown')
                            fact_types[fact_type] = fact_types.get(fact_type, 0) + 1
                    except Exception:
                        continue
                    
        return fact_types
    
    def is_new_user(self, user_id: str, session_id: str) -> bool:
        """
        Check if this is a new user or new session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if new user/session, False if returning user
        """
        return self.user_session_manager.is_new_user(user_id, session_id)
    
    def get_greeting(self, user_id: str, session_id: str) -> str:
        """
        Get appropriate greeting based on user history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Appropriate greeting message
        """
        return self.user_session_manager.get_greeting(user_id, session_id)
    
    def record_user_session(self, user_id: str, session_id: str):
        """
        Record that a user has started a session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        self.user_session_manager.record_session(user_id, session_id)
    
    def get_user_session_count(self, user_id: str) -> int:
        """
        Get the number of sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of sessions for this user
        """
        return self.user_session_manager.get_user_session_count(user_id)
    
    def get_detailed_memory_state(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed memory state for debugging.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID
            
        Returns:
            Detailed memory state dictionary
        """
        try:
            # Get STM state
            stm_context = self.stm.get_context(session_id)
            stm_messages = len(stm_context) if stm_context else 0
            
            # Get EpTM state
            episodic_messages = self.episodic.get_session_messages(session_id)
            episodic_count = len(episodic_messages) if episodic_messages else 0
            
            # Get LTM state
            ltm_stats = self._get_ltm_fact_types()
            total_facts = sum(ltm_stats.values())
            
            # Get user session state
            user_session_count = self.get_user_session_count(user_id) if user_id else 0
            is_new_user = self.is_new_user(user_id, session_id) if user_id else None
            
            return {
                'session_id': session_id,
                'user_id': user_id,
                'stm': {
                    'active_sessions': len(self.stm.get_all_sessions()),
                    'messages_in_session': stm_messages,
                    'recent_messages': stm_context[-3:] if stm_context else []
                },
                'episodic': {
                    'messages_in_session': episodic_count,
                    'session_exists': episodic_count > 0
                },
                'ltm': {
                    'total_facts': total_facts,
                    'fact_types': ltm_stats
                },
                'user_session': {
                    'session_count': user_session_count,
                    'is_new_user': is_new_user
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting detailed memory state: {e}")
            return {'error': str(e)} 
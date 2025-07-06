"""
Memory Manager for Amy
Orchestrates STM, EpTM, and LTM systems and provides unified interface
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import os
import json

from .stm import ShortTermMemory
from .ltm import LTM as LongTermMemory

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
            db_path: Path to the SQLite database for EpTM (coming soon)
            vector_db_path: Path to the vector database for LTM
        """
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory(vector_db_path)
        # TODO: Add EpTM when implemented
        # self.episodic = EpisodicMemory(db_path)
        
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
        
        # TODO: Add to EpTM when implemented
        # self.episodic.add_message(session_id, role, content, timestamp)
        
        # Extract facts for LTM (if user message)
        if role == 'user':
            facts = self.ltm.extract_facts_from_conversation([{'role': role, 'content': content}])
            for fact_content, fact_type in facts:
                try:
                    self.ltm.store_fact(fact_content, fact_type)
                except Exception as e:
                    logger.warning(f"Failed to process fact '{fact_content}' of type '{fact_type}': {e}")
                
        logger.info(f"Processed message through memory systems: {session_id} - {role}")
        
    def get_context_for_query(self, session_id: str, query: str) -> str:
        """
        Build comprehensive context for a query using all memory systems.
        
        Args:
            session_id: Current session ID
            query: The user's query
            
        Returns:
            Comprehensive context string
        """
        context_parts = []
        
        # Get STM context (recent conversation)
        stm_context = self.stm.get_context(session_id)
        if stm_context:
            context_parts.append("Recent conversation:")
            for msg in stm_context[-5:]:  # Last 5 messages
                role = msg['role']
                content = msg['content']
                context_parts.append(f"{role}: {content}")
            context_parts.append("")
            
        # TODO: Get EpTM context when implemented
        # episodic_context = self.episodic.get_context(session_id, query)
        # if episodic_context:
        #     context_parts.append(episodic_context)
        #     context_parts.append("")
            
        # Get LTM context (relevant facts)
        ltm_context = self.ltm.build_context_from_query(query)
        if ltm_context:
            context_parts.append(ltm_context)
            context_parts.append("")
            
        return "\n".join(context_parts)
        
    def search_conversations(self, query: str) -> List[Dict]:
        """
        Search all conversations across platforms.
        
        Args:
            query: Search term
            
        Returns:
            List of matching conversations
        """
        # TODO: Implement when EpTM is ready
        logger.warning("Conversation search not yet implemented - EpTM coming soon")
        return []
        
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all conversation sessions.
        
        Returns:
            List of session information
        """
        # TODO: Implement when EpTM is ready
        logger.warning("Session listing not yet implemented - EpTM coming soon")
        return []
        
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """
        Get all messages for a specific session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages
        """
        # TODO: Implement when EpTM is ready
        logger.warning("Session messages not yet implemented - EpTM coming soon")
        return []
        
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
        stats = {
            'stm': {
                'active_sessions': len(self.stm.get_all_sessions())
            },
            'episodic': {
                'total_sessions': 0  # TODO: Implement when EpTM is ready
            },
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
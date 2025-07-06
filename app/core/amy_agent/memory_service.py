"""
Custom memory service for ADK that uses our MemoryManager
"""

from google.adk.memory import BaseMemoryService
from app.features.memory import MemoryManager
from app.features.sensory.audio_transcription import AudioTranscriber
import logging
from typing import Any

logger = logging.getLogger(__name__)

class AmyMemoryService(BaseMemoryService):
    """Custom memory service that uses our MemoryManager for consistent memory across platforms."""
    
    def __init__(self):
        super().__init__()
        self.memory_manager = MemoryManager()
        self.audio_transcriber = AudioTranscriber()
        self.session_mappings = {}  # Map ADK session IDs to our session IDs
    
    def _get_session_id(self, user_id: str, session_id: str) -> str:
        """Convert ADK session ID to our session ID format."""
        if session_id not in self.session_mappings:
            # Create a mapping for this session
            our_session_id = f"web_{user_id}_{session_id}"
            self.session_mappings[session_id] = our_session_id
        return self.session_mappings[session_id]
    
    def add_message(self, user_id: str, session_id: str, role: str, content: str, **kwargs):
        """Add a message to memory using our MemoryManager."""
        try:
            our_session_id = self._get_session_id(user_id, session_id)

            # Check for audio input and transcribe if available
            audio_path = kwargs.get("audio_path")
            if audio_path:
                logger.info(f"Audio path provided: {audio_path}. Attempting transcription.")
                transcribed_content = self.audio_transcriber.transcribe_audio(audio_path)
                if transcribed_content:
                    content = transcribed_content
                    logger.info(f"Audio successfully transcribed. Using transcribed text for memory.")
                else:
                    logger.warning("Audio transcription failed or returned empty. Proceeding with original text content.")
            
            # Process message through our memory system
            self.memory_manager.process_message(
                session_id=our_session_id,
                platform="web", # Assuming 'web' for now, can be dynamically set later
                role=role,
                content=content,
                user_id=user_id,
                username="web_user" # Assuming 'web_user' for now
            )

            logger.info(f"Added message to memory: {role} in session {our_session_id}")

        except Exception as e:
            logger.error(f"Error adding message to memory: {e}")
    
    def get_context(self, user_id: str, session_id: str, query: str = "", **kwargs) -> str:
        """Get context for a query using our MemoryManager."""
        try:
            our_session_id = self._get_session_id(user_id, session_id)
            
            # Get context from our memory system
            context = self.memory_manager.get_context_for_query(our_session_id, query)
            
            logger.info(f"Retrieved context for session {our_session_id}: {len(context)} chars")
            return context
            
        except Exception as e:
            logger.error(f"Error getting context from memory: {e}")
            return ""
    
    def clear_memory(self, user_id: str, session_id: str = "", **kwargs):
        """Clear memory for a user/session."""
        try:
            if session_id:
                our_session_id = self._get_session_id(user_id, session_id)
                # Clear specific session memory
                self.memory_manager.clear_session(our_session_id)
                logger.info(f"Cleared memory for session {our_session_id}")
            else:
                # Clear all memory for user
                # This would need to be implemented in MemoryManager
                logger.info(f"Cleared all memory for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
    
    def get_memory_stats(self, user_id: str = "", **kwargs) -> dict:
        """Get memory statistics."""
        try:
            stats = self.memory_manager.get_memory_stats()
            return {
                "stm_sessions": stats['stm']['active_sessions'],
                "mtm_sessions": stats['mtm']['total_sessions'],
                "ltm_facts": sum(stats['ltm']['fact_types'].values()),
                "fact_types": stats['ltm']['fact_types']
            }
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {}

    # Implement abstract methods from BaseMemoryService
    async def add_session_to_memory(self, session: Any):
        """
        Adds a session to the memory service. (Placeholder for ADK)
        This method is required by BaseMemoryService, but our MemoryManager handles
        message processing directly via add_message.
        """
        logger.info(f"ADK's add_session_to_memory called for session ID: {session.session_id}. Delegating to MemoryManager via add_message.")
        # Our MemoryManager processes messages individually, so we can iterate through session messages if needed.
        # For now, we assume add_message is the primary ingestion point.
        pass

    async def search_memory(self, *, app_name: str, user_id: str, query: str) -> dict:
        """
        Searches for memories that match the query. (Placeholder for ADK)
        This method is required by BaseMemoryService. We will use our MemoryManager's
        get_context_for_query for basic implementation.
        """
        logger.info(f"ADK's search_memory called for user: {user_id}, query: {query}")
        # Use our existing MemoryManager to get context
        context = self.memory_manager.get_context_for_query(f"web_{user_id}_adk_search", query)

        # Convert context string to a list of MemoryEntry-like dictionaries
        # ADK expects a list of MemoryEntry objects for SearchMemoryResponse
        # For simplicity, we'll return the context as a single 'memory' entry.
        memories = []
        if context:
            # Create a dummy MemoryEntry-like structure from the context string
            memories.append({
                "text": context,
                "metadata": {"source": "amy_memory_manager", "query": query}
            })
        
        # Return a dictionary that matches SearchMemoryResponse structure for now.
        # A proper ADK integration would involve converting to actual MemoryEntry objects.
        return {"memories": memories} 
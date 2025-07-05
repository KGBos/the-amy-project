"""
Long-Term Memory (LTM) for Amy
Handles semantic search and knowledge storage using vector embeddings
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import os

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    Long-Term Memory system for semantic knowledge storage and retrieval.
    Uses vector embeddings for similarity search and fact extraction.
    """
    
    def __init__(self, vector_db_path: str = "instance/vector_db"):
        """
        Initialize LTM with vector database path.
        
        Args:
            vector_db_path: Path to the vector database storage
        """
        self.vector_db_path = vector_db_path
        self._ensure_db_exists()
        
    def _ensure_db_exists(self) -> None:
        """Ensure the vector database directory exists."""
        os.makedirs(self.vector_db_path, exist_ok=True)
        
    def store_fact(self, fact_type: str, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Store a fact in long-term memory.
        
        Args:
            fact_type: Type of fact (preference, relationship, goal, etc.)
            content: The fact content
            metadata: Additional metadata
            
        Returns:
            Fact ID
        """
        fact_id = f"{fact_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        fact_data = {
            'id': fact_id,
            'type': fact_type,
            'content': content,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'embedding': None  # Will be computed when embedding model is available
        }
        
        # Store in JSON file for now (will be replaced with proper vector DB)
        fact_file = os.path.join(self.vector_db_path, f"{fact_id}.json")
        with open(fact_file, 'w') as f:
            json.dump(fact_data, f, indent=2)
            
        logger.info(f"Stored fact in LTM: {fact_type} - {content[:50]}...")
        return fact_id
        
    def search_facts(self, query: str, fact_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search for facts by content similarity.
        
        Args:
            query: Search query
            fact_type: Optional filter by fact type
            limit: Maximum number of results
            
        Returns:
            List of matching facts
        """
        results = []
        
        # Simple text search for now (will be replaced with vector similarity)
        for filename in os.listdir(self.vector_db_path):
            if filename.endswith('.json'):
                fact_file = os.path.join(self.vector_db_path, filename)
                try:
                    with open(fact_file, 'r') as f:
                        fact_data = json.load(f)
                        
                    # Filter by type if specified
                    if fact_type and fact_data.get('type') != fact_type:
                        continue
                        
                    # Simple text matching (will be replaced with embedding similarity)
                    if query.lower() in fact_data.get('content', '').lower():
                        results.append(fact_data)
                        
                except Exception as e:
                    logger.warning(f"Error reading fact file {filename}: {e}")
                    
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return results[:limit]
        
    def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """
        Get all facts of a specific type.
        
        Args:
            fact_type: Type of facts to retrieve
            
        Returns:
            List of facts of the specified type
        """
        results = []
        
        for filename in os.listdir(self.vector_db_path):
            if filename.endswith('.json'):
                fact_file = os.path.join(self.vector_db_path, filename)
                try:
                    with open(fact_file, 'r') as f:
                        fact_data = json.load(f)
                        
                    if fact_data.get('type') == fact_type:
                        results.append(fact_data)
                        
                except Exception as e:
                    logger.warning(f"Error reading fact file {filename}: {e}")
                    
        return results
        
    def extract_facts_from_conversation(self, messages: List[Dict]) -> List[str]:
        """
        Extract potential facts from a conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of extracted facts
        """
        facts = []
        
        for message in messages:
            content = message.get('content', '')
            role = message.get('role', '')
            
            # Simple fact extraction patterns (will be enhanced with NLP)
            if role == 'user':
                # Look for preference statements
                if any(phrase in content.lower() for phrase in ['i like', 'i prefer', 'i love', 'i hate']):
                    facts.append(f"preference: {content}")
                    
                # Look for relationship information
                if any(phrase in content.lower() for phrase in ['my name is', 'i am', 'i work at', 'i live in']):
                    facts.append(f"personal_info: {content}")
                    
                # Look for goals and plans
                if any(phrase in content.lower() for phrase in ['i want to', 'i plan to', 'i need to', 'my goal is']):
                    facts.append(f"goal: {content}")
                    
        return facts
        
    def build_context_from_query(self, query: str) -> str:
        """
        Build relevant context for a query using LTM.
        
        Args:
            query: The current query
            
        Returns:
            Relevant context string
        """
        # Search for relevant facts
        relevant_facts = self.search_facts(query, limit=5)
        
        if not relevant_facts:
            return ""
            
        context_parts = ["Relevant information from previous conversations:"]
        
        for fact in relevant_facts:
            fact_type = fact.get('type', 'unknown')
            content = fact.get('content', '')
            context_parts.append(f"- {fact_type}: {content}")
            
        return "\n".join(context_parts) 
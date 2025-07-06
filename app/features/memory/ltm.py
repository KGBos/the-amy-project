"""
Long-Term Memory (LTM) for Amy using Mem0
Handles semantic search and knowledge storage using Mem0 vector database
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import os

try:
    import mem0
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    logging.warning("Mem0 not available, falling back to JSON storage")

logger = logging.getLogger(__name__)

class LongTermMemory:
    """
    Long-Term Memory system using Mem0 for semantic knowledge storage and retrieval.
    Uses vector embeddings for similarity search and fact extraction.
    """
    
    def __init__(self, vector_db_path: str = "instance/vector_db"):
        """
        Initialize LTM with Mem0 vector database.
        
        Args:
            vector_db_path: Path to the vector database storage
        """
        self.vector_db_path = vector_db_path
        self._ensure_db_exists()
        
        if MEM0_AVAILABLE:
            try:
                # Configure Mem0 with local file storage (Milvus Lite)
                config = {
                    "vector_store": {
                        "provider": "milvus",
                        "config": {
                            "collection_name": "amy_ltm",
                            "embedding_model_dims": "1536",
                            "url": f"{vector_db_path}/milvus.db",  # Local file storage
                        },
                    },
                    "version": "v1.1",
                }
                
                # Initialize Mem0 memory
                self.memory = Memory.from_config(config)
                logger.info("Initialized Mem0-based LTM with local Milvus storage")
            except Exception as e:
                logger.error(f"Failed to initialize Mem0: {e}")
                self.memory = None
        else:
            self.memory = None
            logger.warning("Mem0 not available, using JSON fallback")
        
    def _ensure_db_exists(self) -> None:
        """Ensure the vector database directory exists."""
        os.makedirs(self.vector_db_path, exist_ok=True)
        
    def store_fact(self, fact_type: str, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Store a fact in long-term memory using Mem0.
        
        Args:
            fact_type: Type of fact (preference, relationship, goal, etc.)
            content: The fact content
            metadata: Additional metadata
            
        Returns:
            Fact ID
        """
        fact_id = f"{fact_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if MEM0_AVAILABLE and self.memory:
            try:
                # Store in Mem0 with metadata
                fact_metadata = {
                    'id': fact_id,
                    'type': fact_type,
                    'created_at': datetime.now().isoformat(),
                    **(metadata or {})
                }
                
                # Add to Mem0 memory
                result = self.memory.add(
                    messages=content,
                    user_id="amy_user",
                    metadata=fact_metadata
                )
                
                logger.info(f"Stored fact in Mem0 LTM: {fact_type} - {content[:50]}...")
                return fact_id
                
            except Exception as e:
                logger.error(f"Failed to store fact in Mem0: {e}")
                # Fall back to JSON storage
                return self._store_fact_json(fact_id, fact_type, content, metadata)
        else:
            # Fall back to JSON storage
            return self._store_fact_json(fact_id, fact_type, content, metadata)
    
    def _store_fact_json(self, fact_id: str, fact_type: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Fallback JSON storage method."""
        fact_data = {
            'id': fact_id,
            'type': fact_type,
            'content': content,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'embedding': None
        }
        
        fact_file = os.path.join(self.vector_db_path, f"{fact_id}.json")
        with open(fact_file, 'w') as f:
            json.dump(fact_data, f, indent=2)
            
        logger.info(f"Stored fact in JSON LTM: {fact_type} - {content[:50]}...")
        return fact_id
        
    def search_facts(self, query: str, fact_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search for facts by content similarity using Mem0.
        
        Args:
            query: Search query
            fact_type: Optional filter by fact type
            limit: Maximum number of results
            
        Returns:
            List of matching facts
        """
        if MEM0_AVAILABLE and self.memory:
            try:
                # Search using Mem0
                search_results = self.memory.search(
                    query=query,
                    user_id="amy_user",
                    limit=limit * 2  # Get more results to filter by type
                )
                
                # Convert results to our format
                facts = []
                for result in search_results.get('results', []):
                    # Filter by type if specified
                    if fact_type and result.get('metadata', {}).get('type') != fact_type:
                        continue
                    
                    facts.append({
                        'id': result.get('id'),
                        'type': result.get('metadata', {}).get('type'),
                        'content': result.get('memory'),
                        'metadata': result.get('metadata', {}),
                        'created_at': result.get('created_at'),
                        'similarity_score': result.get('score', 0.0)
                    })
                
                return facts[:limit]
                
            except Exception as e:
                logger.error(f"Failed to search facts in Mem0: {e}")
                # Fall back to JSON search
                return self._search_facts_json(query, fact_type, limit)
        else:
            # Fall back to JSON search
            return self._search_facts_json(query, fact_type, limit)
    
    def _search_facts_json(self, query: str, fact_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Fallback JSON search method."""
        results = []
        
        for filename in os.listdir(self.vector_db_path):
            if filename.endswith('.json'):
                fact_file = os.path.join(self.vector_db_path, filename)
                try:
                    with open(fact_file, 'r') as f:
                        fact_data = json.load(f)
                        
                    # Filter by type if specified
                    if fact_type and fact_data.get('type') != fact_type:
                        continue
                        
                    # Simple text matching
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
        if MEM0_AVAILABLE and self.memory:
            try:
                # Get all facts and filter by type
                all_results = self.memory.get_all(user_id="amy_user")
                
                # Filter by type
                facts = []
                for result in all_results.get('results', []):
                    if result.get('metadata', {}).get('type') == fact_type:
                        facts.append({
                            'id': result.get('id'),
                            'type': result.get('metadata', {}).get('type'),
                            'content': result.get('memory'),
                            'metadata': result.get('metadata', {}),
                            'created_at': result.get('created_at')
                        })
                
                return facts
                
            except Exception as e:
                logger.error(f"Failed to get facts by type in Mem0: {e}")
                # Fall back to JSON method
                return self._get_facts_by_type_json(fact_type)
        else:
            # Fall back to JSON method
            return self._get_facts_by_type_json(fact_type)
    
    def _get_facts_by_type_json(self, fact_type: str) -> List[Dict]:
        """Fallback JSON method for getting facts by type."""
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
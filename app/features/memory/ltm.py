"""
Long-Term Memory (LTM) for Amy using Mem0
Handles semantic search and knowledge storage using Mem0 vector database
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

# from mem0 import Memory # Temporarily removed mem0 import
from .base import BaseMemory

logger = logging.getLogger(__name__)

class LTM(BaseMemory):
    """
    Long-Term Memory (LTM) system using a JSON file for semantic knowledge storage and retrieval.
    Mem0 integration is temporarily disabled.
    """
    
    def __init__(self, vector_db_path: str = "instance/vector_db"):
        """
        Initialize LTM with JSON file storage. Mem0 integration is temporarily disabled.
        """
        self.vector_db_path = vector_db_path # Still keep for consistency in pathing for JSON file
        self.milvus_collection_name = "amy_memories" # Keep for potential future Mem0 re-integration
        self.memory = None # Mem0 is not used for now

        self.json_file_path = os.path.join(self.vector_db_path, 'ltm_memory.json') # JSON file in vector_db_path
        self._ensure_db_exists() # Ensure JSON DB exists on initialization
        logger.info("LTM initialized using JSON fallback. Mem0 integration temporarily disabled.")
        logger.info(f"DEBUG LTM: vector_db_path={self.vector_db_path}, json_file_path={self.json_file_path}")
        
    def _ensure_db_exists(self) -> None:
        """
        Ensure the JSON file for fallback exists.
        """
        os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True) # Ensure directory exists
        if not os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'w') as f:
                json.dump([], f)
            logger.info(f"Created empty LTM JSON file: {self.json_file_path}")
        
    def store_fact(self, fact_text: str, fact_type: str) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fact_id = f"{fact_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Always use JSON fallback for now
        return self._store_fact_json(fact_text, fact_type, timestamp)
    
    def _store_fact_json(self, fact_text: str, fact_type: str, timestamp: str) -> str:
        """
        Fallback JSON storage method.
        """
        fact_data = {
            'id': f"{fact_type}_{timestamp}",
            'type': fact_type,
            'content': fact_text,
            'metadata': {"timestamp": timestamp},
            'created_at': timestamp,
            'embedding': None # We don't generate embeddings for JSON fallback
        }
        
        # Read existing data, append new fact, and write back
        file_data = []
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as f:
                try:
                    file_data = json.load(f)
                except json.JSONDecodeError:
                    file_data = [] # Handle empty or malformed JSON
        
        file_data.append(fact_data)
        logger.debug(f"[LTM JSON Store] Appending fact_data: {fact_data}") # DEBUG: Log data being appended
        
        with open(self.json_file_path, 'w') as f:
            json.dump(file_data, f, indent=2)
            
        logger.info(f"Stored fact in JSON LTM: {fact_type} - {fact_text[:50]}...")
        return f"{fact_type}_{timestamp}"
        
    def search_facts(self, query: str, fact_type: Optional[str] = None) -> List[Dict]:
        """
        Search for facts by content similarity using JSON fallback.
        """
        limit = 5 # Default limit for search results internally
        # Always use JSON fallback for now
        return self._search_facts_json(query, fact_type, limit)
    
    def _search_facts_json(self, query: str, fact_type: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Fallback JSON search method.
        """
        # This is a very basic search, in a real app you'd want more sophisticated text matching
        # For now, it just checks if the query is in the content of the facts.
        matching_facts = []
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as f:
                try:
                    facts = json.load(f)
                except json.JSONDecodeError:
                    facts = [] # Handle empty or malformed JSON
                logger.debug(f"[LTM JSON Search] Query: '{query}', Fact Type: {fact_type}") # DEBUG: Log search query
                for fact in facts:
                    fact_content = fact.get('content', '')
                    fact_current_type = fact.get('type', 'unknown')
                    logger.debug(f"[LTM JSON Search] Checking fact: Content='{fact_content[:50]}...', Type='{fact_current_type}'")
                    if query.lower() in fact_content.lower():
                        if fact_type is None or fact_current_type == fact_type:
                            matching_facts.append(fact)
                            logger.debug(f"[LTM JSON Search] MATCH found: {fact['id']}") # DEBUG: Log match
        return matching_facts[:limit]
        
    def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """
        Retrieve facts by type using JSON fallback.
        """
        # Always use JSON fallback for now
        return self._get_facts_by_type_json(fact_type)
    
    def _get_facts_by_type_json(self, fact_type: str) -> List[Dict]:
        """
        Fallback JSON method to get facts by type."""
        filtered_facts = []
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'r') as f:
                try:
                    facts = json.load(f)
                except json.JSONDecodeError:
                    facts = [] # Handle empty or malformed JSON
                for fact in facts:
                    if fact['type'] == fact_type:
                        filtered_facts.append(fact)
        return filtered_facts
        
    def extract_facts_from_conversation(self, messages: List[Dict]) -> List[Tuple[str, str]]:
        """
        Extract potential facts from a conversation.

        Args:
            messages: List of conversation messages

        Returns:
            List of extracted facts as (content, type) tuples
        """
        facts = []

        for message in messages:
            content = message.get('content', '')
            role = message.get('role', '')

            # Simple fact extraction patterns (will be enhanced with NLP)
            if role == 'user':
                # Look for preference statements
                if any(phrase in content.lower() for phrase in ['i like', 'i prefer', 'i love', 'i hate']):
                    facts.append((content, "preference"))

                # Look for relationship information
                if any(phrase in content.lower() for phrase in ['my name is', 'i am', 'i work at', 'i live in']):
                    facts.append((content, "personal_info"))

                # Look for goals and plans
                if any(phrase in content.lower() for phrase in ['i want to', 'i plan to', 'i need to', 'my goal is']):
                    facts.append((content, "goal"))

                # Always add the full user message as a 'general' fact if not already categorized
                # This ensures all user input, including transcribed audio, is stored in LTM
                # Check if the content has already been added with any specific fact type
                already_categorized = False
                for fact_content, _ in facts:
                    if content == fact_content: # Check if content matches an already added fact
                        already_categorized = True
                        break
                if not already_categorized:
                    facts.append((content, "general"))

        return facts
        
    def build_context_from_query(self, query: str) -> str:
        """
        Build relevant context for a query using LTM.
        
        Args:
            query: The current query
            
        Returns:
            Relevant context string
        """
        # Search for relevant facts (limit is handled internally by search_facts)
        relevant_facts = self.search_facts(query)
        
        if not relevant_facts:
            return ""
            
        context_parts = ["Relevant information from previous conversations:"]
        
        for fact in relevant_facts:
            fact_type = fact.get('type', 'unknown')
            content = fact.get('content', '')
            context_parts.append(f"- {fact_type}: {content}")
            
        return "\n".join(context_parts) 
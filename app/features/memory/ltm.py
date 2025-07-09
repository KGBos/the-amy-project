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
        else:
            # Check if the file has data
            try:
                with open(self.json_file_path, 'r') as f:
                    data = json.load(f)
                if data:
                    logger.info(f"Loaded existing LTM data with {len(data)} facts")
                else:
                    logger.info(f"LTM file exists but is empty")
            except json.JSONDecodeError:
                logger.warning(f"LTM file exists but is corrupted, creating new one")
                with open(self.json_file_path, 'w') as f:
                    json.dump([], f)
        
    def store_fact(self, fact_text: str, fact_type: str, user_id: Optional[str] = None) -> str:
        """
        Store a fact in LTM with improved deduplication.
        
        Args:
            fact_text: The fact content
            fact_type: Type of fact (personal_info, preference, etc.)
            user_id: Optional user ID
            
        Returns:
            Fact ID
        """
        try:
            # Check for duplicates before storing
            if self._is_duplicate_fact(fact_text, fact_type, user_id):
                logger.info(f"Duplicate fact not stored: {fact_text[:50]}... (type: {fact_type}, user: {user_id})")
                return "duplicate"
                
            # Store the fact
            timestamp = datetime.now().isoformat()
            return self._store_fact_json(fact_text, fact_type, timestamp, user_id)
            
        except Exception as e:
            logger.error(f"Error storing fact: {e}")
            return "error"
            
    def _is_duplicate_fact(self, fact_text: str, fact_type: str, user_id: Optional[str] = None) -> bool:
        """
        Check if a fact is a duplicate using improved matching.
        
        Args:
            fact_text: The fact content to check
            fact_type: Type of fact
            user_id: Optional user ID
            
        Returns:
            True if duplicate, False otherwise
        """
        if not os.path.exists(self.json_file_path):
            return False
            
        try:
            with open(self.json_file_path, 'r') as f:
                facts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return False
            
        fact_text_lower = fact_text.lower().strip()
        
        for fact in facts:
            existing_content = fact.get('content', '').lower().strip()
            existing_type = fact.get('type', 'unknown')
            existing_user_id = fact.get('user_id')
            
            # Skip if types don't match
            if existing_type != fact_type:
                continue
                
            # Skip if user IDs don't match (but allow null user_id for legacy)
            if user_id and existing_user_id != user_id and existing_user_id is not None:
                continue
                
            # Check for exact match
            if existing_content == fact_text_lower:
                return True
                
            # Check for similar content (for personal_info facts)
            if fact_type == 'personal_info':
                # Remove common words and compare
                common_words = ['my', 'name', 'is', 'i', 'am', 'call', 'me']
                clean_existing = ' '.join([w for w in existing_content.split() if w not in common_words])
                clean_new = ' '.join([w for w in fact_text_lower.split() if w not in common_words])
                
                if clean_existing == clean_new and clean_existing:
                    return True
                    
                # Check for name variations (e.g., "Leon" vs "my name is Leon")
                if any(name in existing_content for name in ['leon', 'leon']) and any(name in fact_text_lower for name in ['leon', 'leon']):
                    return True
                    
            # Check for general content similarity (for general facts)
            if fact_type == 'general':
                # If both facts are very similar (80%+ word overlap), consider duplicate
                existing_words = set(existing_content.split())
                new_words = set(fact_text_lower.split())
                
                if existing_words and new_words:
                    overlap = len(existing_words.intersection(new_words))
                    total = len(existing_words.union(new_words))
                    similarity = overlap / total if total > 0 else 0
                    
                    if similarity > 0.8:  # 80% similarity threshold
                        return True
                        
        return False
    
    def _store_fact_json(self, fact_text: str, fact_type: str, timestamp: str, user_id: Optional[str] = None) -> str:
        """
        Fallback JSON storage method with deduplication.
        """
        fact_data = {
            'id': f"{fact_type}_{timestamp}",
            'type': fact_type,
            'content': fact_text,
            'metadata': {"timestamp": timestamp, "user_id": user_id},
            'created_at': timestamp,
            'user_id': user_id,
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
            
        logger.info(f"Stored fact in JSON LTM: {fact_type} - {fact_text[:50]}... (user: {user_id})")
        return f"{fact_type}_{timestamp}"
        
    def search_facts(self, query: str, fact_type: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict]:
        """
        Search for facts by content similarity using JSON fallback.
        
        Args:
            query: Search query
            fact_type: Optional fact type filter
            user_id: Optional user ID filter to only return facts from this user
        """
        limit = 5 # Default limit for search results internally
        # Always use JSON fallback for now
        return self._search_facts_json(query, fact_type, limit, user_id)
    
    def _search_facts_json(self, query: str, fact_type: Optional[str] = None, limit: int = 5, user_id: Optional[str] = None) -> List[Dict]:
        """
        Search facts using JSON fallback with improved relevance scoring.
        
        Args:
            query: Search query
            fact_type: Optional fact type filter
            limit: Maximum number of facts to return
            user_id: Optional user ID to filter facts
            
        Returns:
            List of relevant facts sorted by relevance
        """
        if not os.path.exists(self.json_file_path):
            return []
            
        try:
            with open(self.json_file_path, 'r') as f:
                facts = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
        matching_facts = []
        query_lower = query.lower().strip()
        
        # Split query into meaningful terms
        query_terms = [term for term in query_lower.split() if len(term) > 2]
        
        for fact in facts:
            fact_content = fact.get('content', '').lower()
            fact_current_type = fact.get('type', 'unknown')
            fact_user_id = fact.get('user_id', None)
            
            # Skip if fact type doesn't match
            if fact_type and fact_current_type != fact_type:
                continue
                
            # Filter by user_id if provided, but allow null user_id for legacy data
            if user_id and fact_user_id != user_id and fact_user_id is not None:
                continue
            
            # Calculate relevance score
            relevance_score = 0
            
            # Exact phrase match (highest priority)
            if query_lower in fact_content:
                relevance_score += 100
                
            # All query terms present (high priority)
            if all(term in fact_content for term in query_terms):
                relevance_score += 50
                
            # Partial term matches (medium priority)
            term_matches = sum(1 for term in query_terms if term in fact_content)
            if term_matches > 0:
                relevance_score += (term_matches / len(query_terms)) * 30
                
            # Personal info facts get bonus for name-related queries
            if fact_current_type == 'personal_info' and any(word in query_lower for word in ['name', 'who', 'leon']):
                relevance_score += 20
                
            # User-specific facts get priority over legacy null user_id facts
            if user_id and fact_user_id == user_id:
                relevance_score += 10
                
            # Only include facts with meaningful relevance
            if relevance_score >= 30:  # Minimum relevance threshold
                fact['relevance_score'] = relevance_score
                matching_facts.append(fact)
                
        # Sort by relevance score (highest first) and limit results
        matching_facts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Limit to most relevant facts
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
                # Look for name introductions
                if any(phrase in content.lower() for phrase in ['my name is', 'i am', 'call me', 'i\'m']):
                    facts.append((content, "personal_info"))
                # Look for standalone names (likely name introductions)
                elif len(content.strip()) <= 20 and content.strip().isalpha() and content.strip().istitle():
                    facts.append((content, "personal_info"))
                
                # Look for preference statements
                elif any(phrase in content.lower() for phrase in ['i like', 'i prefer', 'i love', 'i hate', 'i enjoy']):
                    facts.append((content, "preference"))

                # Look for relationship information
                elif any(phrase in content.lower() for phrase in ['i work at', 'i live in', 'i study', 'i go to']):
                    facts.append((content, "personal_info"))

                # Look for goals and plans
                elif any(phrase in content.lower() for phrase in ['i want to', 'i plan to', 'i need to', 'my goal is']):
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
        
    def build_context_from_query(self, query: str, user_id: Optional[str] = None) -> str:
        """
        Build relevant context for a query using LTM.
        
        Args:
            query: The current query
            user_id: Optional user ID to filter facts by user
            
        Returns:
            Relevant context string
        """
        # Search for relevant facts (limit is handled internally by search_facts)
        relevant_facts = self.search_facts(query, user_id=user_id)
        
        if not relevant_facts:
            return ""
            
        context_parts = ["Relevant information from previous conversations:"]
        
        for fact in relevant_facts:
            fact_type = fact.get('type', 'unknown')
            content = fact.get('content', '')
            context_parts.append(f"- {fact_type}: {content}")
            
        return "\n".join(context_parts)

    def cleanup_duplicates(self) -> int:
        """
        Clean up existing duplicate facts in the LTM.
        
        Returns:
            Number of duplicates removed
        """
        if not os.path.exists(self.json_file_path):
            return 0
        
        try:
            with open(self.json_file_path, 'r') as f:
                facts = json.load(f)
            
            # Group facts by content and type
            fact_groups = {}
            for fact in facts:
                content = fact.get('content', '')
                fact_type = fact.get('type', 'unknown')
                user_id = fact.get('user_id')
                
                # Create key for grouping
                key = (content.lower().strip(), fact_type, user_id)
                
                if key not in fact_groups:
                    fact_groups[key] = []
                fact_groups[key].append(fact)
            
            # Keep only the first fact from each group, remove duplicates
            cleaned_facts = []
            duplicates_removed = 0
            
            for key, fact_list in fact_groups.items():
                if len(fact_list) > 1:
                    # Keep the first fact, remove the rest
                    cleaned_facts.append(fact_list[0])
                    duplicates_removed += len(fact_list) - 1
                    logger.info(f"Removed {len(fact_list) - 1} duplicate(s) for: {key[0][:50]}...")
                else:
                    cleaned_facts.append(fact_list[0])
            
            # Write back cleaned facts
            with open(self.json_file_path, 'w') as f:
                json.dump(cleaned_facts, f, indent=2)
            
            logger.info(f"Cleaned up {duplicates_removed} duplicate facts from LTM")
            return duplicates_removed
            
        except Exception as e:
            logger.error(f"Error cleaning up duplicates: {e}")
            return 0 
"""
Long-Term Memory (LTM) for Amy using Mem0
Handles semantic search and knowledge storage using Mem0 vector database
"""

import logging
import os
from typing import List, Dict, Optional, Tuple
from mem0 import Memory
from .base import BaseMemory
from amy.config import DEFAULT_MODEL, LTM_TEMPERATURE, EMBEDDER_MODEL

logger = logging.getLogger(__name__)

class LTM(BaseMemory):
    """
    Long-Term Memory (LTM) system using Mem0 for semantic knowledge storage and retrieval.
    """
    
    def __init__(self, vector_db_path: str = "instance/mem0_storage"):
        """
        Initialize LTM with Mem0.
        
        Args:
            vector_db_path: Path where Mem0 should store its data (if local).
        """
        self.vector_db_path = vector_db_path
        
        # Ensure the directory exists
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Configure Mem0 for local usage
        # We explicitly set the embedder to 'huggingface' to avoid OpenAI dependency
        # and set vector_store to 'chroma' for local file-based storage.
        
        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "amy_memories",
                    "path": self.vector_db_path
                }
            },
            "llm": {
                "provider": "gemini",
                "config": {
                    "model": DEFAULT_MODEL,
                    "temperature": LTM_TEMPERATURE
                }
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": EMBEDDER_MODEL
                }
            }
        }
        
        try:
            self.memory = Memory.from_config(config)
            logger.info(f"LTM initialized using Mem0 (local storage at {self.vector_db_path}, embeddings: huggingface)")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            # Raise explicit error instead of silent failure
            raise RuntimeError(
                f"Failed to initialize LTM: Mem0 unavailable. "
                f"Check that embeddings model is downloadable and config is correct. "
                f"Original error: {e}"
            ) 
        
    def store_fact(self, fact_text: str, fact_type: str, user_id: Optional[str] = None) -> str:
        """
        Store a fact in LTM using Mem0.
        
        Args:
            fact_text: The fact content
            fact_type: Type of fact (personal_info, preference, etc.)
            user_id: Optional user ID
            
        Returns:
            Fact ID (or confirmation string)
        """
        try:
            # Add metadata to the memory
            metadata = {"type": fact_type}
            
            # Mem0.add returns a list of added memories or a dict
            result = self.memory.add(
                messages=fact_text, 
                user_id=user_id, 
                metadata=metadata
            )
            
            logger.debug(f"Stored fact in Mem0: {fact_text[:50]}... Result: {result}")
            return str(result)
            
        except Exception as e:
            logger.error(f"Error storing fact in Mem0: {e}")
            return "error"
            
    def search_facts(self, query: str, fact_type: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict]:
        """
        Search for facts using Mem0 semantic search.
        
        Args:
            query: Search query
            fact_type: Optional fact type filter
            user_id: Optional user ID filter
        """
        try:
            # Prepare filters if allowed by Mem0 search (check latest API)
            # Basic Mem0 search signature: search(query, user_id=None, agent_id=None, run_id=None, limit=5, filters=None)
            
            filters = {}
            if fact_type:
                filters["type"] = fact_type
                
            results = self.memory.search(
                query=query, 
                user_id=user_id,
                filters=filters if filters else None,
                limit=5
            )
            
            # Normalize results to expected format for Amy
            # Mem0 results typically look like: [{'memory': 'text', 'metadata': {...}, 'score': 0.9}]
            normalized_results = []
            for res in results:
                # Handle different return formats (dict or object)
                content = res.get('memory', '') if isinstance(res, dict) else getattr(res, 'memory', '')
                metadata = res.get('metadata', {}) if isinstance(res, dict) else getattr(res, 'metadata', {})
                score = res.get('score', 0) if isinstance(res, dict) else getattr(res, 'score', 0)
                
                normalized_results.append({
                    'content': content,
                    'type': metadata.get('type', 'unknown'),
                    'relevance_score': score,
                    'metadata': metadata
                })
                
            return normalized_results
            
        except Exception as e:
            logger.error(f"Error searching facts in Mem0: {e}")
            return []
            
    def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """
        Retrieve facts by type.
        Mem0 doesn't support 'get all by filter' natively without a query in some versions.
        We will use a generic query to find relevant info or note limitation.
        """
        # Workaround: Search with a generic term relevant to the type
        # Ideally Mem0 adds a .get_all(filters={...}) method.
        # For now, we search for "everything" with the filter.
        return self.search_facts(query="*", fact_type=fact_type)
        
    def extract_facts_from_conversation(self, messages: List[Dict]) -> List[Tuple[str, str]]:
        """
        Extract potential facts from a conversation.
        """
        facts = []
        for message in messages:
            content = message.get('content', '')
            role = message.get('role', '')

            if role == 'user':
                # Simple extraction heuristics
                lower_content = content.lower()
                if any(p in lower_content for p in ['my name is', 'i am', 'call me']):
                    facts.append((content, "personal_info"))
                elif any(p in lower_content for p in ['i like', 'i love', 'i prefer']):
                    facts.append((content, "preference"))
                elif any(p in lower_content for p in ['i work', 'i live']):
                    facts.append((content, "personal_info"))
                
                # General fallback
                if len(facts) == 0:
                   facts.append((content, "general"))
                   
        return facts
        
    def build_context_from_query(self, query: str, user_id: Optional[str] = None) -> str:
        """
        Build relevant context for a query using LTM.
        """
        relevant_facts = self.search_facts(query, user_id=user_id)
        
        if not relevant_facts:
            return ""
        
        # Collect actual facts first
        fact_lines = []
        seen_facts = set()
        
        for fact in relevant_facts:
            content = fact.get('content', '')
            if content and content not in seen_facts:
                fact_type = fact.get('type', 'general')
                fact_lines.append(f"- [{fact_type}] {content}")
                seen_facts.add(content)
        
        # Only return header + facts if we have actual content
        if not fact_lines:
            return ""
            
        return "Relevant information from previous conversations:\n" + "\n".join(fact_lines)

    def cleanup_duplicates(self) -> int:
        """
        Clean up existing duplicate facts in the LTM.
        Mem0 handles some deduplication internally typically.
        """
        # Placeholder as Mem0 manages vector store consistency
        return 0
 
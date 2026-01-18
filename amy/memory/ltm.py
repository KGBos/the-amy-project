import asyncio
import logging
import os
import concurrent.futures
import functools
import re
from typing import List, Dict, Optional
from mem0 import Memory
from amy.config import DEFAULT_MODEL, LTM_TEMPERATURE, EMBEDDER_MODEL, LTM_SCORE_THRESHOLD, PII_REDACTION_ENABLED

logger = logging.getLogger(__name__)

# Simple in-memory cache for LTM (LRU style)
# We use a dict and manual management or a library if available.
# Let's use a simple per-instance dict with max size for now to avoid extra deps if possible,
# or better, use async_lru if we can assume it's installed (it's standard in many async stacks).
# If not, we'll implement a simple decorator.
try:
    from async_lru import alru_cache
except ImportError:
    # Fallback to a simple memoization if async_lru is missing (though we should add it)
    # For now, let's assume valid environment or provide a simple dummy
    def alru_cache(maxsize=128):
        def decorator(func):
            cache = {}
            @functools.wraps(func)
            async def wrapper(self, *args, **kwargs):
                key = (args, frozenset(kwargs.items()))
                if key in cache:
                    return cache[key]
                result = await func(self, *args, **kwargs)
                if len(cache) > maxsize:
                    cache.pop(next(iter(cache)))
                cache[key] = result
                return result
            return wrapper
        return decorator

class LTM:
    """
    Long-Term Memory (LTM) management using Mem0.
    Handles semantic storage and retrieval of user-related facts.
    """
    
    def __init__(self, vector_db_path: str = "instance/mem0_storage"):
        """Initialize LTM with Mem0."""
        self.vector_db_path = vector_db_path
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Specialized executor for embedding generation (I/O & CPU bound)
        # Prevents LTM from stalling the main event loop's default executor
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4, 
            thread_name_prefix="ltm_worker"
        )
        
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
            logger.info(f"LTM initialized using Mem0 (local storage at {self.vector_db_path})")
        except Exception as e:
            import traceback
            logger.error(f"Failed to initialize Mem0: {e}\n{traceback.format_exc()}")
            raise RuntimeError(f"Failed to initialize LTM: {e}") 

    def close(self):
        """Shut down the specialized thread pool."""
        self._executor.shutdown(wait=False)
        logger.debug("LTM worker pool shut down")
        
    def _redact_pii(self, text: str) -> str:
        """Simple regex-based PII redaction."""
        if not PII_REDACTION_ENABLED:
            return text
        
        # Redact emails
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]', text)
        # Redact phone numbers (basic patterns)
        text = re.sub(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_REDACTED]', text)
        
        return text

    async def store_fact(self, fact_text: str, fact_type: str, user_id: Optional[str] = None) -> str:
        """
        Store a fact in Mem0 using a specialized thread pool.
        """
        try:
            # Redact PII before storing
            sanitized_text = self._redact_pii(fact_text)
            
            metadata = {"type": fact_type}
            
            # Use dedicated executor for embedding/vector storage
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self._executor,
                functools.partial(
                    self.memory.add,
                    messages=sanitized_text, 
                    user_id=user_id, 
                    metadata=metadata
                )
            )
            
            logger.debug(f"Stored fact in Mem0: {sanitized_text[:50]}...")
            return str(result)
            
        except Exception as e:
            logger.error(f"Error storing fact in Mem0: {e}")
            return "error"
            
    @alru_cache(maxsize=128)
    async def search_facts(self, query: str, user_id: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Search facts in Mem0 using a specialized thread pool.
        Cached to prevent redundant lookups for unchanged queries.
        """
        try:
            # Validation: Mem0 requires at least one ID
            if not user_id:
                logger.warning("LTM search skipped: No user_id provided.")
                return []

            # Use dedicated executor for embedding/vector search
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(
                self._executor,
                functools.partial(
                    self.memory.search,
                    query=query,
                    user_id=user_id,
                    limit=limit
                )
            )
            
            # Mem0 returns a list of dictionaries, or a dict with 'results' key.
            if not results:
                return []
                
            results_list = results.get('results', []) if isinstance(results, dict) else results
            
            filtered_results = []
            for res in results_list:
                # Mem0 score is usually distance (lower = better) or similarity (higher = better)
                score = res.get('score', 1.0)
                
                # Check threshold (assuming similarity 0.0 to 1.0)
                if score >= LTM_SCORE_THRESHOLD:
                    filtered_results.append(res)
                else:
                    logger.debug(f"Fact filtered by threshold ({score} < {LTM_SCORE_THRESHOLD}): {res.get('content', '')[:30]}")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error searching facts in Mem0: {e}")
            return []
            
    async def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """Retrieve facts by type."""
        return await self.search_facts(query="*", fact_type=fact_type)
        
    async def build_context_from_query(self, query: str, user_id: Optional[str] = None) -> str:
        """
        Build relevant context for a query using LTM (Non-blocking).
        """
        relevant_facts = await self.search_facts(query, user_id=user_id)
        
        if not relevant_facts:
            return ""
        
        fact_lines = []
        seen_facts = set()
        
        for fact in relevant_facts:
            content = fact.get('content', '')
            if content and content not in seen_facts:
                fact_type = fact.get('type', 'general')
                fact_lines.append(f"- [{fact_type}] {content}")
                seen_facts.add(content)
        
        if not fact_lines:
            return ""
            
        return "Relevant information from previous conversations:\n" + "\n".join(fact_lines)

    def cleanup_duplicates(self) -> int:
        """Placeholder for cleanup."""
        return 0
 
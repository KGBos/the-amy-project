"""
Memory Tools for Amy
ADK-style tools for explicit memory save/recall
"""

import logging
from typing import Optional
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


def create_save_memory_tool(ltm):
    """Create a save_memory tool bound to an LTM instance."""
    
    async def save_memory(
        fact: str,
        category: str,
        tool_context: ToolContext
    ) -> str:
        """Save an important fact to long-term memory.
        
        Use this when a user tells you something worth remembering, like:
        - Their name, preferences, or personal details
        - Things they like or dislike
        - Important dates or events
        - Work or hobby information
        
        Args:
            fact: The information to remember (e.g., "User's name is Leon")
            category: Type of information - one of: personal_info, preference, 
                      work, hobby, relationship, general
        
        Returns:
            Confirmation that the fact was saved
        """
        try:
            # Get user_id from context if available
            user_id = None
            if tool_context and hasattr(tool_context, 'state'):
                user_id = tool_context.state.get('user_id')
            
            result = await ltm.store_fact(fact, category, user_id)
            logger.info(f"Saved memory: {fact[:50]}... (category: {category})")
            return f"✓ Remembered: {fact}"
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return f"Failed to save memory: {str(e)}"
    
    return FunctionTool(save_memory)


def create_search_memory_tool(ltm):
    """Create a search_memory tool bound to an LTM instance."""
    
    async def search_memory(
        query: str,
        tool_context: ToolContext
    ) -> str:
        """Search long-term memory for relevant information.
        
        Use this when you need to recall something about the user, like:
        - What is their name?
        - What do they like/prefer?
        - What have they told you before?
        
        Args:
            query: What to search for (e.g., "user's name", "favorite food")
        
        Returns:
            Relevant memories if found, or indication that nothing was found
        """
        try:
            # Get user_id from context if available
            user_id = None
            if tool_context and hasattr(tool_context, 'state'):
                user_id = tool_context.state.get('user_id')
            
            facts = await ltm.search_facts(query, user_id=user_id)
            
            if not facts:
                return "No relevant memories found."
            
            result_lines = ["Found in memory:"]
            for fact in facts[:5]:  # Limit to 5 results
                content = fact.get('content', '')
                if content:
                    result_lines.append(f"• {content}")
            
            logger.info(f"Memory search '{query}' returned {len(facts)} results")
            return "\n".join(result_lines)
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return f"Memory search failed: {str(e)}"
    
    return FunctionTool(search_memory)

"""
Unified Memory Toolset for Amy
ADK-compliant Toolset for Long-Term Memory (Lending itself to specialists).
"""

import logging
from typing import Optional, List, Any, Dict
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool

logger = logging.getLogger(__name__)

class MemoryToolset(BaseToolset):
    """
    Toolset for interacting with Amy's Long-Term Memory (LTM).
    Can be injected into specialist agents.
    """
    
    def __init__(self, ltm):
        super().__init__()
        self.ltm = ltm

    async def get_tools(self, readonly_context: Optional[Any] = None) -> List[BaseTool]:
        """Returns the list of tools in this toolset."""
        return [
            FunctionTool(func=self.save_memory),
            FunctionTool(func=self.search_memory)
        ]

    async def save_memory(self, fact: str, category: str = "general", tool_context: Optional[ToolContext] = None) -> str:
        """
        Save an important fact or preference about the user to long-term memory.
        """
        try:
            # Get user_id from context if available
            user_id = None
            if tool_context and hasattr(tool_context, '_invocation_context'):
                user_id = tool_context._invocation_context.user_id
            
            await self.ltm.store_fact(fact, category, user_id=user_id)
            return f"Successfully saved to memory: {fact}"
        except Exception as e:
            logger.error(f"Error in save_memory tool: {e}")
            return f"Failed to save memory: {str(e)}"

    async def search_memory(self, query: str, tool_context: Optional[ToolContext] = None) -> List[str]:
        """
        Search long-term memory for facts, preferences, or past interactions related to the user.
        """
        try:
            # Get user_id from context if available
            user_id = None
            if tool_context and hasattr(tool_context, '_invocation_context'):
                user_id = tool_context._invocation_context.user_id
            
            facts = await self.ltm.search_facts(query, user_id=user_id)
            if not facts:
                return ["No relevant memories found."]
            return facts
        except Exception as e:
            logger.error(f"Error in search_memory tool: {e}")
            return [f"Error searching memory: {str(e)}"]

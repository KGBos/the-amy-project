"""
Search Tools for Amy
Uses duckduckgo-search for free, private web searching.
"""
import logging
import asyncio
from typing import Optional

from google.adk.tools import FunctionTool
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def create_web_search_tool():
    """Create a tool for searching the web."""

    async def search_web(query: str, max_results: int = 5) -> str:
        """
        Search the web for real-time information.
        
        Args:
            query: The search query string.
            max_results: Max number of results (default 5).
            
        Returns:
            Search results with titles, URLs, and snippets.
        """
        logger.info(f"Searching web for: {query}")
        
        try:
            # Simple text search - wrapped in to_thread to prevent blocking
            results = await asyncio.to_thread(DDGS().text, query, max_results=max_results)
            
            if not results:
                return "No results found."
                
            formatted_results = []
            for i, r in enumerate(results, 1):
                title = r.get('title', 'No Title')
                link = r.get('href', '#')
                body = r.get('body', '')
                formatted_results.append(f"{i}. [{title}]({link})\n   {body}\n")
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}"

    return FunctionTool(search_web)

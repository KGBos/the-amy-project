"""
Search Tools for Amy
Uses Google Search Grounding (via ADK native tool).
Replaces custom DuckDuckGo implementation.
"""
import logging
from google.adk.tools import google_search

logger = logging.getLogger(__name__)

def create_web_search_tool():
    """
    Returns the Native Google Search Grounding tool from ADK.
    Requires GOOGLE_API_KEY environment variable.
    """
    logger.info("Initializing Google Search Grounding Tool")
    return google_search

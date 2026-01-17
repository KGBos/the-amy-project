"""
Core Agent definition for Amy.
Uses ADK-style memory tools for explicit save/recall.
"""

import os
import logging
from typing import AsyncGenerator, Optional

import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from amy.config import GEMINI_API_KEY, DEFAULT_MODEL, SYSTEM_PROMPT
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM
from amy.tools.memory_tools import create_save_memory_tool, create_search_memory_tool

logger = logging.getLogger(__name__)

# Initialize persistent storage
conversation_db = ConversationDB()
ltm = LTM()

# Create memory tools
save_memory_tool = create_save_memory_tool(ltm)
search_memory_tool = create_search_memory_tool(ltm)


def before_agent_callback(callback_context):
    """
    Called before each agent invocation.
    Injects recent conversation history into context.
    """
    try:
        # Get session_id from state
        session_id = callback_context.state.get('session_id')
        if not session_id:
            return
        
        # Get recent conversation context
        context = conversation_db.get_context_for_session(
            session_id, 
            limit=10, 
            max_chars=2000
        )
        
        if context:
            # Append to system instruction
            callback_context.state['conversation_context'] = context
            logger.debug(f"Injected {len(context)} chars of context")
    except Exception as e:
        logger.error(f"Error in before_agent_callback: {e}")


def after_agent_callback(callback_context):
    """
    Called after each agent invocation.
    Stores the conversation to the database.
    """
    try:
        session_id = callback_context.state.get('session_id')
        user_id = callback_context.state.get('user_id')
        platform = callback_context.state.get('platform', 'unknown')
        
        if not session_id:
            return
        
        # Get the user's message and Amy's response from events
        user_message = callback_context.state.get('user_message')
        amy_response = callback_context.state.get('amy_response')
        
        if user_message:
            conversation_db.add_message(
                session_id=session_id,
                role='user',
                content=user_message,
                user_id=user_id,
                platform=platform
            )
        
        if amy_response:
            conversation_db.add_message(
                session_id=session_id,
                role='assistant',
                content=amy_response,
                user_id=user_id,
                platform=platform
            )
            
        logger.debug(f"Stored conversation for session {session_id}")
    except Exception as e:
        logger.error(f"Error in after_agent_callback: {e}")


# Build full instruction with context placeholder
def build_instruction():
    """Build the system instruction for Amy."""
    return f"""{SYSTEM_PROMPT}

You have two memory tools available:
- save_memory: Save important facts about users (name, preferences, etc.)
- search_memory: Recall information you've saved about users

Use save_memory when users tell you something worth remembering.
Use search_memory when you need to recall something about them.

If conversation context is provided, use it to maintain continuity."""


# Create the root agent
root_agent = Agent(
    name="amy",
    model=DEFAULT_MODEL,
    instruction=build_instruction(),
    tools=[save_memory_tool, search_memory_tool],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback
)


# Helper functions for external use
def get_conversation_db() -> ConversationDB:
    """Get the conversation database instance."""
    return conversation_db


def get_ltm() -> LTM:
    """Get the LTM instance."""
    return ltm

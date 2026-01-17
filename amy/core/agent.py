"""
Amy Agent - Root Agent Definition
"""
import logging
import asyncio
from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.adk.agents.invocation_context import InvocationContext
from google.genai.types import GenerateContentConfig

from amy.config import DEFAULT_MODEL, SYSTEM_PROMPT
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM
from amy.tools.memory_tools import (
    create_save_memory_tool,
    create_search_memory_tool
)
from amy.tools.code_tools import create_code_interpreter_tool
from amy.tools.search_tools import create_web_search_tool
from google.adk.planners.plan_re_act_planner import PlanReActPlanner

logger = logging.getLogger(__name__)

# Initialize Planner
# We use the PlanReActPlanner to force a "Plan -> Act -> Observe" loop
planner = PlanReActPlanner()

def create_root_agent(ltm: LTM, conversation_db: ConversationDB) -> Agent:
    """
    Factory to create the root agent with dependencies injected.
    """
    
    # Create tools bound to LTM instance
    save_memory_tool = create_save_memory_tool(ltm)
    search_memory_tool = create_search_memory_tool(ltm)
    code_tool = create_code_interpreter_tool()
    search_tool = create_web_search_tool()

    async def root_instruction_provider(ctx: ReadonlyContext) -> str:
        """
        Dynamic instruction provider that builds the system prompt with context.
        """
        try:
            session_id = ctx.state.get('session_id')
            user_id = ctx.state.get('user_id')
            user_message = ""
            
            # safely extract user message
            if ctx.user_content and ctx.user_content.parts:
                user_message = ctx.user_content.parts[0].text or ""

            # 1. Get recent conversation history
            recent_context = conversation_db.get_context_for_session(session_id, limit=10)
            
            # 2. Get LTM context (using the user's current message)
            ltm_context = ""
            if user_message:
                ltm_context = ltm.build_context_from_query(user_message, user_id=user_id)
                
            # 3. Assemble full prompt
            full_prompt = SYSTEM_PROMPT
            
            if recent_context:
                full_prompt += f"\n\n=== RECENT CONVERSATION (Chronological) ===\n{recent_context}"
            
            if ltm_context:
                full_prompt += f"\n\n=== LONG-TERM MEMORY (Facts about User) ===\n{ltm_context}"
                
            if user_message:
                full_prompt += f"\n\nCurrent Request: {user_message}"
                
            return full_prompt

        except Exception as e:
            logger.error(f"Error building instruction: {e}")
            return SYSTEM_PROMPT

    return Agent(
        name="amy_root",
        model=DEFAULT_MODEL,
        instruction=root_instruction_provider,
        tools=[save_memory_tool, search_memory_tool, code_tool, search_tool],
        planner=planner,
    )

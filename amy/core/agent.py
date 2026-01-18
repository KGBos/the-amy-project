"""
Amy Agent - Root Agent Definition
"""
import logging
from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.config_agent_utils import from_config as load_agent_from_config
from google.adk.planners.plan_re_act_planner import PlanReActPlanner

import os
import asyncio
from amy.config import DEFAULT_MODEL
from amy.memory.ltm import LTM
from amy.tools.memory_tools import (
    create_save_memory_tool,
    create_search_memory_tool
)
from amy.tools.code_tools import create_code_interpreter_tool
from amy.tools.search_tools import create_web_search_tool

logger = logging.getLogger(__name__)

# Initialize Planner
# We use the PlanReActPlanner to force a "Plan -> Act -> Observe" loop
planner = PlanReActPlanner()

def create_root_agent(ltm: LTM) -> Agent:
    """
    Factory to create the root agent with dependencies injected.
    Now loads metadata and base instructions from YAML (ADK v1.22+).
    """
    
    # 1. Load Agent from YAML
    yaml_path = os.path.join(os.path.dirname(__file__), "agents", "amy", "root_agent.yaml")
    agent = load_agent_from_config(yaml_path)
    
    # 2. Create tools bound to LTM instance
    save_memory_tool = create_save_memory_tool(ltm)
    search_memory_tool = create_search_memory_tool(ltm)
    code_tool = create_code_interpreter_tool()
    search_tool = create_web_search_tool()

    base_instruction = agent.instruction

    async def root_instruction_provider(ctx: ReadonlyContext) -> str:
        """
        Dynamic instruction provider that builds the system prompt with context.
        """
        try:
            user_id = ctx.state.get('user_id')
            user_message = ""
            
            # safely extract user message
            if ctx.user_content and ctx.user_content.parts:
                user_message = ctx.user_content.parts[0].text or ""

            # Parallel Context Gathering
            context_tasks = []
            if user_message:
                context_tasks.append(ltm.build_context_from_query(user_message, user_id=user_id))
            
            context_results = await asyncio.gather(*context_tasks)
            ltm_context = context_results[0] if context_results else ""
                
            # Combine static YAML instruction with dynamic context
            full_prompt = base_instruction
            
            if ltm_context:
                full_prompt += f"\n\n=== LONG-TERM MEMORY (Facts about User) ===\n{ltm_context}"
                
            if user_message:
                full_prompt += f"\n\nCurrent Request: {user_message}"
                
            return full_prompt

        except Exception as e:
            logger.error(f"Error building instruction: {e}")
            return base_instruction

    # 3. Inject dynamic logic and tools into the loaded agent
    agent.instruction = root_instruction_provider
    agent.tools = [save_memory_tool, search_memory_tool, code_tool, search_tool]
    agent.planner = planner
    
    return agent

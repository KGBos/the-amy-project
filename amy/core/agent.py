"""
Amy Agent - Root Agent Definition (Multi-Agent Router)
"""
import logging
import os
import asyncio
from typing import Optional

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.config_agent_utils import from_config as load_agent_from_config
from google.adk.planners.plan_re_act_planner import PlanReActPlanner

from amy.config import DEFAULT_MODEL
from amy.memory.ltm import LTM
from amy.tools.memory_tools import (
    create_save_memory_tool,
    create_search_memory_tool
)
from amy.tools.code_tools import create_code_interpreter_tool
from amy.tools.search_tools import create_web_search_tool
from amy.core.callbacks import SafetyCallback
from amy.core.telemetry import get_telemetry_plugins

logger = logging.getLogger(__name__)

# Initialize Planner
# We use PlanReActPlanner for sub-agents to enable tool usage loops
planner = PlanReActPlanner()

def create_root_agent(ltm: LTM) -> Agent:
    """
    Factory to create the Multi-Agent System (Router + Specialists).
    """
    base_dir = os.path.join(os.path.dirname(__file__), "agents", "amy")
    
    # --- 1. Create Specialist Agents ---
    
    # A. Coder Agent
    coder_path = os.path.join(base_dir, "recruitment", "coder.yaml")
    coder_agent = load_agent_from_config(coder_path)
    coder_agent.model = DEFAULT_MODEL
    coder_agent.tools = [create_code_interpreter_tool()]
    coder_agent.planner = planner # Needs planner to use tools
    
    # B. Researcher Agent
    researcher_path = os.path.join(base_dir, "recruitment", "researcher.yaml")
    researcher_agent = load_agent_from_config(researcher_path)
    researcher_agent.model = DEFAULT_MODEL
    # Inject tools: Google Search + Memory Tools
    researcher_agent.tools = [
        create_web_search_tool(), # Native Google Grounding
        create_save_memory_tool(ltm),
        create_search_memory_tool(ltm)
    ]
    researcher_agent.planner = planner # Needs planner to use tools

    # --- 2. Create Root Router Agent ---
    root_path = os.path.join(base_dir, "root_agent.yaml")
    root_agent = load_agent_from_config(root_path)
    root_agent.model = DEFAULT_MODEL
    
    # NEW: Restore memory tools to Root Agent to allow it to directly manage memory if needed,
    # ensuring it can satisfy core tests while we unify instructions.
    root_agent.tools = [
        create_save_memory_tool(ltm),
        create_search_memory_tool(ltm)
    ]
    
    # 3. Assemble Team (Add Sub-Agents)
    root_agent.sub_agents = [coder_agent, researcher_agent]
    
    # 4. Bind Global Features (Safety, Telemetry) to ALL agents
    security = SafetyCallback()
    
    for ag in [root_agent, coder_agent, researcher_agent]:
        # Ensure list initialization
        if not ag.before_model_callback:
            ag.before_model_callback = []
        elif not isinstance(ag.before_model_callback, list):
            ag.before_model_callback = [ag.before_model_callback]
        
        ag.before_model_callback.append(security)

    # 5. Global Instruction (Static from YAML, wrapped in async for compatibility)
    # The Root Agent now relies on its specialized sub-agents (Researcher) 
    # to handle complex memory retrieval, but keeps its own tools for observability.
    
    base_instruction = root_agent.instruction
    async def root_instruction_provider(ctx: ReadonlyContext) -> str:
        # Simple relay of static YAML instruction (no sidecar injection)
        return base_instruction

    root_agent.instruction = root_instruction_provider
    
    return root_agent
    
    return root_agent

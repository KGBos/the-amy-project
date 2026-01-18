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
from amy.tools.memory_tools import MemoryToolset
from amy.tools.code_tools import create_code_interpreter_tool
from amy.tools.search_tools import create_web_search_tool
from amy.tools.search_tools import create_web_search_tool
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
    
    # Init Toolsets once for all specialists
    mem_tools = MemoryToolset(ltm)
    
    # B. LTM Specialist
    ltm_path = os.path.join(base_dir, "recruitment", "ltm_specialist.yaml")
    ltm_specialist = load_agent_from_config(ltm_path)
    ltm_specialist.model = DEFAULT_MODEL
    ltm_specialist.tools = [mem_tools]
    ltm_specialist.planner = planner

    # C. Web Specialist
    web_path = os.path.join(base_dir, "recruitment", "web_specialist.yaml")
    web_specialist = load_agent_from_config(web_path)
    web_specialist.model = DEFAULT_MODEL
    web_specialist.tools = [create_web_search_tool()]
    web_specialist.planner = planner

    # --- 2. Create Root Router Agent ---
    root_path = os.path.join(base_dir, "root_agent.yaml")
    root_agent = load_agent_from_config(root_path)
    root_agent.model = DEFAULT_MODEL
    
    # NEW: Root has its own memory access for quick oversight
    root_agent.tools = [mem_tools]
    
    # 3. Assemble Team (Add Sub-Agents)
    root_agent.sub_agents = [coder_agent, ltm_specialist, web_specialist]
    
    # 4. Telemetry binding (Plugins handle safety now)
    # The Runner will automatically apply plugins to these agents.

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

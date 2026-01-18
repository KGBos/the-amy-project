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
    
    # 3. Assemble Team (Add Sub-Agents)
    root_agent.sub_agents = [coder_agent, researcher_agent]
    
    # 4. Bind Global Features (Safety, Telemetry) to ROOT only?
    # Or to all? Callbacks usually propagate or are agent-specific.
    # For safety, we bind to ALL agents to ensure no one bypasses guardrails.
    
    security = SafetyCallback()
    
    for ag in [root_agent, coder_agent, researcher_agent]:
        # Ensure list initialization
        if not ag.before_model_callback:
            ag.before_model_callback = []
        elif not isinstance(ag.before_model_callback, list):
            ag.before_model_callback = [ag.before_model_callback]
        
        ag.before_model_callback.append(security)

    # 5. Dynamic Root Instruction (Optional Context Injection)
    # We keep the dynamic context injection on the Root Router so it knows context
    # before delegating.
    
    base_instruction = root_agent.instruction
    
    async def root_instruction_provider(ctx: ReadonlyContext) -> str:
        """
        Dynamic instruction for Router. 
        Injects LTM context so Router knows if it should recall memory.
        """
        try:
            user_id = ctx.state.get('user_id')
            user_message = ""
            if ctx.user_content and ctx.user_content.parts:
                user_message = ctx.user_content.parts[0].text or ""

            # Check LTM briefly (light lookup)
            # Or reliance on Researcher?
            # For now, let's keep it simple: Router has context, passes it down implicitly?
            # Actually, agents don't share instruction context automatically.
            # Let's simple allow Router to see LTM so it can say "I know you liked X"
            # before delegating.
            
            context_tasks = []
            if user_message:
                context_tasks.append(ltm.build_context_from_query(user_message, user_id=user_id))
            
            try:
                # Circuit Breaker: Timeout LTM lookup after 2.0 seconds to prevent blocking
                if context_tasks:
                    context_results = await asyncio.wait_for(asyncio.gather(*context_tasks), timeout=2.0)
                else:
                    context_results = []
            except asyncio.TimeoutError:
                logger.warning("LTM context lookup timed out (exceeded 2.0s). Proceeding without memory.")
                context_results = []
            except Exception as e:
                logger.error(f"LTM lookup failed: {e}")
                context_results = []

            ltm_context = context_results[0] if context_results else ""
                
            full_prompt = base_instruction
            if ltm_context:
                full_prompt += f"\n\n=== CONTEXT (Facts about User) ===\n{ltm_context}"
            if user_message:
                full_prompt += f"\n\nCurrent Request: {user_message}"
                
            return full_prompt

        except Exception as e:
            logger.error(f"Error building instruction: {e}")
            return base_instruction

    root_agent.instruction = root_instruction_provider
    
    return root_agent

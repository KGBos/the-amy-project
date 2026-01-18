"""
Tests for Amy's ADK Agent
"""

import pytest
from amy.core.agent import create_root_agent
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM


class TestRootAgent:
    """Tests for the root ADK agent."""
    
    def test_agent_factory_creates_agent(self):
        """Test that the factory creates an agent with dependencies."""
        ltm = LTM()
        agent = create_root_agent(ltm)
        
        assert agent is not None
        assert agent.name == "amy_root"
    
    @pytest.mark.asyncio
    async def test_agent_has_memory_tools(self):
        """Test that the agent has the required memory tools."""
        ltm = LTM()
        agent = create_root_agent(ltm)
        
        # Resolve tools if they are toolsets
        from google.adk.tools.base_toolset import BaseToolset
        resolved_tools = []
        for t in agent.tools or []:
            if isinstance(t, BaseToolset):
                resolved_tools.extend(await t.get_tools())
            else:
                resolved_tools.append(t)
        
        tool_names = [t.name for t in resolved_tools]
        assert 'save_memory' in tool_names
        assert 'search_memory' in tool_names
    
    def test_agent_configuration(self):
        """Test that the agent has instruction configured."""
        ltm = LTM()
        agent = create_root_agent(ltm)
        
        assert callable(agent.instruction)
    
    def test_agent_uses_correct_model(self):
        """Test that the agent uses the configured model."""
        from amy.config import DEFAULT_MODEL
        ltm = LTM()
        agent = create_root_agent(ltm)
        
        # Handle both string and model object (for Interactions API)
        model_name = agent.model if isinstance(agent.model, str) else agent.model.model
        assert model_name == DEFAULT_MODEL

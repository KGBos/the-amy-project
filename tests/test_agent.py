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
        db = ConversationDB()
        ltm = LTM()
        agent = create_root_agent(ltm, db)
        
        assert agent is not None
        assert agent.name == "amy_root"
    
    def test_agent_has_memory_tools(self):
        """Test that the agent has the required memory tools."""
        db = ConversationDB()
        ltm = LTM()
        agent = create_root_agent(ltm, db)
        
        tool_names = [t.name for t in agent.tools]
        assert 'save_memory' in tool_names
        assert 'search_memory' in tool_names
    
    def test_agent_configuration(self):
        """Test that the agent has instruction configured."""
        db = ConversationDB()
        ltm = LTM()
        agent = create_root_agent(ltm, db)
        
        assert callable(agent.instruction)
    
    def test_agent_uses_correct_model(self):
        """Test that the agent uses the configured model."""
        from amy.config import DEFAULT_MODEL
        db = ConversationDB()
        ltm = LTM()
        agent = create_root_agent(ltm, db)
        
        assert agent.model == DEFAULT_MODEL

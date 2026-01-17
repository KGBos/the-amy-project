"""
Tests for Amy's ADK Agent
"""

import pytest
from amy.core.agent import root_agent, get_conversation_db, get_ltm


class TestRootAgent:
    """Tests for the root ADK agent."""
    
    def test_agent_has_memory_tools(self):
        """Test that the agent has the required memory tools."""
        tool_names = [t.name for t in root_agent.tools]
        assert 'save_memory' in tool_names
        assert 'search_memory' in tool_names
    
    def test_agent_has_callbacks(self):
        """Test that the agent has before/after callbacks configured."""
        assert root_agent.before_agent_callback is not None
        assert root_agent.after_agent_callback is not None
    
    def test_agent_uses_correct_model(self):
        """Test that the agent uses the configured model."""
        from amy.config import DEFAULT_MODEL
        assert root_agent.model == DEFAULT_MODEL


class TestAgentHelperFunctions:
    """Tests for agent helper functions."""
    
    def test_get_conversation_db(self):
        """Test that get_conversation_db returns a ConversationDB instance."""
        from amy.memory.conversation import ConversationDB
        db = get_conversation_db()
        assert isinstance(db, ConversationDB)
    
    def test_get_ltm(self):
        """Test that get_ltm returns an LTM instance."""
        from amy.memory.ltm import LTM
        ltm = get_ltm()
        assert isinstance(ltm, LTM)

"""
Tests for Amy and memory system
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM


class TestConversationDB:
    """Tests for ConversationDB."""
    
    def test_add_and_retrieve_message(self):
        """Test storing and retrieving messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = ConversationDB(db_path=db_path)
            
            msg_id = db.add_message(
                session_id="test_session",
                role="user",
                content="Hello Amy!",
                user_id="user123",
                platform="telegram"
            )
            
            assert msg_id > 0
            
            messages = db.get_recent_messages("test_session", limit=10)
            assert len(messages) == 1
            assert messages[0]['content'] == "Hello Amy!"
    
    def test_message_count(self):
        """Test message counting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = ConversationDB(db_path=db_path)
            
            db.add_message("session1", "user", "Message 1")
            db.add_message("session1", "assistant", "Response 1")
            db.add_message("session1", "user", "Message 2")
            
            assert db.get_message_count("session1") == 3
    
    def test_context_formatting(self):
        """Test context string generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "test.db")
            db = ConversationDB(db_path=db_path)
            
            db.add_message("session1", "user", "Hi")
            db.add_message("session1", "assistant", "Hello!")
            
            context = db.get_context_for_session("session1")
            assert "user:" in context
            assert "Recent conversation:" in context


class TestLTM:
    """Tests for Long-Term Memory."""
    
    def test_store_and_search_fact(self):
        """Test storing and searching facts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('amy.memory.ltm.Memory') as MockMemory:
                mock_memory = MagicMock()
                mock_memory.add.return_value = {'results': [{'id': '123'}]}
                mock_memory.search.return_value = {
                    'results': [{
                        'memory': 'User likes pizza',
                        'metadata': {'type': 'preference'},
                        'score': 0.9
                    }]
                }
                MockMemory.from_config.return_value = mock_memory
                
                ltm = LTM(vector_db_path=temp_dir)
                
                result = ltm.store_fact("User likes pizza", "preference", "user123")
                assert result is not None
                
                facts = ltm.search_facts("What food?", user_id="user123")
                assert len(facts) > 0


class TestAmy:
    """Tests for Amy class."""
    
    def test_get_brain_returns_amy(self):
        """Test that get_brain returns an Amy instance."""
        from amy.core.amy import Amy, get_brain
        amy = get_brain()
        assert isinstance(amy, Amy)
    
    @pytest.mark.asyncio
    async def test_chat_returns_response(self):
        """Test that amy.chat returns a response string."""
        from amy.core.amy import Amy
        
        with patch('amy.core.amy.Runner') as MockRunner:
            mock_runner = MagicMock()
            
            async def mock_run_async(*args, **kwargs):
                event = MagicMock()
                event.content = MagicMock()
                event.content.parts = [MagicMock(text="Hello!")]
                yield event
            
            mock_runner.run_async = mock_run_async
            MockRunner.return_value = mock_runner
            
            amy = Amy()
            response = await amy.chat("test", "Hi", "user", "test")
            
            assert isinstance(response, str)
            assert len(response) > 0

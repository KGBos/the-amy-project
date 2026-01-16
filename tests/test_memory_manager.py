import pytest
import asyncio
import os
from amy.features.memory.memory_manager import MemoryManager
from datetime import datetime

@pytest.fixture
def memory_manager():
    """Fixture to provide a MemoryManager instance for tests."""
    # Use a temporary in-memory SQLite database for testing MTM
    # and a temporary directory for LTM JSON files
    return MemoryManager(db_path=":memory:", vector_db_path="./test_vector_db")

@pytest.mark.asyncio
async def test_memory_manager_process_message_and_get_context(memory_manager):
    """Test that MemoryManager can process a message and retrieve it in context."""
    session_id = "test-session-123"
    platform = "test_platform"
    user_id = "test_user"
    username = "test_username"
    message_content = "This is a test message for memory manager."

    # Process the message
    memory_manager.process_message(session_id, platform, "user", message_content, user_id, username)

    # Get context for the session
    context = memory_manager.get_context_for_query(session_id, "test query")

    # Assert that the message content is in the retrieved context
    assert message_content in context
    assert "Recent conversation:" in context
    assert "user: This is a test message for memory manager." in context

    # Clean up temporary vector_db directory if it was created
    import shutil
    if memory_manager.ltm.vector_db_path != "instance/vector_db" and os.path.exists(memory_manager.ltm.vector_db_path):
        shutil.rmtree(memory_manager.ltm.vector_db_path)

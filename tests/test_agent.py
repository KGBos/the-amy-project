import pytest
import asyncio
from amy.core.amy_agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_root_agent_response():
    """Test that the root_agent can receive a message and provide a response."""
    # Note: We are using the root_agent from import, which might have already attempted to config genai.
    # Ideally for unit tests we should instantiate a fresh agent with mocks.
    
    session_service = InMemorySessionService()
    
    import os
    import tempfile
    from amy.features.memory import MemoryManager
    from amy.core.amy_agent.agent import AmyAgent

    # Use a temporary directory for the test database to avoid locking issues
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, "test_memory.db")
        vector_db_path = os.path.join(temp_dir, "vector_db")
        
        # Initialize MemoryManager with test paths
        test_memory_manager = MemoryManager(db_path=db_path, vector_db_path=vector_db_path)
        
        # Use patch to mock the genai module where it is imported in the agent module
        # We need to mock it BEFORE we instantiate AmyAgent, because __init__ now calls genai.configure
        with patch('amy.core.amy_agent.agent.genai') as mock_genai:
            # Configure the mock to return a specific response
            mock_model = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "I am ready to assist you."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Create a test agent with the test memory manager
            # This will trigger __init__ which uses the mocked genai
            test_agent = AmyAgent(memory_manager=test_memory_manager)
            
            # Re-create the runner with the test agent
            runner = Runner(
                app_name="test_agent",
                agent=test_agent,
                session_service=session_service,
            )

            session_id = "test-session-agent-response"
            user_id = "test-user-agent"
            user_message = "Hello Amy, how are you today?"
            content = Content(parts=[Part(text=user_message)])

            # Create the session
            await session_service.create_session(
                app_name="test_agent",
                user_id=user_id,
                session_id=session_id
            )

            response_text = ""
            print("\n--- ADK Runner Events ---")
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            ):
                print(f"Received event: {event}") # Log each event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
            print("--- End ADK Runner Events ---")
            
            assert len(response_text) > 0 and ("ready to" in response_text.lower() and ("assist" in response_text.lower() or "help" in response_text.lower())), "Agent should provide a relevant response indicating readiness to assist."
            print(f"\nFinal Agent response: {response_text}") # For debugging during test run

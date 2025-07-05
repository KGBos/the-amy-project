import pytest
import asyncio
from app.core.amy_agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

@pytest.mark.asyncio
async def test_root_agent_response():
    """Test that the root_agent can receive a message and provide a response."""
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="test_agent",
        agent=root_agent,
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

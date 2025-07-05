import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

import asyncio
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

async def main():
    # Define a minimal agent (same as amy_agent)
    agent = Agent(
        name="Amy",
        model="gemini-2.5-flash",
        description="Your personal AI assistant, Amy, with persistent memory.",
        instruction="You are Amy, a helpful and friendly AI assistant. You enjoy chatting and can answer general questions. You remember past conversations and use them to inform your responses.",
        tools=[]
    )

    # Use in-memory session service
    session_service = InMemorySessionService()

    # Create the runner
    runner = Runner(
        app_name="minimal_adk_test",
        agent=agent,
        session_service=session_service,
    )

    # Use a unique session ID for this test
    session_id = "test-session-1"
    user_id = "test-user"

    # The test message
    user_message = "Hello, Amy! Can you hear me?"
    content = Content(parts=[Part(text=user_message)])
    print(f"Sending to agent: {user_message}")

    # Create the session before running the agent
    await session_service.create_session(
        app_name="minimal_adk_test",
        user_id=user_id,
        session_id=session_id
    )

    # Run the agent and print the response
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
    print(f"Agent response: {response_text}")

if __name__ == "__main__":
    asyncio.run(main()) 
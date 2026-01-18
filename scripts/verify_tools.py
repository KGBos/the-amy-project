
import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock

# Ensure project root is in path
sys.path.append(os.getcwd())


import asyncio
import logging
import os
import sys
from unittest.mock import MagicMock

# Ensure project root is in path
sys.path.append(os.getcwd())

from google.adk import Runner
from google.genai.types import Content, Part
from amy.core.agent import create_root_agent

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tools():
    print("--- Verifying Tool Compatibility (Google Search + Function Calling) ---")
    
    # Mock LTM
    mock_ltm = MagicMock()
    mock_ltm.store_fact.return_value = "Success"
    mock_ltm.build_context_from_query.return_value = "" # Async mock needed?
    
    # Fix Async Mock
    async def async_return(*args, **kwargs):
        return ""
    mock_ltm.build_context_from_query.side_effect = async_return
    
    async def async_store(*args, **kwargs):
        print(f"LTM Store called with: {args}")
        return "Success"
    mock_ltm.store_fact.side_effect = async_store
    mock_ltm.search_facts.side_effect = lambda *a, **k: []

    # Create Agent
    root_agent = create_root_agent(mock_ltm)
    
    # Create Session Service (using InMemory or Temp DB)
    from amy.memory.conversation import ConversationDB
    from amy.memory.session_service import SqliteSessionService
    import tempfile
    
    td = tempfile.mkdtemp()
    db_path = os.path.join(td, "test_tools.db")
    db = ConversationDB(db_path)
    await db.initialize()
    session_service = SqliteSessionService(db)
    
    # Create Runner
    runner = Runner(agent=root_agent, session_service=session_service, app_name="amy")
    
    print("Runner created. Starting chat...")
    
    user_id = "test_user"
    session_id = "test_session"
    
    # Pre-create session to avoid "Not Found" logic in app
    await session_service.create_session("amy", user_id, session_id)

    
    # 1. Trigger Memory Save
    msg = Content(parts=[Part(text="My name is Leon, please remember that.")])
    
    print("\nSending Message: 'My name is Leon...'")
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=msg
        ):
            # Print minimal event info
            if event.content:
               print(f"Event Content: {event.content.parts}")
            if event.tool_call:
               print(f"Event Tool Call: {event.tool_call}")

        print("\nSUCCESS: Run completed without 400 error.")
        
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tools())


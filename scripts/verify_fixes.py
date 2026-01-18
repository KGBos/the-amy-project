
import asyncio
import os
import sys

# Ensure project root is in path
sys.path.append(os.getcwd())

# Mock Environment for Telemetry
os.environ["FREEPLAY_API_KEY"] = "mock_key"
os.environ["FREEPLAY_PROJECT_ID"] = "mock_project"

# 1. Verify Telemetry Monkeypatch
print("--- Verifying LlmRequest Monkeypatch ---")
try:
    from amy.core.telemetry import get_telemetry_plugins
    # Trigger import
    get_telemetry_plugins()
    
    from google.adk.models.llm_request import LlmRequest
    from google.genai import types

    req = LlmRequest(contents=[types.Content(parts=[types.Part(text="test")])])
    
    # Check alias
    print(f"LlmRequest.contents: {req.contents}")
    try:
        print(f"LlmRequest.messages (via property): {req.messages}")
        if req.messages == req.contents:
            print("SUCCESS: LlmRequest.messages aliases contents.")
        else:
            print("FAILURE: LlmRequest.messages does not match contents.")
    except AttributeError:
        print("FAILURE: LlmRequest has no 'messages' attribute.")

except Exception as e:
    print(f"FAILURE during Telemetry Check: {e}")
    import traceback
    traceback.print_exc()

# 2. Verify Session Service User ID Injection
print("\n--- Verifying Session Service User ID Injection ---")
import tempfile
import shutil
from amy.memory.conversation import ConversationDB
from amy.memory.session_service import SqliteSessionService

async def test_session():
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        db = ConversationDB(db_path)
        await db.initialize()
        service = SqliteSessionService(db)
        
        # Test Create Session
        s1 = await service.create_session("app", "user_123", "sess_1")
        print(f"Created Session State: {s1.state}")
        
        if s1.state.get("user_id") == "user_123":
            print("SUCCESS: create_session injected user_id.")
        else:
            print(f"FAILURE: create_session missing user_id. State: {s1.state}")

        # Test Get Session
        s2 = await service.get_session("app", "user_123", "sess_1")
        print(f"Retrieved Session State: {s2.state}")
        
        if s2.state.get("user_id") == "user_123":
            print("SUCCESS: get_session injected user_id.")
        else:
            print(f"FAILURE: get_session missing user_id. State: {s2.state}")
            
        await db.close()
        
    except Exception as e:
        print(f"FAILURE during Session Check: {e}")
        import traceback
        traceback.print_exc()
    finally:
        shutil.rmtree(temp_dir)

asyncio.run(test_session())

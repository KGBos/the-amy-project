import pytest
import os, warnings
import logging
from amy.core.amy import get_brain

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("amy")
logger.setLevel(logging.INFO)

# Suppress noisy logs
warnings.filterwarnings("ignore")
os.environ['IO_GRPC_PYTHON_MAX_METADATA_SIZE'] = '1024'

@pytest.mark.asyncio
async def test_amy_integration():
    print("=" * 50)
    print("TESTING ADK INTEGRATION")
    print("=" * 50)
    
    try:
        amy = get_brain()
        print("✅ ADK Brain retrieved")
        
        session_id = "test_adk_integration_v2"
        user_id = "test_user_adk_v2"
        
        msgs = ["Hi, I'm verifying the ADK rebuild.", "What did I just say?"]
        
        for m in msgs:
            print(f"\nME: {m}")
            response = await amy.chat(session_id, m, user_id=user_id, platform="test_script")
            print(f"AMY (via ADK Runner): {response}")
            assert response is not None
            
        print("\n" + "=" * 50)
        
        # Check Persistence
        db = amy.db
        count = db.get_message_count(session_id)
        print(f"Messages in DB: {count}")
        
        # We expect >= 4 messages (2 user + 2 model)
        assert count >= 4, f"Persistence FAILED (Count: {count})"
        print("✅ Persistence via Agent Callback WORKING")
        
    except Exception as e:
        pytest.fail(f"TEST FAILED WITH ERROR: {e}")

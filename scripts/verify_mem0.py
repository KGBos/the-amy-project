import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from amy.memory.ltm import LTM

async def test_ltm():
    print("Initializing LTM...")
    try:
        ltm = LTM(vector_db_path="instance/test_mem0")
        
        print("Storing fact...")
        await ltm.store_fact("The user likes python.", "preference", user_id="test_user")
        
        print("Searching fact...")
        results = await ltm.search_facts("python", user_id="test_user")
        print(f"Results: {results}")
        
        ltm.close()
        print("LTM Test Passed!")
    except Exception as e:
        print(f"LTM Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ltm())

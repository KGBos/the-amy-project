import sys
import os
import logging
from typing import Optional

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_mem0")

from dotenv import load_dotenv
load_dotenv()

# Ensure GOOGLE_API_KEY is set for Mem0 if GEMINI_API_KEY is present
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from amy.memory.ltm import LTM

def test_mem0_persistence():
    print("\n--- Testing Mem0 Integration ---")
    
    # Initialize LTM
    # Uses default or configured local path
    ltm = LTM()
    
    user_id = "test_user_verifier"
    fact_text = "The user prefers dark mode interfaces."
    fact_type = "preference"
    
    print(f"1. Storing fact: '{fact_text}'")
    result = ltm.store_fact(fact_text, fact_type, user_id)
    print(f"   Store Result: {result}")
    
    print("\n2. Searching for fact (query: 'interface preference')")
    results = ltm.search_facts("interface preference", user_id=user_id)
    
    found = False
    for res in results:
        res_content = res.get('content', '')
        print(f"   Found memory: {res_content} (Score: {res.get('relevance_score')})")
        if fact_text in res_content:
            found = True
            
    if found:
        print("\n✅ Verification SUCCESS: Memory was stored and retrieved via Mem0.")
    else:
        print("\n❌ Verification FAILED: Could not retrieve the stored memory.")
        # Print all results for debug
        print(f"   All Results: {results}")

if __name__ == "__main__":
    test_mem0_persistence()

"""
Debug script for Mem0 initialization.
"""
import os
import sys

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load Env
from dotenv import load_dotenv
load_dotenv()

from mem0 import Memory
import traceback

DEFAULT_MODEL = "gemini-2.0-flash-001"
LTM_TEMPERATURE = 0.1
EMBEDDER_MODEL = "all-MiniLM-L6-v2"
vector_db_path = "instance/mem0_storage"

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "amy_memories",
            "path": vector_db_path
        }
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "model": DEFAULT_MODEL,
            "temperature": LTM_TEMPERATURE,
            # Just in case API Key is needed explicitly here, though it should check Env
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": EMBEDDER_MODEL
        }
    }
}

print("Attempting to initialize Mem0...")
try:
    m = Memory.from_config(config)
    print("Success!")
except Exception:
    traceback.print_exc()

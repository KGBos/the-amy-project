"""
Verification Script for Phase 2
Checks if the Agent correctly loads the new Google Search tool.
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amy.core.agent import create_root_agent
from amy.memory.ltm import LTM

async def main():
    print("Initializing LTM...")
    ltm = LTM() # Mock or real LTM
    
    print("Creating Root Agent...")
    agent = create_root_agent(ltm)
    
    print(f"Agent Name: {agent.name}")
    print("Tools Loaded:")
    found_search = False
    for tool in agent.tools:
        # tool might be a FunctionTool or a Tool object
        name = getattr(tool, 'name', str(tool))
        print(f" - {name}")
        if "google_search" in str(name) or "google_search" in str(tool):
            found_search = True
            
    if found_search:
        print("\nSUCCESS: Google Search tool found!")
    else:
        print("\nFAILURE: Google Search tool NOT found.")

if __name__ == "__main__":
    asyncio.run(main())

"""
Verification Script for Phase 3 (Multi-Agent)
Checks if the Root Agent correctly loads sub-agents and tools.
"""
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from amy.core.agent import create_root_agent
from amy.memory.ltm import LTM

async def main():
    print("Initializing Agent Tree...")
    ltm = LTM()
    root = create_root_agent(ltm)
    
    print(f"Root Agent: {root.name}")
    print(f"  Description: {root.description}")
    print(f"  Tools: {[t.name if hasattr(t, 'name') else str(t) for t in root.tools]}")
    
    if not root.sub_agents:
        print("FAILURE: No sub-agents found on Root!")
        return

    print("\nSub-Agents:")
    for sub in root.sub_agents:
        print(f"  - Name: {sub.name}")
        print(f"    Class: {sub.__class__.__name__}")
        tool_names = []
        for t in sub.tools:
             # Handle FunctionTool or direct callables
             name = getattr(t, 'name', None)
             if not name and hasattr(t, 'func'):
                 name = t.func.__name__
             if not name:
                 name = str(t)
             tool_names.append(name)
        print(f"    Tools: {tool_names}")

    # Check specific requirements
    coder = next((a for a in root.sub_agents if a.name == 'coder_agent'), None)
    researcher = next((a for a in root.sub_agents if a.name == 'researcher_agent'), None)
    
    if coder and researcher:
        print("\nSUCCESS: Both Coder and Researcher agents found.")
    else:
        print("\nFAILURE: Missing one or more specialist agents.")

if __name__ == "__main__":
    asyncio.run(main())

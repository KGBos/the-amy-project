import os
import sys

# Add project root to sys.path to allow absolute imports of the 'amy' package
# without colliding with the agent's folder name.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from amy.core.agent import create_root_agent
from amy.memory.ltm import LTM

# Initialize a default LTM for CLI use
ltm = LTM()

# Export root_agent for ADK discovery
root_agent = create_root_agent(ltm)

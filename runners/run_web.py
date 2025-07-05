import os
import sys

# Add the project root to the Python path to resolve import issues
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from app.core.amy_agent.agent import root_agent
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Construct the absolute path to the database
db_path = os.path.join(project_root, "instance", "amy_memory.db")
db_url = f"sqlite:///{db_path}"

# Initialize the session service with the correct database
session_service = DatabaseSessionService(db_url=db_url)

# Create the Runner instance that the web UI will use
adk_runner = Runner(
    app_name="amy_agent",
    agent=root_agent,
    session_service=session_service,
)

print(f"Web runner configured to use database: {db_url}")

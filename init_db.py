from google.adk.sessions import DatabaseSessionService

import os

# Get the absolute path to the project's root directory
project_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_root, 'instance', 'amy_memory.db')
db_url = f"sqlite:///{db_path}"

session_service = DatabaseSessionService(db_url=db_url)
session_service.init_db()

print(f"Database schema initialized for {db_path}")
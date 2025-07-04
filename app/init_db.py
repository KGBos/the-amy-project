from google.adk.sessions import DatabaseSessionService

db_url = "sqlite:///./amy_memory.db"
session_service = DatabaseSessionService(db_url=db_url)
session_service.init_db()

print("Database schema initialized for amy_memory.db")
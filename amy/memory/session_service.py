
import logging
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session, Event
from google.genai.types import Content, Part
from amy.memory.conversation import ConversationDB

logger = logging.getLogger(__name__)

class SqliteSessionService(BaseSessionService):
    """
    ADK Session Service implementation backed by SQLite (ConversationDB).
    
    This allows the ADK Runner to automatically manage conversation history
    persistence, replacing manual management in the application layer.
    """
    
    def __init__(self, db: ConversationDB):
        self.db = db
        # Cache for active session objects to maintain state in memory during run
        self._cache: Dict[str, Session] = {}
        
    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Optional[Session]:
        """
        Retrieve a session from the database.
        """
        # Check cache first (optional, but good for performance within a run)
        cache_key = f"{app_name}:{session_id}"
        if cache_key in self._cache:
             return self._cache[cache_key]

        # Check existence
        if not self.db.get_message_count(session_id):
            return None

        # Load history
        # Note: ConversationDB stores messages (User/Model). 
        # ADK Sessions are lists of Events (which contain Content).
        # We need to map DB Messages -> ADK Events -> Session.history (which is List[Event])
        
        # NOTE: Standard ADK logic reconstructs Session from stored Events.
        # Our DB stores "messages", which are a simplified view.
        # We will map them back to simplified Events for compatibility.
        
        messages = self.db.get_recent_messages(session_id, limit=50) # Load reasonable context
        
        events = []
        for msg in messages:
            role = msg['role']
            text = msg['content']
            adk_role = 'user' if role == 'user' else 'model'
            
            # Construct Content
            content = Content(role=adk_role, parts=[Part(text=text)])
            
            # Construct Event (simplified)
            # We don't have exact timestamps or event types in simple DB, 
            # so we infer a basic "turn" event.
            event = Event(
                id=str(msg.get('id', '')), # Use DB ID if available
                author=adk_role, # Map role to author
                timestamp=0.0, # Unknown
                content=content
            )
            events.append(event)
            
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            events=events,
            state={'platform': 'unknown'} # State can hold other metadata
        )
        
        self._cache[cache_key] = session
        return session

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session."""
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            events=[], # Empty start
            state=state or {}
        )
        
        cache_key = f"{app_name}:{session_id}"
        self._cache[cache_key] = session
        return session

    async def append_event(self, session: Session, event: Event) -> None:
        """
        Persist a single event to the database.
        This is called by the Runner for every new event (User msg, Model response, Tool call).
        """
        # Update in-memory object first
        session.events.append(event)
        
        # We only care about persisting "Content" events (User/Model messages)
        # to our simple SQLite DB.
        # We might ignore ToolCalls for now if DB schema doesn't support them,
        # or just persist the final text response.
        
        if not event.content:
            return

        # Extract role/text
        role = event.content.role # 'user' or 'model'
        
        # Combine parts into single text for simple DB
        text_parts = [p.text for p in event.content.parts if p.text]
        text_content = "\n".join(text_parts).strip()
        
        if not text_content:
            return

        user_id = session.user_id
        platform = session.state.get('platform', 'unknown')
        
        # Map ADK role to DB role
        db_role = 'user' if role == 'user' else 'assistant'

        # Persist
        self.db.add_message(
            session.id,
            db_role,
            text_content,
            user_id,
            platform
        )

    async def list_sessions(self, app_name: str, limit: int = 10) -> List[Session]:
        return []

    async def delete_session(self, app_name: str, session_id: str) -> None:
        pass

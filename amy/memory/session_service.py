import logging
import asyncio
from typing import Optional, Dict, Any, List
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session, Event
from google.genai.types import Content, Part
from amy.memory.conversation import ConversationDB
from amy.config import MAX_SESSION_HISTORY

logger = logging.getLogger(__name__)

class SqliteSessionService(BaseSessionService):
    """
    ADK Session Service implementation backed by SQLite (ConversationDB).
    Refactored for native async support.
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
        Retrieve a session from the database asynchronously.
        """
        cache_key = f"{app_name}:{session_id}"
        if cache_key in self._cache:
             return self._cache[cache_key]

        # Use native async DB methods in parallel
        count_task = self.db.get_message_count(session_id)
        m_task = self.db.get_recent_messages(session_id, MAX_SESSION_HISTORY)
        
        message_count, messages = await asyncio.gather(count_task, m_task)
        
        if not message_count:
            return None
        
        events = []
        for msg in messages:
            role = msg['role']
            text = msg['content']
            adk_role = 'user' if role == 'user' else 'model'
            
            content = Content(role=adk_role, parts=[Part(text=text)])
            event = Event(
                id=str(msg.get('id', '')),
                author=adk_role,
                timestamp=0.0, # Placeholder
                content=content
            )
            events.append(event)
            
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            events=events,
            state={'platform': 'unknown'}
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
            events=[],
            state=state or {}
        )
        
        cache_key = f"{app_name}:{session_id}"
        self._cache[cache_key] = session
        return session

    async def append_event(self, session: Session, event: Event) -> None:
        """
        Persist a single event asynchronously.
        """
        session.events.append(event)
        
        if not event.content:
            return

        role = event.content.role
        text_content = "\n".join([p.text for p in event.content.parts if p.text]).strip()
        
        if not text_content:
            return

        user_id = session.user_id
        platform = session.state.get('platform', 'unknown')
        db_role = 'user' if role == 'user' else 'assistant'

        # Persist using new async method
        await self.db.add_message(
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


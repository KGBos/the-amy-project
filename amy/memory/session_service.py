
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Optional, Dict, Any, List
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session, Event
from google.genai.types import Content, Part
from amy.memory.conversation import ConversationDB
from amy.config import MAX_SESSION_HISTORY

logger = logging.getLogger(__name__)

# Thread pool for non-blocking DB operations
_db_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="db_worker")


class SqliteSessionService(BaseSessionService):
    """
    ADK Session Service implementation backed by SQLite (ConversationDB).
    
    This allows the ADK Runner to automatically manage conversation history
    persistence, replacing manual management in the application layer.
    
    Uses run_in_executor for non-blocking database operations.
    """
    
    def __init__(self, db: ConversationDB):
        self.db = db
        # Cache for active session objects to maintain state in memory during run
        self._cache: Dict[str, Session] = {}
    
    async def _run_sync(self, func, *args):
        """Run a synchronous function in the executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_db_executor, partial(func, *args))
        
    async def get_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> Optional[Session]:
        """
        Retrieve a session from the database.
        """
        # Check cache first (good for performance within a run)
        cache_key = f"{app_name}:{session_id}"
        if cache_key in self._cache:
             return self._cache[cache_key]

        # Check existence (async)
        message_count = await self._run_sync(self.db.get_message_count, session_id)
        if not message_count:
            return None

        # Load history (async)
        messages = await self._run_sync(
            self.db.get_recent_messages, 
            session_id, 
            MAX_SESSION_HISTORY
        )
        
        events = []
        for msg in messages:
            role = msg['role']
            text = msg['content']
            adk_role = 'user' if role == 'user' else 'model'
            
            # Construct Content
            content = Content(role=adk_role, parts=[Part(text=text)])
            
            # Construct Event (simplified)
            event = Event(
                id=str(msg.get('id', '')),
                author=adk_role,
                timestamp=0.0,
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
        Persist a single event to the database.
        This is called by the Runner for every new event (User msg, Model response, Tool call).
        """
        # Update in-memory object first
        session.events.append(event)
        
        # We only care about persisting "Content" events (User/Model messages)
        if not event.content:
            return

        # Extract role/text
        role = event.content.role
        
        # Combine parts into single text for simple DB
        text_parts = [p.text for p in event.content.parts if p.text]
        text_content = "\n".join(text_parts).strip()
        
        if not text_content:
            return

        user_id = session.user_id
        platform = session.state.get('platform', 'unknown')
        
        # Map ADK role to DB role
        db_role = 'user' if role == 'user' else 'assistant'

        # Persist (async)
        await self._run_sync(
            self.db.add_message,
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


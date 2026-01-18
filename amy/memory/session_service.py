import logging
import asyncio
import json
from typing import Optional, Dict, Any, List
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session, Event
from google.genai.types import Content, Part, FunctionCall
from amy.memory.conversation import ConversationDB
from amy.config import MAX_SESSION_HISTORY

logger = logging.getLogger(__name__)

class SqliteSessionService(BaseSessionService):
    """
    ADK Session Service implementation backed by SQLite (ConversationDB).
    Refactored for native async support and strict ADK compliance.
    """
    
    def __init__(self, db: ConversationDB):
        self.db = db
        # Cache to reduce DB reads for active sessions in the same run-loop.
        # However, for statelessness across restarts, we always rely on DB first.
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
        # 1. Fetch Session Metadata (State)
        metadata = await self.db.get_session_metadata(session_id)
        if not metadata:
            return None
            
        state = metadata.get('state', {})
        
        # 2. Fetch Events
        # We fetch ALL events for the session to reconstruct context.
        # In production, we might want to window this, but for now we fetch recent history.
        # Note: 'limit' here applies to distinct messages/turns.
        messages = await self.db.get_recent_messages(session_id, MAX_SESSION_HISTORY)
        
        events = []
        # messages come in reverse chronological order (newest first), so we flip them
        for msg in reversed(messages):
            event = None
            event_json = msg.get('event_json')
            
            # 1. Try to reconstruct from full JSON fidelity
            if event_json:
                try:
                    event_dict = json.loads(event_json)
                    # Reconstruct Content
                    if 'content' in event_dict and event_dict['content']:
                        c_data = event_dict['content']
                        parts = []
                        for p in c_data.get('parts', []):
                            if 'text' in p:
                                parts.append(Part(text=p['text']))
                            elif 'function_call' in p:
                                fc_data = p['function_call']
                                parts.append(Part(function_call=FunctionCall(
                                    name=fc_data.get('name', 'unknown'),
                                    args=fc_data.get('args', {})
                                )))
                        
                        content = Content(role=c_data.get('role', 'user'), parts=parts)
                    else:
                        content = None
                    
                    event = Event(
                        id=event_dict.get('id', str(msg.get('id', ''))),
                        author=event_dict.get('author', 'unknown'),
                        timestamp=event_dict.get('timestamp', 0.0),
                        content=content
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse event JSON for msg {msg['id']}: {e}")

            # 2. Fallback: Reconstruct from DB text columns
            if not event:
                role = msg['role']
                text = msg['content']
                adk_role = 'user' if role == 'user' else 'amy_root'
                
                parts = [Part(text=text)] if text else []
                content = Content(role=adk_role, parts=parts)
                
                event = Event(
                    id=str(msg.get('id', '')),
                    author=adk_role,
                    timestamp=0.0,
                    content=content
                )
            
            events.append(event)
            
        # The user_id is already available on the Session object.
            
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            events=events,
            state=state
        )
        
        self._cache[session_id] = session
        return session

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session and persist it."""
        state = state or {}
        
        # The user_id is already available on the Session object.

        # Persist to DB
        await self.db.upsert_session(session_id, app_name, user_id, state)
        
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            events=[],
            state=state
        )
        
        self._cache[session_id] = session
        return session

    async def append_event(self, session: Session, event: Event) -> None:
        """
        Persist a single event asynchronously using full serialization.
        """
        session.events.append(event)
        
        # 1. Serialize Event to JSON Implementation
        # We iterate over parts to make them serializable dicts
        event_dict = {
            "id": event.id,
            "author": event.author,
            "timestamp": event.timestamp,
        }
        
        text_content = ""
        role = "unknown"
        
        if event.content:
            role = event.content.role
            event_dict["content"] = {
                "role": role,
                "parts": []
            }
            if event.content.parts:
                text_parts = []
                for p in event.content.parts:
                    p_dict = {}
                    # Prioritize text
                    if hasattr(p, 'text') and p.text:
                        p_dict['text'] = p.text
                        text_parts.append(p.text)
                    
                    # Handle function calls
                    if hasattr(p, 'function_call') and p.function_call:
                        fc = p.function_call
                        p_dict['function_call'] = {
                            "name": getattr(fc, 'name', 'unknown'),
                            "args": getattr(fc, 'args', {})
                        }
                    
                    # Handle function responses
                    if hasattr(p, 'function_response') and p.function_response:
                        fr = p.function_response
                        p_dict['function_response'] = {
                            "name": getattr(fr, 'name', 'unknown'),
                            "response": getattr(fr, 'response', {})
                        }
                    
                    if p_dict:
                        event_dict["content"]["parts"].append(p_dict)
                
                text_content = "\n".join(text_parts).strip()

        user_id = session.user_id
        platform = session.state.get('platform', 'unknown')
        
        # Map ADK roles back to DB roles (user vs assistant)
        db_role = 'user' if role == 'user' else 'assistant'

        # Persist using new add_event method
        await self.db.add_event(
            session_id=session.id,
            role=db_role,
            content_text=text_content,
            event_dict=event_dict,
            user_id=user_id,
            platform=platform
        )

    async def update_session_state(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Update and persist session state."""
        # Update local object if cached (optional, but good for consistency)
        if session_id in self._cache:
            self._cache[session_id].state = state
            
        # Persist to DB
        await self.db.upsert_session(session_id, app_name, user_id, state)

    async def list_sessions(self, app_name: str, limit: int = 10) -> List[Session]:
        """List sessions for a given app. 
        Note: The BaseSessionService signature only asks for app_name and limit, but user_id is crucial.
        The ADK might assume app-level sessions, but practical implementations usually need user context.
        To comply with signature, we might need to change how we query or ignore user filter if not passed.
        
        However, for strict compliance matching the base class `list_sessions(self, app_name: str, limit: int = 10)`,
        we can't easily filter by user without extending the interface or assuming global scope.
        
        Let's implement a best-effort global list or modify usage. 
        Actually, BaseSessionService defines: `list_sessions(self, app_name: str, limit: int = 10)`.
        It doesn't take user_id. This implies admin-level listing.
        """
        # We'll list most recent sessions for the app regardless of user
        # Note: ConversationDB specific method for this
        async with self.db._get_connection() as conn:
             async with conn.execute("""
                SELECT * FROM sessions 
                WHERE app_name = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (app_name, limit)) as cursor:
                 rows = await cursor.fetchall()
                 sessions = []
                 for row in rows:
                     d = dict(row)
                     state = {}
                     if d['state_json']:
                         try:
                             state = json.loads(d['state_json'])
                         except:
                             pass
                     
                     # Minimal session object for listing (no events loaded for perf)
                     s = Session(
                         id=d['session_id'],
                         app_name=d['app_name'],
                         user_id=d['user_id'],
                         events=[],
                         state=state
                     )
                     sessions.append(s)
                 return sessions

    async def delete_session(self, app_name: str, session_id: str) -> None:
        """Delete a session."""
        # Clean cache
        if session_id in self._cache:
            del self._cache[session_id]
            
        await self.db.delete_session(session_id)


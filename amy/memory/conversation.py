"""
Conversation Database for Amy
Single source of truth for all conversation persistence.
Refactored for non-blocking I/O using aiosqlite.
NOW SUPPORTS: Full Google ADK Session & Event persistence.
"""

import aiosqlite
import logging
import asyncio
import json
import contextlib
from typing import List, Dict, Optional, Any, AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDB:
    """
    Persistent conversation storage using SQLite with aiosqlite for async support.
    
    Enables WAL mode for high concurrency between Telegram and Web UI.
    Supports full Google ADK Session and Event models.
    """
    
    def __init__(self, db_path: str = "instance/amy.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        self._ensure_dir()
        logger.info(f"ConversationDB initialized: {self.db_path}")

    def _ensure_dir(self):
        """Ensure the database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @contextlib.asynccontextmanager
    async def _get_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Get or reuse a persistent connection with optimized pragmas.
        """
        async with self._lock:
            if self._conn is None:
                self._conn = await aiosqlite.connect(self.db_path)
                self._conn.row_factory = aiosqlite.Row
                
                # Optimize for concurrency and speed
                await self._conn.execute("PRAGMA journal_mode=WAL")
                await self._conn.execute("PRAGMA synchronous=NORMAL")
                await self._conn.execute("PRAGMA busy_timeout=5000")
                logger.debug("Database connection established and optimized")
            
            yield self._conn

    async def close(self):
        """Close the persistent database connection."""
        async with self._lock:
            if self._conn:
                await self._conn.close()
                self._conn = None
                logger.info("Database connection closed")

    async def initialize(self):
        """
        Create database and tables if they don't exist.
        Includes lazy schema migration (drop & recreate) if columns are missing.
        """
        async with self._get_connection() as conn:
            # Check for schema compatibility (dirty check)
            try:
                # Check if 'event_json' exists in messages
                cursor = await conn.execute("PRAGMA table_info(messages)")
                columns = [row['name'] for row in await cursor.fetchall()]
                if 'messages' in columns and 'event_json' not in columns:
                    logger.warning("Old schema detected. Dropping 'messages' table for migration.")
                    await conn.execute("DROP TABLE messages")
            except Exception:
                pass

            # 1. Sessions Table (New for ADK Compliance)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    app_name TEXT NOT NULL,
                    user_id TEXT,
                    state_json TEXT,  -- JSON serialized session state
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Messages/Events Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT,     -- Human readable text (can be null for tool events)
                    event_json TEXT,  -- Full ADK Event object serialized
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    platform TEXT DEFAULT 'unknown',
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, timestamp DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user 
                ON messages(user_id)
            """)
            
            await conn.commit()
            logger.debug("Database schema verified")
    
    # --- Session Management ---

    async def upsert_session(
        self,
        session_id: str,
        app_name: str,
        user_id: str,
        state: Dict[str, Any]
    ):
        """Create or update a session."""
        state_json = json.dumps(state)
        async with self._get_connection() as conn:
            await conn.execute("""
                INSERT INTO sessions (session_id, app_name, user_id, state_json, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (session_id, app_name, user_id, state_json))
            await conn.commit()

    async def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session metadata including state."""
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT * FROM sessions WHERE session_id = ?
            """, (session_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                bs = dict(row)
                if bs['state_json']:
                    bs['state'] = json.loads(bs['state_json'])
                else:
                    bs['state'] = {}
                return bs

    # --- Message/Event Management ---

    async def add_event(
        self, 
        session_id: str, 
        role: str, 
        content_text: str,
        event_dict: Dict[str, Any],
        user_id: Optional[str] = None,
        platform: str = "unknown"
    ) -> int:
        """
        Store a full ADK event.
        """
        event_json = json.dumps(event_dict)
        async with self._get_connection() as conn:
            cursor = await conn.execute("""
                INSERT INTO messages (session_id, user_id, role, content, event_json, platform)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, role, content_text, event_json, platform))
            await conn.commit()
            msg_id = cursor.lastrowid
            logger.debug(f"Stored event {msg_id} for session {session_id}")
            return msg_id
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        user_id: Optional[str] = None,
        platform: str = "unknown"
    ) -> int:
        """
        Legacy method kept for minimal back-compat, though should be avoided in favor of add_event.
        """
        # Create a dummy event wrapper
        dummy_event = {
            "type": "message",
            "role": role,
            "content": content
        }
        return await self.add_event(session_id, role, content, dummy_event, user_id, platform)

    async def get_recent_messages(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent messages for a session asynchronously.
        Returns dicts with 'role', 'content', and 'event_json'.
        """
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT id, role, content, event_json, timestamp 
                FROM messages 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit)) as cursor:
                rows = await cursor.fetchall()
                messages = []
                for row in reversed(rows):
                    d = dict(row)
                    # Parse JSON if needed by caller, but for now return raw or parsed?
                    # Let's return the raw dict, SessionService will parse.
                    messages.append(d)
                return messages
    
    async def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session asynchronously."""
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            """, (session_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0]
    
    async def get_user_sessions(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get sessions for a user asynchronously.
        Returns list of metadata dicts.
        """
        async with self._get_connection() as conn:
            # We can now query the sessions table directly
            async with conn.execute("""
                SELECT * FROM sessions 
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                results = []
                if rows:
                    for row in rows:
                        d = dict(row)
                        if d['state_json']:
                            d['state'] = json.loads(d['state_json'])
                        results.append(d)
                return results

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all its messages."""
        async with self._get_connection() as conn:
            await conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            await conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            await conn.commit()
            logger.info(f"Deleted session {session_id}")
    
    async def has_previous_conversations(self, user_id: str) -> bool:
        """Check if user has any previous conversations asynchronously."""
        async with self._get_connection() as conn:
             async with conn.execute("""
                SELECT 1 FROM sessions WHERE user_id = ? LIMIT 1
            """, (user_id,)) as cursor:
                if await cursor.fetchone():
                    return True
                    
             async with conn.execute("""
                SELECT 1 FROM messages WHERE user_id = ? LIMIT 1
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row is not None
    
    async def get_context_for_session(
        self, 
        session_id: str, 
        limit: int = 10,
        max_chars: int = 2000
    ) -> str:
        """
        Get formatted context string for a session asynchronously.
        Only uses text content.
        """
        messages = await self.get_recent_messages(session_id, limit)
        return self.format_for_context(messages, max_chars)

    def format_for_context(
        self, 
        messages: List[Dict], 
        max_chars: int = 2000
    ) -> str:
        """
        Format messages as a conversation string for LLM context.
        """
        if not messages:
            return ""
        
        valid_lines = []
        total_chars = 0
        
        for msg in reversed(messages): # Messages coming in chronological order from get_recent_messages
            role = msg['role']
            content = msg['content']
            if not content:
                continue # Skip tool events without text representation for simple context
                
            line = f"{role}: {content}"
            
            if total_chars + len(line) + 1 > max_chars:
                break
            
            valid_lines.append(line)
            total_chars += len(line) + 1
            
        if not valid_lines:
            return ""
            
        chronological_lines = reversed(valid_lines)
        return "Recent conversation:\n" + "\n".join(chronological_lines)

    def close_sync(self):
        """No-op for aiosqlite as it manages connections per-context."""
        pass

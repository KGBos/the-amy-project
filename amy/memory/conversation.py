"""
Conversation Database for Amy
Single source of truth for all conversation persistence.
Refactored for non-blocking I/O using aiosqlite.
"""

import aiosqlite
import logging
import asyncio
import contextlib
from typing import List, Dict, Optional, AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDB:
    """
    Persistent conversation storage using SQLite with aiosqlite for async support.
    
    Enables WAL mode for high concurrency between Telegram and Web UI.
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
        """Create database and tables if they don't exist."""
        async with self._get_connection() as conn:
            # Messages table - the core of conversation storage
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    platform TEXT DEFAULT 'unknown'
                )
            """)
            # ... and other indexes as before ...
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
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        user_id: Optional[str] = None,
        platform: str = "unknown"
    ) -> int:
        """
        Store a message asynchronously.
        """
        async with self._get_connection() as conn:
            cursor = await conn.execute("""
                INSERT INTO messages (session_id, user_id, role, content, platform)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, role, content, platform))
            await conn.commit()
            msg_id = cursor.lastrowid
            logger.debug(f"Stored message {msg_id}: {role}: {content[:50]}...")
            return msg_id
    
    async def get_recent_messages(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent messages for a session asynchronously.
        """
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT id, role, content, timestamp 
                FROM messages 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit)) as cursor:
                rows = await cursor.fetchall()
                messages = [dict(row) for row in reversed(rows)]
                return messages
    
    async def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session asynchronously."""
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            """, (session_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0]
    
    async def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user asynchronously."""
        async with self._get_connection() as conn:
            async with conn.execute("""
                SELECT DISTINCT session_id FROM messages 
                WHERE user_id = ?
                ORDER BY MAX(timestamp) DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def has_previous_conversations(self, user_id: str) -> bool:
        """Check if user has any previous conversations asynchronously."""
        async with self._get_connection() as conn:
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
        (Synchronous helper as it only processes data in memory)
        """
        if not messages:
            return ""
        
        valid_lines = []
        total_chars = 0
        
        for msg in reversed(messages):
            role = msg['role']
            content = msg['content']
            line = f"{role}: {content}"
            
            if total_chars + len(line) + 1 > max_chars:
                break
            
            valid_lines.append(line)
            total_chars += len(line) + 1
            
        if not valid_lines:
            return ""
            
        chronological_lines = reversed(valid_lines)
        return "Recent conversation:\n" + "\n".join(chronological_lines)

    def close(self):
        """No-op for aiosqlite as it manages connections per-context."""
        pass

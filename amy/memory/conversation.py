"""
Conversation Database for Amy
Single source of truth for all conversation persistence
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationDB:
    """
    Persistent conversation storage using SQLite.
    
    Replaces the complex STM/EpTM/SessionManager mess with a single,
    clean database layer.
    """
    
    def __init__(self, db_path: str = "instance/amy.db"):
        """Initialize with database path."""
        self.db_path = db_path
        self._ensure_db_exists()
        logger.info(f"ConversationDB initialized: {db_path}")
    
    def _ensure_db_exists(self):
        """Create database and tables if they don't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Messages table - the core of conversation storage
            cursor.execute("""
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
            
            # Index for fast session lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, timestamp DESC)
            """)
            
            # Index for user lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_user 
                ON messages(user_id)
            """)
            
            conn.commit()
            logger.debug("Database schema verified")
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        user_id: Optional[str] = None,
        platform: str = "unknown"
    ) -> int:
        """
        Store a message.
        
        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message text
            user_id: Optional user identifier
            platform: Platform name (telegram, web, etc.)
            
        Returns:
            The message ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (session_id, user_id, role, content, platform)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, role, content, platform))
            conn.commit()
            
            msg_id = cursor.lastrowid
            logger.debug(f"Stored message {msg_id}: {role}: {content[:50]}...")
            return msg_id
    
    def get_recent_messages(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Get recent messages for a session.
        
        Args:
            session_id: Session to get messages for
            limit: Maximum number of messages to return
            
        Returns:
            List of message dicts, oldest first
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get last N messages, then reverse to get chronological order
            cursor.execute("""
                SELECT id, role, content, timestamp 
                FROM messages 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, limit))
            
            rows = cursor.fetchall()
            # Reverse to get chronological order
            messages = [dict(row) for row in reversed(rows)]
            return messages
    
    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            """, (session_id,))
            return cursor.fetchone()[0]
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT session_id FROM messages 
                WHERE user_id = ?
                ORDER BY MAX(timestamp) DESC
            """, (user_id,))
            return [row[0] for row in cursor.fetchall()]
    
    def has_previous_conversations(self, user_id: str) -> bool:
        """Check if user has any previous conversations."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM messages WHERE user_id = ? LIMIT 1
            """, (user_id,))
            return cursor.fetchone() is not None
    
    def format_for_context(
        self, 
        messages: List[Dict], 
        max_chars: int = 2000
    ) -> str:
        """
        Format messages as a conversation string for LLM context.
        
        Args:
            messages: List of message dicts
            max_chars: Maximum characters to include
            
        Returns:
            Formatted conversation string
        """
        if not messages:
            return ""
        
        lines = []
        total_chars = 0
        
        # Process in reverse to prioritize recent messages
        for msg in reversed(messages):
            role = msg['role']
            content = msg['content']
            line = f"{role}: {content}"
            
            if total_chars + len(line) + 1 > max_chars:
                break
            
            lines.insert(0, line)
            total_chars += len(line) + 1
        
        if not lines:
            return ""
            
        return "Recent conversation:\n" + "\n".join(lines)
    
    def get_context_for_session(
        self, 
        session_id: str, 
        limit: int = 10,
        max_chars: int = 2000
    ) -> str:
        """
        Get formatted context string for a session.
        
        Convenience method combining get_recent_messages and format_for_context.
        """
        messages = self.get_recent_messages(session_id, limit)
        return self.format_for_context(messages, max_chars)

"""
Medium-Term Memory (MTM) for Amy
Handles permanent conversation storage and session management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3
import json
import logging
import os

logger = logging.getLogger(__name__)

class MediumTermMemory:
    """
    Medium-Term Memory system for permanent conversation storage.
    Stores all conversations across all platforms in SQLite database.
    """
    
    def __init__(self, db_path: str = "instance/amy_memory.db"):
        """
        Initialize MTM with database path.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._ensure_db_exists()
        
    def _ensure_db_exists(self) -> None:
        """Ensure the database and tables exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    user_id TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            
            conn.commit()
            
    def add_conversation(self, session_id: str, platform: str, user_id: Optional[str] = None, username: Optional[str] = None) -> int:
        """
        Add a new conversation session.
        
        Args:
            session_id: Unique session identifier
            platform: Platform name (telegram, web, etc.)
            user_id: User identifier
            username: Username
            
        Returns:
            Conversation ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (session_id, platform, user_id, username)
                VALUES (?, ?, ?, ?)
            """, (session_id, platform, user_id, username))
            conn.commit()
            conversation_id = cursor.lastrowid
            if conversation_id is None:
                raise RuntimeError("Failed to create conversation - no ID returned")
            return conversation_id
            
    def add_message(self, conversation_id: int, role: str, content: str, timestamp: Optional[datetime] = None) -> None:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation ID
            role: 'user' or 'model'
            content: Message content
            timestamp: Message timestamp
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, role, content, timestamp or datetime.now()))
            conn.commit()
            
    def get_conversation_messages(self, session_id: str) -> List[dict]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages with role, content, and timestamp
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.role, m.content, m.timestamp
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.session_id = ?
                ORDER BY m.timestamp ASC
            """, (session_id,))
            
            return [
                {'role': row[0], 'content': row[1], 'timestamp': row[2]}
                for row in cursor.fetchall()
            ]
            
    def get_all_sessions(self) -> List[dict]:
        """
        Get all conversation sessions.
        
        Returns:
            List of session information
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, platform, user_id, username, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
            """)
            
            return [
                {
                    'session_id': row[0],
                    'platform': row[1],
                    'user_id': row[2],
                    'username': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                for row in cursor.fetchall()
            ]
            
    def search_conversations(self, query: str) -> List[dict]:
        """
        Search conversations by content.
        
        Args:
            query: Search term
            
        Returns:
            List of matching conversations
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT c.session_id, c.platform, c.username, m.content
                FROM conversations c
                JOIN messages m ON c.id = m.conversation_id
                WHERE m.content LIKE ?
                ORDER BY m.timestamp DESC
            """, (f'%{query}%',))
            
            return [
                {
                    'session_id': row[0],
                    'platform': row[1],
                    'username': row[2],
                    'content': row[3]
                }
                for row in cursor.fetchall()
            ] 
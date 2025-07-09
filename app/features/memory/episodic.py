"""
Episodic Memory (EpTM) for Amy
Handles conversation summarization and session storage
"""

import logging
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class EpisodicMemory:
    """
    Episodic Memory system for storing conversation summaries and session data.
    Provides a middle layer between STM and LTM for conversation patterns.
    """
    
    def __init__(self, db_path: str = "instance/amy_memory.db"):
        """
        Initialize Episodic Memory with SQLite storage.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self._ensure_db_exists()
        logger.info(f"Episodic Memory initialized with database: {db_path}")
    
    def _ensure_db_exists(self) -> None:
        """Ensure the SQLite database exists with proper schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create conversations table (if not exists)
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
        
        # Create messages table (if not exists)
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
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
            ON conversations(session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
            ON messages(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Episodic Memory database schema created/verified")
    
    def add_message(self, session_id: str, role: str, content: str, timestamp: datetime) -> None:
        """
        Add a message to episodic memory.
        
        Args:
            session_id: Session identifier
            role: 'user' or 'model'
            content: Message content
            timestamp: Message timestamp
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get or create conversation for this session
            cursor.execute("""
                SELECT id FROM conversations 
                WHERE session_id = ?
            """, (session_id,))
            
            conversation_row = cursor.fetchone()
            if conversation_row:
                conversation_id = conversation_row[0]
            else:
                # Create new conversation
                cursor.execute("""
                    INSERT INTO conversations (session_id, platform, user_id, username)
                    VALUES (?, ?, ?, ?)
                """, (session_id, "telegram", None, None))
                conversation_id = cursor.lastrowid
            
            # Insert message
            cursor.execute("""
                INSERT INTO messages (conversation_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (conversation_id, role, content, timestamp))
            
            # Update conversation timestamp
            cursor.execute("""
                UPDATE conversations 
                SET updated_at = ?
                WHERE id = ?
            """, (timestamp, conversation_id))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Added message to EpTM: {session_id} - {role}")
            
        except Exception as e:
            logger.error(f"Error adding message to EpTM: {e}")
    
    def create_session(self, session_id: str, user_id: str, platform: str) -> None:
        """
        Create a new session in episodic memory.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            platform: Platform name
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO conversations (session_id, platform, user_id, username)
                VALUES (?, ?, ?, ?)
            """, (session_id, platform, user_id, None))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created EpTM session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error creating EpTM session: {e}")
    
    def get_session_messages(self, session_id: str) -> List[Dict]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT m.role, m.content, m.timestamp
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.session_id = ?
                ORDER BY m.timestamp
            """, (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2]
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            logger.error(f"Error getting session messages: {e}")
            return []
    
    def summarize_session(self, session_id: str) -> str:
        """
        Generate a simple summary of a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session summary
        """
        messages = self.get_session_messages(session_id)
        if not messages:
            return ""
        
        # Simple summary: count messages and extract key topics
        user_messages = [msg for msg in messages if msg['role'] == 'user']
        model_messages = [msg for msg in messages if msg['role'] == 'model']
        
        summary_parts = [
            f"Session: {session_id}",
            f"Total messages: {len(messages)}",
            f"User messages: {len(user_messages)}",
            f"AI responses: {len(model_messages)}"
        ]
        
        # Extract key topics from user messages
        topics = []
        for msg in user_messages[:5]:  # Look at first 5 user messages
            content = msg['content'].lower()
            if any(word in content for word in ['name', 'call', 'i am']):
                topics.append("name introduction")
            if any(word in content for word in ['work', 'job', 'profession']):
                topics.append("work/profession")
            if any(word in content for word in ['live', 'location', 'city']):
                topics.append("location")
            if any(word in content for word in ['like', 'love', 'enjoy']):
                topics.append("preferences")
        
        if topics:
            summary_parts.append(f"Topics discussed: {', '.join(set(topics))}")
        
        return " | ".join(summary_parts)
    
    def get_context(self, session_id: str, query: str) -> str:
        """
        Get episodic context for a query.
        
        Args:
            session_id: Session identifier
            query: The query to get context for
            
        Returns:
            Episodic context string
        """
        summary = self.summarize_session(session_id)
        if summary:
            return f"Previous conversation: {summary}"
        return ""
    
    def search_conversations(self, query: str, user_id: Optional[str] = None) -> List[Dict]:
        """
        Search conversations by content.
        
        Args:
            query: Search query
            user_id: Optional user ID filter
            
        Returns:
            List of matching conversations
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT s.id, s.user_id, s.platform, s.created_at, s.message_count
                    FROM sessions s
                    JOIN messages m ON s.id = m.session_id
                    WHERE s.user_id = ? AND m.content LIKE ?
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """, (user_id, f"%{query}%"))
            else:
                cursor.execute("""
                    SELECT s.id, s.user_id, s.platform, s.created_at, s.message_count
                    FROM sessions s
                    JOIN messages m ON s.id = m.session_id
                    WHERE m.content LIKE ?
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """, (f"%{query}%",))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'session_id': row[0],
                    'user_id': row[1],
                    'platform': row[2],
                    'created_at': row[3],
                    'message_count': row[4]
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get all sessions.
        
        Returns:
            List of session information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, platform, created_at, updated_at, message_count
                FROM sessions
                ORDER BY created_at DESC
            """)
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'user_id': row[1],
                    'platform': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'message_count': row[5]
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting all sessions: {e}")
            return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get episodic memory statistics.
        
        Returns:
            Dictionary with EpTM statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total sessions
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Get total messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
            
            # Get sessions by platform
            cursor.execute("""
                SELECT platform, COUNT(*) 
                FROM sessions 
                GROUP BY platform
            """)
            platforms = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'platforms': platforms
            }
            
        except Exception as e:
            logger.error(f"Error getting EpTM stats: {e}")
            return {
                'total_sessions': 0,
                'total_messages': 0,
                'platforms': {}
            } 
#!/usr/bin/env python3
"""
Live Memory Monitor for Amy
Real-time monitoring of memory operations during conversations
"""

import time
import json
import threading
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveMemoryMonitor:
    """
    Real-time memory monitoring tool that watches memory operations
    and displays them in a user-friendly format.
    """
    
    def __init__(self, db_path: str = "instance/amy_memory.db", vector_db_path: str = "instance/vector_db"):
        self.db_path = db_path
        self.vector_db_path = vector_db_path
        self.monitoring = False
        self.last_db_size = 0
        self.last_vector_db_count = 0
        self.session_activity = {}
        
    def start_monitoring(self):
        """Start real-time memory monitoring."""
        self.monitoring = True
        print("🔍 Starting live memory monitoring...")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        try:
            while self.monitoring:
                self.check_memory_changes()
                time.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop memory monitoring."""
        self.monitoring = False
        print("\n🛑 Memory monitoring stopped.")
    
    def check_memory_changes(self):
        """Check for changes in memory systems and display them."""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Check database size changes
        if os.path.exists(self.db_path):
            current_db_size = os.path.getsize(self.db_path)
            if current_db_size != self.last_db_size:
                size_diff = current_db_size - self.last_db_size
                print(f"[{current_time}] 📊 MTM Database size changed: {size_diff:+d} bytes")
                self.last_db_size = current_db_size
        
        # Check vector database changes
        if os.path.exists(self.vector_db_path):
            current_vector_files = len([f for f in os.listdir(self.vector_db_path) if f.endswith('.json')])
            if current_vector_files != self.last_vector_db_count:
                file_diff = current_vector_files - self.last_vector_db_count
                print(f"[{current_time}] 🧠 LTM Facts changed: {file_diff:+d} files")
                self.last_vector_db_count = current_vector_files
        
        # Check STM activity
        self.check_stm_activity(current_time)
        
        # Check for new conversations
        self.check_new_conversations(current_time)
    
    def check_stm_activity(self, timestamp: str):
        """Check for STM activity changes."""
        try:
            from app.features.memory.stm import ShortTermMemory
            stm = ShortTermMemory()
            
            current_sessions = set(stm.get_all_sessions())
            
            for session_id in current_sessions:
                if session_id not in self.session_activity:
                    self.session_activity[session_id] = {
                        'first_seen': timestamp,
                        'message_count': 0
                    }
                    print(f"[{timestamp}] 🆕 New STM session: {session_id}")
                
                # Check message count
                messages = stm.get_context(session_id)
                current_count = len(messages)
                previous_count = self.session_activity[session_id]['message_count']
                
                if current_count > previous_count:
                    new_messages = current_count - previous_count
                    print(f"[{timestamp}] 💬 STM session {session_id}: +{new_messages} messages (total: {current_count})")
                    self.session_activity[session_id]['message_count'] = current_count
                    
        except Exception as e:
            logger.debug(f"Error checking STM activity: {e}")
    
    def check_new_conversations(self, timestamp: str):
        """Check for new conversations in MTM."""
        try:
            if not os.path.exists(self.db_path):
                return
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, platform, user_id, username, created_at
                    FROM conversations
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    session_id, platform, user_id, username, created_at = row
                    
                    # Check if this is a new conversation (created in last 10 seconds)
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_diff = (datetime.now() - created_time).total_seconds()
                    
                    if time_diff < 10:  # New conversation
                        print(f"[{timestamp}] 🆕 New MTM conversation: {session_id} ({platform})")
                        
        except Exception as e:
            logger.debug(f"Error checking new conversations: {e}")
    
    def show_memory_snapshot(self):
        """Show a snapshot of current memory state."""
        print("\n📸 MEMORY SNAPSHOT")
        print("=" * 50)
        
        # STM Snapshot
        try:
            from app.features.memory.stm import ShortTermMemory
            stm = ShortTermMemory()
            active_sessions = stm.get_all_sessions()
            
            print(f"📝 STM Active Sessions: {len(active_sessions)}")
            for session_id in active_sessions:
                messages = stm.get_context(session_id)
                print(f"  • {session_id}: {len(messages)} messages")
                
        except Exception as e:
            print(f"❌ Error getting STM snapshot: {e}")
        
        # MTM Snapshot
        try:
            if os.path.exists(self.db_path):
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM conversations")
                    conversation_count = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT COUNT(*) FROM messages")
                    message_count = cursor.fetchone()[0]
                    
                    print(f"💾 MTM Conversations: {conversation_count}")
                    print(f"💾 MTM Messages: {message_count}")
                    
        except Exception as e:
            print(f"❌ Error getting MTM snapshot: {e}")
        
        # LTM Snapshot
        try:
            if os.path.exists(self.vector_db_path):
                fact_files = [f for f in os.listdir(self.vector_db_path) if f.endswith('.json')]
                print(f"🧠 LTM Facts: {len(fact_files)}")
                
        except Exception as e:
            print(f"❌ Error getting LTM snapshot: {e}")
        
        print("=" * 50)

def main():
    """Run the live memory monitor."""
    monitor = LiveMemoryMonitor()
    
    print("🔍 Amy Live Memory Monitor")
    print("This tool will show real-time memory operations as they happen.")
    print("Start a conversation with Amy in another terminal to see the memory system in action!")
    print()
    
    # Show initial snapshot
    monitor.show_memory_snapshot()
    print()
    
    # Start monitoring
    monitor.start_monitoring()

if __name__ == "__main__":
    main() 
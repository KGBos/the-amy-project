#!/usr/bin/env python3
"""
Simple script to view ADK sessions and their contents
"""

import sqlite3
import json
import os
from datetime import datetime

def view_sessions():
    """View all sessions in the database"""
    db_path = "instance/amy_memory.db"
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all sessions
    cursor.execute("SELECT app_name, user_id, id, create_time, update_time FROM sessions ORDER BY update_time DESC")
    sessions = cursor.fetchall()
    
    print("=== ADK Sessions ===")
    for session in sessions:
        app_name, user_id, session_id, created_at, updated_at = session
        print(f"\n📱 Session: {session_id}")
        print(f"   App: {app_name}")
        print(f"   User: {user_id}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        # Get events for this session
        cursor.execute("""
            SELECT author, content, timestamp 
            FROM events 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
        """, (session_id,))
        
        events = cursor.fetchall()
        if events:
            print(f"   📝 Events ({len(events)} messages):")
            for event in events:
                author, content_json, timestamp = event
                try:
                    content_dict = json.loads(content_json)
                    text_content = ""
                    if 'parts' in content_dict:
                        for part in content_dict['parts']:
                            if 'text' in part:
                                text_content += part['text']
                    
                    # Format timestamp
                    if isinstance(timestamp, (int, float)):
                        dt = datetime.fromtimestamp(timestamp)
                        time_str = dt.strftime("%H:%M:%S")
                    else:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M:%S")
                        except Exception:
                            time_str = str(timestamp)
                    
                    print(f"      [{time_str}] {author.upper()}: {text_content[:100]}{'...' if len(text_content) > 100 else ''}")
                except json.JSONDecodeError:
                    print(f"      [ERROR] Could not parse content: {content_json[:50]}...")
        else:
            print("   📝 No events found")
    
    conn.close()

if __name__ == "__main__":
    view_sessions() 
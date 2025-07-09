#!/usr/bin/env python3
"""
Test script for Episodic Memory implementation.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.features.memory import EpisodicMemory, MemoryManager
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_episodic_memory():
    """Test the Episodic Memory implementation."""
    print("🧪 Testing Episodic Memory Implementation")
    print("=" * 50)
    
    try:
        # Initialize Episodic Memory
        episodic = EpisodicMemory("instance/test_episodic.db")
        
        # Test session creation
        session_id = "test_session_123"
        user_id = "test_user_456"
        platform = "telegram"
        
        print("📝 Creating test session...")
        episodic.create_session(session_id, user_id, platform)
        
        # Test message addition
        test_messages = [
            ("user", "Hi Amy, my name is John"),
            ("model", "Hi John! Nice to meet you. How can I help you today?"),
            ("user", "I work as a software engineer"),
            ("model", "That's great! What kind of software do you work on?"),
            ("user", "I love programming in Python")
        ]
        
        print("💬 Adding test messages...")
        for role, content in test_messages:
            episodic.add_message(session_id, role, content, datetime.now())
            print(f"   Added: {role}: {content[:30]}...")
        
        # Test session summary
        print("\n📊 Testing session summary...")
        summary = episodic.summarize_session(session_id)
        print(f"   Summary: {summary}")
        
        # Test context building
        print("\n🔍 Testing context building...")
        context = episodic.get_context(session_id, "What do you know about John?")
        print(f"   Context: {context}")
        
        # Test conversation search
        print("\n🔎 Testing conversation search...")
        results = episodic.search_conversations("Python", user_id)
        print(f"   Search results: {len(results)} conversations found")
        
        # Test session listing
        print("\n📋 Testing session listing...")
        sessions = episodic.get_all_sessions()
        print(f"   Total sessions: {len(sessions)}")
        
        # Test memory manager integration
        print("\n🧠 Testing Memory Manager integration...")
        memory_manager = MemoryManager("instance/test_memory.db")
        
        # Process messages through memory manager
        for role, content in test_messages:
            memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role=role,
                content=content,
                user_id=user_id,
                username="test_user"
            )
        
        # Get context from memory manager
        context = memory_manager.get_context_for_query(session_id, "What do you know about John?")
        print(f"   Memory Manager context length: {len(context)} characters")
        
        # Get memory stats
        stats = memory_manager.get_memory_stats()
        print(f"   EpTM sessions: {stats['episodic']['total_sessions']}")
        print(f"   EpTM messages: {stats['episodic']['total_messages']}")
        
        print("\n✅ All Episodic Memory tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Episodic Memory: {e}")
        print(f"❌ Test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test database files."""
    test_files = [
        "instance/test_episodic.db",
        "instance/test_memory.db"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Cleaned up: {file_path}")

def main():
    """Run the Episodic Memory test."""
    print("🧪 EPISODIC MEMORY TEST SUITE")
    print("=" * 60)
    
    # Run tests
    success = test_episodic_memory()
    
    # Cleanup
    print("\n🧹 Cleaning up test files...")
    cleanup_test_files()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("✅ Episodic Memory is working correctly")
        return 0
    else:
        print("\n❌ Tests failed!")
        return 1

if __name__ == "__main__":
    exit(main()) 
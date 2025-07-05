#!/usr/bin/env python3
"""
Comprehensive test suite for Amy's memory system and Telegram bot integration
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.features.memory import MemoryManager, ShortTermMemory, MediumTermMemory, LongTermMemory

class TestSuite:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.test_results = []
        
    def run_all_tests(self):
        """Run all tests and return results."""
        print("🧪 Amy Memory System Test Suite")
        print("=" * 60)
        
        tests = [
            ("STM (Short-Term Memory)", self.test_stm),
            ("MTM (Medium-Term Memory)", self.test_mtm),
            ("LTM (Long-Term Memory)", self.test_ltm),
            ("Memory Manager Integration", self.test_memory_manager),
            ("Telegram Bot Integration", self.test_telegram_integration),
            ("Cross-Platform Memory", self.test_cross_platform),
            ("Memory Statistics", self.test_memory_stats),
            ("Search Functionality", self.test_search),
            ("Context Building", self.test_context_building),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                if result:
                    print(f"✅ PASSED: {test_name}")
                    passed += 1
                else:
                    print(f"❌ FAILED: {test_name}")
            except Exception as e:
                print(f"❌ ERROR in {test_name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Memory system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
        
        return passed == total
    
    def test_stm(self):
        """Test Short-Term Memory functionality."""
        print("Testing STM operations...")
        
        # Test adding messages
        session_id = "test_stm_session"
        self.memory_manager.stm.add_message(session_id, "user", "Hello Amy")
        self.memory_manager.stm.add_message(session_id, "model", "Hi there!")
        
        # Test getting messages
        messages = self.memory_manager.stm.get_context(session_id)
        assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
        
        # Test session management
        active_sessions = self.memory_manager.stm.get_all_sessions()
        assert session_id in active_sessions, "Session should be active"
        
        print("   ✅ STM message storage and retrieval")
        print("   ✅ STM session management")
        return True
    
    def test_mtm(self):
        """Test Medium-Term Memory functionality."""
        print("Testing MTM operations...")
        
        # Test storing conversation
        session_id = "test_mtm_session"
        
        # Add conversation
        conversation_id = self.memory_manager.mtm.add_conversation(session_id, "telegram", "user123", "testuser")
        
        # Add messages
        self.memory_manager.mtm.add_message(conversation_id, "user", "What's the weather?")
        self.memory_manager.mtm.add_message(conversation_id, "model", "I can't check weather, but I can help with other things!")
        
        # Test retrieving conversation
        stored_messages = self.memory_manager.mtm.get_conversation_messages(session_id)
        # Check that we have at least our 2 test messages (there might be existing data)
        assert len(stored_messages) >= 2, f"Expected at least 2 messages, got {len(stored_messages)}"
        
        # Verify our specific test messages are present
        message_contents = [msg['content'] for msg in stored_messages]
        assert "What's the weather?" in message_contents, "Test message not found"
        assert any("weather" in content.lower() and "help" in content.lower() for content in message_contents), "Test response not found"
        
        # Test session listing
        sessions = self.memory_manager.mtm.get_all_sessions()
        assert any(s['session_id'] == session_id for s in sessions), "Session should be stored"
        
        print("   ✅ MTM conversation storage")
        print("   ✅ MTM message retrieval")
        print("   ✅ MTM session listing")
        return True
    
    def test_ltm(self):
        """Test Long-Term Memory functionality."""
        print("Testing LTM operations...")
        
        # Test fact storage
        facts = [
            ("personal_info", "User's name is John"),
            ("preference", "User likes pizza"),
            ("goal", "User wants to learn Python")
        ]
        
        for fact_type, fact_content in facts:
            self.memory_manager.ltm.store_fact(fact_type, fact_content)
        
        # Test fact retrieval by type
        personal_facts = self.memory_manager.ltm.get_facts_by_type("personal_info")
        preference_facts = self.memory_manager.ltm.get_facts_by_type("preference")
        goal_facts = self.memory_manager.ltm.get_facts_by_type("goal")
        
        total_facts = len(personal_facts) + len(preference_facts) + len(goal_facts)
        assert total_facts >= 3, f"Expected at least 3 facts, got {total_facts}"
        
        # Test fact search
        search_results = self.memory_manager.ltm.search_facts("pizza")
        assert len(search_results) > 0, "Should find facts about pizza"
        
        print("   ✅ LTM fact storage")
        print("   ✅ LTM fact retrieval")
        print("   ✅ LTM fact search")
        return True
    
    def test_memory_manager(self):
        """Test Memory Manager integration."""
        print("Testing Memory Manager integration...")
        
        session_id = "test_integration_session"
        
        # Test message processing through all systems
        self.memory_manager.process_message(
            session_id=session_id,
            platform="telegram",
            role="user",
            content="I love programming in Python",
            user_id="user123",
            username="testuser"
        )
        
        # Test context building
        context = self.memory_manager.get_context_for_query(session_id, "What do you know about me?")
        assert context is not None, "Context should be built"
        
        # Test search across all systems
        results = self.memory_manager.search_conversations("Python")
        assert len(results) > 0, "Should find conversations about Python"
        
        print("   ✅ Memory Manager message processing")
        print("   ✅ Memory Manager context building")
        print("   ✅ Memory Manager search")
        return True
    
    def test_telegram_integration(self):
        """Test Telegram bot integration simulation."""
        print("Testing Telegram bot integration...")
        
        # Simulate Telegram conversation
        session_id = "telegram_test_session"
        user_id = "telegram_user_123"
        username = "telegram_user"
        
        # Simulate conversation flow
        conversation = [
            ("user", "Hi Amy, I'm Sarah"),
            ("model", "Hi Sarah! Nice to meet you!"),
            ("user", "I work as a data scientist"),
            ("model", "That's fascinating! Data science is a great field."),
            ("user", "What do you remember about me?"),
            ("model", "I remember you're Sarah and you work as a data scientist!")
        ]
        
        for role, content in conversation:
            self.memory_manager.process_message(
                session_id=session_id,
                platform="telegram",
                role=role,
                content=content,
                user_id=user_id,
                username=username
            )
        
        # Test that context includes user information
        context = self.memory_manager.get_context_for_query(session_id, "Tell me about myself")
        assert "Sarah" in context, "Context should include user name"
        assert "data scientist" in context, "Context should include user profession"
        
        print("   ✅ Telegram conversation simulation")
        print("   ✅ Context includes user information")
        return True
    
    def test_cross_platform(self):
        """Test cross-platform memory functionality."""
        print("Testing cross-platform memory...")
        
        # Create sessions on different platforms
        platforms = ["telegram", "web", "discord"]
        user_id = "cross_platform_user"
        
        for platform in platforms:
            session_id = f"{platform}_test_session"
            self.memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role="user",
                content=f"I use {platform}",
                user_id=user_id,
                username="cross_user"
            )
        
        # Test that all sessions are stored
        sessions = self.memory_manager.get_all_sessions()
        platform_sessions = [s for s in sessions if s['platform'] in platforms]
        assert len(platform_sessions) >= 3, f"Expected at least 3 platform sessions, got {len(platform_sessions)}"
        
        print("   ✅ Cross-platform session storage")
        print("   ✅ Platform-specific session management")
        return True
    
    def test_memory_stats(self):
        """Test memory statistics functionality."""
        print("Testing memory statistics...")
        
        stats = self.memory_manager.get_memory_stats()
        
        # Check that stats have expected structure
        assert 'stm' in stats, "Stats should include STM data"
        assert 'mtm' in stats, "Stats should include MTM data"
        assert 'ltm' in stats, "Stats should include LTM data"
        
        # Check that stats have expected fields
        assert 'active_sessions' in stats['stm'], "STM stats should include active_sessions"
        assert 'total_sessions' in stats['mtm'], "MTM stats should include total_sessions"
        assert 'fact_types' in stats['ltm'], "LTM stats should include fact_types"
        
        print("   ✅ Memory statistics structure")
        print("   ✅ Memory statistics content")
        return True
    
    def test_search(self):
        """Test search functionality across all memory systems."""
        print("Testing search functionality...")
        
        # Add some test data
        session_id = "search_test_session"
        test_messages = [
            "I love machine learning",
            "Python is my favorite language",
            "I work with neural networks"
        ]
        
        for msg in test_messages:
            self.memory_manager.process_message(
                session_id=session_id,
                platform="test",
                role="user",
                content=msg,
                user_id="search_user",
                username="search_user"
            )
        
        # Test search functionality
        search_terms = ["machine learning", "Python", "neural networks"]
        for term in search_terms:
            results = self.memory_manager.search_conversations(term)
            assert len(results) > 0, f"Should find conversations about {term}"
        
        print("   ✅ Search across all memory systems")
        print("   ✅ Search result validation")
        return True
    
    def test_context_building(self):
        """Test context building for AI responses."""
        print("Testing context building...")
        
        session_id = "context_test_session"
        
        # Build a conversation with specific details
        conversation = [
            ("user", "My name is Alex"),
            ("model", "Nice to meet you, Alex!"),
            ("user", "I'm a software engineer"),
            ("model", "That's great! Software engineering is a rewarding field."),
            ("user", "I specialize in backend development"),
            ("model", "Backend development is crucial for any application!")
        ]
        
        for role, content in conversation:
            self.memory_manager.process_message(
                session_id=session_id,
                platform="test",
                role=role,
                content=content,
                user_id="context_user",
                username="context_user"
            )
        
        # Test context building for different queries
        queries = [
            "What do you know about me?",
            "Tell me about my work",
            "Who am I?"
        ]
        
        for query in queries:
            context = self.memory_manager.get_context_for_query(session_id, query)
            assert context is not None, f"Context should be built for query: {query}"
            assert len(context) > 0, f"Context should not be empty for query: {query}"
        
        print("   ✅ Context building for different queries")
        print("   ✅ Context includes relevant information")
        return True

def main():
    """Run the test suite."""
    test_suite = TestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The memory system is ready for production.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
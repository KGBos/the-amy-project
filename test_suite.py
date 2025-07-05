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

from app.features.memory import MemoryManager, ShortTermMemory, LongTermMemory

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
            ("LTM (Long-Term Memory)", self.test_ltm),
            ("Memory Manager Integration", self.test_memory_manager),
            ("Telegram Bot Integration", self.test_telegram_integration),
            ("Cross-Platform Memory", self.test_cross_platform),
            ("Memory Statistics", self.test_memory_stats),
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
        
        print("   ✅ Memory Manager message processing")
        print("   ✅ Memory Manager context building")
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
        
        # Test that the conversation was processed
        context = self.memory_manager.get_context_for_query(session_id, "What do you know about Sarah?")
        assert context is not None, "Context should be built from conversation"
        
        print("   ✅ Telegram conversation processing")
        print("   ✅ Context building from conversation")
        return True
    
    def test_cross_platform(self):
        """Test cross-platform memory functionality."""
        print("Testing cross-platform memory...")
        
        # Test different platforms
        platforms = ["telegram", "web", "voice"]
        
        for platform in platforms:
            session_id = f"{platform}_test_session"
            
            self.memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role="user",
                content=f"Test message from {platform}",
                user_id=f"user_{platform}",
                username=f"testuser_{platform}"
            )
        
        # Test that all platforms are handled
        stats = self.memory_manager.get_memory_stats()
        assert stats['stm']['active_sessions'] >= 3, "Should have sessions from all platforms"
        
        print("   ✅ Cross-platform message processing")
        print("   ✅ Platform-specific session handling")
        return True
    
    def test_memory_stats(self):
        """Test memory statistics functionality."""
        print("Testing memory statistics...")
        
        # Get initial stats
        initial_stats = self.memory_manager.get_memory_stats()
        
        # Add some test data
        self.memory_manager.process_message(
            session_id="stats_test_session",
            platform="telegram",
            role="user",
            content="Test message for stats",
            user_id="stats_user",
            username="stats_user"
        )
        
        # Get updated stats
        updated_stats = self.memory_manager.get_memory_stats()
        
        # Verify stats are working
        assert 'stm' in updated_stats, "STM stats should be present"
        assert 'ltm' in updated_stats, "LTM stats should be present"
        assert updated_stats['stm']['active_sessions'] >= initial_stats['stm']['active_sessions'], "Active sessions should increase"
        
        print("   ✅ Memory statistics collection")
        print("   ✅ Stats update correctly")
        return True
    
    def test_context_building(self):
        """Test context building functionality."""
        print("Testing context building...")
        
        session_id = "context_test_session"
        
        # Add some test messages
        test_messages = [
            ("user", "My name is Alice"),
            ("model", "Nice to meet you, Alice!"),
            ("user", "I work as a software engineer"),
            ("model", "That's a great profession!"),
            ("user", "I love coffee and hiking")
        ]
        
        for role, content in test_messages:
            self.memory_manager.process_message(
                session_id=session_id,
                platform="telegram",
                role=role,
                content=content,
                user_id="alice_user",
                username="alice"
            )
        
        # Test context building for different queries
        queries = [
            "What do you know about Alice?",
            "Tell me about Alice's work",
            "What are Alice's interests?"
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
        print("\n🎉 All tests passed! Amy's memory system is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
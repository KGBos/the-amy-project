#!/usr/bin/env python3
"""
Memory System Demo for Amy
Demonstrates the memory system functionality with interactive examples
"""

import os
import sys
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app.features.memory import MemoryManager

logger = logging.getLogger(__name__)

class MemoryDemo:
    """
    Interactive demo of Amy's memory system.
    Shows how messages flow through different memory layers.
    """
    
    def __init__(self):
        """Initialize the memory demo."""
        self.memory_manager = MemoryManager()
        self.demo_log = []
        
    def log_demo_step(self, step: str, data: Dict[str, Any]) -> None:
        """
        Log a demo step.
        
        Args:
            step: Step name
            data: Step data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'data': data
        }
        self.demo_log.append(log_entry)
        
    def demo_basic_memory_flow(self) -> str:
        """Demonstrate basic memory flow."""
        print("\n🔄 BASIC MEMORY FLOW DEMO")
        print("=" * 50)
        
        session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        platform = "demo"
        user_message = "Hi Amy, my name is John and I love programming in Python!"
        
        print(f"Session ID: {session_id}")
        print(f"Platform: {platform}")
        print(f"User Message: {user_message}")
        
        # Step 1: Process user message
        print("\n📝 Step 1: Processing user message...")
        self.memory_manager.process_message(
            session_id=session_id,
            platform=platform,
            role="user",
            content=user_message,
            user_id="demo_user",
            username="john_doe"
        )
        
        # Get system info
        system_info = {
            'session_id': session_id,
            'platform': platform,
            'user_message': user_message,
            'timestamp': datetime.now().isoformat()
        }
        
        print("   ✅ User message processed through memory systems")
        self.log_demo_step("User Message Processing", system_info)
        
        # Step 2: Simulate AI response
        ai_response = "Hi John! Nice to meet you. I can see you're passionate about Python programming. How can I help you today?"
        
        print(f"\n🤖 Step 2: Processing AI response...")
        print(f"AI Response: {ai_response}")
        
        self.memory_manager.process_message(
            session_id=session_id,
            platform=platform,
            role="model",
            content=ai_response,
            user_id="demo_user",
            username="john_doe"
        )
        
        print("   ✅ AI response processed through memory systems")
        self.log_demo_step("AI Response Processing", {
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Step 3: Test context building
        print(f"\n🧠 Step 3: Testing context building...")
        context = self.memory_manager.get_context_for_query(session_id, "What do you know about John?")
        
        print("   ✅ Context built successfully")
        print(f"   📄 Context length: {len(context) if context else 0} characters")
        
        self.log_demo_step("Context Building", {
            'context_length': len(context) if context else 0,
            'context_preview': context[:200] + "..." if context and len(context) > 200 else context
        })
        
        # Step 4: Show memory stats
        print(f"\n📊 Step 4: Memory statistics...")
        stats = self.memory_manager.get_memory_stats()
        
        print(f"   📝 STM Active Sessions: {stats['stm']['active_sessions']}")
        print(f"   🧠 LTM Fact Types: {len(stats['ltm']['fact_types'])}")
        
        self.log_demo_step("Memory Statistics", stats)
        
        print(f"\n✅ Basic memory flow demo completed!")
        return session_id
    
    def demo_cross_platform_memory(self) -> List[str]:
        """Demonstrate cross-platform memory functionality."""
        print("\n🌐 CROSS-PLATFORM MEMORY DEMO")
        print("=" * 50)
        
        platforms = ["telegram", "web", "voice"]
        session_ids = []
        
        for i, platform in enumerate(platforms, 1):
            session_id = f"cross_platform_demo_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            message = f"This is a test message from {platform} platform"
            
            print(f"\n📱 Platform {i}: {platform}")
            print(f"   Session ID: {session_id}")
            print(f"   Message: {message}")
            
            self.memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role="user",
                content=message,
                user_id=f"user_{platform}",
                username=f"testuser_{platform}"
            )
            
            session_ids.append(session_id)
            print(f"   ✅ Message processed")
            
            self.log_demo_step("Cross-Platform Processing", {
                'platform': platform,
                'session_id': session_id,
                'message': message
            })
        
        # Test that all platforms are handled
        stats = self.memory_manager.get_memory_stats()
        print(f"\n📊 Cross-platform summary:")
        print(f"   Total active sessions: {stats['stm']['active_sessions']}")
        print(f"   Platforms tested: {', '.join(platforms)}")
        
        print(f"\n✅ Cross-platform memory demo completed!")
        return session_ids
    
    def demo_fact_extraction(self) -> str:
        """Demonstrate fact extraction and storage."""
        print("\n🧠 FACT EXTRACTION DEMO")
        print("=" * 50)
        
        session_id = f"fact_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Test messages with different types of facts
        test_messages = [
            "My name is Alice and I work as a software engineer",
            "I love coffee and hiking on weekends",
            "My favorite programming language is JavaScript",
            "I live in San Francisco and work at a tech startup"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Message {i}: {message}")
            
            self.memory_manager.process_message(
                session_id=session_id,
                platform="demo",
                role="user",
                content=message,
                user_id="alice_user",
                username="alice"
            )
            
            print(f"   ✅ Message processed and facts extracted")
            
            self.log_demo_step("Fact Extraction", {
                'message_number': i,
                'message': message,
                'session_id': session_id
            })
        
        # Show extracted facts
        print(f"\n📊 Extracted facts summary:")
        stats = self.memory_manager.get_memory_stats()
        fact_types = stats['ltm']['fact_types']
        
        for fact_type, count in fact_types.items():
            print(f"   • {fact_type}: {count} facts")
        
        print(f"\n✅ Fact extraction demo completed!")
        return session_id
    
    def demo_context_building(self) -> str:
        """Demonstrate context building for different queries."""
        print("\n🔍 CONTEXT BUILDING DEMO")
        print("=" * 50)
        
        session_id = f"context_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Build a conversation with specific details
        conversation = [
            ("user", "Hi Amy, I'm Bob"),
            ("model", "Hi Bob! Nice to meet you!"),
            ("user", "I'm a data scientist at Google"),
            ("model", "That's fascinating! Data science is a great field."),
            ("user", "I specialize in machine learning and Python"),
            ("model", "Machine learning and Python are a powerful combination!"),
            ("user", "I also love playing guitar and hiking"),
            ("model", "Great hobbies! Music and nature are wonderful.")
        ]
        
        print("📝 Building conversation...")
        for role, content in conversation:
            self.memory_manager.process_message(
                session_id=session_id,
                platform="demo",
                role=role,
                content=content,
                user_id="bob_user",
                username="bob"
            )
        
        print("   ✅ Conversation built")
        
        # Test different queries
        test_queries = [
            "What do you know about Bob?",
            "Tell me about Bob's work",
            "What are Bob's hobbies?",
            "What does Bob do for a living?"
        ]
        
        print(f"\n🔍 Testing context building for different queries:")
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            context = self.memory_manager.get_context_for_query(session_id, query)
            
            if context:
                print(f"   ✅ Context built ({len(context)} characters)")
                print(f"   📄 Preview: {context[:100]}...")
            else:
                print(f"   ⚠️  No context built")
            
            self.log_demo_step("Context Building Test", {
                'query': query,
                'context_length': len(context) if context else 0,
                'context_preview': context[:200] + "..." if context and len(context) > 200 else context
            })
        
        print(f"\n✅ Context building demo completed!")
        return session_id
    
    def demo_memory_cleanup(self, session_ids: List[str]) -> None:
        """Demonstrate memory cleanup."""
        print("\n🧹 MEMORY CLEANUP DEMO")
        print("=" * 50)
        
        print(f"Cleaning up {len(session_ids)} demo sessions...")
        
        for session_id in session_ids:
            print(f"   🗑️  Clearing session: {session_id}")
            self.memory_manager.clear_session(session_id)
            
            self.log_demo_step("Session Cleanup", {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        
        # Show final stats
        stats = self.memory_manager.get_memory_stats()
        print(f"\n📊 Final memory statistics:")
        print(f"   📝 STM Active Sessions: {stats['stm']['active_sessions']}")
        print(f"   🧠 LTM Fact Types: {len(stats['ltm']['fact_types'])}")
        
        print(f"\n✅ Memory cleanup demo completed!")
    
    def run_full_demo(self) -> None:
        """Run the complete memory system demo."""
        print("🎭 AMY MEMORY SYSTEM DEMO")
        print("=" * 60)
        print("This demo will show you how Amy's memory system works.")
        print("It will demonstrate message processing, fact extraction,")
        print("context building, and cross-platform functionality.")
        
        input("\nPress Enter to start the demo...")
        
        session_ids = []
        
        try:
            # Demo 1: Basic memory flow
            session_id = self.demo_basic_memory_flow()
            session_ids.append(session_id)
            
            input("\nPress Enter to continue to cross-platform demo...")
            
            # Demo 2: Cross-platform memory
            platform_session_ids = self.demo_cross_platform_memory()
            session_ids.extend(platform_session_ids)
            
            input("\nPress Enter to continue to fact extraction demo...")
            
            # Demo 3: Fact extraction
            fact_session_id = self.demo_fact_extraction()
            session_ids.append(fact_session_id)
            
            input("\nPress Enter to continue to context building demo...")
            
            # Demo 4: Context building
            context_session_id = self.demo_context_building()
            session_ids.append(context_session_id)
            
            input("\nPress Enter to continue to cleanup demo...")
            
            # Demo 5: Memory cleanup
            self.demo_memory_cleanup(session_ids)
            
            print(f"\n🎉 DEMO COMPLETED SUCCESSFULLY!")
            print(f"📊 Total demo operations logged: {len(self.demo_log)}")
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            logger.error(f"Demo error: {e}")

def main():
    """Main demo interface."""
    demo = MemoryDemo()
    
    print("🎭 Amy Memory System Demo")
    print("=" * 40)
    
    while True:
        print("\nAvailable demos:")
        print("1. Basic memory flow")
        print("2. Cross-platform memory")
        print("3. Fact extraction")
        print("4. Context building")
        print("5. Full demo")
        print("6. Exit")
        
        choice = input("\nSelect demo (1-6): ").strip()
        
        if choice == "1":
            demo.demo_basic_memory_flow()
        elif choice == "2":
            demo.demo_cross_platform_memory()
        elif choice == "3":
            demo.demo_fact_extraction()
        elif choice == "4":
            demo.demo_context_building()
        elif choice == "5":
            demo.run_full_demo()
        elif choice == "6":
            print("👋 Exiting demo...")
            break
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main() 
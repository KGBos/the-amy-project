#!/usr/bin/env python3
"""
Memory System Demo for Amy
Comprehensive demonstration of how the memory system works
"""

import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MemoryDemo:
    """
    Comprehensive demonstration of Amy's memory system.
    Shows step-by-step how memory operations work.
    """
    
    def __init__(self):
        self.demo_log = []
        
    def log_demo_step(self, step: str, details: Dict[str, Any]) -> None:
        """Log a demo step."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'details': details
        }
        self.demo_log.append(log_entry)
        print(f"📝 {step}: {details}")
        
    def run_complete_demo(self):
        """Run a complete demonstration of the memory system."""
        print("🧠 AMY MEMORY SYSTEM DEMO")
        print("=" * 60)
        print("This demo will show you exactly how the memory system works!")
        print("=" * 60)
        print()
        
        # Step 1: Initialize memory systems
        self.demo_step_1_initialization()
        
        # Step 2: Process a user message
        self.demo_step_2_process_user_message()
        
        # Step 3: Show context building
        self.demo_step_3_context_building()
        
        # Step 4: Process AI response
        self.demo_step_4_process_ai_response()
        
        # Step 5: Show memory inspection
        self.demo_step_5_memory_inspection()
        
        # Step 6: Show cross-platform memory
        self.demo_step_6_cross_platform()
        
        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE!")
        print("=" * 60)
        
    def demo_step_1_initialization(self):
        """Step 1: Initialize memory systems."""
        print("🔧 STEP 1: MEMORY SYSTEM INITIALIZATION")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            self.log_demo_step("Memory Manager Initialized", {
                'stm_max_messages': memory_manager.stm.max_messages,
                'mtm_db_path': memory_manager.mtm.db_path,
                'ltm_vector_db_path': memory_manager.ltm.vector_db_path
            })
            
            print("✅ Memory systems initialized successfully!")
            print("   • STM: In-memory buffer (20 messages max)")
            print("   • MTM: SQLite database (permanent storage)")
            print("   • LTM: Vector database (semantic storage)")
            print()
            
        except Exception as e:
            print(f"❌ Error initializing memory systems: {e}")
            print()
    
    def demo_step_2_process_user_message(self):
        """Step 2: Process a user message through all memory systems."""
        print("📥 STEP 2: PROCESSING USER MESSAGE")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            # Simulate a user message
            session_id = "demo_session_001"
            platform = "telegram"
            user_message = "Hi Amy! My name is John and I love programming in Python."
            
            print(f"User Message: '{user_message}'")
            print(f"Session ID: {session_id}")
            print(f"Platform: {platform}")
            print()
            
            # Process through STM
            print("📝 Processing through STM...")
            memory_manager.stm.add_message(session_id, "user", user_message)
            stm_context = memory_manager.stm.get_context(session_id)
            self.log_demo_step("STM Processing", {
                'session_id': session_id,
                'message_count': len(stm_context),
                'latest_message': stm_context[-1] if stm_context else None
            })
            print(f"   ✅ STM: {len(stm_context)} messages in session")
            
            # Process through MTM
            print("💾 Processing through MTM...")
            conversation_id = memory_manager.mtm.add_conversation(session_id, platform, "user123", "john_doe")
            memory_manager.mtm.add_message(conversation_id, "user", user_message)
            self.log_demo_step("MTM Processing", {
                'conversation_id': conversation_id,
                'session_id': session_id,
                'platform': platform
            })
            print(f"   ✅ MTM: Message stored in conversation {conversation_id}")
            
            # Process through LTM
            print("🧠 Processing through LTM...")
            facts = memory_manager.ltm.extract_facts_from_conversation([{'role': 'user', 'content': user_message}])
            stored_facts = []
            
            for fact in facts:
                if ': ' in fact:
                    fact_type, fact_content = fact.split(': ', 1)
                    memory_manager.ltm.store_fact(fact_type, fact_content)
                    stored_facts.append({'type': fact_type, 'content': fact_content})
                else:
                    memory_manager.ltm.store_fact('general', fact)
                    stored_facts.append({'type': 'general', 'content': fact})
            
            self.log_demo_step("LTM Processing", {
                'extracted_facts': facts,
                'stored_facts': stored_facts
            })
            print(f"   ✅ LTM: {len(stored_facts)} facts extracted and stored")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing user message: {e}")
            print()
    
    def demo_step_3_context_building(self):
        """Step 3: Show how context is built for AI responses."""
        print("🔍 STEP 3: CONTEXT BUILDING")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            session_id = "demo_session_001"
            query = "What do you know about me?"
            
            print(f"Building context for query: '{query}'")
            print(f"Session ID: {session_id}")
            print()
            
            # Get STM context
            print("📝 Retrieving STM context...")
            stm_context = memory_manager.stm.get_context(session_id)
            stm_messages = stm_context[-5:] if stm_context else []  # Last 5 messages
            self.log_demo_step("STM Context Retrieved", {
                'message_count': len(stm_messages),
                'messages': stm_messages
            })
            print(f"   ✅ STM: {len(stm_messages)} recent messages")
            
            # Get LTM context
            print("🧠 Retrieving LTM context...")
            ltm_context = memory_manager.ltm.build_context_from_query(query)
            self.log_demo_step("LTM Context Retrieved", {
                'context': ltm_context,
                'context_length': len(ltm_context) if ltm_context else 0
            })
            print(f"   ✅ LTM: {len(ltm_context) if ltm_context else 0} characters of relevant facts")
            
            # Build final context
            print("🔗 Combining context...")
            final_context = memory_manager.get_context_for_query(session_id, query)
            self.log_demo_step("Final Context Built", {
                'context': final_context,
                'context_length': len(final_context) if final_context else 0
            })
            print(f"   ✅ Final context: {len(final_context) if final_context else 0} characters")
            
            if final_context:
                print("\n📋 Final Context Preview:")
                print("-" * 30)
                print(final_context[:200] + "..." if len(final_context) > 200 else final_context)
                print("-" * 30)
            
            print()
            
        except Exception as e:
            print(f"❌ Error building context: {e}")
            print()
    
    def demo_step_4_process_ai_response(self):
        """Step 4: Process an AI response through memory systems."""
        print("🤖 STEP 4: PROCESSING AI RESPONSE")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            session_id = "demo_session_001"
            ai_response = "Hi John! Nice to meet you! I remember you love programming in Python. That's a great skill to have!"
            
            print(f"AI Response: '{ai_response}'")
            print(f"Session ID: {session_id}")
            print()
            
            # Process through STM
            print("📝 Processing AI response through STM...")
            memory_manager.stm.add_message(session_id, "model", ai_response)
            stm_context = memory_manager.stm.get_context(session_id)
            self.log_demo_step("AI Response STM Processing", {
                'session_id': session_id,
                'message_count': len(stm_context),
                'latest_message': stm_context[-1] if stm_context else None
            })
            print(f"   ✅ STM: {len(stm_context)} messages in session")
            
            # Process through MTM
            print("💾 Processing AI response through MTM...")
            # Get existing conversation
            import sqlite3
            with sqlite3.connect(memory_manager.mtm.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM conversations WHERE session_id = ?", (session_id,))
                conversation_id = cursor.fetchone()[0]
            
            memory_manager.mtm.add_message(conversation_id, "model", ai_response)
            self.log_demo_step("AI Response MTM Processing", {
                'conversation_id': conversation_id,
                'session_id': session_id
            })
            print(f"   ✅ MTM: AI response stored in conversation {conversation_id}")
            
            # Note: No LTM processing for model messages
            print("🧠 No LTM processing for AI responses (model messages)")
            print("   ℹ️  Only user messages trigger fact extraction")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing AI response: {e}")
            print()
    
    def demo_step_5_memory_inspection(self):
        """Step 5: Inspect the current state of all memory systems."""
        print("🔍 STEP 5: MEMORY SYSTEM INSPECTION")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            session_id = "demo_session_001"
            
            # Inspect STM
            print("📝 Inspecting STM...")
            stm_context = memory_manager.stm.get_context(session_id)
            self.log_demo_step("STM Inspection", {
                'session_id': session_id,
                'message_count': len(stm_context),
                'messages': stm_context
            })
            print(f"   ✅ STM: {len(stm_context)} messages in session")
            for i, msg in enumerate(stm_context[-3:], 1):  # Show last 3
                print(f"      {i}. {msg['role']}: {msg['content'][:50]}...")
            
            # Inspect MTM
            print("\n💾 Inspecting MTM...")
            mtm_messages = memory_manager.mtm.get_conversation_messages(session_id)
            self.log_demo_step("MTM Inspection", {
                'session_id': session_id,
                'message_count': len(mtm_messages),
                'messages': mtm_messages
            })
            print(f"   ✅ MTM: {len(mtm_messages)} messages in database")
            for i, msg in enumerate(mtm_messages[-3:], 1):  # Show last 3
                print(f"      {i}. {msg['role']}: {msg['content'][:50]}...")
            
            # Inspect LTM
            print("\n🧠 Inspecting LTM...")
            ltm_stats = memory_manager.get_memory_stats()['ltm']
            fact_types = ltm_stats.get('fact_types', {})
            self.log_demo_step("LTM Inspection", {
                'fact_types': fact_types,
                'total_facts': sum(fact_types.values())
            })
            print(f"   ✅ LTM: {sum(fact_types.values())} total facts")
            for fact_type, count in fact_types.items():
                print(f"      • {fact_type}: {count} facts")
            
            print()
            
        except Exception as e:
            print(f"❌ Error inspecting memory systems: {e}")
            print()
    
    def demo_step_6_cross_platform(self):
        """Step 6: Demonstrate cross-platform memory capabilities."""
        print("🌐 STEP 6: CROSS-PLATFORM MEMORY")
        print("-" * 40)
        
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            # Simulate messages from different platforms
            platforms = [
                ("telegram", "telegram_user_123", "john_telegram"),
                ("web", "web_user_456", "john_web"),
                ("discord", "discord_user_789", "john_discord")
            ]
            
            messages = [
                "I use Telegram for quick chats",
                "I prefer the web interface for longer conversations",
                "Discord is great for community discussions"
            ]
            
            print("Simulating messages across different platforms...")
            print()
            
            for i, ((platform, user_id, username), message) in enumerate(zip(platforms, messages), 1):
                session_id = f"{platform}_demo_session_{i:03d}"
                
                print(f"📱 Platform {i}: {platform.upper()}")
                print(f"   Session: {session_id}")
                print(f"   Message: '{message}'")
                
                # Process message
                memory_manager.process_message(
                    session_id=session_id,
                    platform=platform,
                    role="user",
                    content=message,
                    user_id=user_id,
                    username=username
                )
                
                self.log_demo_step(f"Cross-Platform Processing {i}", {
                    'platform': platform,
                    'session_id': session_id,
                    'message': message
                })
                
                print(f"   ✅ Processed through all memory systems")
                print()
            
            # Show cross-platform statistics
            print("📊 Cross-Platform Memory Statistics:")
            stats = memory_manager.get_memory_stats()
            mtm_stats = stats['mtm']
            
            if 'sessions' in mtm_stats:
                platform_counts = {}
                for session in mtm_stats['sessions']:
                    platform = session['platform']
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
                
                for platform, count in platform_counts.items():
                    print(f"   • {platform}: {count} sessions")
            
            print()
            
        except Exception as e:
            print(f"❌ Error demonstrating cross-platform memory: {e}")
            print()
    
    def export_demo_log(self, filename: Optional[str] = None) -> str:
        """Export the demo log to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_demo_log_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.demo_log, f, indent=2)
        
        return filename

def main():
    """Run the memory system demo."""
    demo = MemoryDemo()
    
    print("🎬 Amy Memory System Demo")
    print("This demo will show you exactly how the memory system works!")
    print()
    
    # Run the complete demo
    demo.run_complete_demo()
    
    # Export the demo log
    filename = demo.export_demo_log()
    print(f"Demo log exported to: {filename}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Memory Flow Visualizer for Amy
Visualizes how messages flow through the memory system
"""

import os
import sys
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

class MemoryFlowVisualizer:
    """
    Visualizes the flow of messages through Amy's memory system.
    Shows step-by-step how data moves through different memory layers.
    """
    
    def __init__(self):
        """Initialize the memory flow visualizer."""
        self.memory_manager = MemoryManager()
        
    def visualize_message_flow(self, session_id: str, platform: str, 
                              user_message: str, ai_response: str) -> str:
        """
        Visualize the complete flow of a message through the memory system.
        
        Args:
            session_id: Session identifier
            platform: Platform name
            user_message: User's message
            ai_response: AI's response
            
        Returns:
            Visualization diagram as string
        """
        diagram = []
        diagram.append("🔄 MEMORY FLOW VISUALIZATION")
        diagram.append("=" * 60)
        diagram.append(f"Session: {session_id}")
        diagram.append(f"Platform: {platform}")
        diagram.append("")
        
        # Step 1: User Message Input
        diagram.append("📥 1. USER MESSAGE INPUT")
        diagram.append(f"   Message: {user_message}")
        diagram.append("")
        
        # Step 2: STM Processing
        diagram.append("📝 2. SHORT-TERM MEMORY (STM)")
        diagram.append("   └── Message stored in immediate context")
        diagram.append("   └── Available for current conversation")
        diagram.append("")
        
        # Step 3: LTM Processing (for user messages)
        diagram.append("🧠 3. LONG-TERM MEMORY (LTM)")
        diagram.append("   └── Facts extracted from user message")
        diagram.append("   └── Stored for future context building")
        diagram.append("")
        
        # Step 4: AI Response Processing
        diagram.append("🤖 4. AI RESPONSE PROCESSING")
        diagram.append(f"   AI Response: {ai_response}")
        diagram.append("   └── Response stored in STM")
        diagram.append("   └── No LTM processing (model message)")
        diagram.append("")
        
        # Step 5: Context Building
        diagram.append("🔍 5. CONTEXT BUILDING")
        diagram.append("   └── STM: Recent conversation context")
        diagram.append("   └── LTM: Relevant facts and knowledge")
        diagram.append("   └── Combined for AI response generation")
        diagram.append("")
        
        return "\n".join(diagram)
    
    def visualize_memory_architecture(self) -> str:
        """
        Visualize the overall memory system architecture.
        
        Returns:
            Architecture diagram as string
        """
        diagram = []
        diagram.append("🧠 MEMORY SYSTEM ARCHITECTURE")
        diagram.append("=" * 50)
        diagram.append("")
        
        # Current Architecture
        diagram.append("📊 CURRENT IMPLEMENTATION:")
        diagram.append("")
        diagram.append("   📝 STM (Short-Term Memory)")
        diagram.append("   ├── In-memory buffer")
        diagram.append("   ├── 20 messages per session")
        diagram.append("   └── Immediate conversation context")
        diagram.append("")
        
        diagram.append("   🧠 LTM (Long-Term Memory)")
        diagram.append("   ├── Vector database storage")
        diagram.append("   ├── Fact extraction and storage")
        diagram.append("   └── Semantic knowledge base")
        diagram.append("")
        
        # Future Architecture
        diagram.append("🚀 FUTURE ARCHITECTURE (Coming Soon):")
        diagram.append("")
        diagram.append("   👁️  Sensory Memory")
        diagram.append("   ├── Audio/visual input processing")
        diagram.append("   ├── Transcription and preprocessing")
        diagram.append("   └── Real-time streaming support")
        diagram.append("")
        
        diagram.append("   📝 STM (Short-Term Memory)")
        diagram.append("   ├── Immediate conversation context")
        diagram.append("   └── Enhanced with sensory data")
        diagram.append("")
        
        diagram.append("   🧩 EpTM (Episodic Memory)")
        diagram.append("   ├── Summarized conversation chunks")
        diagram.append("   ├── Embeddings and semantic storage")
        diagram.append("   └── Mem0 integration")
        diagram.append("")
        
        diagram.append("   🧠 LTM (Long-Term Memory)")
        diagram.append("   ├── Mem0 vector/graph database")
        diagram.append("   ├── Advanced fact extraction")
        diagram.append("   └── Semantic knowledge graph")
        diagram.append("")
        
        return "\n".join(diagram)
    
    def visualize_memory_stats(self) -> str:
        """
        Visualize current memory statistics.
        
        Returns:
            Statistics visualization as string
        """
        try:
            stats = self.memory_manager.get_memory_stats()
            
            visualization = []
            visualization.append("📊 MEMORY SYSTEM STATISTICS")
            visualization.append("=" * 50)
            visualization.append("")
            
            # STM Stats
            stm_stats = stats.get('stm', {})
            active_sessions = stm_stats.get('active_sessions', 0)
            visualization.append("📝 SHORT-TERM MEMORY (STM)")
            visualization.append(f"   Active Sessions: {active_sessions}")
            visualization.append("")
            
            # LTM Stats
            ltm_stats = stats.get('ltm', {})
            fact_types = ltm_stats.get('fact_types', {})
            total_facts = sum(fact_types.values())
            visualization.append("🧠 LONG-TERM MEMORY (LTM)")
            visualization.append(f"   Total Facts: {total_facts}")
            visualization.append("   Facts by Type:")
            
            for fact_type, count in fact_types.items():
                visualization.append(f"   • {fact_type}: {count}")
            
            visualization.append("")
            
            # EpTM Stats (coming soon)
            episodic_stats = stats.get('episodic', {})
            total_sessions = episodic_stats.get('total_sessions', 0)
            visualization.append("🧩 EPISODIC MEMORY (EpTM)")
            visualization.append(f"   Total Sessions: {total_sessions}")
            visualization.append("   Status: Coming Soon")
            visualization.append("")
            
            return "\n".join(visualization)
            
        except Exception as e:
            logger.error(f"Error visualizing memory stats: {e}")
            return f"❌ Error getting memory statistics: {e}"
    
    def visualize_context_building(self, session_id: str, query: str) -> str:
        """
        Visualize the context building process.
        
        Args:
            session_id: Session identifier
            query: The query to build context for
            
        Returns:
            Context building visualization as string
        """
        try:
            visualization = []
            visualization.append("🔍 CONTEXT BUILDING VISUALIZATION")
            visualization.append("=" * 50)
            visualization.append(f"Session: {session_id}")
            visualization.append(f"Query: {query}")
            visualization.append("")
            
            # Get STM context
            stm_context = self.memory_manager.stm.get_context(session_id)
            stm_messages = len(stm_context) if stm_context else 0
            
            visualization.append("📝 STEP 1: STM CONTEXT")
            visualization.append(f"   Recent Messages: {stm_messages}")
            if stm_context:
                visualization.append("   Last 3 messages:")
                for i, msg in enumerate(stm_context[-3:], 1):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')[:50]
                    visualization.append(f"   {i}. {role}: {content}...")
            else:
                visualization.append("   No recent messages")
            visualization.append("")
            
            # Get LTM context
            ltm_context = self.memory_manager.ltm.build_context_from_query(query)
            ltm_length = len(ltm_context) if ltm_context else 0
            
            visualization.append("🧠 STEP 2: LTM CONTEXT")
            visualization.append(f"   Relevant Facts: {ltm_length} characters")
            if ltm_context:
                visualization.append("   Context preview:")
                preview = ltm_context[:200] + "..." if len(ltm_context) > 200 else ltm_context
                visualization.append(f"   {preview}")
            else:
                visualization.append("   No relevant facts found")
            visualization.append("")
            
            # Final context
            final_context = self.memory_manager.get_context_for_query(session_id, query)
            final_length = len(final_context) if final_context else 0
            
            visualization.append("🔗 STEP 3: FINAL CONTEXT")
            visualization.append(f"   Combined Length: {final_length} characters")
            if final_context:
                visualization.append("   Final context preview:")
                preview = final_context[:300] + "..." if len(final_context) > 300 else final_context
                visualization.append(f"   {preview}")
            else:
                visualization.append("   No context built")
            visualization.append("")
            
            return "\n".join(visualization)
            
        except Exception as e:
            logger.error(f"Error visualizing context building: {e}")
            return f"❌ Error visualizing context building: {e}"
    
    def create_flow_diagram(self, session_id: str, platform: str, 
                           user_message: str, ai_response: str) -> str:
        """
        Create a detailed flow diagram for a conversation.
        
        Args:
            session_id: Session identifier
            platform: Platform name
            user_message: User's message
            ai_response: AI's response
            
        Returns:
            Detailed flow diagram as string
        """
        diagram = []
        diagram.append("🔄 DETAILED MEMORY FLOW DIAGRAM")
        diagram.append("=" * 60)
        diagram.append("")
        
        # User Message Flow
        diagram.append("📥 USER MESSAGE FLOW")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 1. User sends message          │")
        diagram.append("   └─────────────────┬───────────────┘")
        diagram.append("                     │")
        diagram.append("                     ▼")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 2. STM Processing              │")
        diagram.append("   │ • Store in immediate context   │")
        diagram.append("   │ • Available for conversation   │")
        diagram.append("   └─────────────────┬───────────────┘")
        diagram.append("                     │")
        diagram.append("                     ▼")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 3. LTM Processing              │")
        diagram.append("   │ • Extract facts from message   │")
        diagram.append("   │ • Store in vector database     │")
        diagram.append("   └─────────────────────────────────┘")
        diagram.append("")
        
        # AI Response Flow
        diagram.append("🤖 AI RESPONSE FLOW")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 4. Context Building            │")
        diagram.append("   │ • Combine STM + LTM context    │")
        diagram.append("   │ • Generate relevant context    │")
        diagram.append("   └─────────────────┬───────────────┘")
        diagram.append("                     │")
        diagram.append("                     ▼")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 5. AI Response Generation      │")
        diagram.append("   │ • Generate response with context│")
        diagram.append("   └─────────────────┬───────────────┘")
        diagram.append("                     │")
        diagram.append("                     ▼")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ 6. Response Storage            │")
        diagram.append("   │ • Store in STM only            │")
        diagram.append("   │ • No LTM processing            │")
        diagram.append("   └─────────────────────────────────┘")
        diagram.append("")
        
        # Memory System Overview
        diagram.append("🧠 MEMORY SYSTEM OVERVIEW")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ STM (Short-Term Memory)        │")
        diagram.append("   │ • Immediate conversation context│")
        diagram.append("   │ • 20 messages per session      │")
        diagram.append("   └─────────────────────────────────┘")
        diagram.append("")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ LTM (Long-Term Memory)         │")
        diagram.append("   │ • Fact extraction and storage  │")
        diagram.append("   │ • Semantic knowledge base      │")
        diagram.append("   └─────────────────────────────────┘")
        diagram.append("")
        diagram.append("   ┌─────────────────────────────────┐")
        diagram.append("   │ EpTM (Episodic Memory)         │")
        diagram.append("   │ • Coming Soon                  │")
        diagram.append("   │ • Mem0 integration planned     │")
        diagram.append("   └─────────────────────────────────┘")
        
        return "\n".join(diagram)

def main():
    """Main visualization interface."""
    visualizer = MemoryFlowVisualizer()
    
    print("🎨 Amy Memory Flow Visualizer")
    print("=" * 40)
    
    while True:
        print("\nAvailable visualizations:")
        print("1. Message flow visualization")
        print("2. Memory architecture")
        print("3. Memory statistics")
        print("4. Context building visualization")
        print("5. Detailed flow diagram")
        print("6. Exit")
        
        choice = input("\nSelect visualization (1-6): ").strip()
        
        if choice == "1":
            session_id = input("Session ID: ").strip()
            platform = input("Platform: ").strip()
            user_message = input("User message: ").strip()
            ai_response = input("AI response: ").strip()
            
            diagram = visualizer.visualize_message_flow(session_id, platform, user_message, ai_response)
            print(f"\n{diagram}")
            
        elif choice == "2":
            diagram = visualizer.visualize_memory_architecture()
            print(f"\n{diagram}")
            
        elif choice == "3":
            diagram = visualizer.visualize_memory_stats()
            print(f"\n{diagram}")
            
        elif choice == "4":
            session_id = input("Session ID: ").strip()
            query = input("Query: ").strip()
            
            diagram = visualizer.visualize_context_building(session_id, query)
            print(f"\n{diagram}")
            
        elif choice == "5":
            session_id = input("Session ID: ").strip()
            platform = input("Platform: ").strip()
            user_message = input("User message: ").strip()
            ai_response = input("AI response: ").strip()
            
            diagram = visualizer.create_flow_diagram(session_id, platform, user_message, ai_response)
            print(f"\n{diagram}")
            
        elif choice == "6":
            print("👋 Exiting visualizer...")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main() 
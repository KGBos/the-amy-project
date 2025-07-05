#!/usr/bin/env python3
"""
Memory Flow Visualizer for Amy
Creates visual diagrams showing how memory operations flow through the system
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)

class MemoryFlowVisualizer:
    """
    Creates visual representations of memory system flow and operations.
    """
    
    def __init__(self):
        self.flow_log = []
        
    def log_flow_step(self, step_name: str, details: Dict[str, Any]) -> None:
        """Log a flow step for visualization."""
        step = {
            'timestamp': datetime.now().isoformat(),
            'step': step_name,
            'details': details
        }
        self.flow_log.append(step)
        
    def create_flow_diagram(self, session_id: str, user_message: str) -> str:
        """Create a text-based flow diagram showing memory operations."""
        diagram = []
        diagram.append("🔄 MEMORY FLOW DIAGRAM")
        diagram.append("=" * 60)
        diagram.append(f"Session: {session_id}")
        diagram.append(f"User Message: {user_message}")
        diagram.append("=" * 60)
        diagram.append("")
        
        # Step 1: Message Reception
        diagram.append("📥 1. MESSAGE RECEPTION")
        diagram.append("   └── User sends message")
        diagram.append("   └── Message logged with timestamp")
        diagram.append("   └── Session ID identified")
        diagram.append("")
        
        # Step 2: STM Processing
        diagram.append("📝 2. SHORT-TERM MEMORY (STM)")
        diagram.append("   └── Message added to in-memory buffer")
        diagram.append("   └── Recent conversation context updated")
        diagram.append("   └── Session tracking maintained")
        diagram.append("   └── Max 20 messages per session")
        diagram.append("")
        
        # Step 3: MTM Processing
        diagram.append("💾 3. MEDIUM-TERM MEMORY (MTM)")
        diagram.append("   └── Message stored in SQLite database")
        diagram.append("   └── Conversation session created/updated")
        diagram.append("   └── Permanent storage across platforms")
        diagram.append("   └── Cross-platform conversation linking")
        diagram.append("")
        
        # Step 4: LTM Processing
        diagram.append("🧠 4. LONG-TERM MEMORY (LTM)")
        diagram.append("   └── Fact extraction from user message")
        diagram.append("   └── Personal info, preferences, goals identified")
        diagram.append("   └── Facts stored in vector database")
        diagram.append("   └── Semantic search capabilities")
        diagram.append("")
        
        # Step 5: Context Building
        diagram.append("🔍 5. CONTEXT BUILDING")
        diagram.append("   └── STM context retrieved (recent messages)")
        diagram.append("   └── LTM context retrieved (relevant facts)")
        diagram.append("   └── Context combined for AI response")
        diagram.append("   └── Relevance filtering applied")
        diagram.append("")
        
        # Step 6: AI Response
        diagram.append("🤖 6. AI RESPONSE GENERATION")
        diagram.append("   └── Context provided to AI model")
        diagram.append("   └── Response generated with memory awareness")
        diagram.append("   └── Response logged back to memory systems")
        diagram.append("")
        
        # Step 7: Response Storage
        diagram.append("💾 7. RESPONSE STORAGE")
        diagram.append("   └── AI response added to STM")
        diagram.append("   └── AI response stored in MTM")
        diagram.append("   └── No LTM extraction (model message)")
        diagram.append("")
        
        diagram.append("=" * 60)
        diagram.append("✅ MEMORY FLOW COMPLETE")
        
        return "\n".join(diagram)
    
    def create_memory_architecture_diagram(self) -> str:
        """Create a diagram showing the memory system architecture."""
        diagram = []
        diagram.append("🏗️  MEMORY SYSTEM ARCHITECTURE")
        diagram.append("=" * 60)
        diagram.append("")
        
        diagram.append("📥 INPUT LAYER")
        diagram.append("   └── User Messages (Telegram, Web, etc.)")
        diagram.append("   └── Session Management")
        diagram.append("   └── Platform Detection")
        diagram.append("")
        
        diagram.append("🧠 MEMORY LAYERS")
        diagram.append("")
        diagram.append("   📝 STM (Short-Term Memory)")
        diagram.append("   ├── In-memory conversation buffer")
        diagram.append("   ├── Last 20 messages per session")
        diagram.append("   ├── Instant access, no database calls")
        diagram.append("   └── Session-scoped only")
        diagram.append("")
        
        diagram.append("   💾 MTM (Medium-Term Memory)")
        diagram.append("   ├── SQLite database storage")
        diagram.append("   ├── All conversations across platforms")
        diagram.append("   ├── Permanent storage")
        diagram.append("   └── Cross-platform conversation linking")
        diagram.append("")
        
        diagram.append("   🧠 LTM (Long-Term Memory)")
        diagram.append("   ├── Vector database (JSON files)")
        diagram.append("   ├── Fact extraction and storage")
        diagram.append("   ├── Semantic search capabilities")
        diagram.append("   └── Personal knowledge building")
        diagram.append("")
        
        diagram.append("🔍 CONTEXT LAYER")
        diagram.append("   └── Context Building Engine")
        diagram.append("   └── Relevance Filtering")
        diagram.append("   └── Context Length Management")
        diagram.append("   └── Cross-Memory Integration")
        diagram.append("")
        
        diagram.append("🤖 OUTPUT LAYER")
        diagram.append("   └── AI Response Generation")
        diagram.append("   └── Memory-Aware Responses")
        diagram.append("   └── Context-Enhanced Interactions")
        diagram.append("")
        
        diagram.append("=" * 60)
        
        return "\n".join(diagram)
    
    def create_data_flow_diagram(self) -> str:
        """Create a data flow diagram showing how data moves through the system."""
        diagram = []
        diagram.append("🔄 DATA FLOW DIAGRAM")
        diagram.append("=" * 60)
        diagram.append("")
        
        diagram.append("1. USER INPUT")
        diagram.append("   User Message → Session ID → Platform Detection")
        diagram.append("")
        
        diagram.append("2. STM PROCESSING")
        diagram.append("   Message → In-Memory Buffer → Recent Context")
        diagram.append("")
        
        diagram.append("3. MTM PROCESSING")
        diagram.append("   Message → SQLite Database → Permanent Storage")
        diagram.append("")
        
        diagram.append("4. LTM PROCESSING")
        diagram.append("   User Message → Fact Extraction → Vector Storage")
        diagram.append("")
        
        diagram.append("5. CONTEXT BUILDING")
        diagram.append("   STM Context + LTM Facts → Combined Context")
        diagram.append("")
        
        diagram.append("6. AI RESPONSE")
        diagram.append("   Context + User Message → AI Model → Response")
        diagram.append("")
        
        diagram.append("7. RESPONSE STORAGE")
        diagram.append("   AI Response → STM + MTM (No LTM)")
        diagram.append("")
        
        diagram.append("=" * 60)
        
        return "\n".join(diagram)
    
    def create_memory_stats_visualization(self) -> str:
        """Create a visual representation of memory statistics."""
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            stats = memory_manager.get_memory_stats()
            
            visualization = []
            visualization.append("📊 MEMORY STATISTICS VISUALIZATION")
            visualization.append("=" * 60)
            visualization.append("")
            
            # STM Stats
            stm_stats = stats.get('stm', {})
            active_sessions = stm_stats.get('active_sessions', 0)
            visualization.append("📝 SHORT-TERM MEMORY (STM)")
            visualization.append(f"   Active Sessions: {active_sessions}")
            if active_sessions > 0:
                visualization.append("   ████████████████████")
            else:
                visualization.append("   ░░░░░░░░░░░░░░░░░░░░")
            visualization.append("")
            
            # MTM Stats
            mtm_stats = stats.get('mtm', {})
            total_sessions = mtm_stats.get('total_sessions', 0)
            visualization.append("💾 MEDIUM-TERM MEMORY (MTM)")
            visualization.append(f"   Total Sessions: {total_sessions}")
            if total_sessions > 0:
                bar_length = min(20, total_sessions)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                visualization.append(f"   {bar}")
            else:
                visualization.append("   ░░░░░░░░░░░░░░░░░░░░")
            visualization.append("")
            
            # LTM Stats
            ltm_stats = stats.get('ltm', {})
            fact_types = ltm_stats.get('fact_types', {})
            total_facts = sum(fact_types.values())
            visualization.append("🧠 LONG-TERM MEMORY (LTM)")
            visualization.append(f"   Total Facts: {total_facts}")
            
            if fact_types:
                for fact_type, count in fact_types.items():
                    bar_length = min(15, count)
                    bar = "█" * bar_length + "░" * (15 - bar_length)
                    visualization.append(f"   {fact_type}: {count} {bar}")
            else:
                visualization.append("   No facts stored")
            
            visualization.append("")
            visualization.append("=" * 60)
            
            return "\n".join(visualization)
            
        except Exception as e:
            return f"Error creating memory stats visualization: {e}"
    
    def export_flow_log(self, filename: Optional[str] = None) -> str:
        """Export the flow log to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_flow_log_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.flow_log, f, indent=2)
        
        return filename

def main():
    """Run the memory flow visualizer."""
    visualizer = MemoryFlowVisualizer()
    
    print("🎨 Amy Memory Flow Visualizer")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Show memory flow diagram")
        print("2. Show memory architecture diagram")
        print("3. Show data flow diagram")
        print("4. Show memory statistics visualization")
        print("5. Export flow log")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            session_id = input("Enter session ID: ").strip() or "example_session"
            user_message = input("Enter user message: ").strip() or "Hello Amy!"
            diagram = visualizer.create_flow_diagram(session_id, user_message)
            print("\n" + diagram)
            
        elif choice == '2':
            diagram = visualizer.create_memory_architecture_diagram()
            print("\n" + diagram)
            
        elif choice == '3':
            diagram = visualizer.create_data_flow_diagram()
            print("\n" + diagram)
            
        elif choice == '4':
            visualization = visualizer.create_memory_stats_visualization()
            print("\n" + visualization)
            
        elif choice == '5':
            filename = visualizer.export_flow_log()
            print(f"Flow log exported to: {filename}")
            
        elif choice == '6':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
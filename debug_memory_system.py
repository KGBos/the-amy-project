#!/usr/bin/env python3
"""
Memory System Debug Tools
Main script to run all memory debugging and visualization tools
"""

import os
import sys
from datetime import datetime

def print_header():
    """Print the header for the debug tools."""
    print("🧠 AMY MEMORY SYSTEM DEBUG TOOLS")
    print("=" * 60)
    print("Choose a tool to understand how the memory system works:")
    print()

def main():
    """Main menu for memory debugging tools."""
    while True:
        print_header()
        print("1. 🎬 Run Complete Memory Demo")
        print("   Shows step-by-step how memory operations work")
        print()
        print("2. 🔍 Live Memory Monitor")
        print("   Real-time monitoring of memory operations")
        print()
        print("3. 🎨 Memory Flow Visualizer")
        print("   Visual diagrams of memory system flow")
        print()
        print("4. 🔧 Memory Debugger")
        print("   Interactive debugging and inspection tools")
        print()
        print("5. 📊 Quick Memory Stats")
        print("   Show current memory system statistics")
        print()
        print("6. 🧪 Run Test Suite")
        print("   Run comprehensive memory system tests")
        print()
        print("7. 📁 View Memory Files")
        print("   Show what's stored in memory files")
        print()
        print("8. 🚪 Exit")
        print()
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            print("\n🎬 Starting Memory Demo...")
            print("=" * 40)
            os.system("python3 memory_demo.py")
            
        elif choice == '2':
            print("\n🔍 Starting Live Memory Monitor...")
            print("=" * 40)
            print("This will show real-time memory operations.")
            print("Start a conversation with Amy in another terminal to see it in action!")
            print("Press Ctrl+C to stop monitoring.")
            print()
            os.system("python3 live_memory_monitor.py")
            
        elif choice == '3':
            print("\n🎨 Starting Memory Flow Visualizer...")
            print("=" * 40)
            os.system("python3 memory_flow_visualizer.py")
            
        elif choice == '4':
            print("\n🔧 Starting Memory Debugger...")
            print("=" * 40)
            os.system("python3 memory_debugger.py")
            
        elif choice == '5':
            print("\n📊 Quick Memory Statistics")
            print("=" * 40)
            try:
                from app.features.memory import MemoryManager
                memory_manager = MemoryManager()
                stats = memory_manager.get_memory_stats()
                
                print("Current Memory System Status:")
                print()
                
                # STM Stats
                stm_stats = stats.get('stm', {})
                active_sessions = stm_stats.get('active_sessions', 0)
                print(f"📝 STM Active Sessions: {active_sessions}")
                
                # MTM Stats
                mtm_stats = stats.get('mtm', {})
                total_sessions = mtm_stats.get('total_sessions', 0)
                print(f"💾 MTM Total Sessions: {total_sessions}")
                
                # LTM Stats
                ltm_stats = stats.get('ltm', {})
                fact_types = ltm_stats.get('fact_types', {})
                total_facts = sum(fact_types.values())
                print(f"🧠 LTM Total Facts: {total_facts}")
                
                if fact_types:
                    print("\nFacts by Type:")
                    for fact_type, count in fact_types.items():
                        print(f"   • {fact_type}: {count}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error getting memory stats: {e}")
                print()
                
        elif choice == '6':
            print("\n🧪 Running Test Suite...")
            print("=" * 40)
            os.system("python3 test_suite.py")
            
        elif choice == '7':
            print("\n📁 Memory Files Inspection")
            print("=" * 40)
            
            # Check MTM database
            if os.path.exists("instance/amy_memory.db"):
                db_size = os.path.getsize("instance/amy_memory.db")
                print(f"💾 MTM Database: instance/amy_memory.db ({db_size} bytes)")
            else:
                print("💾 MTM Database: Not found")
            
            # Check LTM vector database
            if os.path.exists("instance/vector_db"):
                fact_files = [f for f in os.listdir("instance/vector_db") if f.endswith('.json')]
                print(f"🧠 LTM Vector DB: instance/vector_db/ ({len(fact_files)} fact files)")
                
                if fact_files:
                    print("\nFact Files:")
                    for i, filename in enumerate(fact_files[:10], 1):  # Show first 10
                        print(f"   {i}. {filename}")
                    if len(fact_files) > 10:
                        print(f"   ... and {len(fact_files) - 10} more")
            else:
                print("🧠 LTM Vector DB: Not found")
            
            # Check logs
            if os.path.exists("instance/amy_telegram_bot.log"):
                log_size = os.path.getsize("instance/amy_telegram_bot.log")
                print(f"📝 Log File: instance/amy_telegram_bot.log ({log_size} bytes)")
            else:
                print("📝 Log File: Not found")
            
            print()
            
        elif choice == '8':
            print("\n👋 Goodbye! Thanks for exploring Amy's memory system!")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 8.")
            print()
        
        input("Press Enter to continue...")
        print("\n" * 2)

if __name__ == "__main__":
    main() 
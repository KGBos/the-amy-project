#!/usr/bin/env python3
"""
Memory Debugger for Amy
Real-time visualization and debugging of the memory system
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MemoryDebugger:
    """
    Comprehensive debugging and visualization tool for Amy's memory system.
    Shows real-time memory operations, context building, and memory flow.
    """
    
    def __init__(self, db_path: str = "instance/amy_memory.db", vector_db_path: str = "instance/vector_db"):
        self.db_path = db_path
        self.vector_db_path = vector_db_path
        self.operation_log = []
        
    def log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Log a memory operation with timestamp."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details
        }
        self.operation_log.append(log_entry)
        logger.debug(f"MEMORY DEBUG: {operation} - {details}")
        
    def inspect_stm(self, session_id: str) -> Dict[str, Any]:
        """Inspect Short-Term Memory for a session."""
        try:
            from app.features.memory.stm import ShortTermMemory
            stm = ShortTermMemory()
            
            # Get the conversations from STM
            conversations = stm.conversations
            session_data = conversations.get(session_id, [])
            
            result = {
                'session_id': session_id,
                'message_count': len(session_data),
                'messages': session_data,
                'max_messages': stm.max_messages,
                'is_active': session_id in conversations
            }
            
            self.log_operation("STM_INSPECT", result)
            return result
            
        except Exception as e:
            logger.error(f"Error inspecting STM: {e}")
            return {'error': str(e)}
    
    def inspect_mtm(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Inspect Medium-Term Memory (database)."""
        try:
            if not os.path.exists(self.db_path):
                return {'error': 'Database not found', 'path': self.db_path}
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if session_id:
                    # Get specific session
                    cursor.execute("""
                        SELECT c.session_id, c.platform, c.user_id, c.username, 
                               c.created_at, c.updated_at,
                               COUNT(m.id) as message_count
                        FROM conversations c
                        LEFT JOIN messages m ON c.id = m.conversation_id
                        WHERE c.session_id = ?
                        GROUP BY c.id
                    """, (session_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        result = {
                            'session_id': row[0],
                            'platform': row[1],
                            'user_id': row[2],
                            'username': row[3],
                            'created_at': row[4],
                            'updated_at': row[5],
                            'message_count': row[6]
                        }
                        
                        # Get messages for this session
                        cursor.execute("""
                            SELECT m.role, m.content, m.timestamp
                            FROM messages m
                            JOIN conversations c ON m.conversation_id = c.id
                            WHERE c.session_id = ?
                            ORDER BY m.timestamp ASC
                        """, (session_id,))
                        
                        messages = [
                            {'role': row[0], 'content': row[1], 'timestamp': row[2]}
                            for row in cursor.fetchall()
                        ]
                        result['messages'] = messages
                        
                    else:
                        result = {'error': f'Session {session_id} not found'}
                else:
                    # Get all sessions
                    cursor.execute("""
                        SELECT session_id, platform, user_id, username, 
                               created_at, updated_at,
                               COUNT(m.id) as message_count
                        FROM conversations c
                        LEFT JOIN messages m ON c.id = m.conversation_id
                        GROUP BY c.id
                        ORDER BY updated_at DESC
                    """)
                    
                    sessions = []
                    for row in cursor.fetchall():
                        sessions.append({
                            'session_id': row[0],
                            'platform': row[1],
                            'user_id': row[2],
                            'username': row[3],
                            'created_at': row[4],
                            'updated_at': row[5],
                            'message_count': row[6]
                        })
                    
                    result = {'sessions': sessions, 'total_sessions': len(sessions)}
                
                self.log_operation("MTM_INSPECT", result)
                return result
                
        except Exception as e:
            logger.error(f"Error inspecting MTM: {e}")
            return {'error': str(e)}
    
    def inspect_ltm(self) -> Dict[str, Any]:
        """Inspect Long-Term Memory (vector database)."""
        try:
            if not os.path.exists(self.vector_db_path):
                return {'error': 'Vector database not found', 'path': self.vector_db_path}
            
            facts = {}
            fact_types = {}
            
            for filename in os.listdir(self.vector_db_path):
                if filename.endswith('.json'):
                    fact_file = os.path.join(self.vector_db_path, filename)
                    try:
                        with open(fact_file, 'r') as f:
                            fact_data = json.load(f)
                            
                        fact_type = fact_data.get('type', 'unknown')
                        content = fact_data.get('content', '')
                        
                        if fact_type not in facts:
                            facts[fact_type] = []
                        facts[fact_type].append(content)
                        
                        fact_types[fact_type] = fact_types.get(fact_type, 0) + 1
                        
                    except Exception as e:
                        logger.warning(f"Error reading fact file {filename}: {e}")
            
            result = {
                'fact_types': fact_types,
                'facts': facts,
                'total_facts': sum(fact_types.values())
            }
            
            self.log_operation("LTM_INSPECT", result)
            return result
            
        except Exception as e:
            logger.error(f"Error inspecting LTM: {e}")
            return {'error': str(e)}
    
    def trace_context_building(self, session_id: str, query: str) -> Dict[str, Any]:
        """Trace the context building process step by step."""
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            trace = {
                'session_id': session_id,
                'query': query,
                'steps': []
            }
            
            # Step 1: Get STM context
            stm_context = memory_manager.stm.get_context(session_id)
            trace['steps'].append({
                'step': 'STM_Context',
                'message_count': len(stm_context),
                'messages': stm_context[-5:] if stm_context else [],  # Last 5 messages
                'context_length': sum(len(msg.get('content', '')) for msg in stm_context)
            })
            
            # Step 2: Get LTM context
            ltm_context = memory_manager.ltm.build_context_from_query(query)
            trace['steps'].append({
                'step': 'LTM_Context',
                'context': ltm_context,
                'context_length': len(ltm_context) if ltm_context else 0
            })
            
            # Step 3: Build final context
            final_context = memory_manager.get_context_for_query(session_id, query)
            trace['steps'].append({
                'step': 'Final_Context',
                'context': final_context,
                'context_length': len(final_context) if final_context else 0
            })
            
            self.log_operation("CONTEXT_TRACE", trace)
            return trace
            
        except Exception as e:
            logger.error(f"Error tracing context building: {e}")
            return {'error': str(e)}
    
    def simulate_memory_flow(self, session_id: str, platform: str, role: str, content: str) -> Dict[str, Any]:
        """Simulate the complete memory flow for a message."""
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            flow = {
                'session_id': session_id,
                'platform': platform,
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }
            
            # Step 1: Process through STM
            memory_manager.stm.add_message(session_id, role, content)
            flow['steps'].append({
                'step': 'STM_Add',
                'status': 'success',
                'session_active': session_id in memory_manager.stm.conversations
            })
            
            # Step 2: Process through MTM
            conversation_id = memory_manager._get_or_create_conversation(session_id, platform)
            memory_manager.mtm.add_message(conversation_id, role, content)
            flow['steps'].append({
                'step': 'MTM_Add',
                'status': 'success',
                'conversation_id': conversation_id
            })
            
            # Step 3: Process through LTM (if user message)
            if role == 'user':
                facts = memory_manager.ltm.extract_facts_from_conversation([{'role': role, 'content': content}])
                stored_facts = []
                
                for fact in facts:
                    try:
                        if ': ' in fact:
                            fact_type, fact_content = fact.split(': ', 1)
                            memory_manager.ltm.store_fact(fact_type, fact_content)
                            stored_facts.append({'type': fact_type, 'content': fact_content})
                        else:
                            memory_manager.ltm.store_fact('general', fact)
                            stored_facts.append({'type': 'general', 'content': fact})
                    except Exception as e:
                        logger.warning(f"Failed to process fact '{fact}': {e}")
                
                flow['steps'].append({
                    'step': 'LTM_Extract',
                    'status': 'success',
                    'extracted_facts': facts,
                    'stored_facts': stored_facts
                })
            else:
                flow['steps'].append({
                    'step': 'LTM_Extract',
                    'status': 'skipped',
                    'reason': 'Model message - no fact extraction'
                })
            
            self.log_operation("MEMORY_FLOW", flow)
            return flow
            
        except Exception as e:
            logger.error(f"Error simulating memory flow: {e}")
            return {'error': str(e)}
    
    def get_memory_stats_detailed(self) -> Dict[str, Any]:
        """Get detailed statistics about all memory systems."""
        try:
            from app.features.memory import MemoryManager
            memory_manager = MemoryManager()
            
            # STM Stats
            stm_sessions = memory_manager.stm.get_all_sessions()
            stm_stats = {
                'active_sessions': len(stm_sessions),
                'sessions': stm_sessions,
                'total_messages': sum(len(memory_manager.stm.conversations.get(session, [])) for session in stm_sessions)
            }
            
            # MTM Stats
            mtm_sessions = memory_manager.mtm.get_all_sessions()
            mtm_stats = {
                'total_sessions': len(mtm_sessions),
                'sessions': mtm_sessions,
                'platforms': list(set(session['platform'] for session in mtm_sessions))
            }
            
            # LTM Stats
            ltm_stats = self.inspect_ltm()
            
            stats = {
                'stm': stm_stats,
                'mtm': mtm_stats,
                'ltm': ltm_stats,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_operation("MEMORY_STATS", stats)
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}
    
    def print_memory_visualization(self, session_id: Optional[str] = None) -> None:
        """Print a visual representation of the memory system."""
        print("\n" + "="*80)
        print("🧠 AMY MEMORY SYSTEM VISUALIZATION")
        print("="*80)
        
        # Get detailed stats
        stats = self.get_memory_stats_detailed()
        
        if 'error' in stats:
            print(f"❌ Error getting stats: {stats['error']}")
            return
        
        # STM Visualization
        print("\n📝 SHORT-TERM MEMORY (STM)")
        print("-" * 40)
        stm = stats['stm']
        print(f"Active Sessions: {stm['active_sessions']}")
        print(f"Total Messages: {stm['total_messages']}")
        
        if stm['sessions']:
            print("\nActive Sessions:")
            for session in stm['sessions']:
                print(f"  • {session}")
        
        # MTM Visualization
        print("\n💾 MEDIUM-TERM MEMORY (MTM)")
        print("-" * 40)
        mtm = stats['mtm']
        print(f"Total Sessions: {mtm['total_sessions']}")
        print(f"Platforms: {', '.join(mtm['platforms'])}")
        
        if mtm['sessions']:
            print("\nRecent Sessions:")
            for session in mtm['sessions'][:5]:  # Show last 5
                print(f"  • {session['session_id']} ({session['platform']}) - {session['message_count']} messages")
        
        # LTM Visualization
        print("\n🧠 LONG-TERM MEMORY (LTM)")
        print("-" * 40)
        ltm = stats['ltm']
        if 'fact_types' in ltm:
            print(f"Total Facts: {ltm['total_facts']}")
            print("\nFacts by Type:")
            for fact_type, count in ltm['fact_types'].items():
                print(f"  • {fact_type}: {count} facts")
                
                # Show sample facts
                if fact_type in ltm['facts']:
                    for fact in ltm['facts'][fact_type][:3]:  # Show first 3
                        print(f"    - {fact[:50]}...")
        
        print("\n" + "="*80)
    
    def export_operation_log(self, filename: Optional[str] = None) -> str:
        """Export the operation log to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_debug_log_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.operation_log, f, indent=2)
        
        return filename

def main():
    """Interactive memory debugging interface."""
    debugger = MemoryDebugger()
    
    print("🧠 Amy Memory Debugger")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. View memory visualization")
        print("2. Inspect STM for session")
        print("3. Inspect MTM for session")
        print("4. Inspect LTM")
        print("5. Trace context building")
        print("6. Simulate memory flow")
        print("7. Export operation log")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            session_id = input("Enter session ID (or press Enter for all): ").strip() or None
            if session_id:
                debugger.print_memory_visualization(session_id)
            else:
                debugger.print_memory_visualization()
            
        elif choice == '2':
            session_id = input("Enter session ID: ").strip()
            if session_id:
                result = debugger.inspect_stm(session_id)
                print(f"\nSTM Inspection Result:")
                print(json.dumps(result, indent=2))
            
        elif choice == '3':
            session_id = input("Enter session ID (or press Enter for all): ").strip() or None
            result = debugger.inspect_mtm(session_id)
            print(f"\nMTM Inspection Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == '4':
            result = debugger.inspect_ltm()
            print(f"\nLTM Inspection Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == '5':
            session_id = input("Enter session ID: ").strip()
            query = input("Enter query: ").strip()
            if session_id and query:
                result = debugger.trace_context_building(session_id, query)
                print(f"\nContext Building Trace:")
                print(json.dumps(result, indent=2))
            
        elif choice == '6':
            session_id = input("Enter session ID: ").strip()
            platform = input("Enter platform: ").strip()
            role = input("Enter role (user/model): ").strip()
            content = input("Enter content: ").strip()
            
            if all([session_id, platform, role, content]):
                result = debugger.simulate_memory_flow(session_id, platform, role, content)
                print(f"\nMemory Flow Simulation:")
                print(json.dumps(result, indent=2))
            
        elif choice == '7':
            filename = debugger.export_operation_log()
            print(f"Operation log exported to: {filename}")
            
        elif choice == '8':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
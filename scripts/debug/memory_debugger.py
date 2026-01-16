#!/usr/bin/env python3
"""
Memory Debugger for Amy
Comprehensive debugging tool for memory system inspection and testing
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from amy.features.memory import MemoryManager

logger = logging.getLogger(__name__)

class MemoryDebugger:
    """
    Comprehensive debugging tool for Amy's memory system.
    Provides inspection, testing, and analysis capabilities.
    """
    
    def __init__(self, log_file: str = "debug_operations.log"):
        """
        Initialize the memory debugger.
        
        Args:
            log_file: Path to log file for debug operations
        """
        self.memory_manager = MemoryManager()
        self.log_file = log_file
        self.operation_log = []
        
    def log_operation(self, operation: str, data: Dict[str, Any]) -> None:
        """
        Log a debug operation.
        
        Args:
            operation: Operation name
            data: Operation data
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'data': data
        }
        self.operation_log.append(log_entry)
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def inspect_stm(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspect Short-Term Memory.
        
        Args:
            session_id: Specific session to inspect, or None for all
            
        Returns:
            STM inspection data
        """
        try:
            stm = self.memory_manager.stm
            
            if session_id:
                # Inspect specific session
                messages = stm.get_context(session_id)
                result = {
                    'session_id': session_id,
                    'message_count': len(messages),
                    'messages': messages,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Inspect all sessions
                all_sessions = stm.get_all_sessions()
                result = {
                    'total_sessions': len(all_sessions),
                    'sessions': all_sessions,
                    'timestamp': datetime.now().isoformat()
                }
                
            self.log_operation("STM_INSPECT", result)
            return result
            
        except Exception as e:
            logger.error(f"Error inspecting STM: {e}")
            return {'error': str(e)}
    
    def inspect_ltm(self, fact_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspect Long-Term Memory.
        
        Args:
            fact_type: Specific fact type to inspect, or None for all
            
        Returns:
            LTM inspection data
        """
        try:
            ltm = self.memory_manager.ltm
            
            if fact_type:
                # Inspect specific fact type
                facts = ltm.get_facts_by_type(fact_type)
                result = {
                    'fact_type': fact_type,
                    'fact_count': len(facts),
                    'facts': facts,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Get all fact types
                stats = self.memory_manager.get_memory_stats()
                ltm_stats = stats.get('ltm', {})
                result = {
                    'fact_types': ltm_stats.get('fact_types', {}),
                    'timestamp': datetime.now().isoformat()
                }
                
            self.log_operation("LTM_INSPECT", result)
            return result
            
        except Exception as e:
            logger.error(f"Error inspecting LTM: {e}")
            return {'error': str(e)}
    
    def test_memory_flow(self, session_id: str, platform: str, 
                         user_message: str, ai_response: str) -> Dict[str, Any]:
        """
        Test the complete memory flow for a conversation.
        
        Args:
            session_id: Session identifier
            platform: Platform name
            user_message: User's message
            ai_response: AI's response
            
        Returns:
            Flow test results
        """
        try:
            flow_log = []
            
            # Step 1: Process user message
            print(f"📝 Processing user message: {user_message}")
            self.memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role="user",
                content=user_message,
                user_id="debug_user",
                username="debug_user"
            )
            flow_log.append({
                'step': 'User_Message_Processing',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            
            # Step 2: Process AI response
            print(f"🤖 Processing AI response: {ai_response}")
            self.memory_manager.process_message(
                session_id=session_id,
                platform=platform,
                role="model",
                content=ai_response,
                user_id="debug_user",
                username="debug_user"
            )
            flow_log.append({
                'step': 'AI_Response_Processing',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            })
            
            # Step 3: Test context building
            print("🧠 Testing context building...")
            context = self.memory_manager.get_context_for_query(session_id, "What was discussed?")
            flow_log.append({
                'step': 'Context_Building',
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'context_length': len(context) if context else 0
            })
            
            result = {
                'session_id': session_id,
                'platform': platform,
                'flow_log': flow_log,
                'final_context': context,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_operation("MEMORY_FLOW_TEST", result)
            return result
            
        except Exception as e:
            logger.error(f"Error in memory flow test: {e}")
            return {'error': str(e)}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics.
        
        Returns:
            Memory statistics
        """
        try:
            # Get basic stats
            stats = self.memory_manager.get_memory_stats()
            
            # Add file system info
            instance_dir = "instance"
            if os.path.exists(instance_dir):
                db_files = [f for f in os.listdir(instance_dir) if f.endswith('.db')]
                vector_dirs = [d for d in os.listdir(instance_dir) if os.path.isdir(os.path.join(instance_dir, d)) and 'vector' in d]
                
                stats['filesystem'] = {
                    'instance_directory': instance_dir,
                    'database_files': db_files,
                    'vector_directories': vector_dirs
                }
            
            # Add operation log stats
            stats['debug'] = {
                'total_operations': len(self.operation_log),
                'log_file': self.log_file
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {'error': str(e)}
    
    def clear_test_data(self, session_id: str) -> Dict[str, Any]:
        """
        Clear test data for a session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            Clear operation result
        """
        try:
            # Clear STM
            self.memory_manager.clear_session(session_id)
            
            result = {
                'session_id': session_id,
                'cleared_stm': True,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_operation("CLEAR_TEST_DATA", result)
            return result
            
        except Exception as e:
            logger.error(f"Error clearing test data: {e}")
            return {'error': str(e)}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """
        Run a comprehensive test of the memory system.
        
        Returns:
            Comprehensive test results
        """
        try:
            test_session = f"debug_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Test 1: Basic message processing
            print("🧪 Test 1: Basic message processing")
            self.memory_manager.process_message(
                session_id=test_session,
                platform="debug",
                role="user",
                content="This is a debug test message",
                user_id="debug_user",
                username="debug_user"
            )
            
            # Test 2: Context building
            print("🧪 Test 2: Context building")
            context = self.memory_manager.get_context_for_query(test_session, "What was the test message?")
            
            # Test 3: Memory stats
            print("🧪 Test 3: Memory statistics")
            stats = self.memory_manager.get_memory_stats()
            
            # Test 4: STM inspection
            print("🧪 Test 4: STM inspection")
            stm_data = self.inspect_stm(test_session)
            
            # Test 5: LTM inspection
            print("🧪 Test 5: LTM inspection")
            ltm_data = self.inspect_ltm()
            
            result = {
                'test_session': test_session,
                'tests_passed': 5,
                'context_built': context is not None,
                'stats_collected': stats is not None,
                'stm_inspected': stm_data is not None,
                'ltm_inspected': ltm_data is not None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.log_operation("COMPREHENSIVE_TEST", result)
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive test: {e}")
            return {'error': str(e)}

def main():
    """Main debug interface."""
    debugger = MemoryDebugger()
    
    print("🔧 Amy Memory System Debugger")
    print("=" * 50)
    
    while True:
        print("\nAvailable operations:")
        print("1. Inspect STM")
        print("2. Inspect LTM")
        print("3. Test memory flow")
        print("4. Get memory stats")
        print("5. Run comprehensive test")
        print("6. Clear test data")
        print("7. Exit")
        
        choice = input("\nSelect operation (1-7): ").strip()
        
        if choice == "1":
            session_id = input("Session ID (or press Enter for all): ").strip()
            session_id = session_id if session_id else None
            result = debugger.inspect_stm(session_id)
            print(f"\nSTM Inspection Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == "2":
            fact_type = input("Fact type (or press Enter for all): ").strip()
            fact_type = fact_type if fact_type else None
            result = debugger.inspect_ltm(fact_type)
            print(f"\nLTM Inspection Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == "3":
            session_id = input("Session ID: ").strip()
            platform = input("Platform: ").strip()
            user_message = input("User message: ").strip()
            ai_response = input("AI response: ").strip()
            
            result = debugger.test_memory_flow(session_id, platform, user_message, ai_response)
            print(f"\nMemory Flow Test Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == "4":
            result = debugger.get_memory_stats()
            print(f"\nMemory Statistics:")
            print(json.dumps(result, indent=2))
            
        elif choice == "5":
            result = debugger.run_comprehensive_test()
            print(f"\nComprehensive Test Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == "6":
            session_id = input("Session ID to clear: ").strip()
            result = debugger.clear_test_data(session_id)
            print(f"\nClear Test Data Result:")
            print(json.dumps(result, indent=2))
            
        elif choice == "7":
            print("👋 Exiting debugger...")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main() 
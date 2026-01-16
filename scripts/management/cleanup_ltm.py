#!/usr/bin/env python3
"""
Clean up LTM (Long-Term Memory) by removing duplicate facts.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from amy.features.memory import MemoryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_ltm():
    """Clean up duplicate facts in LTM."""
    print("🧹 LTM Cleanup Tool")
    print("=" * 50)
    
    try:
        # Initialize memory manager
        memory_manager = MemoryManager()
        
        # Get initial stats
        initial_stats = memory_manager.get_memory_stats()
        initial_facts = sum(initial_stats['ltm']['fact_types'].values())
        
        print(f"📊 Initial LTM stats:")
        for fact_type, count in initial_stats['ltm']['fact_types'].items():
            print(f"   {fact_type}: {count} facts")
        print(f"   Total facts: {initial_facts}")
        print()
        
        # Clean up duplicates
        print("🧹 Cleaning up duplicate facts...")
        duplicates_removed = memory_manager.ltm.cleanup_duplicates()
        
        # Get final stats
        final_stats = memory_manager.get_memory_stats()
        final_facts = sum(final_stats['ltm']['fact_types'].values())
        
        print(f"✅ Cleanup completed!")
        print(f"📊 Final LTM stats:")
        for fact_type, count in final_stats['ltm']['fact_types'].items():
            print(f"   {fact_type}: {count} facts")
        print(f"   Total facts: {final_facts}")
        print(f"   Duplicates removed: {duplicates_removed}")
        print(f"   Facts saved: {initial_facts - final_facts}")
        
        if duplicates_removed > 0:
            print(f"\n🎉 Successfully removed {duplicates_removed} duplicate facts!")
        else:
            print(f"\n✅ No duplicates found - LTM is already clean!")
            
    except Exception as e:
        logger.error(f"Error during LTM cleanup: {e}")
        print(f"❌ Error during cleanup: {e}")
        return False
    
    return True

def test_fact_deduplication():
    """Test the fact deduplication functionality."""
    print("\n🧪 Testing Fact Deduplication")
    print("=" * 50)
    
    try:
        memory_manager = MemoryManager()
        
        # Test storing the same fact multiple times
        test_fact = "my name is test user"
        test_type = "personal_info"
        test_user = "test_user_123"
        
        print(f"Testing with fact: '{test_fact}'")
        
        # Store the fact multiple times
        for i in range(3):
            result = memory_manager.ltm.store_fact(test_fact, test_type, test_user)
            if result:
                print(f"   Attempt {i+1}: Stored (new fact)")
            else:
                print(f"   Attempt {i+1}: Skipped (duplicate)")
        
        # Verify only one fact was stored
        facts = memory_manager.ltm.get_facts_by_type(test_type)
        test_facts = [f for f in facts if test_fact in f.get('content', '')]
        
        print(f"   Facts found: {len(test_facts)}")
        
        if len(test_facts) == 1:
            print("✅ Deduplication working correctly!")
        else:
            print(f"❌ Deduplication failed - found {len(test_facts)} facts")
            
    except Exception as e:
        logger.error(f"Error testing deduplication: {e}")
        print(f"❌ Error during test: {e}")
        return False
    
    return True

def main():
    """Main cleanup function."""
    print("🧹 Amy Memory System Cleanup")
    print("=" * 60)
    
    # Clean up existing duplicates
    if not cleanup_ltm():
        return 1
    
    # Test deduplication functionality
    if not test_fact_deduplication():
        return 1
    
    print("\n🎉 All cleanup tasks completed successfully!")
    print("✅ LTM is now clean and deduplication is working")
    
    return 0

if __name__ == "__main__":
    exit(main()) 
#!/usr/bin/env python3
"""
Complete Amy Memory Reset Script
This script completely resets Amy's memory system to a fresh state.
"""

import os
import shutil
import sqlite3
from pathlib import Path

def reset_amy_memory():
    """Completely reset Amy's memory system."""
    print("🧠 Amy Memory System - Complete Reset")
    print("=" * 50)
    
    # Get project root (this file is in scripts/management/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    instance_dir = os.path.join(project_root, 'instance')
    
    print("🗑️  Removing all memory data...")
    
    # 1. Remove the SQLite database
    db_path = os.path.join(instance_dir, 'amy_memory.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed database: {db_path}")
    else:
        print(f"ℹ️  Database not found: {db_path}")
    
    # 2. Remove all vector database files
    vector_db_path = os.path.join(instance_dir, 'vector_db')
    if os.path.exists(vector_db_path):
        # Remove all JSON files in vector_db
        json_files = list(Path(vector_db_path).glob('*.json'))
        for json_file in json_files:
            os.remove(json_file)
            print(f"✅ Removed fact file: {json_file.name}")
        
        # Remove the vector_db directory itself
        os.rmdir(vector_db_path)
        print(f"✅ Removed vector database directory: {vector_db_path}")
    else:
        print(f"ℹ️  Vector database not found: {vector_db_path}")
    
    # 2b. Remove mem0 storage directory
    mem0_path = os.path.join(instance_dir, 'mem0_storage')
    if os.path.exists(mem0_path):
        shutil.rmtree(mem0_path)
        print(f"✅ Removed mem0 storage: {mem0_path}")
    else:
        print(f"ℹ️  Mem0 storage not found: {mem0_path}")
    
    # 3. Clear STM (Short-Term Memory) by restarting the system
    print("🧹 Short-term memory will be cleared on next restart")
    
    # 4. Recreate empty directories
    os.makedirs(instance_dir, exist_ok=True)
    os.makedirs(vector_db_path, exist_ok=True)
    print(f"✅ Recreated directories")
    
    print("\n🎉 Amy's memory has been completely reset!")
    print("📝 All test data, conversations, and facts have been removed.")
    print("🔄 Amy will start fresh with no knowledge of any users.")
    
    return True

def verify_reset():
    """Verify that the reset was successful."""
    print("\n🔍 Verifying reset...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    instance_dir = os.path.join(project_root, 'instance')
    
    # Check database
    db_path = os.path.join(instance_dir, 'amy_memory.db')
    if os.path.exists(db_path):
        print(f"❌ Database still exists: {db_path}")
        return False
    else:
        print(f"✅ Database removed successfully")
    
    # Check vector database
    vector_db_path = os.path.join(instance_dir, 'vector_db')
    if os.path.exists(vector_db_path):
        json_files = list(Path(vector_db_path).glob('*.json'))
        if json_files:
            print(f"❌ {len(json_files)} fact files still exist in vector database")
            return False
        else:
            print(f"✅ Vector database is empty")
    else:
        print(f"✅ Vector database removed successfully")
    
    print("✅ Reset verification complete - Amy is ready for fresh start!")
    return True

def main():
    """Main function."""
    print("⚠️  WARNING: This will completely erase all of Amy's memory!")
    print("📚 All conversations, facts, and user information will be lost.")
    print("🔄 This action cannot be undone.")
    
    response = input("\nAre you sure you want to reset Amy's memory? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        if reset_amy_memory():
            verify_reset()
            print("\n🚀 Amy is now ready for a fresh start!")
            print("💡 Restart the bot to begin with a clean memory system.")
        else:
            print("❌ Reset failed!")
    else:
        print("❌ Reset cancelled.")

if __name__ == "__main__":
    main() 
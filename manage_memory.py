#!/usr/bin/env python3
"""
Memory management utility for The Amy Project
Allows backing up, resetting, and restoring conversation memory.
"""

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def get_db_path():
    """Get the database path"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(project_root, 'instance', 'amy_memory.db')

def get_backup_dir():
    """Get the backup directory path"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(project_root, 'instance', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_memory():
    """Create a backup of the current memory database"""
    db_path = get_db_path()
    backup_dir = get_backup_dir()
    
    if not os.path.exists(db_path):
        print("❌ No database found to backup")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"amy_memory_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Memory backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def reset_memory():
    """Reset the memory database (with backup option)"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("❌ No database found to reset")
        return False
    
    # Ask for confirmation
    print("⚠️  This will delete all conversation history!")
    response = input("Do you want to backup first? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        if not backup_memory():
            print("❌ Backup failed, aborting reset")
            return False
    
    # Ask for final confirmation
    response = input("Are you sure you want to reset memory? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Reset cancelled")
        return False
    
    try:
        # Remove the database
        os.remove(db_path)
        print("🗑️  Database deleted")
        
        # Reinitialize the database
        from google.adk.sessions import DatabaseSessionService
        db_url = f"sqlite:///{db_path}"
        session_service = DatabaseSessionService(db_url=db_url)
        session_service.init_db()
        
        print("✅ Memory reset complete - fresh database created")
        return True
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def list_backups():
    """List all available backups"""
    backup_dir = get_backup_dir()
    
    if not os.path.exists(backup_dir):
        print("❌ No backup directory found")
        return
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith("amy_memory_backup_") and file.endswith(".db"):
            file_path = os.path.join(backup_dir, file)
            stat = os.stat(file_path)
            backups.append((file, stat.st_mtime, stat.st_size))
    
    if not backups:
        print("📭 No backups found")
        return
    
    print("📦 Available backups:")
    for filename, mtime, size in sorted(backups, key=lambda x: x[1], reverse=True):
        date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        size_mb = size / (1024 * 1024)
        print(f"  • {filename}")
        print(f"    Date: {date}")
        print(f"    Size: {size_mb:.2f} MB")

def restore_backup(backup_name=None):
    """Restore from a backup"""
    backup_dir = get_backup_dir()
    db_path = get_db_path()
    
    if not backup_name:
        # List available backups
        backups = [f for f in os.listdir(backup_dir) 
                  if f.startswith("amy_memory_backup_") and f.endswith(".db")]
        
        if not backups:
            print("❌ No backups found")
            return False
        
        print("📦 Available backups:")
        for i, backup in enumerate(backups, 1):
            print(f"  {i}. {backup}")
        
        try:
            choice = int(input("Select backup to restore (number): ")) - 1
            if 0 <= choice < len(backups):
                backup_name = backups[choice]
            else:
                print("❌ Invalid selection")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False
    
    backup_path = os.path.join(backup_dir, backup_name)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup not found: {backup_name}")
        return False
    
    # Ask for confirmation
    print(f"⚠️  This will replace current memory with: {backup_name}")
    response = input("Are you sure? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Restore cancelled")
        return False
    
    try:
        # Backup current database if it exists
        if os.path.exists(db_path):
            current_backup = f"amy_memory_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            current_backup_path = os.path.join(backup_dir, current_backup)
            shutil.copy2(db_path, current_backup_path)
            print(f"📦 Current memory backed up as: {current_backup}")
        
        # Restore the backup
        shutil.copy2(backup_path, db_path)
        print(f"✅ Memory restored from: {backup_name}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

def show_memory_stats():
    """Show current memory statistics"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("❌ No database found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get session count
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        # Get event count
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        
        # Get database size
        size = os.path.getsize(db_path)
        size_mb = size / (1024 * 1024)
        
        print("📊 Memory Statistics:")
        print(f"  • Sessions: {session_count}")
        print(f"  • Events: {event_count}")
        print(f"  • Database size: {size_mb:.2f} MB")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error reading statistics: {e}")

def main():
    """Main function"""
    print("🧠 Amy Memory Manager")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Show memory statistics")
        print("2. Backup current memory")
        print("3. Reset memory (with optional backup)")
        print("4. List backups")
        print("5. Restore from backup")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            show_memory_stats()
        elif choice == "2":
            backup_memory()
        elif choice == "3":
            reset_memory()
        elif choice == "4":
            list_backups()
        elif choice == "5":
            restore_backup()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main() 
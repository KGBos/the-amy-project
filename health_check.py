#!/usr/bin/env python3
"""
Health check script for The Amy Project
Verifies that all components are properly configured and working.
"""

import os
import sys
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_environment():
    """Check if environment variables are set"""
    required_vars = ['TELEGRAM_BOT_TOKEN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set these in your .env file")
        return False
    
    print("✅ Environment variables are set")
    return True

def check_database():
    """Check if database exists and is accessible"""
    db_path = Path("instance/amy_memory.db")
    
    if not db_path.exists():
        print("❌ Database not found at instance/amy_memory.db")
        print("   Run: python3 init_db.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables:
            print("❌ Database exists but has no tables")
            return False
        
        print(f"✅ Database exists with {len(tables)} tables")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    # Map package names to their actual import names
    package_imports = {
        'google-adk': 'google.adk',
        'python-telegram-bot': 'telegram',
        'python-dotenv': 'dotenv',
        'google-genai': 'google.genai'
    }
    
    missing_packages = []
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "app/core/amy_agent/agent.py",
        "app/integrations/telegram/bot.py",
        "run_web.py",
        "start_telegram.sh",
        "start_web.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files exist")
    return True

def main():
    """Run all health checks"""
    print("🏥 Running health checks for The Amy Project...\n")
    
    checks = [
        check_python_version,
        check_dependencies,
        check_files,
        check_database,
        check_environment
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print(f"📊 Health check results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All systems are go! You can start the bot or web UI.")
        return 0
    else:
        print("⚠️  Some issues were found. Please fix them before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
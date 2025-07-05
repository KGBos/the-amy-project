#!/usr/bin/env python3
"""
Simple script to run Amy's Telegram bot with memory system
"""

import os
import sys
import signal
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instance/amy_telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal. Stopping Amy bot...")
    sys.exit(0)

def main():
    """Run Amy's Telegram bot with memory system."""
    print("🤖 Starting Amy Telegram Bot with Memory System")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all variables are set.")
        return 1
    
    # Check if instance directory exists
    instance_dir = Path("instance")
    if not instance_dir.exists():
        print("📁 Creating instance directory...")
        instance_dir.mkdir(exist_ok=True)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Import and run the bot
        from app.integrations.telegram.bot import main as run_bot
        
        print("✅ Environment check passed")
        print("✅ Memory system initialized")
        print("✅ Starting bot...")
        print("\n📱 Amy is now running! Send messages to your Telegram bot.")
        print("💡 Use /start to begin, /help for commands, /memory for stats")
        print("🛑 Press Ctrl+C to stop the bot")
        print("-" * 50)
        
        run_bot()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Bot startup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
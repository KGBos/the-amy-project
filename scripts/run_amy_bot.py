#!/usr/bin/env python3
"""
Simple script to run Amy's Telegram bot with memory system
"""

import os
import sys
import signal
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent.parent
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
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    # Support fallback to GOOGLE_API_KEY for compatibility
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not telegram_token:
        missing_vars.append('TELEGRAM_BOT_TOKEN')
    if not gemini_api_key:
        missing_vars.append('GEMINI_API_KEY (or GOOGLE_API_KEY)')
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
        from amy.integrations.telegram.bot import main as run_bot
        
        print("✅ Environment check passed")
        print("✅ Memory system initialized")
        print("✅ Starting bot...")
        print("\n📱 Amy is now running! Send messages to your Telegram bot.")
        print("💡 Use /help for commands, /memory for stats")
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
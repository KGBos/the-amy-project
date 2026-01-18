#!/bin/bash
# Development setup script for The Amy Project

set -e

echo "🚀 Setting up The Amy Project development environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create instance directory if it doesn't exist
if [ ! -d "instance" ]; then
    echo "📁 Creating instance directory..."
    mkdir -p instance
fi

# Initialize database if it doesn't exist
if [ ! -f "instance/amy_memory.db" ]; then
    echo "🗄️  Initializing database..."
    python3 init_db.py
else
    echo "✅ Database already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x start_telegram.sh
chmod +x start_web.sh

echo ""
echo "✅ Setup complete! You can now:"
echo "  • Run the Telegram bot: ./start_telegram.sh"
echo "  • Run the web UI: ./start_web.sh"

echo ""
echo "📝 Don't forget to:"
echo "  • Create a .env file with your TELEGRAM_BOT_TOKEN"
echo "  • Set up your Google API credentials"
echo "" 
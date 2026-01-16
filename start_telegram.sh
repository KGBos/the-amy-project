#!/bin/bash
# Activates the virtual environment and starts the Telegram bot.

# Exit on any error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if bot.py exists
if [ ! -f "$SCRIPT_DIR/amy/integrations/telegram/bot.py" ]; then
    echo "Error: bot.py not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "Warning: .env file not found. Make sure TELEGRAM_BOT_TOKEN is set."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Run the bot
echo "Starting Telegram bot..."
python3 "$SCRIPT_DIR/scripts/run_amy_bot.py"

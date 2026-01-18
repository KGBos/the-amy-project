#!/bin/bash
# Start the Web interface

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Error: Virtual environment not found"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate and run
source "$SCRIPT_DIR/venv/bin/activate"
echo "Starting Amy Web Interface (ADK Native)..."
# We run adk web on the agents directory to enable discovery
adk web "$SCRIPT_DIR/amy/core/agents" --port 8080

#!/bin/bash
# Activates the virtual environment and starts the ADK Web UI.

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

# Check if run_web.py exists
if [ ! -f "$SCRIPT_DIR/run_web.py" ]; then
    echo "Error: run_web.py not found"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Check if adk command is available
if ! command -v adk &> /dev/null; then
    echo "Error: 'adk' command not found. Please install google-adk: pip install google-adk"
    exit 1
fi

# Run the web UI using the runner defined in run_web.py
echo "Starting ADK Web UI..."
echo "Access the web UI at: http://localhost:8000"
adk web --runner_path "$SCRIPT_DIR/run_web.py:adk_runner"

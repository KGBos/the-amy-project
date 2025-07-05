# Gemini Project Configuration

This file stores key configuration details and conventions for the "The Amy Project" to ensure consistent and efficient assistance.

## Project Structure

*   **`app/`**: Main application source code.
    *   **`core/amy_agent/agent.py`**: Defines the primary `root_agent`.
    *   **`integrations/telegram/bot.py`**: Logic for the Telegram bot interface.
*   **`instance/`**: Runtime data, such as the database. This directory is ignored by Git.
    *   **`amy_memory.db`**: The primary SQLite database for conversation history.
*   **`venv/`**: Python virtual environment.
*   **`.env`**: Stores environment variables (API keys, tokens).
*   **`requirements.txt`**: Lists all Python dependencies.
*   **`init_db.py`**: Script to initialize the database schema.
*   **`read_db.py`**: Utility script to read conversation history from the database.
*   **`run_web.py`**: Configuration file for the ADK web UI.
*   **`start_telegram.sh`**: Launcher script for the Telegram bot.
*   **`start_web.sh`**: Launcher script for the ADK web UI.

## Key Files & Variables

*   **Agent Definition**: `app/core/amy_agent/agent.py` contains the `root_agent`.
*   **Database Location**: The SQLite database is located at `instance/amy_memory.db`. All scripts have been updated to use this location.
*   **Environment File**: The `.env` file is located in the project root.

## Launcher Scripts

*   **Telegram Bot**: `./start_telegram.sh`
*   **Web UI**: `./start_web.sh`

These scripts handle activating the virtual environment and running the respective applications with the correct configurations.

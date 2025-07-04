# Amy: Your Personal AI Assistant

Amy is designed to be a helpful and friendly AI assistant. She is built using the Google Agent Development Kit (ADK) and aims to provide a seamless and intelligent conversational experience.

## Core Capabilities:

*   **Conversational Interface:** Interact with Amy through natural language.
*   **Persistent Memory:** Amy remembers past conversations within a session, thanks to local SQLite database storage.
*   **Extensible Tools:** Amy can be extended with various tools to interact with the real world (e.g., getting current time, weather, integrating with calendars, tasks, etc.).
*   **Proactive Assistance (Future):** The long-term vision for Amy includes proactive anticipation of user needs and autonomous action.

## Current Status:

Amy is currently in Phase 0 (Foundation) of her development roadmap. She can engage in text-based conversations and maintain memory across restarts of the ADK web UI.

## How to Interact with Amy:

1.  Ensure your virtual environment is activated.
2.  Navigate to the `app` directory.
3.  Run `adk web app --session_service_uri "sqlite:///./app/amy_memory.db"`.
4.  Access the web UI at `http://localhost:8000` and select Amy's agent.

## Future Enhancements:

Refer to the `README.md` for the detailed roadmap of Amy's development, including real-time voice capabilities, advanced long-term memory, and deeper integrations.

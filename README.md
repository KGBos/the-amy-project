# Amy: The Proactive Digital Twin

## Vision

Amy is not merely a conversational AI; she is your **Proactive Digital Twin**, an intelligent entity deeply integrated into your life, anticipating needs, optimizing your time, and enhancing your capabilities across all domains. She operates with a profound understanding of your context, preferences, and goals, acting as your personal orchestrator of information and action.

## Setup and Usage

### Initial Setup

1.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    ```

2.  **Activate the Environment:**
    ```bash
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Copy the `.env.example` file (if it exists) to a new file named `.env`.
    *   Fill in the required API keys and tokens in the `.env` file (e.g., `TELEGRAM_BOT_TOKEN`, Google API keys).

5.  **Initialize the Database:**
    *   Run the initialization script once to create the database schema in the `instance/` directory.
    ```bash
    python3 init_db.py
    ```

### Running the Bot

*   **Telegram Bot:**
    *   To start the Telegram bot, simply run the launcher script:
    ```bash
    ./start_telegram.sh
    ```

*   **Web UI for Testing:**
    *   To test the agent through a web interface, run the web launcher script:
    ```bash
    ./start_web.sh
    ```
    *   This will provide a URL (usually `http://localhost:8000`) to access the chat interface in your browser. The web UI shares the same database (`instance/amy_memory.db`) as the Telegram bot.

### Development Tools

*   **Quick Setup:**
    ```bash
    ./setup_dev.sh
    ```
    *   Automatically sets up the virtual environment, installs dependencies, and initializes the database.

*   **Health Check:**
    ```bash
    python3 health_check.py
    ```
    *   Verifies that all components are properly configured and working.

*   **View Sessions:**
    ```bash
    python3 view_sessions.py
    ```
    *   Displays all conversation sessions and their history from the database.

*   **Manage Memory:**
    ```bash
    python3 manage_memory.py
    ```
    *   Interactive tool to backup, reset, or restore conversation memory.

**Core Capabilities & Features:**

1.  **Hyper-Contextual Awareness (Beyond Basic Memory):**
    *   **Omni-Modal Perception:** Amy continuously processes and understands your environment through all available modalities:
        *   **Voice:** Not just transcription, but tone, emotion, and intent. She understands interruptions, overlapping speech, and even whispers.
        *   **Vision:** Through wearable cameras or smart home devices, she understands your physical surroundings, activities, and even your emotional state from facial cues.
        *   **Text:** Seamlessly ingests all your digital communications (emails, chats, documents, web browsing history) with privacy-preserving, on-device processing where possible.
    *   **Deep Personal Knowledge Graph (LTM):** Beyond simple chat history, Amy builds a dynamic, evolving knowledge graph of your life:
        *   **Relationships:** Who are your friends, family, colleagues, and what are their roles/preferences?
        *   **Preferences:** Your likes, dislikes, habits, routines, dietary restrictions, preferred communication styles.
        *   **Goals & Projects:** Your long-term aspirations, current tasks, and project statuses, cross-referencing across all your digital tools.
        *   **Contextual Reasoning:** She understands the *why* behind your actions and requests, not just the *what*.

2.  **Proactive Anticipation & Action:**
    *   **Predictive Assistance:** Amy doesn't wait for commands. She anticipates your next need based on context, time, location, and your historical patterns.
        *   *Example:* "Amy, I'm leaving the office now." Amy responds: "Traffic looks heavy on your usual route. I've already rerouted your navigation, sent an ETA update to your family, and pre-heated your oven for dinner."
    *   **Goal-Oriented Orchestration:** You state a high-level goal ("Plan my trip to Japan next spring"), and Amy breaks it down into sub-tasks, researches, books, schedules, and manages all necessary communications, presenting you with options and handling execution.
    *   **Intelligent Delegation:** She identifies tasks you'd rather delegate (e.g., scheduling, routine emails, data entry) and executes them autonomously, only seeking your approval for critical decisions.

3.  **Seamless Integration & Control:**
    *   **Universal Digital Interface:** Amy is the single interface to all your digital services (calendar, email, tasks, smart home, financial apps, social media, productivity suites). You interact with Amy, and she interacts with the underlying services.
    *   **Physical World Interaction:** Through IoT and robotics, she can interact with your physical environment (e.g., "Amy, dim the lights and play my 'focus' playlist," or "Amy, order groceries based on our meal plan and current inventory").
    *   **Granular Privacy & Control:** You have absolute, transparent control over what Amy perceives, remembers, and acts upon. Fine-grained permissions for data access and action execution.

4.  **Continuous Learning & Adaptation:**
    *   **Reinforcement Learning:** Amy learns from your feedback, corrections, and implicit preferences, constantly refining her understanding and proactive behaviors.
    *   **Self-Correction:** She identifies and corrects her own mistakes, learning from failures.
    *   **Skill Acquisition:** As new APIs or capabilities become available, Amy can learn to integrate and utilize them, expanding her own skillset.

5.  **Multimodal Communication & Embodiment:**
    *   **Natural Language Fluency:** Flawless, context-aware conversation across all languages you speak.
    *   **Emotional Intelligence:** She understands and responds to your emotional state, adapting her communication style accordingly.
    *   **Voice & Visual Consistency:** A consistent voice and (optional) visual avatar that evolves with your preferences, providing a comforting and familiar presence.

## Roadmap

**Overall Goal:** To build a personal AI agent that understands context, anticipates needs, and acts proactively across various domains, leveraging ADK's capabilities and external integrations.

---

**Phase 0: Foundation (Current State)**
*   **Goal:** Establish a stable, text-based conversational agent with basic persistence.
*   **Key Features Achieved:**
    *   Basic ADK agent setup (`amy_agent`).
    *   Local persistent memory using SQLite (`amy_memory.db`).
    *   Basic text-based interaction with `gemini-2.5-flash`.
    *   Proper project structure and Git repository.

---

**Phase 1: Core Conversational Intelligence & Essential Real-World Awareness**
*   **Goal:** Make Amy a more capable and context-aware text-based assistant.
*   **Key Features:**
    1.  **Custom Tool: Current Local Time:**
        *   Implement a Python function to get the current time and convert it to a specified timezone.
        *   Integrate this as an ADK tool for Amy.
        *   Update Amy's instructions to use this tool when asked about time.
    2.  **Custom Tool: Current Weather:**
        *   Obtain an API key for a weather service (e.g., OpenWeatherMap).
        *   Implement a Python function to fetch weather data for a given location.
        *   Integrate this as an ADK tool for Amy.
        *   Update Amy's instructions to use this tool when asked about weather.
    3.  **Basic Long-Term Memory (LTM) - Summarization/Key Facts:**
        *   Implement a mechanism to periodically summarize key facts or decisions from the `DatabaseSessionService` history.
        *   Store these summaries in a simple, searchable format (e.g., a separate table in `amy_memory.db` or a text file).
        *   Develop a basic retrieval tool for Amy to access these summaries when relevant.
    4.  **Improved Error Handling & User Feedback:**
        *   Enhance Amy's responses when she encounters limitations or errors (e.g., "I can't find the weather for that location," or "I don't have access to that information yet").

---

**Phase 2: Real-time Voice & Robust Long-Term Memory**
*   **Goal:** Enable natural voice interaction and establish a scalable LTM system.
*   **Key Features:**
    1.  **Gemini Live API Integration (Voice Input/Output):**
        *   **Critical External Dependency:** Gain access to a Gemini Live API model (e.g., `gemini-live-2.5-flash-preview-native-audio-dialog`). This will likely require contacting Google Cloud support or AI Studio support.
        *   Update Amy's `model` parameter to use the Live API model.
        *   Test real-time voice interaction via `adk web`.
    2.  **Advanced Long-Term Memory (LTM) - Retrieval Augmented Generation (RAG):**
        *   **Option A (Recommended): Vertex AI RAG:**
            *   Set up a Google Cloud Project and enable Vertex AI API.
            *   Create a Vertex AI RAG Corpus.
            *   Configure `VertexAiRagMemoryService` in Amy's ADK setup.
            *   Develop tools for Amy to "ingest" (store) and "retrieve" (search) information from the RAG corpus.
        *   **Option B (Alternative): Local Vector Database:**
            *   Choose and set up a local vector database (e.g., ChromaDB, FAISS).
            *   Integrate an embedding model (e.g., from `sentence-transformers`).
            *   Develop custom tools for Amy to store and retrieve information from this local vector database.
    3.  **Basic Proactivity - Time-Based Reminders:**
        *   Implement a tool for Amy to set and trigger simple time-based reminders (e.g., "Remind me to call John at 3 PM"). This would involve storing reminders in the database and a background process to check and trigger them.

---

**Phase 3: Deeper Integration & Contextual Proactivity**
*   **Goal:** Amy starts integrating with personal services and anticipating needs based on broader context.
*   **Key Features:**
    1.  **Calendar Integration:**
        *   Implement tools to read and potentially write events to your calendar (e.g., Google Calendar API).
        *   Update Amy's instructions to manage your schedule.
    2.  **Task Management Integration:**
        *   Implement tools to interact with a task management system (e.g., Google Tasks, Todoist API).
        *   Enable Amy to create, update, and query tasks.
    3.  **Contextual Triggers (Basic):**
        *   Develop logic for Amy to proactively offer help based on simple contextual cues (e.g., time of day, upcoming calendar events).
        *   *Example:* "It's 5 PM, would you like me to summarize your day's tasks?"
    4.  **User Preferences (LTM Extension):**
        *   Expand the LTM to explicitly store and retrieve user preferences (e.g., preferred coffee, communication style, common contacts).

---

**Phase 4: Multimodal Perception & Advanced Proactivity**
*   **Goal:** Amy becomes truly multimodal and highly anticipatory, acting as a digital twin.
*   **Key Features:**
    1.  **Vision Integration:**
        *   Integrate with ADK's video streaming capabilities (requires Live API model with vision).
        *   Develop tools for Amy to "see" and describe her surroundings or analyze visual input.
    2.  **Advanced Proactivity (Predictive):**
        *   Implement more sophisticated anticipation based on complex patterns, external data feeds, and predictive analytics.
        *   *Example:* "Based on your calendar and traffic, you should leave in 10 minutes to make your meeting on time. I've already sent directions to your car."
    3.  **Emotional Intelligence (Basic):**
        *   Integrate sentiment analysis or tone detection (from voice/text input) to allow Amy to adapt her communication style.
    4.  **Complex Workflow Orchestration:**
        *   Utilize ADK's `WorkflowAgent` and `ParallelAgent` to manage multi-step, complex tasks autonomously.

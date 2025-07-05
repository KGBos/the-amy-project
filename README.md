# Amy: The Proactive Digital Twin

## Vision

Amy is not merely a conversational AI; she is your **Proactive Digital Twin**, an intelligent entity deeply integrated into your life, anticipating needs, optimizing your time, and enhancing your capabilities across all domains. She operates with a profound understanding of your context, preferences, and goals, acting as your personal orchestrator of information and action.

## 🧠 Memory Architecture

Amy implements a robust three-tier memory system to ensure comprehensive recall and contextual awareness across all communication modes:

### **STM (Short-Term Memory)**
- **Purpose**: Immediate conversation context for current interaction
- **Storage**: In-memory conversation buffer (last 20 messages)
- **Access**: Instant, no database calls
- **Scope**: Current session only

### **MTM (Medium-Term Memory)**
- **Purpose**: Complete conversation history and session management
- **Storage**: SQLite database with full conversation sessions
- **Access**: All conversations across all communication modes (Telegram, Web UI, etc.)
- **Scope**: Permanent storage of every line of dialogue
- **Features**: 
  - Session summarization after completion
  - Cross-platform conversation linking
  - Readable through ADK web interface

### **LTM (Long-Term Memory)**
- **Purpose**: Semantic knowledge and contextual recall
- **Storage**: Vector database (JSON files in `instance/vector_db/`) for semantic search
- **Access**: Intelligent retrieval based on conversation relevance
- **Scope**: Key facts, preferences, relationships, and contextual knowledge
- **Features**:
  - Automatic fact extraction and storage
  - Context-aware retrieval system
  - Personal information learning

### **Memory Flow**
1. **STM**: Immediate context for current conversation
2. **MTM**: Permanent storage of all conversations across all platforms
3. **LTM**: Intelligent context building based on conversation relevance

### **Key Requirements**
- **Universal Recording**: Every conversation from Telegram, Web UI, and future endpoints is permanently recorded
- **Cross-Platform Access**: All conversations visible through ADK web interface
- **Complete Recall**: Amy can access any conversation ever had
- **Intelligent Context**: System builds relevant context based on current conversation needs
- **Privacy-First**: All data stored locally with user control

## 🚀 Setup and Usage

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
    *   Copy the `.env.example` file to a new file named `.env`:
    ```bash
    cp .env.example .env
    ```
    *   Fill in the required API keys and tokens in the `.env` file:
        - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
        - `TELEGRAM_BOT_TOKEN`: Get from [@BotFather](https://t.me/botfather) on Telegram

5.  **Initialize the Database:**
    ```bash
    python3 init_db.py
    ```

### Running Amy

#### **Telegram Bot (Recommended)**
```bash
python3 run_amy_bot.py
```
- Amy will start and connect to your Telegram bot
- Send messages to your bot to interact with Amy
- Use `/start`, `/help`, and `/memory` commands
- All conversations are permanently stored and cross-platform accessible

#### **Web UI for Testing**
```bash
./start_web.sh
```
- Provides a web interface at `http://localhost:8000`
- Shares the same memory system as the Telegram bot
- Good for development and testing

### 🛠️ Development Tools

#### **Quick Setup**
```bash
./setup_dev.sh
```
- Automatically sets up the virtual environment, installs dependencies, and initializes the database.

#### **Health Check**
```bash
python3 health_check.py
```
- Verifies that all components are properly configured and working.

#### **Memory Management**
```bash
python3 manage_memory.py
```
- Interactive tool to backup, reset, or restore conversation memory.

#### **Memory Reset (Complete Clean Start)**
```bash
python3 reset_amy_memory.py
```
- Completely resets Amy's memory system
- Removes all conversations, facts, and test data
- Use when you want Amy to start fresh

#### **View Sessions**
```bash
python3 view_sessions.py
```
- Displays all conversation sessions and their history from the database.

#### **Test Suite**
```bash
python3 test_suite.py
```
- Comprehensive test suite for the memory system
- Tests STM, MTM, LTM, and integration features

### 📊 Memory Commands

#### **Telegram Bot Commands**
- `/start` - Initialize conversation with Amy
- `/help` - Show available commands
- `/memory` - Display memory statistics

#### **Memory Statistics**
The `/memory` command shows:
- Active sessions in STM
- Total conversations in MTM
- Facts stored in LTM by type
- Cross-platform session counts

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

### Database Paths
- **MTM Database**: `instance/amy_memory.db`
- **LTM Vector DB**: `instance/vector_db/`
- **Logs**: `instance/amy_telegram_bot.log`

## 📁 Project Structure

```
app/
├── core/amy_agent/          # Amy's core agent definition
├── features/memory/         # Memory system (STM, MTM, LTM)
└── integrations/telegram/   # Telegram bot integration

# Management Scripts
run_amy_bot.py              # Main bot launcher
reset_amy_memory.py         # Complete memory reset
manage_memory.py            # Memory management tool
test_suite.py               # Comprehensive test suite

# Documentation
MEMORY_SYSTEM.md            # Detailed memory system docs
AMY_ISSUES.md              # Known issues and improvements
GEMINI.md                  # Gemini API integration guide
```

## 🧪 Testing

### Comprehensive Test Suite
The `test_suite.py` runs 9 different test categories:

1. **STM Tests**: Message storage, retrieval, and session management
2. **MTM Tests**: Conversation storage, database operations
3. **LTM Tests**: Fact storage, retrieval, and search
4. **Memory Manager Tests**: Integration between all systems
5. **Telegram Integration Tests**: Bot conversation simulation
6. **Cross-Platform Tests**: Multi-platform session handling
7. **Memory Statistics Tests**: System health and metrics
8. **Search Tests**: Content search across all systems
9. **Context Building Tests**: AI response context generation

### Running Tests
```bash
# Run all tests
python3 test_suite.py

# Run specific test (modify test_suite.py)
python3 -c "
from test_suite import TestSuite
ts = TestSuite()
ts.test_telegram_integration()
"
```

## 🎯 Current Status

**Phase 0: Foundation (Current State) ✅**
*   **Goal:** Establish a stable, text-based conversational agent with comprehensive memory.
*   **Key Features Achieved:**
    *   ✅ Complete three-tier memory system (STM, MTM, LTM)
    *   ✅ Telegram bot integration with persistent memory
    *   ✅ Cross-platform conversation storage
    *   ✅ Automatic fact extraction and learning
    *   ✅ Memory management and reset tools
    *   ✅ Comprehensive test suite
    *   ✅ Local persistent memory using SQLite
    *   ✅ Text-based interaction with `gemini-2.5-flash`

## 🚧 Known Issues

See `AMY_ISSUES.md` for a complete list of known issues and improvements needed. Key areas include:
- Context building optimization
- Memory command functionality
- Conversation flow improvements

## 📈 Roadmap

**Overall Goal:** To build a personal AI agent that understands context, anticipates needs, and acts proactively across various domains, leveraging ADK's capabilities and external integrations.

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
    3.  **Improved Error Handling & User Feedback:**
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

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome! The codebase is designed to be extensible and well-documented.

## 📄 License

This project is for personal use and development.

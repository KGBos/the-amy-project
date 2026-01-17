# Amy Architecture

> Detailed technical documentation for the Amy Project.

## 🎯 Overview

Amy is a **Proactive Multimodal Digital Twin** - an intelligent assistant with persistent memory across conversations. Built on Google ADK with a three-tier memory system.

---

## 🏗️ Architecture

### Three-Tier Memory System

```
User Message → [Telegram / Web Interface]
                        ↓
              Short-Term Memory (STM)
              - In-memory buffer
              - Last 3-20 messages per session
                        ↓
              Episodic Memory (EpTM)
              - SQLite database
              - Session storage & summarization
                        ↓
              Long-Term Memory (LTM)
              - mem0 with ChromaDB
              - HuggingFace embeddings
              - Semantic vector search
                        ↓
              Context Builder (500 char limit)
                        ↓
              Gemini AI Response
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **STM** | In-memory | Recent conversation context (~20 turns) |
| **EpTM** | SQLite | Session storage, conversation summaries |
| **LTM** | mem0 + ChromaDB | Semantic fact storage & retrieval |
| **Memory Manager** | Python | Orchestrates all memory tiers |
| **Agent Core** | Google ADK | Response generation |

---

## 📁 Project Structure

```
amy/
├── core/
│   ├── amy_agent/
│   │   └── agent.py          # Main AmyAgent (BaseAgent)
│   ├── prompts.py            # Prompt building
│   └── agent_logger.py       # Logging utilities
├── features/
│   └── memory/
│       ├── stm.py            # Short-Term Memory
│       ├── episodic.py       # Episodic Memory (SQLite)
│       ├── ltm.py            # Long-Term Memory (mem0)
│       ├── memory_manager.py # Memory orchestration
│       ├── context_builder.py# Context assembly
│       └── session_manager.py# User session tracking
├── integrations/
│   ├── telegram/bot.py       # Telegram bot
│   ├── web/                  # Web interface
│   └── calendar/             # Calendar integration
└── config.py                 # Centralized configuration

scripts/
├── run_amy_bot.py            # Telegram bot launcher
├── run_web.py                # Web UI launcher
├── management/               # Memory management tools
├── debug/                    # Debug utilities
└── testing/                  # Test scripts

docs/
├── ARCHITECTURE.md           # This file
├── GOALS.md                  # Roadmap & priorities
├── MEMORY_SYSTEM.md          # Memory system deep-dive
├── MEMORY_DEBUG_GUIDE.md     # Debugging memory issues
└── SECURITY.md               # Security considerations
```

---

## 🧠 Memory System Details

### Short-Term Memory (STM)
- **Storage**: In-memory dictionary
- **Capacity**: ~20 messages per session
- **Purpose**: Immediate conversation context

### Episodic Memory (EpTM)
- **Storage**: SQLite (`instance/amy_memory.db`)
- **Features**:
  - Session-based conversation storage
  - Message history with timestamps
  - Searchable by content
- **Schema**: ADK-compatible (conversations + messages tables)

### Long-Term Memory (LTM)
- **Storage**: mem0 with ChromaDB (`instance/mem0_storage/`)
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **LLM**: Gemini for fact extraction
- **Features**:
  - Semantic search for relevant facts
  - Automatic fact extraction from conversations
  - Deduplication and relevance scoring

### Memory Manager
- Orchestrates STM → EpTM → LTM flow
- Builds context for AI responses (500 char limit)
- Handles user session detection (new vs returning)

---

## 🚀 Running Amy

### Prerequisites
```bash
# Python 3.11+
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Setup
```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # For Telegram
```

### Launch Options

```bash
# Telegram Bot
./start_telegram.sh
# or: python scripts/run_amy_bot.py

# Web Interface (ADK)
./start_web.sh
# or: python scripts/run_web.py
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_memory_manager.py

# Verify mem0 integration
python scripts/verify_mem0.py

# Health check
python scripts/health_check.py
```

### Test Coverage
- Memory system unit tests
- Integration tests for message flow
- Agent response tests

---

## 🛠️ Development Tools

### Memory Management
```bash
python scripts/management/cleanup_ltm.py      # Clean LTM
python scripts/management/reset_amy_memory.py # Reset all memory
python scripts/management/view_sessions.py    # View sessions
python scripts/management/read_db.py          # Inspect database
```

### Debugging
```bash
python scripts/debug/memory_debugger.py       # Interactive debug
python scripts/debug/live_memory_monitor.py   # Real-time monitor
```

---

## 🔧 Configuration

All configuration is centralized in `amy/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_MODEL` | `gemini-2.0-flash` | Gemini model |
| `CONTEXT_LIMIT` | 500 | Max context chars |
| `LTM_TEMPERATURE` | 0.1 | LTM extraction temp |
| `EMBEDDER_MODEL` | `all-MiniLM-L6-v2` | Embedding model |

---

## 📊 Current Status

| Component | Status |
|-----------|--------|
| Three-tier memory | ✅ Operational |
| mem0/ChromaDB LTM | ✅ Integrated |
| Telegram bot | ✅ Working |
| Web interface | ✅ Working |
| Voice/multimodal | 🔄 Planned |

---

## 📚 Further Reading

- [GOALS.md](GOALS.md) - Roadmap and priorities
- [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) - Detailed memory documentation
- [MEMORY_DEBUG_GUIDE.md](MEMORY_DEBUG_GUIDE.md) - Debugging guide
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

_Last updated: 2026-01-17_

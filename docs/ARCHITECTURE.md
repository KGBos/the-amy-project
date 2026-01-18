# Amy Architecture

> Technical documentation for the Amy Project.

## 🎯 Overview  

Amy is a personal AI assistant with persistent memory. Built with a clean, layered architecture around the Google ADK.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION LAYER (Thin)                      │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │ telegram.py     │              │ web.py          │          │
│  │ (~100 lines)    │              │ (~200 lines)    │          │
│  └────────┬────────┘              └────────┬────────┘          │
└───────────┼────────────────────────────────┼────────────────────┘
            │                                │
            ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                           AMY CORE                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Factory (core/factory.py)                                  ││
│  │  └── Creates ADK Runner                                     ││
│  │      └── Injects Memory Dependencies                        ││
│  │                                                             ││
│  │  Runner (google.adk.runners.Runner)                         ││
│  │  └── Executes Agent loop                                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
            │                                │
            ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MEMORY LAYER                               │
│  ┌───────────────────────┐    ┌────────────────────────────────┐│
│  │ ConversationDB        │    │ LTM                            ││
│  │ (SQLite)              │    │ (Mem0 + ChromaDB)              ││
│  │ • instance/amy.db     │    │ • instance/mem0_storage/       ││
│  └───────────────────────┘    └────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
amy/
├── config.py             # Centralized configuration
├── core/
│   ├── factory.py       # Runner Factory
│   ├── agent.py         # ADK Agent loader (loads from YAML)
│   ├── logger.py        # Logging utilities
│   └── agents/
│       └── amy/
│           └── root_agent.yaml  # YAML Agent Definition
├── memory/
│   ├── conversation.py  # SQLite conversation storage
│   ├── ltm.py           # Semantic memory (Mem0)
│   └── base.py          # Memory interface
├── integrations/
│   ├── telegram.py      # Telegram bot
│   └── web.py           # Legacy web (FastAPI/ADK Web)
└── tools/
    ├── memory_tools.py  # ADK FunctionTools
    ├── search_tools.py  # DuckDuckGo search
    └── code_tools.py    # Python interpreter
```

---

## 🧠 Memory System

| Component | Technology | Purpose |
|-----------|------------|---------|
| **ConversationDB** | SQLite + `aiosqlite` | Async persistent message storage (WAL mode) |
| **LTM** | Mem0 + ChromaDB | Semantic fact retrieval (ThreadPool managed) |
| **Memory Tools** | ADK FunctionTool | Agent-callable save/search |

---

## 📡 Telemetry & Observability

- **Freeplay**: Integration with Freeplay for LLM tracing and evaluation. 
  - Configured in `amy/core/telemetry.py`.
  - Requires `FREEPLAY_API_KEY`.

## 🎙️ Audio Capabilities

- **Whisper**: Local audio transcription support using `openai-whisper`.


## 🚀 Running Amy

### Prerequisites
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment
```bash
# .env file
GEMINI_API_KEY=your_key
TELEGRAM_BOT_TOKEN=your_token
```

### Launch
```bash
# Telegram Bot
./start_telegram.sh

# Web Interface
./start_web.sh
```

---

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

---

## 🎨 ADK Visual Builder Integration

The project is optimized for the **ADK Native Visual Editor**. When loading the project into the ADK dashboard (`./start_web.sh`), the following translations occur:

- **Agents as Nodes**: Each YAML file in `amy/core/agents/` appears as a distinct node in the graph.
- **Hierarchies as Connections**: Sub-agent relationships defined in YAML manifest as visual arrows between nodes.
- **Tools as Icons**: Attached capabilities like `search_memory` or `PythonInterpreter` appear directly on the agent blocks.
- **Workflow as Structure**: Orchestrators like `SequentialAgent` or `ParallelAgent` visually fork or sequence the control flow.
- **Configuration as Properties**: Instructions, model types, and parameters are accessible via the side property panel upon selecting a node.

---

_Last updated: 2026-01-18_

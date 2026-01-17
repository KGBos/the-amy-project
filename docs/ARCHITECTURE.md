# Amy Architecture

> Technical documentation for the Amy Project.

## 🎯 Overview

Amy is a personal AI assistant with persistent memory. Built with a clean, simple architecture focused on conversation storage and semantic recall.

---

## 🏗️ Architecture

```
User Message → [Telegram / Web Interface]
                        ↓
              ConversationDB (SQLite)
              - Persistent message storage
              - Last N messages for context
                        ↓
              Long-Term Memory (LTM)
              - mem0 with ChromaDB
              - Semantic fact search
                        ↓
              Gemini AI Response
                        ↓
              ConversationDB (store response)
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **ConversationDB** | SQLite | All conversation storage |
| **LTM** | mem0 + ChromaDB | Semantic fact storage & retrieval |
| **Memory Tools** | ADK FunctionTool | Explicit save/search for agent |
| **Agent** | Google ADK / Gemini | Response generation |

---

## 📁 Project Structure

```
amy/
├── core/
│   └── amy_agent/
│       └── agent.py          # ADK Agent with memory tools
├── features/
│   └── memory/
│       ├── conversation_db.py # SQLite conversation storage
│       ├── ltm.py            # Long-Term Memory (mem0)
│       └── episodic.py       # Legacy (kept for compat)
├── tools/
│   └── memory_tools.py       # ADK save/search tools
├── integrations/
│   ├── telegram/bot.py       # Telegram bot
│   └── web/                  # Web interface
└── config.py                 # Configuration

scripts/
├── run_amy_bot.py            # Telegram launcher
├── run_web.py                # Web launcher
└── management/               # DB tools
```

---

## 🧠 Memory System

### ConversationDB
- **Storage**: SQLite (`instance/amy.db`)
- **Schema**: messages table with session_id, user_id, role, content, timestamp
- **Purpose**: Persistent conversation history

### Long-Term Memory (LTM)
- **Storage**: mem0 with ChromaDB (`instance/mem0_storage/`)
- **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
- **Purpose**: Semantic fact storage and retrieval

### Message Flow
1. User message stored in ConversationDB
2. Recent messages retrieved for context
3. LTM searched for relevant facts
4. Gemini generates response
5. Response stored in ConversationDB
6. Facts extracted and stored in LTM

---

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
TELEGRAM_BOT_TOKEN=your_token  # For Telegram
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
# Run tests
python -m pytest tests/

# Verify mem0
python scripts/verify_mem0.py
```

---

## 🔧 Configuration

All in `amy/config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_MODEL` | `gemini-2.0-flash` | Gemini model |
| `EMBEDDER_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `LTM_TEMPERATURE` | 0.1 | LTM extraction temp |

---

## 📊 Status

| Component | Status |
|-----------|--------|
| ConversationDB | ✅ Operational |
| LTM (mem0) | ✅ Operational |
| Telegram bot | ✅ Working |
| Web interface | ✅ Working |
| Memory tools | ✅ Working |

---

_Last updated: 2026-01-17_

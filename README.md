# Amy: Personal AI Assistant with Memory

## 🧠 Architecture (2026)

Amy is a personal AI assistant with a clean, persistent memory system:

- **ConversationDB:** SQLite-backed conversation storage
- **Long-Term Memory (LTM):** Vector-based semantic storage using **mem0** with ChromaDB
- **Memory Tools:** ADK-style explicit save/search tools

```
User Message → ConversationDB (persistent storage)
                    ↓
              Recent Context (last 10 messages)
                    ↓
              LTM (semantic fact search)
                    ↓
              Gemini AI → Response
                    ↓
              ConversationDB (store response)
```

## ✅ Features
- Persistent conversation storage (SQLite)
- Semantic memory search (ChromaDB + HuggingFace)
- Automatic fact extraction (name, preferences)
- Memory tools for explicit save/recall
- Telegram and Web interfaces

## 🛠️ How to Use

### Run the Bot
```bash
./start_telegram.sh
```

### Run Web Interface
```bash
./start_web.sh
```

## 📁 Key Files

```
├── core/
│   ├── factory.py           # Runner Factory
│   └── agent.py             # ADK Agent loader
├── memory/
│   ├── conversation.py      # SQLite conversation storage
│   └── ltm.py               # Long-term memory (mem0)
├── tools/
│   └── memory_tools.py      # ADK memory tools
├── integrations/
│   └── telegram/bot.py      # Telegram bot
└── config.py                # Configuration
```

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design
- [Memory System](docs/MEMORY_SYSTEM.md) - Memory documentation
- [Goals & Roadmap](docs/GOALS.md) - Priorities
- [Changelog](docs/CHANGELOG.md) - Version history

---

_Last updated: 2026-01-17_
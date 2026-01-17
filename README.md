# Amy: Personal AI Assistant with Real Memory

## 🧠 Current Architecture (2025)

Amy is a personal AI assistant with a real, working memory system. The architecture now includes:

- **Short-Term Memory (STM):** In-memory buffer for recent conversation context.
- **Episodic Memory (EpTM):** SQLite-backed session and message storage, with summarization and search.
- **Long-Term Memory (LTM):** Vector-based semantic storage using **mem0** with ChromaDB and HuggingFace embeddings.
- **MemoryManager:** Orchestrates all three layers and provides a unified interface.

```
User Message → STM (recent context)
           ↓
        EpTM (session storage, summarization)
           ↓
        LTM (fact extraction, deduplication)
           ↓
    Context Builder (500 char limit)
           ↓
      AI Response
```

## ✅ Current Capabilities
- Remembers recent conversation (STM)
- Stores and summarizes sessions (EpTM)
- Extracts and deduplicates facts (LTM)
- Builds context for AI responses (max 500 chars)
- Properly greets new vs. returning users
- Tools for memory cleanup and testing

## 🚫 What's NOT Implemented
- No Sensory Memory (audio/video) in core memory system
- No proactive or multimodal features (yet)
- No reminder/notification system

## 🛠️ How to Use

### 1. Run the Bot
```bash
python3 run_amy_bot.py
```

### 2. Test the Memory System
```bash
python3 tools/testing/test_episodic_memory.py
```

### 3. Clean Up Memory
```bash
python3 tools/management/cleanup_ltm.py
```

## 🗺️ Roadmap
- **Phase 1:** Fix context, deduplication, greeting bugs (**DONE**)
- **Phase 2:** Implement EpTM, clean up codebase (**DONE**)
- **Phase 3:** Documentation alignment, more tests, error handling (**IN PROGRESS**)
- **Phase 4:** Advanced features (proactive, multimodal, etc.) (**PLANNED**)

## 📊 Success Metrics
- Context length always < 500 chars
- No duplicate facts in LTM
- Proper greeting logic
- All memory layers working and tested

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and components
- [Goals & Roadmap](docs/GOALS.md) - Current priorities and future plans
- [Memory System](docs/MEMORY_SYSTEM.md) - Detailed memory documentation
- [Changelog](docs/CHANGELOG.md) - Version history

## 📝 Contributing
- See [GOALS.md](docs/GOALS.md) for current priorities
- See `scripts/testing/` for test scripts

---

_Last updated: 2026-01-17_ 
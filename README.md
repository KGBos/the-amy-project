# Amy: Personal AI Assistant with Real Memory

## 🧠 Current Architecture (2025)

Amy is a personal AI assistant with a real, working memory system. The architecture now includes:

- **Short-Term Memory (STM):** In-memory buffer for recent conversation context.
- **Episodic Memory (EpTM):** SQLite-backed session and message storage, with summarization and search.
- **Long-Term Memory (LTM):** JSON-based fact storage with deduplication and context building.
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
- No Mem0/Vector DB integration (LTM is JSON-based)
- No Sensory Memory (audio/video) in core memory system
- No proactive or multimodal features (yet)
- No broken/legacy code or TODOs for EpTM

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

## 📝 Contributing
- See GOALS.md for current priorities and progress
- See tools/testing/ for test scripts

---

**Amy is now a clean, working foundation for further development.**

_Last updated: 2025-07-06_ 
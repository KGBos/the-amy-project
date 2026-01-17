# Amy's Memory System (2026)

Amy has a clean two-component memory system:
- **ConversationDB** - SQLite storage for all conversations
- **Long-Term Memory (LTM)** - Semantic vector storage via mem0

## 🧠 Architecture

```
User Message
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot                         │
│                                                         │
│  1. conversation_db.add_message(user_msg)               │
│  2. context = recent messages + LTM facts               │
│  3. response = Gemini(system_prompt + context)          │
│  4. conversation_db.add_message(response)               │
│  5. Extract facts → LTM                                 │
└─────────────────────────────────────────────────────────┘
     │                    │
     ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│ ConversationDB  │  │      LTM        │
│ (SQLite)        │  │  (mem0/Chroma)  │
│                 │  │                 │
│ • add_message() │  │ • store_fact()  │
│ • get_recent()  │  │ • search_facts()|
│ • format()      │  │ • contexts      │
└─────────────────┘  └─────────────────┘
```

## 📦 Components

### ConversationDB (`amy/features/memory/conversation_db.py`)

Single SQLite source of truth for all conversations.

| Method | Description |
|--------|-------------|
| `add_message(session_id, role, content)` | Store a message |
| `get_recent_messages(session_id, limit=10)` | Get last N messages |
| `format_for_context(messages)` | Format as context string |
| `get_message_count(session_id)` | Count messages in session |
| `has_previous_conversations(user_id)` | Check if user has history |

**Database:** `instance/amy.db`

### Long-Term Memory (`amy/features/memory/ltm.py`)

Semantic vector storage using mem0 with ChromaDB and HuggingFace embeddings.

| Method | Description |
|--------|-------------|
| `store_fact(text, category, user_id)` | Save a fact |
| `search_facts(query, user_id)` | Semantic search |
| `build_context_from_query(query)` | Get relevant facts as context |

**Storage:** `instance/mem0_storage/`

## 🔧 Fact Extraction

Facts are automatically extracted when users say things like:
- "My name is Leon" → `personal_info`
- "I love pizza" → `preference`
- "I work at Google" → `personal_info`

## 🛠️ Testing

```bash
# Test the memory system
python -m pytest tests/

# Manual test
python scripts/verify_mem0.py
```

## 📊 Data Flow

1. **User sends message**
2. **Store in ConversationDB** (persistent)
3. **Get recent context** (last 10 messages)
4. **Search LTM** for relevant facts
5. **Build prompt** = system + context + message
6. **Gemini generates response**
7. **Store response** in ConversationDB
8. **Extract facts** → store in LTM

## ❌ Removed Components

The following were removed in the 2026 rebuild:
- `STM` (volatile, duplicated EpTM)
- `SessionManager` (in-memory only)
- `ContextBuilder` (overly complex)
- `MemoryManager` (unnecessary orchestration)
- `prompts.py` (greeting hacks)

---

_Last updated: 2026-01-17_
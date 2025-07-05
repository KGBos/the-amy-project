# 🧠 Amy Memory System Debug Guide

This guide will help you understand exactly how Amy's memory system works, what's being stored where, and how decisions are made.

## 🚀 Quick Start

Run the main debug tool to explore the memory system:

```bash
python3 debug_memory_system.py
```

This will give you a menu with all the debugging tools.

## 📋 Available Debug Tools

### 1. 🎬 Memory Demo (`memory_demo.py`)
**What it does:** Walks through the complete memory system step-by-step
**Best for:** Understanding the overall flow

```bash
python3 memory_demo.py
```

**Shows you:**
- How messages flow through STM, MTM, and LTM
- How context is built for AI responses
- How facts are extracted and stored
- Cross-platform memory capabilities

### 2. 🔍 Live Memory Monitor (`live_memory_monitor.py`)
**What it does:** Real-time monitoring of memory operations
**Best for:** Seeing memory in action during conversations

```bash
python3 live_memory_monitor.py
```

**Shows you:**
- Real-time database changes
- New sessions being created
- Messages being added to STM
- Facts being stored in LTM

### 3. 🎨 Memory Flow Visualizer (`memory_flow_visualizer.py`)
**What it does:** Creates visual diagrams of memory operations
**Best for:** Understanding the architecture and data flow

```bash
python3 memory_flow_visualizer.py
```

**Shows you:**
- Memory system architecture diagrams
- Data flow diagrams
- Memory statistics visualizations
- Step-by-step flow diagrams

### 4. 🔧 Memory Debugger (`memory_debugger.py`)
**What it does:** Interactive inspection and debugging tools
**Best for:** Deep diving into specific memory operations

```bash
python3 memory_debugger.py
```

**Shows you:**
- Inspect STM for specific sessions
- Inspect MTM database contents
- Inspect LTM fact storage
- Trace context building process
- Simulate memory flow

## 🧠 Understanding the Memory System

### Three-Tier Memory Architecture

#### 📝 STM (Short-Term Memory)
- **Purpose:** Immediate conversation context
- **Storage:** In-memory buffer (last 20 messages)
- **Access:** Instant, no database calls
- **Scope:** Current session only

**What you'll see:**
- Messages being added to session buffers
- Recent conversation context
- Session management

#### 💾 MTM (Medium-Term Memory)
- **Purpose:** Permanent conversation storage
- **Storage:** SQLite database
- **Access:** All conversations across platforms
- **Scope:** Permanent storage of every message

**What you'll see:**
- Database size changes
- New conversations being created
- Cross-platform message storage
- Conversation history

#### 🧠 LTM (Long-Term Memory)
- **Purpose:** Semantic knowledge and facts
- **Storage:** Vector database (JSON files)
- **Access:** Intelligent retrieval based on relevance
- **Scope:** Personal information, preferences, goals

**What you'll see:**
- Fact extraction from user messages
- Facts being stored by type (personal_info, preference, goal)
- Semantic search capabilities
- Knowledge building over time

## 🔍 What Happens When You Send a Message

### Step 1: Message Reception
```
User Message → Session ID → Platform Detection
```

### Step 2: STM Processing
```
Message → In-Memory Buffer → Recent Context
```

### Step 3: MTM Processing
```
Message → SQLite Database → Permanent Storage
```

### Step 4: LTM Processing (User messages only)
```
User Message → Fact Extraction → Vector Storage
```

### Step 5: Context Building
```
STM Context + LTM Facts → Combined Context
```

### Step 6: AI Response
```
Context + User Message → AI Model → Response
```

### Step 7: Response Storage
```
AI Response → STM + MTM (No LTM)
```

## 📊 Memory Statistics Explained

### STM Statistics
- **Active Sessions:** Number of sessions with recent messages
- **Message Count:** Total messages across all sessions
- **Session Details:** Recent messages in each session

### MTM Statistics
- **Total Sessions:** All conversations ever stored
- **Platforms:** Which platforms have been used
- **Message Count:** Total messages in database
- **Session Details:** Full conversation history

### LTM Statistics
- **Total Facts:** All facts stored across all types
- **Fact Types:** Breakdown by category (personal_info, preference, goal, etc.)
- **Fact Content:** What specific facts are stored

## 🔧 Debugging Common Issues

### Issue: "Hi again!" Problem
**What's happening:** Amy thinks she's met you before
**Debug steps:**
1. Check STM for active sessions: `memory_debugger.py` → Inspect STM
2. Check MTM for existing conversations: `memory_debugger.py` → Inspect MTM
3. Look for old session data that wasn't cleared

### Issue: Context Too Long
**What's happening:** Amy gives overly detailed responses
**Debug steps:**
1. Use `memory_debugger.py` → Trace Context Building
2. Check how much STM context is being included
3. Check how many LTM facts are being retrieved
4. Look for irrelevant old conversations

### Issue: Memory Command Confusion
**What's happening:** Amy confuses asking about commands with using them
**Debug steps:**
1. Check how commands are being processed
2. Look at the conversation flow in MTM
3. See if command detection logic needs improvement

### Issue: Inconsistent Memory Recognition
**What's happening:** Amy gives mixed signals about remembering you
**Debug steps:**
1. Check LTM for stored facts about the user
2. Look at context building for the specific query
3. See if facts are being retrieved properly

## 📁 Memory Files Structure

### Database Files
```
instance/
├── amy_memory.db          # MTM: SQLite database
├── vector_db/             # LTM: Vector database
│   ├── personal_info_*.json
│   ├── preference_*.json
│   └── goal_*.json
└── amy_telegram_bot.log   # Log file
```

### What's Stored Where

#### `amy_memory.db` (MTM)
- **conversations table:** Session information
- **messages table:** All messages ever sent
- **Indexes:** For fast searching

#### `vector_db/` (LTM)
- **personal_info_*.json:** Names, relationships, locations
- **preference_*.json:** Likes, dislikes, interests
- **goal_*.json:** Plans, aspirations, objectives

## 🧪 Testing the Memory System

### Run the Test Suite
```bash
python3 test_suite.py
```

This runs 9 different test categories:
1. STM Tests
2. MTM Tests
3. LTM Tests
4. Memory Manager Tests
5. Telegram Integration Tests
6. Cross-Platform Tests
7. Memory Statistics Tests
8. Search Functionality Tests
9. Context Building Tests

### Manual Testing
1. Start a conversation with Amy
2. Run the live memory monitor in another terminal
3. Watch the memory operations in real-time
4. Use the debugger to inspect what was stored

## 🎯 Key Debugging Questions

### "What is being stored?"
- Use `memory_debugger.py` → Inspect LTM
- Check the `vector_db/` directory
- Look at the database contents

### "Where is it being stored?"
- STM: In-memory (session buffers)
- MTM: SQLite database (`instance/amy_memory.db`)
- LTM: JSON files (`instance/vector_db/`)

### "How is context built?"
- Use `memory_debugger.py` → Trace Context Building
- See how STM and LTM context is combined
- Check relevance filtering

### "Why is Amy responding this way?"
- Check the context being provided to the AI
- Look at recent conversation history
- Examine stored facts about the user

## 📈 Performance Monitoring

### Memory Usage
- **STM:** ~1MB per active session
- **MTM:** ~10-50MB database
- **LTM:** ~1-5MB vector database

### Response Times
- **Context Building:** <100ms
- **Message Processing:** <50ms
- **Search Operations:** <200ms

## 🔄 Memory Flow Examples

### Example 1: First Conversation
```
User: "Hi, I'm John"
↓
STM: Stores "Hi, I'm John"
MTM: Creates conversation, stores message
LTM: Extracts "personal_info: I'm John"
↓
Context: "Recent: Hi, I'm John" + "personal_info: I'm John"
↓
AI: "Hi John! Nice to meet you!"
```

### Example 2: Follow-up Conversation
```
User: "What do you remember about me?"
↓
STM: Recent conversation context
LTM: Retrieves "personal_info: I'm John"
↓
Context: "Recent conversation" + "personal_info: I'm John"
↓
AI: "I remember you're John!"
```

## 🛠️ Advanced Debugging

### Database Inspection
```bash
sqlite3 instance/amy_memory.db
.tables
SELECT * FROM conversations;
SELECT * FROM messages LIMIT 10;
```

### Vector Database Inspection
```bash
ls instance/vector_db/
cat instance/vector_db/personal_info_*.json
```

### Log Analysis
```bash
tail -f instance/amy_telegram_bot.log
```

## 🎉 Success Indicators

You'll know the memory system is working correctly when:

1. **Fact Extraction:** Personal information is being stored in LTM
2. **Context Building:** Relevant facts are included in AI responses
3. **Cross-Platform:** Conversations work across different platforms
4. **Persistence:** Information is retained between sessions
5. **Relevance:** Context is appropriate and not overwhelming

## 🚨 Troubleshooting

### Common Errors
- **Import Errors:** Make sure all dependencies are installed
- **Database Errors:** Check file permissions on `instance/` directory
- **Memory Errors:** Check available system memory
- **Log Errors:** Check log file for detailed error messages

### Getting Help
1. Run the test suite to identify issues
2. Use the debugger to inspect specific problems
3. Check the log files for error messages
4. Export debug logs for analysis

---

**Happy Debugging! 🧠✨**

The memory system is designed to be transparent and debuggable. Use these tools to understand exactly what's happening and why Amy responds the way she does. 
# Amy: Proactive Multimodal Digital Twin

## 🎯 Vision

Amy is your **Proactive Multimodal Digital Twin** - an intelligent entity that remembers you, adapts to context, and handles tasks across text and voice. She uses layered memory systems (Sensory, STM, EpTM, LTM) and is built atop Google ADK with Mem0, Telegram, and SQLite—scalable and future-proof for audio/video streaming.

## 🏗️ Architecture Overview

### **Four-Tier Memory System**

```text
[Telegram: text/voice] → [Web: text/voice] → [Future: video]
        ↓
Sensory Memory (ADK streaming + Whisper transcriptions)
        ↓
Short-Term Memory (ADK session buffer)
        ↓
Episodic Memory (epoch summaries + chunk embeddings in SQLite)
        ↓
Long-Term Memory (Mem0 vector/graph memory)
        ↑        ↓
   Memory Manager (promotion, pruning, aging, lineage)
        ↓
ADK Agent Runner (prompt builder using all layers + planner)
        ↓
Agent Response (voice/text back to Telegram)
        ↓
Archive Responses in SQLite; feed critical info to Mem0
```

### **Core Components**

- **Sensory Memory**: Handles live input via ADK (text + voice + future video)
- **STM**: Buffers current interaction context (~20 turns)
- **EpTM**: Summarizes chunks via LLM for middle-layer memory
- **LTM**: Mem0 stores distilled facts/preferences and retrieves them
- **Memory Manager**: Lifecycle control across layers
- **Agent Core**: ADK Runner orchestration with planning
- **Storage**: SQLite archives full transcripts and summary logs

## 🚀 Quick Start

### **Environment Setup**
```bash
# Clone and setup
git clone <repository>
cd the-amy-project

# Setup development environment
./tools/scripts/setup_dev.sh

# Setup agent logging
./tools/scripts/setup_git_hooks.sh
```

### **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Add your API keys
GEMINI_API_KEY=your_google_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
MEM0_API_KEY=your_mem0_api_key  # Coming soon
```

### **Running Amy**
```bash
# Telegram Bot (Recommended)
./runners/run_amy_bot.py

# Web Interface
./runners/run_web.py

# Debug Memory System
./tools/debug/debug_memory_system.py
```

## 🧠 Memory System

### **Sensory Memory**
- **Purpose**: Process audio/visual input and transcribe to text
- **Technology**: Whisper for audio transcription, future video processing
- **Integration**: Seamless flow into STM for immediate context

### **STM (Short-Term Memory)**
- **Purpose**: Immediate conversation context and recent message history
- **Storage**: In-memory buffer (20 messages per session)
- **Use Case**: Fast access to recent conversation for context building

### **EpTM (Episodic Memory)**
- **Purpose**: Summarized conversation chunks and semantic embeddings
- **Storage**: SQLite database with chunk summaries and embeddings
- **Use Case**: Middle-layer memory for conversation patterns and themes

### **LTM (Long-Term Memory)**
- **Purpose**: Semantic knowledge storage and fact extraction via Mem0
- **Storage**: Mem0 vector/graph database
- **Use Case**: Learning user preferences, relationships, and goals

### **Memory Manager**
- **Purpose**: Orchestrates all four memory systems
- **Features**: Unified interface for processing messages and building context
- **Advanced Features**: Memory promotion, pruning, aging, and lineage tracking

## 📊 Current Status

### **Phase 0: Foundation ✅**
- ✅ Complete three-tier memory system (STM, MTM, LTM)
- ✅ Telegram bot integration with persistent memory
- ✅ Cross-platform conversation storage
- ✅ Automatic fact extraction and learning
- ✅ Memory management and reset tools
- ✅ Comprehensive test suite
- ✅ Local persistent memory using SQLite
- ✅ Text-based interaction with `gemini-2.5-flash`

### **Phase 1: Multimodal Foundation 🚧**
- 🚧 Mem0 integration for LTM
- 🚧 Sensory memory layer (audio transcription)
- 🚧 Enhanced episodic memory with summarization
- 🚧 Basic planning capabilities

### **Phase 2: Voice & Advanced Memory 🎯**
- 🎯 Real-time voice interaction
- 🎯 Advanced memory management (promotion, pruning)
- 🎯 Task planning and multi-step workflows
- 🎯 Tool integration (weather, calendar, tasks)

### **Phase 3: Multimodal & Proactivity 🎯**
- 🎯 Video processing and analysis
- 🎯 Advanced proactivity and anticipation
- 🎯 Complex workflow orchestration
- 🎯 Emotional intelligence and adaptation

## 🛠️ Development Tools

### **Agent Logging System**
```bash
# Agent-specific commits
python3 tools/scripts/agent_commit.py claude "Added memory system features"
python3 tools/scripts/agent_commit.py gemini "Fixed web interface"
python3 tools/scripts/agent_commit.py user "Manual configuration changes"

# Manual agent logging
python3 tools/scripts/agent_logger.py --action=session_start --agent=claude --model=claude-3.5-sonnet
```

### **Debug Tools**
```bash
# Interactive memory debugging
./tools/debug/memory_debugger.py

# Real-time memory monitoring
./tools/debug/live_memory_monitor.py

# Memory flow visualization
./tools/debug/memory_flow_visualizer.py

# Complete memory demo
./tools/debug/memory_demo.py
```

### **Management Tools**
```bash
# Memory management
./tools/management/manage_memory.py

# Reset memory system
./tools/management/reset_amy_memory.py

# View conversation sessions
./tools/management/view_sessions.py
```

## 🧪 Testing

### **Comprehensive Test Suite**
```bash
# Run all tests
python3 test_suite.py

# Run specific tests
python3 -m pytest tests/
```

The test suite covers:
1. **STM Tests**: Message storage, retrieval, and session management
2. **MTM Tests**: Conversation storage, database operations
3. **LTM Tests**: Fact storage, retrieval, and search
4. **Memory Manager Tests**: Integration between all systems
5. **Telegram Integration Tests**: Bot conversation simulation
6. **Cross-Platform Tests**: Multi-platform session handling
7. **Memory Statistics Tests**: System health and metrics
8. **Search Tests**: Content search across all systems
9. **Context Building Tests**: AI response context generation

## 📋 Memory Commands

### **Telegram Bot Commands**
- `/help` - Show available commands
- `/memory` - Display memory statistics

### **Memory Statistics**
The `/memory` command shows:
- Active sessions in STM
- Total conversations in MTM
- Facts stored in LTM by type
- Cross-platform session counts

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Coming Soon
MEM0_API_KEY=your_mem0_api_key_here
```

### **Database Paths**
- **MTM Database**: `instance/amy_memory.db`
- **LTM Vector DB**: `instance/vector_db/` (will migrate to Mem0)
- **Logs**: `instance/amy_telegram_bot.log`

## 📁 Project Structure

```
amy/
├── core/amy_agent/          # Amy's core agent definition
├── features/memory/         # Memory system (STM, EpTM, LTM)
│   ├── sensory.py          # Sensory memory (audio/video processing)
│   ├── stm.py              # Short-term memory
│   ├── episodic.py         # Episodic memory (enhanced MTM)
│   ├── ltm.py              # Long-term memory (Mem0 integration)
│   └── memory_manager.py   # Unified memory manager
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

## 🚧 Known Issues

See `AMY_ISSUES.md` for a complete list of known issues and improvements needed. Key areas include:
- Context building optimization
- Memory command functionality
- Conversation flow improvements
- Mem0 integration (planned)
- Voice processing (planned)

## 📈 Roadmap

### **Phase 1: Multimodal Foundation (Current)**
**Goal**: Establish multimodal capabilities and enhanced memory systems.

**Key Features:**
1. **Mem0 Integration for LTM**:
   - Replace JSON-based LTM with Mem0 vector/graph memory
   - Implement semantic search and retrieval
   - Add memory promotion and pruning

2. **Sensory Memory Layer**:
   - Audio transcription with Whisper
   - Voice input handling in Telegram
   - Real-time audio processing pipeline

3. **Enhanced Episodic Memory**:
   - Add conversation summarization to MTM
   - Implement chunk embeddings
   - Create episodic memory manager

4. **Basic Planning**:
   - Simple task planner module
   - Multi-step task handling
   - Workflow orchestration

### **Phase 2: Voice & Advanced Memory**
**Goal**: Enable natural voice interaction and establish scalable memory systems.

**Key Features:**
1. **Real-time Voice Integration**:
   - Gemini Live API for voice input/output
   - Real-time audio streaming
   - Voice response generation

2. **Advanced Memory Management**:
   - Memory promotion and pruning algorithms
   - Aging and lineage tracking
   - Contextual memory retrieval

3. **Tool Integration**:
   - Weather API integration
   - Calendar API integration
   - Task management systems

### **Phase 3: Multimodal & Proactivity**
**Goal**: Amy becomes truly multimodal and highly anticipatory.

**Key Features:**
1. **Video Processing**:
   - ADK video streaming capabilities
   - Visual analysis and description
   - Multimodal context building

2. **Advanced Proactivity**:
   - Predictive analytics
   - Contextual triggers
   - Anticipatory assistance

3. **Complex Workflows**:
   - Multi-agent orchestration
   - Parallel task execution
   - Workflow automation

## 🤝 Contributing

This is a personal project, but feedback and suggestions are welcome! The codebase is designed to be extensible and well-documented.

## 📄 License

This project is for personal use and development.

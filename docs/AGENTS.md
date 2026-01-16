# Amy: Proactive Multimodal Digital Twin - Agent Instructions

## 🎯 Project Vision

Amy is your **Proactive Multimodal Digital Twin** - an intelligent entity that remembers you, adapts to context, and handles tasks across text and voice. She uses layered memory systems (Sensory, STM, EpTM, LTM) and is built atop Google ADK with Mem0, Telegram, and SQLite—scalable and future-proof for audio/video streaming.

## 🧠 Memory System Architecture

### Current Implementation: Four-Tier Memory System
- **Sensory Memory**: Audio/visual input processing and transcription (coming soon)
- **STM (Short-Term Memory)**: Immediate conversation context (20 messages)
- **EpTM (Episodic Memory)**: Summarized conversation chunks and embeddings (coming soon)
- **LTM (Long-Term Memory)**: Semantic knowledge and fact extraction via Mem0 (coming soon)

### Memory Flow
```text
Input (Text/Voice/Video) → Sensory Memory → STM → EpTM → LTM
                                    ↓
                              Memory Manager
                                    ↓
                              Context Building
                                    ↓
                              AI Response
```

## 🚀 Current Status: Phase 1 (Multimodal Foundation)

### ✅ Implemented Features
- Three-tier memory system (STM, MTM, LTM) - transitioning to four-tier
- Cross-platform support (Telegram, Web)
- Fact extraction and storage
- Context-aware response generation
- Memory commands (`/memory`, `/help`)
- Comprehensive debugging tools
- Health check and testing suite

### 🔄 In Progress (Phase 1)
- Mem0 integration for LTM
- Sensory memory layer (audio transcription)
- Enhanced episodic memory with summarization
- Basic planning capabilities

### 📋 Planned Features (Phase 2-3)
- Real-time voice interaction
- Advanced memory management (promotion, pruning)
- Tool integration (weather, calendar, tasks)
- Video processing capabilities
- Advanced proactivity and anticipation

## 🛠️ Development Guidelines

### Code Quality Standards
- **Testability**: All code must be easily testable
- **Documentation**: Update docs for any vision changes
- **Memory Consistency**: Ensure same memory behavior across platforms
- **Error Handling**: Comprehensive error handling and logging
- **Performance**: Optimize for response time and memory usage

### Memory System Requirements
- **Universal Recording**: Every conversation permanently stored
- **Cross-Platform Access**: Same memory across all interfaces
- **Complete Recall**: Access any conversation ever had
- **Intelligent Context**: Build relevant context based on current needs
- **Privacy-First**: Local storage with user control
- **Multimodal Ready**: Handle text, voice, and future video

### File Structure Conventions
```
amy/
├── core/amy_agent/          # Amy's core agent definition
├── features/memory/         # Memory system (Sensory, STM, EpTM, LTM)
│   ├── sensory.py          # Sensory memory (coming soon)
│   ├── stm.py              # Short-term memory
│   ├── episodic.py         # Episodic memory (coming soon)
│   ├── ltm.py              # Long-term memory (Mem0 integration)
│   └── memory_manager.py   # Unified memory manager
├── integrations/            # Platform integrations (telegram, web)
└── tools/                  # Development and debugging tools

docs/                       # Always update documentation
├── README.md              # Main project documentation
├── MEMORY_SYSTEM.md       # Memory system details
├── MULTIMODAL_ARCHITECTURE.md # Voice, video, and multimodal capabilities
├── AGENTS.md              # This file - agent instructions
└── AMY_ISSUES.md         # Known issues and solutions
```

## 🔧 Technical Implementation Notes

### Memory Manager Usage
```python
from app.features.memory import MemoryManager

# Initialize memory manager
memory_manager = MemoryManager()

# Process messages through all systems
memory_manager.process_message(
    session_id="session_id",
    platform="telegram|web|voice",
    role="user|model",
    content="message content",
    user_id="user_id",
    username="username"
)

# Get context for AI response
context = memory_manager.get_context_for_query(session_id, query)

# Get memory statistics
stats = memory_manager.get_memory_stats()
```

### Database Schema
- **EpTM**: SQLite database (`instance/amy_memory.db`) - coming soon
- **LTM**: Mem0 vector/graph database - coming soon
- **Logs**: `instance/amy_telegram_bot.log`

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
MEM0_API_KEY=your_mem0_api_key  # Coming soon
```

## 🎯 Vision Alignment Checklist

When implementing features, ensure they align with the **Proactive Multimodal Digital Twin** vision:

- [ ] **Anticipates needs** based on patterns and context
- [ ] **Optimizes time** through intelligent assistance
- [ ] **Enhances capabilities** across multiple domains
- [ ] **Learns and adapts** to user preferences
- [ ] **Maintains privacy** with local-first approach
- [ ] **Provides seamless** cross-platform experience
- [ ] **Handles multimodal** input (text, voice, future video)
- [ ] **Uses advanced memory** systems (Sensory, STM, EpTM, LTM)

## 🚨 Critical Notes for AI Agents

### Memory Consistency
- **NEVER** use different memory systems for different platforms
- **ALWAYS** use the `MemoryManager` for all memory operations
- **ENSURE** same memory behavior across Telegram and Web interfaces
- **PREPARE** for multimodal memory integration

### Documentation Updates
- **UPDATE** docs when vision changes occur
- **MAINTAIN** consistency between README.md and implementation
- **DOCUMENT** any new features or architectural changes
- **REFERENCE** the new multimodal architecture

### Testing Requirements
- **TEST** memory system thoroughly before deployment
- **VERIFY** cross-platform memory consistency
- **VALIDATE** fact extraction and context building
- **PREPARE** for multimodal testing

### Code Standards
- **FOLLOW** existing patterns in the codebase
- **MAINTAIN** testability of all new code
- **USE** comprehensive error handling
- **LOG** important operations for debugging
- **PREPARE** for Mem0 and multimodal integration

## 🔄 Development Workflow

1. **Understand Vision**: Read docs to understand Amy's purpose as a Multimodal Digital Twin
2. **Check Current State**: Review existing implementation and new architecture
3. **Plan Changes**: Ensure alignment with four-tier memory vision
4. **Implement**: Follow coding standards and prepare for multimodal
5. **Test**: Verify memory consistency and functionality
6. **Document**: Update relevant documentation
7. **Deploy**: Ensure cross-platform compatibility

## 📞 Communication Guidelines

- **Be specific** about vision changes and multimodal capabilities
- **Explain reasoning** for architectural decisions
- **Document trade-offs** when making choices
- **Maintain consistency** with existing patterns
- **Update docs** for any significant changes
- **Reference** the new multimodal architecture

---

**Remember**: Amy is a Proactive Multimodal Digital Twin, not just a chatbot. Every feature should contribute to her ability to anticipate, optimize, and enhance the user's life across multiple modalities.

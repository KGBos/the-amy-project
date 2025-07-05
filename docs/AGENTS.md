# Amy: Proactive Digital Twin - Agent Instructions

## 🎯 Project Vision

Amy is not merely a conversational AI; she is your **Proactive Digital Twin**, an intelligent entity deeply integrated into your life, anticipating needs, optimizing your time, and enhancing your capabilities across all domains. She operates with a profound understanding of your context, preferences, and goals, acting as your personal orchestrator of information and action.

## 🧠 Memory System Architecture

### Current Implementation: Tiered Memory System
- **STM (Short-Term Memory)**: Immediate conversation context (20 messages)
- **MTM (Medium-Term Memory)**: Permanent conversation storage (SQLite)
- **LTM (Long-Term Memory)**: Semantic knowledge and fact extraction (Vector DB)

### Memory Flow
1. **STM**: Immediate context for current conversation
2. **MTM**: Permanent storage of all conversations across all platforms
3. **LTM**: Intelligent context building based on conversation relevance

## 🚀 Current Status: Phase 0 (Foundation)

### ✅ Implemented Features
- Three-tier memory system (STM, MTM, LTM)
- Cross-platform support (Telegram, Web)
- Fact extraction and storage
- Context-aware response generation
- Memory commands (`/memory`, `/help`)
- Comprehensive debugging tools
- Health check and testing suite

### 🔄 In Progress
- Web interface memory consistency (Telegram vs Web)
- Enhanced fact extraction capabilities
- Memory visualization tools

### 📋 Planned Features
- Proactive behavior patterns
- Calendar and task integration
- Voice interface capabilities
- Advanced learning algorithms
- Autonomous action capabilities

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

### File Structure Conventions
```
app/
├── core/amy_agent/          # Amy's core agent definition
├── features/memory/         # Memory system (STM, MTM, LTM)
├── integrations/            # Platform integrations (telegram, web)
└── tools/                  # Development and debugging tools

docs/                       # Always update documentation
├── README.md              # Main project documentation
├── MEMORY_SYSTEM.md       # Memory system details
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
    platform="telegram|web",
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
- **MTM**: SQLite database (`instance/amy_memory.db`)
- **LTM**: Vector database (`instance/vector_db/`)
- **Logs**: `instance/amy_telegram_bot.log`

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

## 🎯 Vision Alignment Checklist

When implementing features, ensure they align with the **Proactive Digital Twin** vision:

- [ ] **Anticipates needs** based on patterns and context
- [ ] **Optimizes time** through intelligent assistance
- [ ] **Enhances capabilities** across multiple domains
- [ ] **Learns and adapts** to user preferences
- [ ] **Maintains privacy** with local-first approach
- [ ] **Provides seamless** cross-platform experience

## 🚨 Critical Notes for AI Agents

### Memory Consistency
- **NEVER** use different memory systems for different platforms
- **ALWAYS** use the `MemoryManager` for all memory operations
- **ENSURE** same memory behavior across Telegram and Web interfaces

### Documentation Updates
- **UPDATE** docs when vision changes occur
- **MAINTAIN** consistency between README.md and implementation
- **DOCUMENT** any new features or architectural changes

### Testing Requirements
- **TEST** memory system thoroughly before deployment
- **VERIFY** cross-platform memory consistency
- **VALIDATE** fact extraction and context building

### Code Standards
- **FOLLOW** existing patterns in the codebase
- **MAINTAIN** testability of all new code
- **USE** comprehensive error handling
- **LOG** important operations for debugging

## 🔄 Development Workflow

1. **Understand Vision**: Read docs to understand Amy's purpose
2. **Check Current State**: Review existing implementation
3. **Plan Changes**: Ensure alignment with vision
4. **Implement**: Follow coding standards
5. **Test**: Verify memory consistency and functionality
6. **Document**: Update relevant documentation
7. **Deploy**: Ensure cross-platform compatibility

## 📞 Communication Guidelines

- **Be specific** about vision changes
- **Explain reasoning** for architectural decisions
- **Document trade-offs** when making choices
- **Maintain consistency** with existing patterns
- **Update docs** for any significant changes

---

**Remember**: Amy is a Proactive Digital Twin, not just a chatbot. Every feature should contribute to her ability to anticipate, optimize, and enhance the user's life.

# Amy: The Proactive Digital Twin

## 🚀 Quick Start

```bash
# Setup development environment
./tools/scripts/setup_dev.sh

# Run Amy (Telegram Bot)
./runners/run_amy_bot.py

# Run Amy (Web Interface)
./runners/run_web.py

# Debug Memory System
./tools/debug/debug_memory_system.py
```

## 📁 Project Structure

```
the-amy-project/
├── 📁 app/                    # Core application
│   ├── core/amy_agent/       # Amy's core logic
│   ├── features/memory/      # Memory system (STM, MTM, LTM)
│   └── integrations/         # Platform integrations
├── 📁 tools/                 # Development & debugging tools
│   ├── debug/               # Memory debugging tools
│   ├── management/          # Memory management tools
│   └── scripts/             # Utility scripts
├── 📁 runners/              # Application launchers
├── 📁 docs/                 # Documentation
├── 📁 tests/                # Test files
├── 📁 instance/             # Data storage
└── 📁 logs/                 # Log files
```

## 📚 Documentation

- **[Main Documentation](docs/README.md)** - Complete setup and usage guide
- **[Memory System](docs/MEMORY_SYSTEM.md)** - Detailed memory architecture
- **[Debug Guide](docs/MEMORY_DEBUG_GUIDE.md)** - How to debug the memory system
- **[Known Issues](docs/AMY_ISSUES.md)** - Current issues and solutions
- **[API Integration](docs/GEMINI.md)** - Gemini API integration guide
- **[Security](docs/SECURITY.md)** - Security guidelines

## 🧠 Memory System

Amy implements a sophisticated three-tier memory system:

- **STM (Short-Term Memory)** - Immediate conversation context
- **MTM (Medium-Term Memory)** - Permanent conversation storage
- **LTM (Long-Term Memory)** - Semantic knowledge and facts

## 🛠️ Development Tools

### Debug Tools
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

### Management Tools
```bash
# Memory management
./tools/management/manage_memory.py

# Reset memory system
./tools/management/reset_amy_memory.py

# View conversation sessions
./tools/management/view_sessions.py
```

### Utility Scripts
```bash
# Health check
./tools/scripts/health_check.py

# Initialize database
./tools/scripts/init_db.py

# Setup development environment
./tools/scripts/setup_dev.sh
```

## 🧪 Testing

```bash
# Run comprehensive test suite
python3 test_suite.py

# Run specific tests
python3 -m pytest tests/
```

## 🚀 Running Amy

### Telegram Bot (Recommended)
```bash
./runners/run_amy_bot.py
```

### Web Interface
```bash
./runners/run_web.py
```

### Quick Start Scripts
```bash
./runners/start_telegram.sh
./runners/start_web.sh
```

## 📊 Memory Commands

- `/help` - Show available commands
- `/memory` - Display memory statistics

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Add your API keys:
   - `GEMINI_API_KEY` - Google AI Studio
   - `TELEGRAM_BOT_TOKEN` - BotFather

## 📈 Features

- **Proactive Digital Twin** - Intelligent personal assistant
- **Three-Tier Memory** - STM, MTM, LTM systems
- **Cross-Platform** - Telegram, Web, extensible
- **Fact Extraction** - Automatic learning from conversations
- **Context Building** - Intelligent response generation
- **Real-Time Debugging** - Comprehensive debugging tools

## 🎯 Vision

Amy is not merely a conversational AI; she is your **Proactive Digital Twin**, an intelligent entity deeply integrated into your life, anticipating needs, optimizing your time, and enhancing your capabilities across all domains.

---

**For detailed documentation, see the [docs/](docs/) directory.** 
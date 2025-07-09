# Amy Codebase Audit Plan

## 🎯 **Audit Objective**
Identify what files to **KEEP**, **TOSS**, or **SIMPLIFY** to create a clean foundation for building toward the Proactive Multimodal Digital Twin vision.

## 📋 **Audit Categories**

### **KEEP** - Essential files that work and are needed
### **TOSS** - Legacy files that are broken, unused, or aspirational
### **SIMPLIFY** - Files that work but are over-engineered
### **CONSOLIDATE** - Multiple files that do the same thing

---

## 🔍 **Root Directory Audit**

### **KEEP**
- `README.md` ✅ (Updated to reflect reality)
- `GOALS.md` ✅ (Our tracking system)
- `requirements.txt` ✅ (Core dependencies)
- `.gitignore` ✅ (Essential)
- `.cursorignore` ✅ (Development tool)

### **TOSS**
- `test_sensory_memory.py` ❌ (Tests broken sensory memory)
- `test_suite.py` ❌ (Tests features that don't work)
- `test_vector_db/` ❌ (Vector DB not implemented)

### **SIMPLIFY**
- `app/` - Over-engineered, needs simplification
- `tools/` - Too many tools for broken features
- `docs/` - Aspirational documentation
- `wiki/` - Duplicate documentation

---

## 🏗️ **Core Application (`app/`)**

### **KEEP**
- `app/integrations/telegram/bot.py` ✅ (Core functionality)
- `app/features/memory/stm.py` ✅ (Working STM)
- `app/features/memory/memory_manager.py` ✅ (Core orchestration)

### **TOSS**
- `app/core/amy_agent/agent.py` ❌ (ADK integration not working)
- `app/core/amy_agent/memory_service.py` ❌ (ADK integration not working)
- `app/features/memory/ltm.py` ❌ (JSON fallback, needs rewrite)
- `app/features/sensory/` ❌ (Audio processing not working)
- `app/features/weather_reporting/` ❌ (Not implemented)
- `app/features/time_management/` ❌ (Not implemented)
- `app/integrations/web/` ❌ (Web interface not working)
- `app/integrations/calendar/` ❌ (Not implemented)

### **SIMPLIFY**
- `app/features/memory/` - Remove TODO comments, implement working EpTM
- `app/features/memory/base.py` - Simplify base classes

---

## 🛠️ **Tools Directory (`tools/`)**

### **KEEP**
- `tools/scripts/setup_dev.sh` ✅ (Essential setup)
- `tools/scripts/agent_commit.py` ✅ (Useful for development)
- `tools/debug/memory_debugger.py` ✅ (Needed for debugging)
- `tools/management/reset_amy_memory.py` ✅ (Essential for testing)

### **TOSS**
- `tools/debug/memory_flow_visualizer.py` ❌ (Visualizes broken system)
- `tools/debug/live_memory_monitor.py` ❌ (Monitors broken system)
- `tools/debug/memory_demo.py` ❌ (Demo of broken features)
- `tools/management/manage_memory.py` ❌ (Manages broken system)
- `tools/management/view_sessions.py` ❌ (Views broken sessions)

### **SIMPLIFY**
- `tools/debug/` - Keep only essential debugging tools
- `tools/management/` - Keep only essential management tools

---

## 📚 **Documentation Audit**

### **KEEP**
- `docs/README.md` ✅ (Main documentation)
- `docs/GEMINI.md` ✅ (API integration guide)
- `docs/SECURITY.md` ✅ (Security guidelines)

### **TOSS**
- `docs/AMY_ISSUES.md` ❌ (User said it's trash)
- `docs/MEMORY_SYSTEM.md` ❌ (Documents broken system)
- `docs/MULTIMODAL_ARCHITECTURE.md` ❌ (Aspirational)
- `docs/MEMORY_DEBUG_GUIDE.md` ❌ (Debug guide for broken system)

### **SIMPLIFY**
- `docs/AGENTS.md` - Update to reflect actual capabilities

### **ENTIRE WIKI** ❌
- All wiki files are aspirational and don't match reality
- Duplicate documentation in multiple places
- Remove entire `wiki/` directory

---

## 🧪 **Testing Audit**

### **TOSS**
- `tests/` directory ❌ (Tests broken features)
- `test_suite.py` ❌ (Tests broken system)
- `test_sensory_memory.py` ❌ (Tests broken sensory memory)

### **SIMPLIFY**
- Create new, simple tests for what actually works
- Focus on core functionality tests

---

## 🚀 **Runners Audit**

### **KEEP**
- `runners/run_amy_bot.py` ✅ (Core Telegram bot)
- `runners/start_telegram.sh` ✅ (Essential startup script)

### **TOSS**
- `runners/run_web.py` ❌ (Web interface not working)
- `runners/start_web.sh` ❌ (Web interface not working)

---

## 📁 **Directory Audit**

### **KEEP**
- `instance/` ✅ (Data storage)
- `logs/` ✅ (Log files)
- `venv/` ✅ (Virtual environment)

### **TOSS**
- `agent_logs/` ❌ (Legacy logging)
- `test_vector_db/` ❌ (Vector DB not implemented)
- `.githooks/` ❌ (Complex git hooks)

---

## 🎯 **Simplified Structure Plan**

### **Target Structure**
```
the-amy-project/
├── README.md                    # Honest current status
├── GOALS.md                     # Our tracking system
├── requirements.txt             # Core dependencies
├── app/
│   ├── integrations/
│   │   └── telegram/
│   │       └── bot.py          # Core Telegram bot
│   │   └── features/
│   │       └── memory/
│   │           ├── stm.py          # Working STM
│   │           └── memory_manager.py # Core orchestration
│   └── tools/
│       ├── scripts/
│       │   └── setup_dev.sh       # Essential setup
│       └── debug/
│           └── memory_debugger.py # Essential debugging
├── runners/
│   ├── run_amy_bot.py         # Core runner
│   └── start_telegram.sh      # Startup script
├── docs/
│   ├── README.md              # Main documentation
│   ├── GEMINI.md              # API guide
│   └── SECURITY.md            # Security guide
├── instance/                   # Data storage
└── logs/                      # Log files
```

---

## 🚨 **Immediate Action Plan**

### **Phase 1: Remove Broken Files**
1. Delete entire `wiki/` directory
2. Delete `test_sensory_memory.py`
3. Delete `test_suite.py`
4. Delete `test_vector_db/` directory
5. Delete `app/core/` directory (ADK not working)
6. Delete `app/features/sensory/` directory
7. Delete `app/features/weather_reporting/` directory
8. Delete `app/features/time_management/` directory
9. Delete `app/integrations/web/` directory
10. Delete `app/integrations/calendar/` directory

### **Phase 2: Simplify Core Files**
1. Simplify `app/features/memory/ltm.py` (remove JSON fallback)
2. Simplify `app/features/memory/memory_manager.py` (remove TODO comments)
3. Simplify `tools/debug/` (keep only essential tools)
4. Simplify `tools/management/` (keep only essential tools)

### **Phase 3: Update Documentation**
1. Update `docs/README.md` to reflect actual capabilities
2. Remove aspirational features from all docs
3. Create simple, accurate documentation

### **Phase 4: Create New Tests**
1. Create simple tests for what actually works
2. Focus on core functionality testing
3. Remove tests for broken features

---

## 📊 **Expected Results**

### **Before Audit**
- **Files**: ~50+ files
- **Directories**: 15+ directories
- **Documentation**: 15+ files (duplicate/aspirational)
- **Complexity**: High (broken features everywhere)

### **After Audit**
- **Files**: ~20 files
- **Directories**: 8 directories
- **Documentation**: 3 files (accurate)
- **Complexity**: Low (only working features)

---

## 🎯 **Success Criteria**

- [ ] Removed all broken/aspirational files
- [ ] Simplified core functionality
- [ ] Accurate documentation
- [ ] Clean, maintainable codebase
- [ ] Ready for Phase 1 fixes

---

**Next Step**: Execute Phase 1 (Remove Broken Files) to create a clean foundation. 
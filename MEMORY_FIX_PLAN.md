# Memory System Fix Plan

## 🎯 **Current Memory Issues (From Logs)**

### **Critical Problems**
1. **Context Pollution**: 261 → 469 → 1015 characters (unlimited growth)
2. **Fact Duplication**: 5x "my name is Leon" entries in LTM
3. **"Hi again!" Bug**: Greets new users like old friends
4. **Broken LTM**: Using JSON fallback instead of proper storage
5. **Missing EpTM**: Episodic Memory completely unimplemented

### **What's Actually Working**
- ✅ STM (Short-Term Memory) - Basic conversation buffer
- ✅ Basic fact extraction - Extracts facts from user messages
- ✅ Memory manager orchestration - Routes messages through systems

---

## 🏗️ **Current Memory Architecture**

```
User Message → Memory Manager → STM + LTM (JSON fallback)
     ↓
Context Building → Polluted Context (1000+ chars)
     ↓
AI Response → More context pollution
```

### **Problems with Current Flow**
1. **No context limits** - Context grows indefinitely
2. **No fact deduplication** - Stores same facts multiple times
3. **No relevance scoring** - Includes irrelevant historical data
4. **No session boundaries** - Can't distinguish new vs. old users
5. **No EpTM layer** - Missing middle-tier memory

---

## 🎯 **Target Memory Architecture**

```
User Message → Memory Manager → STM + EpTM + LTM
     ↓
Smart Context Building → Relevant Context (< 500 chars)
     ↓
AI Response → Clean, contextual responses
```

### **Key Improvements**
1. **Context limits** - Max 500 characters
2. **Fact deduplication** - Check before storing
3. **Relevance scoring** - Only include relevant context
4. **Session boundaries** - Proper new user detection
5. **Working EpTM** - Conversation summarization

---

## 🚨 **Phase 1: Critical Fixes (This Week)**

### **1. Fix Context Building (Priority #1)**
**Problem**: Context grows to 1000+ characters with irrelevant info
**Solution**: Implement smart context building with limits

```python
class SmartContextBuilder:
    def __init__(self, max_length: int = 500):
        self.max_length = max_length
    
    def build_context(self, session_id: str, query: str) -> str:
        # Get recent STM context (last 5 messages)
        stm_context = self.get_stm_context(session_id, limit=5)
        
        # Get relevant LTM facts (max 3 facts)
        ltm_context = self.get_relevant_ltm_facts(query, limit=3)
        
        # Combine and truncate to max_length
        combined = f"{stm_context}\n{ltm_context}"
        return self.truncate_context(combined, self.max_length)
```

**Success Criteria**: Context length < 500 chars, relevant content only

### **2. Add Fact Deduplication (Priority #2)**
**Problem**: Stores 5x "my name is Leon" entries
**Solution**: Check existing facts before storing

```python
class DeduplicatedLTM:
    def store_fact(self, fact_content: str, fact_type: str, user_id: str) -> bool:
        # Check if fact already exists
        existing_facts = self.search_facts(fact_content, fact_type, user_id)
        if existing_facts:
            return False  # Don't store duplicate
        
        # Store new fact
        return self._store_new_fact(fact_content, fact_type, user_id)
```

**Success Criteria**: Zero duplicate facts in LTM

### **3. Fix Greeting Logic (Priority #3)**
**Problem**: "Hi again!" to new users
**Solution**: Proper new user detection

```python
class UserSessionManager:
    def is_new_user(self, user_id: str) -> bool:
        # Check if user has previous conversations
        previous_sessions = self.get_user_sessions(user_id)
        return len(previous_sessions) == 0
    
    def get_greeting(self, user_id: str) -> str:
        if self.is_new_user(user_id):
            return "Hi! I'm Amy, your AI assistant. How can I help you today?"
        else:
            return "Hi again! How can I help you today?"
```

**Success Criteria**: Proper greeting for new vs. returning users

### **4. Clean Up LTM (Priority #4)**
**Problem**: JSON fallback with duplicates
**Solution**: Remove duplicates and implement proper storage

```python
class CleanLTM:
    def cleanup_duplicates(self):
        # Remove duplicate facts
        facts = self.get_all_facts()
        unique_facts = self.deduplicate_facts(facts)
        self.replace_all_facts(unique_facts)
    
    def implement_proper_storage(self):
        # Replace JSON with proper vector storage
        # (Simplified version for now)
        pass
```

**Success Criteria**: Clean LTM with no duplicates

### **5. Add Basic Monitoring (Priority #5)**
**Problem**: No visibility into memory performance
**Solution**: Track key metrics

```python
class MemoryMonitor:
    def track_context_length(self, context: str) -> int:
        length = len(context)
        if length > 500:
            logger.warning(f"Context too long: {length} chars")
        return length
    
    def track_fact_storage(self, fact: str, success: bool):
        if not success:
            logger.info(f"Duplicate fact not stored: {fact[:50]}...")
```

**Success Criteria**: Monitor context length, fact storage, error rates

---

## 🚀 **Phase 2: Implement Missing Features (Next Week)**

### **1. Implement Episodic Memory**
**Current**: TODO comments only
**Target**: Working conversation summarization

```python
class EpisodicMemory:
    def __init__(self):
        self.summarizer = LLMSummarizer()
    
    def summarize_conversation(self, session_id: str) -> str:
        # Get conversation messages
        messages = self.get_session_messages(session_id)
        
        # Generate summary
        summary = self.summarizer.summarize(messages)
        
        # Store summary
        self.store_summary(session_id, summary)
        return summary
```

### **2. Implement Proper LTM**
**Current**: JSON fallback
**Target**: Vector storage with semantic search

```python
class VectorLTM:
    def __init__(self):
        self.vector_store = ChromaDB()  # Or similar
    
    def store_fact(self, fact: str, fact_type: str, user_id: str):
        # Create embedding
        embedding = self.create_embedding(fact)
        
        # Store with metadata
        self.vector_store.add(
            documents=[fact],
            embeddings=[embedding],
            metadatas=[{"type": fact_type, "user_id": user_id}]
        )
```

### **3. Add Relevance Scoring**
**Current**: No relevance filtering
**Target**: Smart context selection

```python
class RelevanceScorer:
    def score_context_relevance(self, context: str, query: str) -> float:
        # Simple keyword matching for now
        query_words = set(query.lower().split())
        context_words = set(context.lower().split())
        
        overlap = len(query_words.intersection(context_words))
        return overlap / len(query_words) if query_words else 0.0
```

---

## 📊 **Success Metrics**

### **Phase 1 Success Criteria**
- [ ] Context length < 500 characters consistently
- [ ] Zero duplicate facts in LTM
- [ ] Proper greeting for new users
- [ ] Error rate < 1%
- [ ] Response time < 2 seconds

### **Phase 2 Success Criteria**
- [ ] Working Episodic Memory with summarization
- [ ] Proper vector storage for LTM
- [ ] Smart context relevance scoring
- [ ] Memory system performance monitoring
- [ ] Clean, maintainable memory code

---

## 🛠️ **Implementation Order**

### **Week 1: Critical Fixes**
1. **Day 1-2**: Fix context building (500 char limit)
2. **Day 3**: Add fact deduplication
3. **Day 4**: Fix greeting logic
4. **Day 5**: Clean up LTM and add monitoring

### **Week 2: Missing Features**
1. **Day 1-2**: Implement Episodic Memory
2. **Day 3-4**: Implement proper LTM storage
3. **Day 5**: Add relevance scoring and testing

---

## 🎯 **Expected Results**

### **Before Fixes**
- Context: 1000+ characters with irrelevant info
- Facts: 5x duplicates in LTM
- Greeting: "Hi again!" to new users
- Performance: Unknown error rates
- Architecture: 2-tier (STM + broken LTM)

### **After Fixes**
- Context: < 500 characters, relevant only
- Facts: Zero duplicates, clean storage
- Greeting: Proper new user detection
- Performance: Monitored and optimized
- Architecture: 3-tier (STM + EpTM + LTM)

---

**Next Step**: Start with Priority #1 - Fix context building by implementing the 500 character limit and relevance scoring. 
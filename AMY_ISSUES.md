# Amy Memory System Issues

## 🔍 **Issues Identified from User Dialogue**

### 1. **"Hi again!" Greeting Problem**
- **Issue**: Amy says "Hi again!" when user first says "hi" - acting like they've talked before
- **Expected**: Should be a fresh greeting since memory was reset
- **Root Cause**: Memory system still pulling old context or STM not properly cleared

### 2. **Memory Command Confusion**
- **Issue**: When user asks about `/memory` command usage, Amy says they've used it once, but they haven't actually used the command
- **Problem**: Amy confuses asking *about* the command with actually *using* the command
- **Example**: User asks "what about when i write /memory" → Amy counts this as using the command

### 3. **Context Length Problems**
- **Issue**: Context getting very long (1462 characters) and may include irrelevant old conversation
- **Problem**: Memory system isn't properly filtering or limiting context relevance
- **Impact**: Amy gives overly detailed responses assuming more context than exists

### 4. **Missing Memory Statistics**
- **Issue**: User mentioned `/memory` but actual memory statistics response not shown in logs
- **Problem**: Either the command wasn't processed or the response isn't being logged
- **Need**: Verify `/memory` command functionality

### 5. **Inconsistent Memory Recognition**
- **Issue**: Amy gives mixed signals about whether she remembers the user
- **Problem**: Sometimes acts like fresh start, sometimes like continuing conversation
- **Example**: Says "I don't believe you've told me your name yet" but then says "Hi again!"

### 6. **Conversation Flow Issues**
- **Issue**: Amy gives very long, detailed responses that seem to assume more context than exists
- **Problem**: Context building might be including too much irrelevant information
- **Impact**: Responses feel overly verbose for simple questions

## ✅ **What's Working Correctly**

### Fact Extraction
- **Positive**: Amy correctly extracted and stored "my name is Leon" as personal_info
- **Positive**: Amy correctly extracted and stored "i live in Salem, OR" as personal_info
- **Status**: LTM fact extraction is working as intended

### Memory Reset
- **Positive**: No more "Sarah" test data appearing in responses
- **Status**: Complete memory reset was successful

## 🎯 **Priority Issues to Address**

1. **"Hi again!" greeting** - Critical UX issue
2. **Memory command confusion** - Functionality issue
3. **Context length and relevance** - Performance/UX issue
4. **Missing memory statistics** - Debugging needed

## 📝 **Notes**

- Issues identified from dialogue on 2025-07-05
- Memory system is functional but needs refinement
- Fact extraction and storage working correctly
- Need to focus on context building and conversation flow 
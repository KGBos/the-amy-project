# Changelog

All notable changes to the Amy project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Episodic Memory System**: Complete SQLite-based implementation for conversation storage
- **Smart Context Builder**: 500-character limit with intelligent truncation
- **Fact Deduplication**: Prevents duplicate facts in Long-Term Memory
- **User Session Management**: Proper greeting logic for new vs returning users
- **Memory Statistics**: Comprehensive memory system monitoring
- **Database Schema**: Proper ADK-compatible schema for Episodic Memory
- **Comprehensive Prompt Logging**: Complete visibility into what Amy sees
  - Full system prompt logging
  - Complete context display
  - User message logging
  - Total prompt length tracking
  - Debug command (/debug) for real-time prompt inspection
  - Memory state visualization
  - Detailed memory statistics in debug output

### Fixed
- **Episodic Memory Database Schema**: Fixed column mismatch between code and database
  - Changed from `session_id` to `conversation_id` in messages table
  - Updated to use `conversations` table instead of `sessions` table
  - Added proper foreign key relationships
- **Context Pollution**: Implemented 500-character hard limit with truncation logging
- **Fact Duplication**: Added duplicate checking before storing facts in LTM
- **"Hi again!" Bug**: Fixed greeting logic to properly distinguish new vs returning users
- **Memory System Integration**: All three tiers (STM, EpTM, LTM) now working together
- **Session Creation Logic**: Fixed duplicate session creation for every message
  - Now only creates session on first message of conversation
  - Prevents unnecessary database operations
- **Context Building Logic**: Fixed context pollution and relevance issues
  - Implemented smart context building with priority system
  - Added relevance scoring for LTM facts
  - Improved truncation logic to preserve meaning
  - Limited context to 500 characters with intelligent space allocation
- **LTM Search Logic**: Completely rewrote fact search for better relevance
  - Added relevance scoring system (exact matches, term matches, user-specific priority)
  - Implemented minimum relevance threshold (30 points)
  - Added intelligent fact filtering by user and type
  - Reduced irrelevant fact inclusion in context
- **Fact Deduplication**: Enhanced duplicate detection
  - Added similarity-based deduplication for general facts (80% threshold)
  - Improved name matching for personal_info facts
  - Added content cleaning for better comparison
  - Prevents near-duplicate facts from being stored
- **Session Management**: Fixed user session detection logic
  - Corrected new vs returning user detection
  - Fixed session boundary logic
  - Improved greeting system accuracy

### Changed
- **Memory Architecture**: Simplified from 4-tier to 3-tier system
  - Removed broken/unimplemented features
  - Consolidated storage (SQLite for EpTM, JSON for LTM)
  - Streamlined context building process
- **Documentation**: Updated README.md and MEMORY_SYSTEM.md to reflect actual capabilities
- **Code Cleanup**: Removed unused files and simplified imports

### Removed
- **Legacy Files**: Removed broken/unimplemented features
- **Aspirational Content**: Removed claims about unimplemented features from documentation
- **Complex Orchestration**: Simplified memory management architecture

## [0.1.0] - 2025-07-06

### Added
- **Basic Chatbot**: Initial Telegram bot implementation
- **Memory System Foundation**: Basic STM and LTM implementation
- **Fact Extraction**: Simple fact extraction from user messages
- **Context Building**: Basic context assembly for AI responses

### Known Issues
- Context pollution (unlimited growth)
- Fact duplication in LTM
- "Hi again!" greeting bug
- Missing Episodic Memory implementation
- Database schema mismatches

---

## Version History

- **0.1.0**: Initial basic chatbot with memory issues
- **Unreleased**: Major fixes and improvements (current)

## Migration Guide

### From 0.1.0 to Unreleased

#### Database Changes
The Episodic Memory database schema has been updated to use the correct ADK schema:
- Messages now use `conversation_id` instead of `session_id`
- Sessions are stored in `conversations` table with proper foreign keys
- Added database indexes for improved performance

#### Memory System Changes
- Context is now limited to 500 characters with intelligent truncation
- Facts are deduplicated before storage
- User sessions are properly tracked for greeting logic
- All three memory tiers (STM, EpTM, LTM) are functional

#### Breaking Changes
- Database schema changes require fresh database or migration
- Memory system API has been simplified
- Some legacy features have been removed

## Contributing

When adding entries to this changelog, please follow these guidelines:

1. **Added**: New features
2. **Changed**: Changes in existing functionality
3. **Deprecated**: Soon-to-be removed features
4. **Removed**: Removed features
5. **Fixed**: Bug fixes
6. **Security**: Vulnerability fixes

Use clear, concise language and include relevant issue numbers when applicable. 
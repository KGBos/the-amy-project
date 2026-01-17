"""
Centralized configuration for The Amy Project.
All constants, model names, and configurable values in one place.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# API Configuration
# =============================================================================

# API Keys (from environment)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# =============================================================================
# Model Configuration
# =============================================================================

# Default model used across all components (Agent, Bot, LTM)
DEFAULT_MODEL = "gemini-2.0-flash-001"

# Model configuration for content generation
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.8
DEFAULT_TOP_K = 40
DEFAULT_MAX_OUTPUT_TOKENS = 1024

# LTM-specific model settings (lower temperature for factual recall)
LTM_TEMPERATURE = 0.1

# Embedder configuration (for LTM vector search)
EMBEDDER_MODEL = "all-MiniLM-L6-v2"

# =============================================================================
# Memory System Configuration
# =============================================================================

# Database paths
DEFAULT_DB_PATH = "instance/amy_memory.db"
DEFAULT_VECTOR_DB_PATH = "instance/mem0_storage"

# Context limits
MAX_CONTEXT_LENGTH = 500

# Short-Term Memory settings
STM_MAX_MESSAGES = 20

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_DIRECTORY = "agent_logs"
TELEGRAM_LOG_FILE = "instance/amy_telegram_bot.log"

# =============================================================================
# System Prompts
# =============================================================================

SYSTEM_PROMPT = (
    "You are Amy, a helpful and friendly AI assistant with memory. "
    "You can remember past conversations and learn about users over time.\n\n"
    "IMPORTANT - Memory Management:\n"
    "- When users share important personal information (name, preferences, facts about themselves), "
    "use the 'save_memory' tool to store it for future conversations.\n"
    "- Before answering questions about the user, use the 'search_memory' tool to check if you have relevant stored information.\n"
    "- Always keep track of important details to provide a personalized experience.\n\n"
    "Respond directly to the user's message in a conversational way, "
    "using context from previous conversations when relevant."
)

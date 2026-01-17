"""
Prompt building utilities for Amy.
Provides consistent prompt construction across all interfaces (ADK, Telegram, Web).
"""

from typing import Optional
from amy.config import SYSTEM_PROMPT


class AmyPromptBuilder:
    """
    Builds prompts for Amy consistently across all interfaces.
    """
    
    @staticmethod
    def build_full_prompt(
        user_message: str,
        context: str = "",
        greeting_context: str = ""
    ) -> str:
        """
        Build the complete prompt for Amy.
        
        Args:
            user_message: The user's message
            context: Memory context (from MemoryManager)
            greeting_context: Optional greeting context for new users
            
        Returns:
            Complete prompt string ready for the model
        """
        prompt_parts = [SYSTEM_PROMPT]
        
        if greeting_context:
            prompt_parts.append(greeting_context)
        
        if context:
            prompt_parts.append(f"\n{context}")
        
        prompt_parts.append(f"\nUser: {user_message}")
        prompt_parts.append("Amy:")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_greeting_context(greeting: str) -> str:
        """
        Build greeting context for new users.
        
        Args:
            greeting: The greeting message
            
        Returns:
            Formatted greeting context
        """
        return f"\n[INSTRUCTION: This is a BRAND NEW user you have NEVER spoken to before. Your first word MUST start with 'Hi!' followed by introducing yourself. DO NOT say 'Hi again'.]"
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Get the standard system prompt.
        
        Returns:
            The system prompt string
        """
        return SYSTEM_PROMPT

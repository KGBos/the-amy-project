"""
Smart Context Builder for Amy
Builds context with length limits and relevance scoring
"""

from typing import Dict, List
import logging

from amy.config import MAX_CONTEXT_LENGTH

logger = logging.getLogger(__name__)


class SmartContextBuilder:
    """
    Smart context builder with length limits and relevance scoring.
    """
    
    def __init__(self, max_length: int = None):
        self.max_length = max_length or MAX_CONTEXT_LENGTH
    
    def build_context(self, stm_context: List[Dict], ltm_context: str, query: str, episodic_context: str = "") -> str:
        """
        Build smart context with length limits and relevance scoring.
        
        Args:
            stm_context: Recent conversation messages
            ltm_context: Relevant facts from LTM
            query: User's current query
            episodic_context: Episodic context for the query
            
        Returns:
            Truncated, relevant context string (max 500 characters)
        """
        context_parts = []
        available_space = self.max_length
        
        # Add recent conversation (last 3 messages max) - Priority 1
        if stm_context:
            recent_section = ["Recent conversation:"]
            recent_messages = stm_context[-3:]  # Limit to last 3 messages
            for msg in recent_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                recent_section.append(f"{role}: {content}")
            
            recent_text = "\n".join(recent_section)
            if len(recent_text) <= available_space:
                context_parts.append(recent_text)
                available_space -= len(recent_text) + 1  # +1 for newline
            else:
                # Truncate recent conversation if needed
                truncated_recent = self._truncate_text(recent_text, available_space)
                context_parts.append(truncated_recent)
                available_space = 0
        
        # Add relevant LTM facts (if any and if space allows) - Priority 2
        if ltm_context and available_space > 50:
            # Only include LTM if it's highly relevant and we have space
            if len(ltm_context) <= available_space:
                context_parts.append(ltm_context)
                available_space -= len(ltm_context) + 1
            else:
                # Truncate LTM context if needed
                truncated_ltm = self._truncate_text(ltm_context, available_space)
                if truncated_ltm:
                    context_parts.append(truncated_ltm)
                    available_space = 0
        
        # Add episodic context (if any and if space allows) - Priority 3
        if episodic_context and available_space > 50:
            if len(episodic_context) <= available_space:
                context_parts.append(episodic_context)
            else:
                # Truncate episodic context if needed
                truncated_episodic = self._truncate_text(episodic_context, available_space)
                if truncated_episodic:
                    context_parts.append(truncated_episodic)
        
        # Combine all parts
        combined = "\n\n".join(context_parts)
        return self._truncate_context(combined, self.max_length)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to fit within max_length while preserving meaning.
        
        Args:
            text: Text to truncate
            max_length: Maximum allowed length
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
            
        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_length:
                truncated += sentence + '. '
            else:
                break
                
        if truncated:
            return truncated.strip()
            
        # If no sentences fit, truncate at word boundaries
        words = text.split()
        truncated = ""
        
        for word in words:
            if len(truncated + word + ' ') <= max_length:
                truncated += word + ' '
            else:
                break
                
        return truncated.strip() + "..."
    
    def _truncate_context(self, context: str, max_length: int) -> str:
        """
        Truncate context to max length while preserving structure.
        
        Args:
            context: Full context string
            max_length: Maximum allowed length
            
        Returns:
            Truncated context string
        """
        if len(context) <= max_length:
            return context
        
        # If context is too long, prioritize recent conversation
        lines = context.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 <= max_length:
                truncated_lines.append(line)
                current_length += len(line) + 1
            else:
                break
        
        result = '\n'.join(truncated_lines)
        
        # Log if we had to truncate
        if len(context) > max_length:
            logger.warning(f"Context truncated from {len(context)} to {len(result)} characters")
        
        return result

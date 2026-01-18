"""
Safety Callbacks for Amy
Intercepts messages before they reach the model to prevent unsafe queries.
"""
import logging
from typing import Optional, List, Union, Awaitable

# Correct ADK imports for 1.22+
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext

logger = logging.getLogger(__name__)

class SafetyCallback:
    """
    A callable callback that checks user input for unsafe keywords.
    """
    
    def __init__(self, blocked_words: List[str] = None):
        self.blocked_words = blocked_words or ["sudo rm -rf", "drop table", "system32"]
        
    async def __call__(self, callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """
        Called before the request is sent to the LLM.
        """
        if not llm_request.messages or not isinstance(llm_request.messages, list):
            return None
            
        # Extract text from the last turn
        last_turn = llm_request.messages[-1]
        content_text = ""
        
        # Use ADK native property access if available, else fallback
        if hasattr(last_turn, 'parts') and last_turn.parts:
            for part in last_turn.parts:
                if hasattr(part, 'text') and part.text:
                    content_text += part.text
        elif hasattr(last_turn, 'text') and last_turn.text:
            content_text = last_turn.text
        else:
            # Last resort: str conversion
            content_text = str(last_turn)
            
        if not content_text:
            return None
            
        for word in self.blocked_words:
            if word.lower() in content_text.lower():
                logger.warning(f"Safety Guardrail triggered: Blocked '{word}'")
                return LlmResponse(
                    text=f"I cannot fulfill this request because it contains unsafe content ('{word}').",
                    raw_response={"blocked": True}
                )
        
        return None

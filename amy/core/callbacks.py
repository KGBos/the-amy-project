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
        Signature matches _SingleBeforeModelCallback: (CallbackContext, LlmRequest)
        """
        if not llm_request.messages:
            return None
            
        # Check the last user message
        # llm_request.messages is list of Content or Part
        # We need to extract text.
        
        last_message = llm_request.messages[-1]
        
        # Simple text extraction for safety check
        # This depends on structure of 'last_message' (usually Content object)
        content_text = ""
        if hasattr(last_message, 'parts'):
             for part in last_message.parts:
                 if hasattr(part, 'text') and part.text:
                     content_text += part.text
        elif hasattr(last_message, 'content'):
            content_text = str(last_message.content)
        else:
            content_text = str(last_message)
            
        for word in self.blocked_words:
            if word in content_text.lower():
                logger.warning(f"Safety Guardrail triggered: Blocked '{word}'")
                return LlmResponse(
                    text=f"I cannot fulfill this request because it contains unsafe content ('{word}').",
                    raw_response={"blocked": True}
                )
        
        return None

"""
Plugins for Amy
Native ADK Runner Plugins for cross-cutting concerns.
"""

import logging
from typing import Optional, List, Any, Dict
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

logger = logging.getLogger(__name__)

class SafetyPlugin(BasePlugin):
    """
    Runner-level safety filter that blocks sensitive keywords globally.
    Replaces the legacy SafetyCallback for better coverage across all agents.
    """
    
    def __init__(self, blocked_words: Optional[List[str]] = None):
        super().__init__(name="safety_plugin")
        self.blocked_words = blocked_words or [
            "password", "secret_key", "private_key", "api_key",
            "malware", "exploit", "hack", "bypass"
        ]

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """
        Check user input for blocked words before sending to the model.
        Applying this at the Runner level ensures all agents are protected.
        """
        if not llm_request.contents:
            return None
            
        # Extract text from the latest content
        last_turn = llm_request.contents[-1]
        content_text = ""
        
        if hasattr(last_turn, 'parts') and last_turn.parts:
            for part in last_turn.parts:
                if hasattr(part, 'text') and part.text:
                    content_text += part.text
        elif hasattr(last_turn, 'text') and last_turn.text:
            content_text = last_turn.text
        else:
            content_text = str(last_turn)
            
        if not content_text:
            return None
            
        for word in self.blocked_words:
            if word.lower() in content_text.lower():
                logger.warning(f"Safety Plugin triggered: Blocked '{word}'")
                
                # Construct proper LlmResponse
                content = types.Content(
                    role="model",
                    parts=[types.Part(text=f"I cannot fulfill this request because it contains unsafe content ('{word}').")]
                )
                
                return LlmResponse(
                    content=content,
                    custom_metadata={"blocked": True, "source": "SafetyPlugin"}
                )
        
        return None

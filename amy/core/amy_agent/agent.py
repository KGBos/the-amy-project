"""
Core Agent definition for Amy.
This agent acts as the brain, orchestrating memory and response generation.
"""

import os
from typing import AsyncGenerator, Optional

import google.generativeai as genai
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai.types import Content, Part

from amy.features.memory import MemoryManager
from amy.core.agent_logger import setup_agent_logger

logger = setup_agent_logger(__name__)

class AmyAgent(BaseAgent):
    """
    Amy's brain. Uses MemoryManager to provide context-aware responses.
    """
    memory_manager: Optional[MemoryManager] = None
    model: Optional[genai.GenerativeModel] = None

    def __init__(self, name: str = "Amy", memory_manager: Optional[MemoryManager] = None):
        super().__init__(name=name)
        self.memory_manager = memory_manager or MemoryManager()
        
        # Initialize the Gemini model
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.warning("No API KEY found for Gemini. Agent may fail to generate responses.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Processes a user message and returns a streamed response.
        """
        user_id = ctx.user_id
        session_id = ctx.session.id
        message = ctx.user_content
        
        # Fallback: Check if there are events in the session if message is None
        if message is None and ctx.session.events:
             user_events = [e for e in ctx.session.events if e.author == 'user' and e.content]
             if user_events:
                 message = user_events[-1].content
        
        if message is None or not message.parts:
            yield Event(author=self.name, content=Content(parts=[Part(text="I'm sorry, I didn't receive any message.")]))
            return

        # Extract text from the message parts
        user_text = "".join([part.text for part in message.parts if part.text])
        
        if not user_text:
            yield Content(parts=[Part(text="I'm sorry, I didn't receive any text.")])
            return

        try:
            # Process the message through memory
            self.memory_manager.process_message(
                session_id=session_id,
                platform="adk",
                role="user",
                content=user_text,
                user_id=user_id
            )
            
            # Get context for the query
            mem_context = self.memory_manager.get_context_for_query(session_id, user_text, user_id)
            
            # System prompt
            system_prompt = (
                "You are Amy, a helpful and friendly AI assistant with memory. "
                "You can remember past conversations and learn about users over time. "
                "Respond directly to the user's message in a conversational way, "
                "using context from previous conversations when relevant."
            )
            
            # Build the full prompt (simplification for ADK runner)
            # Todo: Use properly structured history from memory manager if available
            full_prompt = f"{system_prompt}\n\n{mem_context}\n\nUser: {user_text}\nAmy:"
            
            response = self.model.generate_content(full_prompt)
            amy_response = response.text if response.text else "I'm sorry, I couldn't generate a response."
            
            # Record Amy's response
            self.memory_manager.process_message(
                session_id=session_id,
                platform="adk",
                role="model",
                content=amy_response,
                user_id=user_id
            )
            
            yield Event(author=self.name, content=Content(parts=[Part(text=amy_response)]))
            
        except Exception as e:
            logger.error(f"Error in AmyAgent._run_async_impl: {e}")
            yield Event(author=self.name, content=Content(parts=[Part(text=f"I encountered an error: {e}")]))

# Create the root_agent instance
root_agent = AmyAgent()

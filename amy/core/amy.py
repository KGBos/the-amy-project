"""
Amy's Brain - Unified interface to the ADK Agent

This module provides a simple async interface for all integrations
(Telegram, Web, etc.) to use the ADK agent without duplicating logic.
"""

import logging
from typing import Optional

from google.adk.runners import Runner
from google.genai.types import Content, Part

from amy.core.agent import create_root_agent
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM
from amy.memory.session_service import SqliteSessionService

logger = logging.getLogger(__name__)


class Amy:
    """
    Unified brain interface that wraps the ADK agent.
    
    All integrations should use this instead of calling Gemini directly.
    This ensures consistent behavior, memory management, and tool access.
    """
    
    def __init__(self):
        """Initialize the brain with ADK runner."""
        logger.info("Initializing Amy Brain...")
        
        # 1. Initialize Memory Systems (Dependencies)
        self.db = ConversationDB()
        self.ltm = LTM()
        logger.info("Memory systems initialized")
        
        # 2. Create the Root Agent (Dependency Injection)
        self.agent = create_root_agent(self.ltm, self.db)
        
        # 3. Initialize Persistence Service
        self.session_service = SqliteSessionService(self.db)
        
        # 4. Initialize the Runner
        self.runner = Runner(
            app_name="amy",
            agent=self.agent,
            session_service=self.session_service,
        )
        logger.info("Amy initialized with ADK agent")
    
    async def chat(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        platform: str = "unknown"
    ) -> str:
        """
        Process a user message and return Amy's response.
        
        This is the ONLY method integrations need to call.
        Everything else (memory, context, tools) is handled internally.
        
        Args:
            session_id: Unique session identifier (e.g., "telegram_123456")
            message: The user's message text
            user_id: Optional user identifier for memory
            platform: Platform name for logging (telegram, web, etc.)
            
        Returns:
            Amy's response text
        """
        try:
            # Ensure session exists (ADK requires explicit creation if not found)
            # The SessionService.get_session will load history if it exists in DB
            session = await self.session_service.get_session(
                app_name="amy",
                user_id=user_id or session_id,
                session_id=session_id
            )
            
            if session is None:
                session = await self.session_service.create_session(
                    app_name="amy",
                    user_id=user_id or session_id,
                    session_id=session_id,
                    state={
                        'session_id': session_id,
                        'user_id': user_id,
                        'platform': platform,
                        'user_message': message,
                    }
                )
            
            # Update session state with current message metadata
            # This 'state' is transient in RAM during the run but helpful for our Service
            # to know metadata (platform, user_id) when saving new messages.
            session.state.update({
                'user_message': message,
                'session_id': session_id,
                'user_id': user_id,
                'platform': platform
            })
            
            # Create the message content
            content = Content(parts=[Part(text=message)])
            
            # Run the agent!
            # The Runner will:
            # 1. Add 'content' to session.history
            # 2. Run the model/agent
            # 3. Add model response to session.history
            # 4. Call session_service.save_session() automatically!
            
            response_text = ""
            async for event in self.runner.run_async(
                user_id=user_id or session_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Skip reasoning/thought parts from the Planner
                        if getattr(part, 'thought', False):
                            continue
                            
                        if part.text:
                            response_text += part.text
            
            # Cleanup Planner tags if they leaked
            for tag in ['/*PLANNING*/', '/*REASONING*/', '/*ACTION*/', '/*FINAL_ANSWER*/', '/*REPLANNING*/']:
                response_text = response_text.replace(tag, '')
            
            response_text = response_text.strip()
            
            # No sidecar logic! Agent tools handle memory now.
            
            logger.info(f"[{platform}] Processed message for {session_id}")
            return response_text or "I'm sorry, I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error in Amy.process: {e}")
            return "I'm having trouble thinking right now. Please try again."

    def get_memory_stats(self, session_id: str) -> dict:
        """Get memory statistics for a session."""
        return {
            'message_count': self.db.get_message_count(session_id),
            'has_history': self.db.has_previous_conversations(session_id.split('_')[-1])
        }


# Singleton instance for easy import
_brain_instance: Optional[Amy] = None


def get_brain() -> Amy:
    """Get or create the singleton Amy instance."""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = Amy()
    return _brain_instance

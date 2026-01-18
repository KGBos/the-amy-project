"""
Amy's Brain - Unified interface to the ADK Agent

This module provides a simple async interface for all integrations
(Telegram, Web, etc.) to use the ADK agent without duplicating logic.
"""

import asyncio
import logging
from typing import Optional

from google.adk.runners import Runner
from google.genai.types import Content, Part

from amy.config import MAX_MESSAGE_LENGTH, PLANNER_TAGS
from amy.core.agent import create_root_agent
from amy.core.errors import (
    AmyError, 
    InputValidationError, 
    TransientError, 
    RateLimitError
)
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM
from amy.memory.session_service import SqliteSessionService

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 2
RETRY_DELAY = 1.0  # seconds


class Amy:
    """
    Unified brain interface that wraps the ADK agent.
    
    All integrations should use this instead of calling Gemini directly.
    This ensures consistent behavior, memory management, and tool access.
    """
    
    def __init__(self):
        """Initialize the brain's core components."""
        logger.info("Setting up Amy Brain core components...")
        
        # 1. Initialize Memory Systems (Dependencies)
        self.conversation_db = ConversationDB()
        self.ltm = LTM()
        logger.info("Memory systems instantiated")
        
        # 2. Create the Root Agent (Dependency Injection)
        self.root_agent = create_root_agent(self.ltm)
        
        # Initialization state
        self._initialized = False
        self._init_lock = asyncio.Lock()
        self.session_service: Optional[SqliteSessionService] = None
        self.runner: Optional[Runner] = None
    
    async def initialize(self):
        """
        Asynchronously initialize the brain components.
        """
        async with self._init_lock:
            if self._initialized:
                return
                
            logger.info("Initializing Amy Brain Components...")
            try:
                # Initialize async database
                await self.conversation_db.initialize()
                
                # ADK SqliteSessionService
                self.session_service = SqliteSessionService(self.conversation_db)
                
                # ADK Runner
                self.runner = Runner(
                    app_name="amy",
                    agent=self.root_agent,
                    session_service=self.session_service,
                )
                
                self._initialized = True
                logger.info("Amy initialized with ADK agent")
            except Exception as e:
                logger.error(f"Failed to initialize Amy components: {e}")
                raise RuntimeError(f"Brain initialization failed: {e}")
        
    async def stop(self):
        """Cleanly shut down all resources."""
        logger.info("Closing Amy Brain resources...")
        if self.conversation_db:
            await self.conversation_db.close()
        if self.ltm:
            self.ltm.close()
        self._initialized = False

    def _validate_input(self, message: str) -> None:
        """
        Validate user input before processing.
        
        Raises:
            InputValidationError: If input is invalid
        """
        if not message or not message.strip():
            raise InputValidationError(
                "Empty message received",
                "I didn't receive a message. What can I help you with?"
            )
        
        if len(message) > MAX_MESSAGE_LENGTH:
            raise InputValidationError(
                f"Message too long: {len(message)} chars",
                f"Your message is too long ({len(message)} characters). "
                f"Please keep it under {MAX_MESSAGE_LENGTH} characters."
            )
    
    def _clean_response(self, response_text: str) -> str:
        """Clean up model response by removing planner tags."""
        for tag in PLANNER_TAGS:
            response_text = response_text.replace(tag, '')
        return response_text.strip()
    
    async def _run_agent(
        self,
        session_id: str,
        message: str,
        user_id: str,
        platform: str
    ) -> str:
        """
        Internal method to run the agent with session management.
        
        Separated from chat() to allow retry logic wrapper.
        """
        # Ensure session exists
        session = await self.session_service.get_session(
            app_name="amy",
            user_id=user_id,
            session_id=session_id
        )
        
        if session is None:
            # Create session with initial state
            session = await self.session_service.create_session(
                app_name="amy",
                user_id=user_id,
                session_id=session_id,
                state={
                    'session_id': session_id,
                    'user_id': user_id,
                    'platform': platform,
                }
            )
        elif session.state.get('platform') != platform:
            # Update platform if it changed (rare but possible)
            session.state['platform'] = platform
        
        # Create the message content
        content = Content(parts=[Part(text=message)])
        
        # Run the agent
        response_text = ""
        async for chunk in self.chat_stream(session_id, message, user_id, platform):
            response_text += chunk
        
        return response_text

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        user_id: str,
        platform: str
    ):
        """
        Steam the agent's response chunk by chunk.
        """
        if not self._initialized:
            await self.initialize()

        # Ensure session exists
        session = await self.session_service.get_session(
            app_name="amy",
            user_id=user_id,
            session_id=session_id
        )
        
        if session is None:
            session = await self.session_service.create_session(
                app_name="amy",
                user_id=user_id,
                session_id=session_id,
                state={
                    'session_id': session_id,
                    'user_id': user_id,
                    'platform': platform,
                }
            )
        
        content = Content(parts=[Part(text=message)])
        
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if getattr(part, 'thought', False):
                        continue
                    if part.text:
                        clean_text = self._clean_response(part.text)
                        if clean_text:
                            yield clean_text
    
    async def rewind_session(
        self, 
        user_id: str, 
        session_id: str, 
        rewind_before_invocation_id: str
    ) -> bool:
        """
        Rewind a session to a previous state.
        New in ADK v1.22.
        """
        if not self._initialized:
            await self.initialize()

        try:
            await self.runner.rewind_async(
                user_id=user_id,
                session_id=session_id,
                rewind_before_invocation_id=rewind_before_invocation_id
            )
            logger.info(f"Rewound session {session_id} to before {rewind_before_invocation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to rewind session {session_id}: {e}")
            return False

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
        effective_user_id = user_id or session_id
        
        # Input validation
        try:
            self._validate_input(message)
        except InputValidationError as e:
            logger.warning(f"Input validation failed: {e}")
            return e.user_message
        
        # Run with retry logic for transient errors
        last_error: Optional[Exception] = None
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                response_text = await self._run_agent(
                    session_id, message, effective_user_id, platform
                )
                
                logger.info(f"[{platform}] Processed message for {session_id}")
                return response_text or "I'm sorry, I couldn't generate a response."
                
            except AmyError as e:
                last_error = e
                if e.is_retryable and attempt < MAX_RETRIES:
                    delay = RETRY_DELAY * (attempt + 1)  # Exponential backoff
                    logger.warning(
                        f"Retryable error (attempt {attempt + 1}/{MAX_RETRIES + 1}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.error(f"Amy error after {attempt + 1} attempts: {e}")
                    return e.user_message
                    
            except Exception as e:
                # Check for known API error patterns
                error_str = str(e).lower()
                
                if 'quota' in error_str or 'rate' in error_str or '429' in error_str:
                    last_error = RateLimitError("API rate limit", e)
                    if attempt < MAX_RETRIES:
                        delay = RETRY_DELAY * (attempt + 2)  # Longer backoff for rate limits
                        logger.warning(f"Rate limit hit, waiting {delay}s...")
                        await asyncio.sleep(delay)
                        continue
                    return last_error.user_message
                    
                elif 'timeout' in error_str or 'connection' in error_str:
                    last_error = TransientError("Connection error", e)
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    return last_error.user_message
                    
                else:
                    # Unknown error - don't retry
                    logger.error(f"Unexpected error in Amy.chat: {e}", exc_info=True)
                    return "I'm having trouble thinking right now. Please try again."
        
        # Should not reach here, but just in case
        if last_error:
            return getattr(last_error, 'user_message', 
                          "I'm having trouble thinking right now. Please try again.")
        return "I'm having trouble thinking right now. Please try again."

    async def get_memory_stats(self, session_id: str) -> dict:
        """Get memory statistics for a session."""
        if not self._initialized:
            await self.initialize()
            
        m_count = await self.conversation_db.get_message_count(session_id)
        has_hist = await self.conversation_db.has_previous_conversations(session_id.split('_')[-1])
        return {
            'message_count': m_count,
            'has_history': has_hist
        }


class AmyProvider:
    """
    Provides Amy instances with reset capability for testing.
    
    Use this instead of direct instantiation for better testability.
    """
    _instance: Optional[Amy] = None
    
    @classmethod
    def get(cls) -> Amy:
        """Get or create the singleton Amy instance."""
        if cls._instance is None:
            cls._instance = Amy()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """
        Reset the singleton instance.
        
        Useful for testing to ensure clean state between tests.
        """
        if cls._instance is not None:
            # Clean up resources
            if hasattr(cls._instance, 'conversation_db') and cls._instance.conversation_db:
                cls._instance.conversation_db.close()
        cls._instance = None


# Backward compatible function
def get_brain() -> Amy:
    """Get or create the singleton Amy instance."""
    return AmyProvider.get()


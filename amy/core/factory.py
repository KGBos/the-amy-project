"""
Amy Agent Factory

Provides a factory function to create a fully configured ADK Runner for Amy.
Replaces the old 'Amy' wrapper class for stricter ADK compliance.
"""
import logging
from typing import Optional

from google.adk.runners import Runner

from amy.config import APP_NAME
from amy.core.agent import create_root_agent
from amy.memory.conversation import ConversationDB
from amy.memory.ltm import LTM
from amy.memory.session_service import SqliteSessionService
from amy.core.plugins import SafetyPlugin

logger = logging.getLogger(__name__)

async def create_amy_runner(
    conversation_db: Optional[ConversationDB] = None,
    ltm: Optional[LTM] = None
) -> Runner:
    """
    Create a configured ADK Runner for the Amy agent.
    
    Args:
        conversation_db: Optional existing ConversationDB instance (dependency injection)
        ltm: Optional existing LTM instance (dependency injection)
        
    Returns:
        Initialized ADK Runner instance
    """
    logger.info("Creating Amy ADK Runner...")
    
    # 1. Initialize Memory Systems if not provided
    if conversation_db is None:
        conversation_db = ConversationDB()
        await conversation_db.initialize()
        
    if ltm is None:
        ltm = LTM()
        
    # 2. Create the Root Agent
    root_agent = create_root_agent(ltm)
    
    # 3. Create Session Service
    session_service = SqliteSessionService(conversation_db)
    
    # 4. Create and return Runner
    from amy.core.telemetry import get_telemetry_plugins
    plugins = get_telemetry_plugins()
    
    # Add Safety Plugin (Cross-cutting concern)
    plugins.append(SafetyPlugin())
    
    logger.info(f"Initializing Runner for app: {APP_NAME} (plugins: {len(plugins)})")
    return Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        plugins=plugins
    )

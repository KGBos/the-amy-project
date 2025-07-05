import logging
import os
from datetime import datetime

def setup_agent_logger(agent_name: str):
    """Sets up a session-specific logger for an agent's actions.

    Args:
        agent_name: The name of the agent (e.g., "Gemini", "Amy").
    """
    log_dir = "agent_logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{agent_name.lower()}_session_{timestamp}.log")

    logger = logging.getLogger(agent_name) # Use agent_name as logger name
    logger.setLevel(logging.INFO)

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Include %(name)s
    fh.setFormatter(formatter)

    # Add the handler to the logger
    # Prevent duplicate logs if called multiple times
    if not logger.handlers:
        logger.addHandler(fh)

    return logger
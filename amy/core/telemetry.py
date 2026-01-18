"""
Telemetry Configuration for Amy
Configures Observability plugins (Freeplay, OpenTelemetry) if available.
"""
import os
import logging
from typing import List, Any

# Try to import Freeplay, handle if not installed
try:
    from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
    _FREEPLAY_AVAILABLE = True
except ImportError:
    _FREEPLAY_AVAILABLE = False

logger = logging.getLogger(__name__)

def get_telemetry_plugins() -> List[Any]:
    """
    Returns a list of configured observability plugins.
    Only enables Freeplay if the API key is present in env.
    """
    plugins = []
    
    # Check for Freeplay
    if _FREEPLAY_AVAILABLE:
        api_key = os.environ.get("FREEPLAY_API_KEY")
        if api_key:
            logger.info(f"Initializing Freeplay Observability Plugin (Key: ...{api_key[-4:]})")
            try:
                plugins.append(FreeplayObservabilityPlugin())
                logger.info("Freeplay plugin successfully added to telemetry stack.")
            except Exception as e:
                logger.error(f"Failed to initialize Freeplay plugin: {e}")
        else:
            logger.warning("Freeplay module found but FREEPLAY_API_KEY is not set. Telemetry will be disabled.")
    
    return plugins

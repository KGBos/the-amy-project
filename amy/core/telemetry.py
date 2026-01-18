"""
Telemetry Configuration for Amy
Configures Observability plugins (Freeplay, OpenTelemetry) if available.
"""
import os
import logging
from typing import List, Any


logger = logging.getLogger(__name__)

# Try to import Freeplay, handle if not installed
try:
    from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
    _FREEPLAY_AVAILABLE = True
except ImportError:
    _FREEPLAY_AVAILABLE = False

# --- Compatibility Fix for OpenInference/Freeplay ---
# google-adk 1.22.1 uses 'contents' in LlmRequest, but openinference expects 'messages'.
# We monkeypatch LlmRequest to add a 'messages' property alias.
try:
    from google.adk.models.llm_request import LlmRequest
    
    if not hasattr(LlmRequest, 'messages'):
        # Define a property that aliases contents
        def get_messages(self):
            return self.contents
            
        def set_messages(self, value):
            self.contents = value
            
        # Add the property to the class
        LlmRequest.messages = property(get_messages, set_messages)
        logger.info("Applied compatibility patch: LlmRequest.messages -> LlmRequest.contents")
except ImportError:
    pass
# ----------------------------------------------------

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
            # Get additional config
            project_id = os.environ.get("FREEPLAY_PROJECT_ID")
            api_url = os.environ.get("FREEPLAY_API_URL")
            if not api_url:
                api_url = "https://app.freeplay.ai/api"
            
            if not project_id:
                logger.warning("FREEPLAY_API_KEY found but FREEPLAY_PROJECT_ID is missing. Telemetry may fail.")
            
            logger.info(f"Initializing Freeplay Telemetry (URL: {api_url}, Project: {project_id})")
            
            try:
                # Initialize the Exporter
                from freeplay_python_adk.client import FreeplayADK
                FreeplayADK.initialize_observability(
                    freeplay_api_url=api_url,
                    freeplay_api_key=api_key,
                    project_id=project_id,
                    log_spans_to_console=False
                )
                
                # Add the plugin for span attributes
                plugins.append(FreeplayObservabilityPlugin())
                logger.info("Freeplay observability initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Freeplay: {e}")
        else:
            logger.warning("Freeplay module found but FREEPLAY_API_KEY is not set. Telemetry will be disabled.")
    
    return plugins

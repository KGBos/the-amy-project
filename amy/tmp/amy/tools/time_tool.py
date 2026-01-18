import datetime
from google.adk.tools import FunctionTool

@FunctionTool
def get_current_time() -> str:
    """
    Returns the current date and time.

    Returns:
        A string representing the current date and time in ISO 8601 format.
    """
    return datetime.datetime.now().isoformat()

"""
Code Execution Tools for Amy via ADK
"""
import logging
import sys
import io
import contextlib
import traceback
from typing import Optional

from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

def create_code_interpreter_tool():
    """Create a code_interpreter tool for running Python code."""

    async def code_interpreter(
        code: str,
        tool_context: ToolContext = None
    ) -> str:
        """
        Execute Python code to solve math problems, process data, or perform logic.
        
        Usage:
        - Use this for ANY math calculation (don't try to do math in your head).
        - Use this for list processing, filtering, or sorting data.
        - The code must be valid Python.
        - The code should `print()` the final result so I can see it.
        - Variables do NOT persist between calls (stateless).
        
        Args:
            code: Valid Python code block.
        
        Returns:
            The standard output (stdout) of the code execution, or error message.
        """
        logger.info(f"Executing code:\n{code}")
        
        # Capture stdout and stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            # We use a restricted global environment for slight safety,
            # but this is still "unsafe" local execution.
            # In a real prod env, use docker/gvisor.
            safe_globals = {
                "math": __import__("math"),
                "datetime": __import__("datetime"),
                "json": __import__("json"),
                "random": __import__("random"),
                "print": print,
                "__builtins__": __builtins__ # Required for basic python
            }
            
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                # exec() is dangerous, but we are in a dev environment requested by user.
                exec(code, safe_globals)
                
            output = stdout_buffer.getvalue()
            error = stderr_buffer.getvalue()
            
            if error:
                 return f"Executed with errors:\nSTDOUT:\n{output}\nSTDERR:\n{error}"
            
            if not output.strip():
                return "Code executed successfully but printed no output. Did you forget to print(result)?"
                
            return output

        except Exception as e:
            # Capture the full traceback for the agent to debug itself
            tb = traceback.format_exc()
            return f"Runtime Error:\n{tb}"
            
    return FunctionTool(code_interpreter)

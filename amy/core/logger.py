import logging
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

def setup_agent_logger(agent_name: str, model_name: Optional[str] = None):
    """Sets up a session-specific logger for an agent's actions.

    Args:
        agent_name: The name of the agent (e.g., "claude", "gemini").
        model_name: The specific model name (e.g., "claude-3.5-sonnet").
    """
    log_dir = "agent_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Use model name if provided, otherwise use agent name
    logger_name = model_name if model_name else agent_name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{logger_name}_session_{timestamp}.log")

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(fh)

    return logger

def log_agent_action(agent_name: str, action: str, details: str, 
                    model_name: Optional[str] = None, 
                    metadata: Optional[Dict[str, Any]] = None):
    """Log agent actions with context and metadata.

    Args:
        agent_name: The name of the agent (e.g., "claude", "gemini").
        action: The action being performed (e.g., "file_modified", "commit", "decision").
        details: Detailed description of the action.
        model_name: The specific model name (e.g., "claude-3.5-sonnet").
        metadata: Additional metadata as dictionary.
    """
    logger = setup_agent_logger(agent_name, model_name)
    
    # Create log entry
    log_entry = {
        "agent": agent_name,
        "model": model_name or agent_name,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Log as JSON for structured data
    logger.info(f"AGENT_ACTION: {json.dumps(log_entry, indent=2)}")
    
    return logger

def log_file_change(agent_name: str, file_path: str, change_type: str, 
                   model_name: Optional[str] = None, 
                   description: Optional[str] = None):
    """Log file changes made by agents.

    Args:
        agent_name: The name of the agent.
        file_path: Path to the modified file.
        change_type: Type of change (created, modified, deleted).
        model_name: The specific model name.
        description: Optional description of the change.
    """
    metadata = {
        "file_path": file_path,
        "change_type": change_type,
        "description": description
    }
    
    return log_agent_action(
        agent_name=agent_name,
        action="file_change",
        details=f"{change_type} {file_path}",
        model_name=model_name,
        metadata=metadata
    )

def log_commit(agent_name: str, commit_hash: str, commit_message: str,
              model_name: Optional[str] = None, 
              files_changed: Optional[list] = None):
    """Log commits made by agents.

    Args:
        agent_name: The name of the agent.
        commit_hash: The git commit hash.
        commit_message: The commit message.
        model_name: The specific model name.
        files_changed: List of files changed in the commit.
    """
    metadata = {
        "commit_hash": commit_hash,
        "commit_message": commit_message,
        "files_changed": files_changed or []
    }
    
    return log_agent_action(
        agent_name=agent_name,
        action="commit",
        details=f"Commit {commit_hash}: {commit_message}",
        model_name=model_name,
        metadata=metadata
    )

def log_decision(agent_name: str, decision: str, reasoning: str,
                model_name: Optional[str] = None,
                alternatives: Optional[list] = None):
    """Log decisions made by agents.

    Args:
        agent_name: The name of the agent.
        decision: The decision made.
        reasoning: The reasoning behind the decision.
        model_name: The specific model name.
        alternatives: Alternative options considered.
    """
    metadata = {
        "decision": decision,
        "reasoning": reasoning,
        "alternatives": alternatives or []
    }
    
    return log_agent_action(
        agent_name=agent_name,
        action="decision",
        details=f"Decision: {decision}",
        model_name=model_name,
        metadata=metadata
    )

def log_session_start(agent_name: str, session_purpose: str,
                     model_name: Optional[str] = None):
    """Log the start of an agent session.

    Args:
        agent_name: The name of the agent.
        session_purpose: Purpose of the session.
        model_name: The specific model name.
    """
    return log_agent_action(
        agent_name=agent_name,
        action="session_start",
        details=f"Session started: {session_purpose}",
        model_name=model_name
    )

def log_session_end(agent_name: str, session_summary: str,
                   model_name: Optional[str] = None,
                   files_modified: Optional[list] = None):
    """Log the end of an agent session.

    Args:
        agent_name: The name of the agent.
        session_summary: Summary of what was accomplished.
        model_name: The specific model name.
        files_modified: List of files modified during session.
    """
    metadata = {
        "session_summary": session_summary,
        "files_modified": files_modified or []
    }
    
    return log_agent_action(
        agent_name=agent_name,
        action="session_end",
        details=f"Session ended: {session_summary}",
        model_name=model_name,
        metadata=metadata
    )

# Convenience functions for common agents
def log_claude_action(action: str, details: str, metadata: Optional[Dict[str, Any]] = None):
    """Log actions for Claude agent."""
    return log_agent_action("claude", action, details, "claude-3.5-sonnet", metadata)

def log_gemini_action(action: str, details: str, metadata: Optional[Dict[str, Any]] = None):
    """Log actions for Gemini agent."""
    return log_agent_action("gemini", action, details, "gemini-2.0-flash", metadata)

def log_codex_action(action: str, details: str, metadata: Optional[Dict[str, Any]] = None):
    """Log actions for Codex agent."""
    return log_agent_action("codex", action, details, "gpt-4-turbo", metadata)

# Command line interface for git hooks
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Agent logging utility")
    parser.add_argument("--action", required=True, help="Action being performed")
    parser.add_argument("--agent", required=True, help="Agent name")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--files", help="Files changed (comma-separated)")
    parser.add_argument("--message", help="Commit message or details")
    parser.add_argument("--commit_hash", help="Git commit hash")
    
    args = parser.parse_args()
    
    # Parse files list
    files_list = args.files.split(",") if args.files else []
    
    # Create metadata
    metadata = {}
    if args.files:
        metadata["files_changed"] = files_list
    if args.message:
        metadata["message"] = args.message
    if args.commit_hash:
        metadata["commit_hash"] = args.commit_hash
    
    # Log the action
    try:
        log_agent_action(
            agent_name=args.agent,
            action=args.action,
            details=args.message or args.action,
            model_name=args.model,
            metadata=metadata
        )
        print(f"✅ Logged action: {args.action} for {args.agent}")
    except Exception as e:
        print(f"❌ Error logging action: {e}")
        sys.exit(1)
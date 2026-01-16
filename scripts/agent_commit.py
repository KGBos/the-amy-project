#!/usr/bin/env python3
"""
Agent commit script - allows agents to commit with their own names
Integrates with agent logging system
"""

import sys
import subprocess
import argparse
from tools.scripts.agent_logger import log_agent_action

# Agent configurations
AGENT_CONFIGS = {
    "claude": {
        "email": "claude@anthropic.com",
        "model": "claude-3.5-sonnet"
    },
    "gemini": {
        "email": "gemini@google.com", 
        "model": "gemini-2.5-flash"
    },
    "codex": {
        "email": "codex@openai.com",
        "model": "gpt-4-turbo"
    },
    "KGBos": {
        "email": "leon.kuzmin@icloud.com",  # Replace with your actual email
        "model": "human"
    }
}

def get_changed_files():
    """Get list of files that have been modified."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def commit_as_agent(agent_name: str, commit_message: str):
    """Commit changes as a specific agent."""
    
    # Validate agent name
    if agent_name not in AGENT_CONFIGS:
        print(f"❌ Error: Unknown agent '{agent_name}'")
        print(f"Available agents: {', '.join(AGENT_CONFIGS.keys())}")
        return False
    
    agent_config = AGENT_CONFIGS[agent_name]
    agent_email = agent_config["email"]
    model_name = agent_config["model"]
    
    print(f"🤖 Committing as agent: {agent_name} ({agent_email})")
    print(f"📝 Message: {commit_message}")
    
    # Stage all changes
    try:
        subprocess.run(["git", "add", "."], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error staging files: {e}")
        return False
    
    # Check if there are changes to commit
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("❌ No changes to commit")
            return False
    except subprocess.CalledProcessError:
        pass
    
    # Get changed files for logging
    changed_files = get_changed_files()
    
    # Log the commit action
    try:
        log_agent_action(
            agent_name=agent_name,
            action="commit",
            details=commit_message,
            model_name=model_name,
            metadata={
                "files_changed": changed_files,
                "commit_message": commit_message
            }
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not log agent action: {e}")
    
    # Commit with agent signature
    try:
        subprocess.run([
            "git", "commit", 
            f"--author={agent_name} <{agent_email}>",
            "-m", commit_message
        ], check=True)
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        )
        commit_hash = result.stdout.strip()
        
        print(f"✅ Committed successfully as {agent_name}")
        print(f"🔍 Commit hash: {commit_hash}")
        
        # Log commit completion
        try:
            log_agent_action(
                agent_name=agent_name,
                action="commit_complete",
                details=f"Commit {commit_hash} completed",
                model_name=model_name,
                metadata={
                    "commit_hash": commit_hash,
                    "files_changed": changed_files
                }
            )
        except Exception as e:
            print(f"⚠️  Warning: Could not log commit completion: {e}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error committing: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Commit changes as a specific agent")
    parser.add_argument("agent", help="Agent name (claude, gemini, codex, user)")
    parser.add_argument("message", help="Commit message")
    
    args = parser.parse_args()
    
    success = commit_as_agent(args.agent, args.message)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 
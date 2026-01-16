#!/bin/bash
# Agent commit script - allows agents to commit with their own names
# Usage: ./tools/scripts/agent_commit.sh [agent_name] [commit_message]

set -e

# Get agent name from command line or detect from git config
AGENT_NAME=${1:-$(git config user.name)}
COMMIT_MESSAGE=${2:-"Agent commit"}

# Agent configurations
declare -A AGENT_CONFIGS
AGENT_CONFIGS["claude"]="claude@anthropic.com"
AGENT_CONFIGS["gemini"]="gemini@google.com"
AGENT_CONFIGS["codex"]="codex@openai.com"
AGENT_CONFIGS["user"]="your@email.com"  # Replace with your actual email

# Validate agent name
if [ -z "$AGENT_NAME" ]; then
    echo "❌ Error: No agent name provided"
    echo "Usage: $0 [agent_name] [commit_message]"
    echo "Available agents: claude, gemini, codex, user"
    exit 1
fi

# Check if agent is valid
if [ -z "${AGENT_CONFIGS[$AGENT_NAME]}" ]; then
    echo "❌ Error: Unknown agent '$AGENT_NAME'"
    echo "Available agents: claude, gemini, codex, user"
    exit 1
fi

# Get agent email
AGENT_EMAIL="${AGENT_CONFIGS[$AGENT_NAME]}"

echo "🤖 Committing as agent: $AGENT_NAME ($AGENT_EMAIL)"
echo "📝 Message: $COMMIT_MESSAGE"

# Stage all changes
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "❌ No changes to commit"
    exit 1
fi

# Commit with agent signature
git commit --author="$AGENT_NAME <$AGENT_EMAIL>" -m "$COMMIT_MESSAGE"

echo "✅ Committed successfully as $AGENT_NAME"
echo "🔍 Commit hash: $(git rev-parse HEAD)" 
#!/bin/bash
# Setup script for git hooks and agent logging
# This script configures git hooks for agent logging in any environment

set -e

echo "🔧 Setting up git hooks for agent logging..."

# Make sure we're in the project root
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Make hooks executable
echo "📝 Making git hooks executable..."
chmod +x .githooks/*

# Configure git to use our hooks directory
echo "⚙️  Configuring git to use custom hooks directory..."
git config core.hooksPath .githooks

# Create agent_logs directory if it doesn't exist
echo "📁 Creating agent_logs directory..."
mkdir -p agent_logs

# Test the setup
echo "🧪 Testing git hooks setup..."
if [ -x ".githooks/pre-commit" ]; then
    echo "✅ Pre-commit hook is executable"
else
    echo "❌ Error: Pre-commit hook is not executable"
    exit 1
fi

if [ -x ".githooks/post-commit" ]; then
    echo "✅ Post-commit hook is executable"
else
    echo "❌ Error: Post-commit hook is not executable"
    exit 1
fi

# Verify git configuration
HOOKS_PATH=$(git config core.hooksPath)
if [ "$HOOKS_PATH" = ".githooks" ]; then
    echo "✅ Git hooks path configured correctly"
else
    echo "❌ Error: Git hooks path not configured correctly"
    exit 1
fi

echo ""
echo "🎉 Git hooks setup complete!"
echo ""
echo "📋 Agent logging is now configured:"
echo "   • Pre-commit hook: Logs agent actions before commits"
echo "   • Post-commit hook: Logs additional commit information"
echo "   • Agent logs: Stored in agent_logs/ directory"
echo ""
echo "🚀 Next steps:"
echo "   1. Set your git user name to your agent name:"
echo "      git config user.name 'claude'"
echo "      git config user.email 'claude@anthropic.com'"
echo ""
echo "   2. Start logging your actions:"
echo "      python3 tools/scripts/agent_logger.py --action=session_start --agent=claude --model=claude-3.5-sonnet"
echo ""
echo "   3. Make a commit to test the system!" 
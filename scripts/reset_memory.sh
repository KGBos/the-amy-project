#!/bin/bash
# scripts/reset_memory.sh
# Resets Amy's memory by deleting the database and vector store.

echo "⚠️  WARNING: This will delete ALL of Amy's memory (conversations and facts)."
echo "   - Database: instance/amy_memory.db"
echo "   - Vector DB: instance/mem0_storage"
echo ""

read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping any running instances (optional safety)..."
    # Optional: try to warn if python/bot is running, but we won't force kill here 
    # as the user controls the terminal.
    
    echo "🗑️  Deleting SQLite Database..."
    rm -f instance/amy_memory.db
    
    echo "🗑️  Deleting Vector Storage..."
    rm -rf instance/mem0_storage
    
    echo "🗑️  Deleting Log Files (optional clean start)..."
    rm -f instance/amy_telegram_bot.log
    
    echo "✨ Memory reset complete. Amy is now a blank slate."
else
    echo "❌ Operation cancelled."
fi

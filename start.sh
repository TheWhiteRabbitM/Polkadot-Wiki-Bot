#!/usr/bin/env bash
# Polkadot Wiki Bot Startup Script
# Usage: ./start.sh

set -e

echo "🪐 Starting Polkadot Wiki Bot..."

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
fi

# Load environment variables
if [ -f .env ]; then
    echo "✅ Loading environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if token is set
if [ -z "$WIKI_BOT_TOKEN" ]; then
    echo "❌ Error: WIKI_BOT_TOKEN not set!"
    echo "Please create a .env file with your bot token."
    echo "Example: WIKI_BOT_TOKEN=your_token_here"
    exit 1
fi

echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop"
echo ""

# Run the bot
python3 wikibot.py

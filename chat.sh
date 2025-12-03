#!/bin/bash

# Save current directory
ORIGINAL_DIR=$(pwd)

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Run the chat
python chat.py

# Cleanup after chat exits
deactivate
cd "$ORIGINAL_DIR"
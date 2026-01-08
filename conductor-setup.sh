#!/bin/bash
set -e

# Get the parent directory (where .env lives, shared across all workspaces)
PARENT_DIR="$(dirname "$(pwd)")"

# Copy .env from parent directory to workspace
if [ -f "$PARENT_DIR/.env" ]; then
    cp "$PARENT_DIR/.env" .env
    echo "Environment loaded from $PARENT_DIR/.env"
else
    echo "Warning: No .env found at $PARENT_DIR/.env"
    echo "Please create a .env file in: $PARENT_DIR"
fi

# Optional: Set up Python virtual environment if it doesn't exist
# if [ ! -d "backend/venv" ]; then
#     cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
#     cd ..
# fi

# Optional: Install frontend dependencies
# if [ ! -d "frontend/node_modules" ]; then
#     cd frontend && npm install
#     cd ..
# fi

#!/bin/bash
set -e

# Copy .env from repo root to workspace
if [ -f "$CONDUCTOR_ROOT_PATH/.env" ]; then
    cp "$CONDUCTOR_ROOT_PATH/.env" .env
    echo "Environment loaded from repo root."
else
    echo "Warning: No .env found at $CONDUCTOR_ROOT_PATH/.env"
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

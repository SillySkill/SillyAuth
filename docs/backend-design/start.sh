# ============================================
# SillyMD Backend - Quick Start
# ============================================

#!/bin/bash

echo "=========================================="
echo "   SillyMD Backend - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ".env created"
fi

echo "Starting Docker services..."
docker-compose up -d postgres redis meilisearch

echo "Waiting for services to be ready..."
sleep 10

echo "Starting FastAPI backend..."
# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "Starting Uvicorn server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo ""
echo "=========================================="
echo "Backend started!"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "=========================================="

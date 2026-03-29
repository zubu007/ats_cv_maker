#!/bin/bash

# ATS CV Maker - Backend Startup Script

echo "🚀 Starting ATS CV Maker Backend..."

# Navigate to project root
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please configure your API keys."
    else
        echo "❌ .env.example not found"
        exit 1
    fi
fi

# Start the backend server
echo "✅ Starting backend server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
python start_backend.py

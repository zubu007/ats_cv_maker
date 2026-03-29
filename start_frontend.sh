#!/bin/bash

# ATS CV Maker - Frontend Startup Script

echo "🚀 Starting ATS CV Maker Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
fi

# Start the frontend dev server
echo "✅ Starting frontend development server..."
echo "🌐 Frontend will be available at: http://localhost:5173"
echo ""
npm run dev

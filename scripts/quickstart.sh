#!/bin/bash

# Quick Start Script for ATS CV Maker
# This script helps you get started quickly with the ATS CV scoring system

echo "🚀 ATS CV Maker - Quick Start"
echo "================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY (for OpenAI GPT models)"
    echo "   - OR ANTHROPIC_API_KEY (for Claude models)"
    echo ""
    echo "Press Enter after you've added your API keys..."
    read
else
    echo "✓ Found .env file"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -e .

# Download spaCy model
echo ""
echo "🔍 Checking for spaCy language model..."
if python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✓ spaCy model already installed"
else
    echo "📥 Downloading spaCy language model..."
    python -m spacy download en_core_web_sm
    echo "✓ spaCy model installed"
fi

# Run sample analysis
echo ""
echo "================================"
echo "✅ Setup complete!"
echo ""
echo "📊 Running sample analysis..."
echo "================================"
echo ""

python main.py sample_cv.txt sample_job_description.txt

echo ""
echo "================================"
echo "🎉 Quick start complete!"
echo ""
echo "To run your own analysis:"
echo "  python main.py your_cv.pdf your_job_description.txt"
echo ""
echo "To save a report:"
echo "  python main.py your_cv.pdf your_job_description.txt --output report.txt"
echo "================================"

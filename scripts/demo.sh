#!/bin/bash

# ATS CV Improver - Demo Script
# Demonstrates the full CV improvement workflow

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ATS CV Maker - Improvement Demo                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if files exist
if [ ! -f "examples/sample_cv.txt" ] || [ ! -f "examples/sample_job_description.txt" ]; then
    echo "❌ Sample files not found!"
    echo "   Please ensure examples/sample_cv.txt and examples/sample_job_description.txt exist"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys!"
    echo "   Press Enter after adding your API keys..."
    read
fi

echo "════════════════════════════════════════════════════════════"
echo " Step 1: Analyze Original CV"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Running initial analysis..."
echo ""

python improve_cv.py examples/sample_cv.txt examples/sample_job_description.txt --analyze-only

echo ""
echo "Press Enter to continue to CV improvement..."
read

echo ""
echo "════════════════════════════════════════════════════════════"
echo " Step 2: Improve CV and Generate PDF"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Running full improvement workflow..."
echo ""

python improve_cv.py examples/sample_cv.txt examples/sample_job_description.txt --output demo_improved_cv --max-keywords 8

echo ""
echo "════════════════════════════════════════════════════════════"
echo " ✅ Demo Complete!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📁 Check these output files:"
echo "   • cv_sections/                   - Original CV sections"
echo "   • improved_cv_sections/          - Improved sections with keywords"
echo "   • improved_cv_sections/placement_notes.txt - Details on what was added"
echo "   • demo_improved_cv.tex          - LaTeX source"
echo "   • demo_improved_cv.pdf          - Final PDF (if LaTeX installed)"
echo ""
echo "💡 To view the improved CV:"
if [ -f "demo_improved_cv.pdf" ]; then
    echo "   open demo_improved_cv.pdf"
else
    echo "   Install LaTeX and run: pdflatex demo_improved_cv.tex"
fi
echo ""

#!/bin/bash
# Quick start script for Financial News Auto-Generation System

set -e

echo "=========================================="
echo "Financial News Auto-Generation System"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env file and add your CLAUDE_API_KEY"
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run health check
echo "Running health check..."
python main.py --health-check

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "System ready!"
    echo "=========================================="
    echo ""
    echo "Available commands:"
    echo "  python main.py                    # Start scheduler"
    echo "  python main.py --run-once daily   # Generate daily news"
    echo "  python main.py --run-once market  # Generate market update"
    echo "  python main.py --run-once weekly  # Generate weekly summary"
    echo "  python test_system.py             # Run tests"
    echo ""
else
    echo ""
    echo "❌ Health check failed!"
    echo "Please check the error messages above and fix the issues."
    exit 1
fi

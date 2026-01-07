#!/bin/bash
# Setup script for Lighter Pair Monitor

set -e

echo "Setting up Lighter Pair Monitor..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || . venv/Scripts/activate

echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create data directory
mkdir -p .data

echo ""
echo "================================"
echo "Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your settings"
echo "2. Run once to test: python3 monitor.py"
echo "3. For continuous monitoring: python3 scheduler.py"
echo ""
echo "For more information, see README.md"

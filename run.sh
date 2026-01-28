#!/bin/bash
echo "🏀 Starting Roster Scraper..."
echo ""

# Detect which pip/python to use
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Error: Python not found. Please install Python 3.7 or higher."
    exit 1
fi

echo "Using: $PYTHON_CMD"
echo ""

# Install dependencies
echo "Installing dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet --user

if [ $? -ne 0 ]; then
    echo "⚠️  Pip install failed. Trying without --quiet flag..."
    $PYTHON_CMD -m pip install -r requirements.txt --user
fi

echo ""
echo "Starting server..."
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

$PYTHON_CMD app.py

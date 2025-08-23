#!/bin/bash
# GPS Analysis Suite - Linux/Mac Launcher
# Double-click this file to start the GPS Analysis Suite

# Get the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

echo ""
echo " ====================================================="
echo "  🦅 Bearded Vulture GPS Analysis Suite"
echo " ====================================================="
echo ""
echo "  Starting application..."
echo ""

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 main.py
elif command -v python &> /dev/null; then
    python main.py
else
    echo "❌ Error: Python not found"
    echo ""
    echo "🔧 Please install Python 3.8 or later:"
    echo "   Ubuntu/Debian: sudo apt install python3"
    echo "   macOS: brew install python3"
    echo "   Or download from: https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
fi

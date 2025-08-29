#!/bin/bash
# GPS Analysis Suite - Build Script
# Creates standalone executable for easy distribution

echo "🦅 Building GPS Analysis Suite..."
echo "================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the GPS_make_BGs_fly directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install PyInstaller if not present
if ! pip list | grep -q PyInstaller; then
    echo "📥 Installing PyInstaller..."
    pip install pyinstaller
fi

# Create version file
echo "🏷️  Creating version info..."
echo "1.0.0" > version.txt
echo "GPS Analysis Suite v1.0.0" >> version.txt
echo "Built on $(date)" >> version.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the application
echo "🔨 Building standalone executable..."
echo "   This may take a few minutes..."

if pyinstaller --clean GPS_Analysis_Suite.spec; then
    echo "✅ Build completed successfully!"
    echo ""
    echo "📁 Output location: ./dist/GPS_Analysis_Suite"
    echo ""
    echo "📦 Distribution package created!"
    echo "   - Size: $(du -sh dist/GPS_Analysis_Suite | cut -f1)"
    echo "   - Ready for distribution"
    echo ""
    echo "🚀 To test the executable:"
    echo "   ./dist/GPS_Analysis_Suite"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Test the executable on your system"
    echo "   2. Create a release on GitHub"
    echo "   3. Upload the executable to the release"
    echo "   4. Users can download and run without installing Python!"
else
    echo "❌ Build failed!"
    exit 1
fi

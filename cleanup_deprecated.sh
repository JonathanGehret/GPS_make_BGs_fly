#!/bin/bash
# Quick cleanup script for deprecated files
# Run this if VS Code or other editors recreate unwanted files

echo "🧹 Cleaning up deprecated files..."

# Remove deprecated script patterns
find scripts/ -name "*_professional.py" -delete 2>/dev/null
find scripts/ -name "*_optimized.py" -delete 2>/dev/null
find scripts/ -name "animate_2d.py" -delete 2>/dev/null
find scripts/ -name "animate_3d_*.py" ! -name "animation_3d.py" -delete 2>/dev/null
find scripts/ -name "plot_*.py" -delete 2>/dev/null
find scripts/ -name "demo_*.py" -delete 2>/dev/null
find scripts/ -name "export_test_data.py" -delete 2>/dev/null

# Remove deprecated directories
rm -rf scripts/main_scripts 2>/dev/null

# Remove empty Python files (often created by auto-recovery)
find scripts/ -name "*.py" -size 0 -delete 2>/dev/null

# Remove root-level markdown documentation files (keep READMEs)
find . -maxdepth 1 -name "*.md" ! -name "README*" -delete 2>/dev/null

echo "✅ Cleanup complete!"
echo "📁 Current scripts directory contents:"
ls scripts/

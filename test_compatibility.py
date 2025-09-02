#!/usr/bin/env python3
"""
Cross-Platform Compatibility Test

This script tests if all GPS Analysis Suite components
work correctly on the current platform.
"""

import os
import sys
import platform

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    tests = [
        ("tkinter", "GUI framework"),
        ("pandas", "Data processing"),
        ("numpy", "Numerical computing"),
        ("matplotlib", "Basic plotting"),
        ("plotly", "Interactive plotting"),
        ("requests", "HTTP requests"),
    ]
    
    failed = []
    for module, description in tests:
        try:
            __import__(module)
            print(f"  ✅ {module:<12} - {description}")
        except ImportError:
            print(f"  ❌ {module:<12} - {description} - MISSING")
            failed.append(module)
    
    return failed

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "gui/analysis_mode_selector.py",
        "gui/live_map_2d_gui.py",
        "scripts/animate_live_map.py",
        "scripts/utils/animation_controls.py",
        "scripts/gps_utils.py",
        "data",
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    return missing

def test_data_folder():
    """Test data folder contents"""
    print("\n📊 Testing data folder...")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"  ❌ Data directory not found: {data_dir}")
        return False
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    if csv_files:
        print(f"  ✅ Found {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"    - {csv_file}")
        return True
    else:
        print("  ⚠️  No CSV files found in data directory")
        return False

def main():
    """Run compatibility tests"""
    print("=" * 60)
    print("🦅 GPS Analysis Suite - Compatibility Test")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60)
    
    # Run tests
    failed_imports = test_imports()
    missing_files = test_file_structure()
    data_ok = test_data_folder()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 COMPATIBILITY TEST SUMMARY")
    print("=" * 60)
    
    if not failed_imports and not missing_files and data_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ GPS Analysis Suite should work correctly on this platform")
        exit_code = 0
    else:
        print("❌ SOME TESTS FAILED:")
        
        if failed_imports:
            print(f"  📦 Missing packages: {', '.join(failed_imports)}")
            print("     💡 Install with: pip install -r requirements.txt")
        
        if missing_files:
            print(f"  📁 Missing files: {', '.join(missing_files)}")
            print("     💡 Make sure you have the complete source code")
        
        if not data_ok:
            print("  📊 Data folder issues detected")
            print("     💡 Make sure the data folder contains CSV files")
        
        exit_code = 1
    
    print("=" * 60)
    
    # Windows-specific instructions
    if platform.system() == "Windows":
        print("\n🪟 WINDOWS BUILD INSTRUCTIONS:")
        print("1. Install Python 3.8+ from python.org")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: pip install pyinstaller")
        print("4. Double-click: build_windows.bat")
        print("5. Executable will be in: dist\\GPS_Analysis_Suite.exe")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

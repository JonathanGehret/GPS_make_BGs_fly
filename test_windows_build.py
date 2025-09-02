#!/usr/bin/env python3
"""
Quick Windows Build Test

This script tests if the GPS Analysis Suite can be built on Windows
Run this BEFORE attempting the full build to catch issues early.
"""

import sys
import os
import subprocess

def test_python_version():
    """Test Python version compatibility"""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   GPS Analysis Suite requires Python 3.8 or later")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def test_pip():
    """Test pip installation"""
    print("📦 Testing pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ pip available: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip not working")
            return False
    except Exception as e:
        print(f"❌ pip test failed: {e}")
        return False

def test_critical_imports():
    """Test critical package imports"""
    print("📚 Testing critical imports...")
    
    critical_packages = [
        ("tkinter", "GUI framework"),
        ("os", "Operating system interface"),
        ("sys", "System-specific parameters"),
        ("subprocess", "Process management"),
        ("pathlib", "File path handling"),
    ]
    
    failed = []
    for package, description in critical_packages:
        try:
            __import__(package)
            print(f"  ✅ {package:<12} - {description}")
        except ImportError:
            print(f"  ❌ {package:<12} - {description} - MISSING")
            failed.append(package)
    
    return len(failed) == 0

def test_file_structure():
    """Test required files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt", 
        "GPS_Analysis_Suite.spec",
        "gui/analysis_mode_selector.py",
        "gui/live_map_2d_gui.py",
        "scripts/animate_live_map.py",
        "scripts/gps_utils.py",
    ]
    
    missing = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    return len(missing) == 0

def test_pyinstaller_install():
    """Test if PyInstaller can be installed"""
    print("🔨 Testing PyInstaller installation...")
    try:
        # Try importing first
        import PyInstaller
        print("✅ PyInstaller already installed")
        return True
    except ImportError:
        print("⚠️  PyInstaller not installed, testing installation...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ PyInstaller installed successfully")
                return True
            else:
                print(f"❌ PyInstaller installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ PyInstaller installation error: {e}")
            return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🪟 GPS Analysis Suite - Windows Build Test")
    print("=" * 60)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("pip Availability", test_pip),
        ("Critical Imports", test_critical_imports),
        ("File Structure", test_file_structure),
        ("PyInstaller", test_pyinstaller_install),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 WINDOWS BUILD TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your system is ready for Windows build")
        print("\n🚀 Next steps:")
        print("   1. Run: build_windows_enhanced.bat")
        print("   2. Or run: build_windows.bat")
        print("   3. Or follow: WINDOWS_BUILD_GUIDE.md")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n🔧 Fix the failed tests before building:")
        
        for test_name, result in results:
            if not result:
                if "Python Version" in test_name:
                    print(f"   • {test_name}: Install Python 3.8+ from python.org")
                elif "pip" in test_name:
                    print(f"   • {test_name}: Run 'python -m ensurepip --upgrade'")
                elif "Critical Imports" in test_name:
                    print(f"   • {test_name}: Reinstall Python with all components")
                elif "File Structure" in test_name:
                    print(f"   • {test_name}: Download complete source code")
                elif "PyInstaller" in test_name:
                    print(f"   • {test_name}: Run 'pip install pyinstaller'")
        
        print("\n📖 For detailed help: WINDOWS_BUILD_GUIDE.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())

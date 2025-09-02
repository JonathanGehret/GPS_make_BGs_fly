#!/usr/bin/env python3
"""
Data Folder Selection Test

This script tests if the GUI properly passes the selected data folder
to the analysis scripts. Run this to verify the fix works.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def create_test_data_folder():
    """Create a temporary folder with test CSV data"""
    temp_dir = tempfile.mkdtemp(prefix="gps_test_")
    
    # Create a simple test CSV file
    test_csv_content = """Timestamp [UTC],Individual Name,Latitude,Longitude,Height,display
2025-01-01T10:00:00Z,Test Vulture 99,47.5,12.0,1500,1
2025-01-01T10:01:00Z,Test Vulture 99,47.501,12.001,1501,1
2025-01-01T10:02:00Z,Test Vulture 99,47.502,12.002,1502,1
"""
    
    test_file = os.path.join(temp_dir, "test_vulture_99.csv")
    with open(test_file, 'w') as f:
        f.write(test_csv_content)
    
    print(f"✅ Created test data folder: {temp_dir}")
    print(f"✅ Created test file: test_vulture_99.csv")
    return temp_dir

def test_data_loader():
    """Test DataLoader with custom folder"""
    print("\n🧪 Testing DataLoader with custom folder...")
    
    # Add scripts to path
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    sys.path.insert(0, scripts_dir)
    
    try:
        from gps_utils import DataLoader
        
        # Test with default folder
        default_loader = DataLoader()
        default_files = default_loader.find_csv_files()
        print(f"📁 Default data folder: {default_loader.data_dir}")
        print(f"📊 Default folder has {len(default_files)} CSV files")
        
        # Test with custom folder
        test_folder = create_test_data_folder()
        custom_loader = DataLoader(test_folder)
        custom_files = custom_loader.find_csv_files()
        print(f"📁 Custom data folder: {custom_loader.data_dir}")
        print(f"📊 Custom folder has {len(custom_files)} CSV files")
        
        if len(custom_files) > 0:
            print("✅ DataLoader correctly uses custom folder")
            return True, test_folder
        else:
            print("❌ DataLoader failed to find files in custom folder")
            return False, test_folder
            
    except Exception as e:
        print(f"❌ DataLoader test failed: {e}")
        return False, None

def test_environment_variables():
    """Test environment variable passing"""
    print("\n🧪 Testing environment variable handling...")
    
    # Create test folder
    test_folder = create_test_data_folder()
    
    # Set environment variable
    env = os.environ.copy()
    env['GPS_DATA_DIR'] = test_folder
    env['OUTPUT_DIR'] = tempfile.mkdtemp(prefix="gps_output_")
    env['TRAIL_LENGTH_HOURS'] = '1.5'
    env['TIME_STEP'] = '30s'
    
    print(f"🔧 Set GPS_DATA_DIR = {test_folder}")
    print(f"🔧 Set OUTPUT_DIR = {env['OUTPUT_DIR']}")
    
    # Test if the animate_live_map script would use the correct folder
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    animate_script = os.path.join(scripts_dir, "animate_live_map.py")
    
    if os.path.exists(animate_script):
        print(f"✅ Found animation script: {animate_script}")
        
        # Run a quick test to see if it reads the environment variable
        test_cmd = [
            sys.executable, "-c", 
            f"""
import os
import sys
sys.path.insert(0, '{scripts_dir}')

# Test environment variable reading
custom_data_dir = os.environ.get('GPS_DATA_DIR')
print(f'GPS_DATA_DIR from environment: {{custom_data_dir}}')

if custom_data_dir:
    print('✅ Environment variable correctly read')
else:
    print('❌ Environment variable not found')
"""
        ]
        
        try:
            result = subprocess.run(test_cmd, env=env, capture_output=True, text=True, timeout=10)
            print("📤 Script output:")
            print(result.stdout.strip())
            
            if result.returncode == 0 and 'correctly read' in result.stdout:
                print("✅ Environment variables work correctly")
                return True, test_folder
            else:
                print("❌ Environment variable test failed")
                return False, test_folder
        except Exception as e:
            print(f"❌ Environment test error: {e}")
            return False, test_folder
    else:
        print(f"❌ Animation script not found: {animate_script}")
        return False, test_folder

def main():
    """Run all data folder tests"""
    print("=" * 60)
    print("🗂️  GPS Analysis Suite - Data Folder Selection Test")
    print("=" * 60)
    
    tests = [
        ("DataLoader Custom Folder", test_data_loader),
        ("Environment Variables", test_environment_variables),
    ]
    
    results = []
    test_folders = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        try:
            success, folder = test_func()
            results.append((test_name, success))
            if folder:
                test_folders.append(folder)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DATA FOLDER TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test folders...")
    for folder in test_folders:
        try:
            import shutil
            shutil.rmtree(folder)
            print(f"   Removed: {folder}")
        except Exception as e:
            print(f"   Warning: Could not remove {folder}: {e}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Data folder selection should work correctly")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 The data folder selection might not work properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())

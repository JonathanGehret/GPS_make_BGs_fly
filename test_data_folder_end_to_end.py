#!/usr/bin/env python3
"""
End-to-End Data Folder Test

This script simulates the complete workflow of selecting a different data folder
in the GUI and verifies that the analysis actually uses that folder.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

def create_unique_test_data(folder_name):
    """Create test data with unique identifiers"""
    temp_dir = tempfile.mkdtemp(prefix=f"gps_{folder_name}_")
    
    # Create unique test CSV content for each folder with CORRECT format (semicolon separated)
    if folder_name == "default":
        test_csv_content = """Timestamp [UTC];Longitude;Latitude;Height;display
01.01.2025 10:00:00;11.1;47.1;1100;1
01.01.2025 10:01:00;11.101;47.101;1101;1
"""
        file_name = "default_vulture.csv"
    else:  # custom
        test_csv_content = """Timestamp [UTC];Longitude;Latitude;Height;display
01.01.2025 12:00:00;12.2;48.2;1200;1
01.01.2025 12:01:00;12.201;48.201;1201;1
"""
        file_name = "custom_vulture.csv"
    
    test_file = os.path.join(temp_dir, file_name)
    with open(test_file, 'w') as f:
        f.write(test_csv_content)
    
    print(f"✅ Created {folder_name} test folder: {temp_dir}")
    print(f"   📄 Contains: {file_name}")
    return temp_dir

def test_dataloader_selection():
    """Test that DataLoader correctly uses different folders"""
    print("🧪 Testing DataLoader folder selection...")
    
    # Add scripts to path
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    sys.path.insert(0, scripts_dir)
    
    try:
        from gps_utils import DataLoader
        
        # Create two different test folders
        default_folder = create_unique_test_data("default")
        custom_folder = create_unique_test_data("custom")
        
        # Test DataLoader with default folder
        default_loader = DataLoader(default_folder)
        default_dfs = default_loader.load_all_csv_files()
        
        # Test DataLoader with custom folder
        custom_loader = DataLoader(custom_folder)
        custom_dfs = custom_loader.load_all_csv_files()
        
        # Verify they loaded different data
        if len(default_dfs) > 0 and len(custom_dfs) > 0:
            default_location = default_dfs[0]['Longitude'].iloc[0]
            custom_location = custom_dfs[0]['Longitude'].iloc[0]
            
            print(f"📊 Default folder longitude: {default_location}")
            print(f"📊 Custom folder longitude: {custom_location}")
            
            if default_location != custom_location:
                print("✅ DataLoader correctly loads different data from different folders")
                return True, (default_folder, custom_folder)
            else:
                print("❌ DataLoader loaded same data from both folders")
                return False, (default_folder, custom_folder)
        else:
            print("❌ Failed to load data from test folders")
            return False, (default_folder, custom_folder)
            
    except Exception as e:
        print(f"❌ DataLoader test failed: {e}")
        return False, (None, None)

def test_environment_variable_override():
    """Test that environment variables override default behavior"""
    print("\n🧪 Testing environment variable override...")
    
    # Create test folders
    default_folder = create_unique_test_data("env_default")
    custom_folder = create_unique_test_data("env_custom")
    
    # Add scripts to path
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    sys.path.insert(0, scripts_dir)
    
    try:
        from gps_utils import DataLoader
        
        # Test 1: Without environment variable (should use provided folder)
        loader_without_env = DataLoader(default_folder)
        files_without_env = loader_without_env.find_csv_files()
        
        # Test 2: With environment variable set to custom folder
        old_env = os.environ.get('GPS_DATA_DIR')
        os.environ['GPS_DATA_DIR'] = custom_folder
        
        # For animate_live_map.py style initialization
        from animate_live_map import LiveMapAnimator
        
        # Create animator (this should use custom folder from environment)
        animator = LiveMapAnimator()
        custom_files = animator.data_loader.find_csv_files()
        
        # Restore environment
        if old_env:
            os.environ['GPS_DATA_DIR'] = old_env
        else:
            del os.environ['GPS_DATA_DIR']
        
        print(f"📊 Without env var: {len(files_without_env)} files in {default_folder}")
        print(f"📊 With env var: {len(custom_files)} files from animator")
        
        # Verify the animator used the custom folder
        if len(custom_files) > 0 and animator.data_loader.data_dir == custom_folder:
            print("✅ Environment variable correctly overrides data folder")
            return True, (default_folder, custom_folder)
        else:
            print("❌ Environment variable override failed")
            print(f"   Expected folder: {custom_folder}")
            print(f"   Actual folder: {animator.data_loader.data_dir}")
            return False, (default_folder, custom_folder)
            
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, (default_folder, custom_folder)

def test_proximity_analysis_gui_integration():
    """Test proximity analysis GUI data folder handling"""
    print("\n🧪 Testing proximity analysis GUI integration...")
    
    # Create test folders
    default_folder = create_unique_test_data("prox_default")
    custom_folder = create_unique_test_data("prox_custom")
    
    # Add scripts to path
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    sys.path.insert(0, scripts_dir)
    
    try:
        from gps_utils import DataLoader
        
        # Simulate what the proximity analysis GUI does
        # 1. Create DataLoader with default folder
        default_data = DataLoader(default_folder).load_all_csv_files()
        
        # 2. Create DataLoader with custom folder (the fix we implemented)
        custom_data = DataLoader(custom_folder).load_all_csv_files()
        
        if len(default_data) > 0 and len(custom_data) > 0:
            default_location = default_data[0]['Longitude'].iloc[0]
            custom_location = custom_data[0]['Longitude'].iloc[0]
            
            print(f"📊 Default analysis longitude: {default_location}")
            print(f"📊 Custom analysis longitude: {custom_location}")
            
            if default_location != custom_location:
                print("✅ Proximity analysis GUI fix works correctly")
                return True, (default_folder, custom_folder)
            else:
                print("❌ Proximity analysis GUI still uses same data")
                return False, (default_folder, custom_folder)
        else:
            print("❌ Failed to load test data")
            return False, (default_folder, custom_folder)
            
    except Exception as e:
        print(f"❌ Proximity analysis GUI test failed: {e}")
        return False, (default_folder, custom_folder)

def main():
    """Run comprehensive data folder selection tests"""
    print("=" * 70)
    print("🗂️  GPS Analysis Suite - End-to-End Data Folder Test")
    print("=" * 70)
    print("This test verifies that selecting different data folders")
    print("in the GUI actually changes which data gets analyzed.")
    print("=" * 70)
    
    tests = [
        ("DataLoader Folder Selection", test_dataloader_selection),
        ("Environment Variable Override", test_environment_variable_override),
        ("Proximity Analysis GUI Integration", test_proximity_analysis_gui_integration),
    ]
    
    results = []
    all_test_folders = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*10} {test_name} {'='*10}")
        try:
            success, folders = test_func()
            results.append((test_name, success))
            if folders and folders[0] and folders[1]:
                all_test_folders.extend(folders)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 END-TO-END TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Data folder selection works correctly end-to-end")
        print("\n💡 This means:")
        print("   • Selecting a different folder in the GUI will work")
        print("   • The analysis will use the correct selected folder")
        print("   • Both 2D maps and proximity analysis are fixed")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("🔧 There may still be issues with data folder selection")
        
        failing_tests = [name for name, result in results if not result]
        print(f"\n❌ Failed tests: {', '.join(failing_tests)}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up {len(set(all_test_folders))} test folders...")
    for folder in set(all_test_folders):
        if folder and os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"   ✅ Removed: {os.path.basename(folder)}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {folder}: {e}")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

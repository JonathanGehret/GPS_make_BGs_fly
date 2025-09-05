#!/usr/bin/env python3
"""
Test script to verify that the folder opening functionality works correctly
"""

import os
import subprocess
import platform

def test_folder_opening():
    """Test opening a folder with the system file manager"""
    test_folder = "/home/jonathan/development/GPS_make_BGs_fly/visualizations"
    
    print(f"🧪 Testing folder opening functionality")
    print(f"📁 Test folder: {test_folder}")
    print(f"💻 Operating system: {platform.system()}")
    
    if not os.path.exists(test_folder):
        print(f"❌ Test folder does not exist: {test_folder}")
        return False
    
    try:
        system = platform.system()
        
        if system == "Windows":
            # Windows: use explorer
            subprocess.run(['explorer', test_folder], check=True)
            print("✅ Windows: Used 'explorer' command")
        elif system == "Darwin":
            # macOS: use open
            subprocess.run(['open', test_folder], check=True)
            print("✅ macOS: Used 'open' command")
        else:
            # Linux and others: use xdg-open
            subprocess.run(['xdg-open', test_folder], check=True)
            print("✅ Linux: Used 'xdg-open' command")
        
        print(f"🎉 Successfully opened folder in system file manager!")
        return True
        
    except Exception as e:
        print(f"❌ Error opening folder: {e}")
        return False

if __name__ == "__main__":
    success = test_folder_opening()
    print()
    if success:
        print("✅ Folder opening test passed! The GUI should now open folders in the file manager.")
    else:
        print("❌ Folder opening test failed. Please check the error above.")

#!/usr/bin/env python3
"""
GPS Analysis Suite - Main Launcher

🦅 Bearded Vulture GPS Analysis Suite
Double-click this file to launch the complete GPS analysis application.

Features:
- 2D Live Map Visualization
- 3D Terrain Visualization  
- Proximity Analysis
- Bilingual Interface (German/English)
"""

import sys
import os
import subprocess

def main():
    """Launch the GPS Analysis Suite"""
    try:
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script = os.path.join(script_dir, 'gui', 'analysis_mode_selector.py')
        
        # Check if GUI script exists
        if not os.path.exists(gui_script):
            print("❌ Error: Main GUI script not found!")
            print(f"Looking for: {gui_script}")
            print("\n🔧 Please ensure all project files are present.")
            input("Press Enter to exit...")
            return 1
        
        print("🦅 Launching GPS Analysis Suite...")
        print("📁 Loading application...")
        
        # Launch the GUI
        if sys.platform.startswith('win'):
            # Windows - create new console window
            subprocess.run([sys.executable, gui_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Linux/Mac
            subprocess.run([sys.executable, gui_script])
            
        return 0
        
    except Exception as e:
        print(f"❌ Failed to launch GPS Analysis Suite: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Python 3.8+ is installed")
        print("2. Make sure you're in the GPS_make_BGs_fly directory")
        print("3. Check that all required files are present")
        print("4. Try running: python3 main.py")
        input("\nPress Enter to exit...")
        return 1

if __name__ == "__main__":
    sys.exit(main())

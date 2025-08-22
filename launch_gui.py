#!/usr/bin/env python3
"""
Vulture Proximity Analysis - GUI Launcher

Double-click this file to launch the Vulture Proximity Analysis GUI application.
"""

import sys
import os
import subprocess

def main():
    """Launch the GUI application"""
    try:
        # Get the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        gui_script = os.path.join(script_dir, 'scripts', 'proximity_analysis_gui.py')
        
        # Check if GUI script exists
        if not os.path.exists(gui_script):
            print("❌ Error: GUI script not found!")
            print(f"Looking for: {gui_script}")
            input("Press Enter to exit...")
            return
        
        print("🦅 Launching Vulture Proximity Analysis GUI...")
        print("📁 Loading application...")
        
        # Launch the GUI
        if sys.platform.startswith('win'):
            # Windows
            subprocess.Popen([sys.executable, gui_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Linux/Mac
            subprocess.Popen([sys.executable, gui_script])
            
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Python is installed")
        print("2. Make sure you're in the correct directory")
        print("3. Check that all required files are present")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

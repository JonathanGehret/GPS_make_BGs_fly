#!/usr/bin/env python3
"""
Main GPS Analysis Launcher
Entry point for the GPS Analysis Suite
"""

import subprocess
import sys
import os

def main():
    """Launch the main GPS analysis mode selector"""
    script_path = os.path.join(os.path.dirname(__file__), "gui", "analysis_mode_selector.py")
    
    if not os.path.exists(script_path):
        print(f"Error: Main GUI not found at {script_path}")
        return 1
    
    try:
        subprocess.run([sys.executable, script_path])
        return 0
    except Exception as e:
        print(f"Error launching GPS Analysis Suite: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

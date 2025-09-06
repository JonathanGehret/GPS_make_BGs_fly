#!/usr/bin/env python3
"""
GPS Analysis Suite - Main Launcher

🦅 Bearded Vulture GPS Analysis Suite
Double-click this file to launch the complete GPS analysis application.

Features:
- 2D Live Map Visualization
- Proximity Analysis
- Bilingual Interface (German/English)
"""

import sys
import os

# Version information
__version__ = "1.0.0"
__author__ = "Jonathan Gehret"
__description__ = "GPS Analysis Suite for Bearded Vulture tracking and analysis"

def main():
    """Launch the GPS Analysis Suite"""
    try:
        print("🦅 Launching GPS Analysis Suite...")
        
        # Check if we're running as a PyInstaller bundle
        if getattr(sys, '_MEIPASS', False):
            # Running as standalone executable - import and run GUI directly
            print("📦 Running as standalone executable...")
            
            # Add bundle directory to Python path
            bundle_dir = sys._MEIPASS
            if bundle_dir not in sys.path:
                sys.path.insert(0, bundle_dir)
            
            # Check command line arguments for specific GUI launch
            if len(sys.argv) > 1:
                gui_mode = sys.argv[1]
                print(f"🎯 Launching specific GUI: {gui_mode}")
                
                if gui_mode == "--2d-map":
                    # Import and run 2D map GUI
                    try:
                        from gui.live_map_2d_gui import main as gui_main
                        print("✅ 2D Map GUI module loaded successfully")
                        return gui_main()
                    except Exception as e:
                        print(f"❌ Failed to launch 2D Map GUI: {e}")
                        return 1
                        
                elif gui_mode == "--proximity":
                    # Import and run proximity analysis GUI
                    try:
                        # Ensure bundle path is set up correctly
                        if getattr(sys, '_MEIPASS', False):
                            bundle_dir = sys._MEIPASS
                            if bundle_dir not in sys.path:
                                sys.path.insert(0, bundle_dir)
                            # Also add the scripts directory to path
                            scripts_dir = os.path.join(bundle_dir, 'scripts')
                            if scripts_dir not in sys.path:
                                sys.path.insert(0, scripts_dir)
                        
                        from gui.proximity_analysis_gui import main as gui_main
                        print("✅ Proximity Analysis GUI module loaded successfully")
                        return gui_main()
                    except Exception as e:
                        print(f"❌ Failed to launch Proximity Analysis GUI: {e}")
                        import traceback
                        traceback.print_exc()
                        return 1
                else:
                    print(f"❌ Unknown GUI mode: {gui_mode}")
                    return 1
            else:
                # Launch main GUI
                try:
                    from gui.analysis_mode_selector import main as gui_main
                    print("✅ GUI module loaded successfully")
                    return gui_main()
                except ImportError as e:
                    print(f"❌ Failed to import GUI module: {e}")
                    print(f"Bundle directory: {bundle_dir}")
                    print("Files in bundle:")
                    for item in os.listdir(bundle_dir):
                        print(f"  - {item}")
                    return 1
                except Exception as e:
                    print(f"❌ Failed to run GUI: {e}")
                    return 1
                
        else:
            # Running in development mode
            print("🔧 Running in development mode...")
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            gui_script = os.path.join(script_dir, 'gui', 'analysis_mode_selector.py')
            
            if not os.path.exists(gui_script):
                print("❌ Error: GUI script not found in development mode!")
                print(f"Looking for: {gui_script}")
                return 1
            
            # Import and run GUI directly in development
            try:
                sys.path.insert(0, script_dir)
                from gui.analysis_mode_selector import main as gui_main
                return gui_main()
            except Exception as e:
                print(f"❌ Failed to run GUI in development mode: {e}")
                return 1
    
    except Exception as e:
        print(f"❌ Failed to launch GPS Analysis Suite: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

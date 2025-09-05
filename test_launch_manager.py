#!/usr/bin/env python3
"""
Test script for LaunchManager component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.launch_manager import LaunchManager
    from components.folder_manager import FolderManager
    from components.settings_manager import SettingsManager
    print("Successfully imported LaunchManager and dependencies")
except ImportError as e:
    print(f"Failed to import components: {e}")
    sys.exit(1)

def test_launch_manager():
    root = tk.Tk()
    root.title("LaunchManager Component Test")
    root.geometry("500x300")
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Status label
    status_label = ttk.Label(main_frame, text="Status: Ready")
    status_label.grid(row=0, column=0, pady=5, sticky="ew")
    
    def get_language():
        return 'en'
    
    # Mock configuration for testing
    test_config = {
        'data_folder': os.path.join(os.path.dirname(__file__), 'data'),
        'output_folder': os.path.join(os.path.dirname(__file__), 'visualizations'),
        'trail_length': 2.0,
        'time_step': '1m',
        'playback_speed': 1.0,
        'performance_mode': True
    }
    
    try:
        # Create LaunchManager component  
        launch_manager = LaunchManager(get_language)
        
        # Create mock folder_manager and settings_manager for testing
        folder_manager = FolderManager(main_frame, get_language)
        folder_manager.setup_ui()
        folder_manager.data_folder.set(test_config['data_folder'])
        folder_manager.output_folder.set(test_config['output_folder'])
        
        settings_manager = SettingsManager(main_frame, get_language)
        settings_manager.setup_ui()
        
        # Add test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10, sticky="ew")
        
        def test_launch():
            print("Testing launch with real components")
            status_label.config(text="Launching...")
            try:
                result = launch_manager.launch_map(folder_manager, settings_manager)
                if result:
                    status_label.config(text="Launch completed successfully")
                else:
                    status_label.config(text="Launch failed")
            except Exception as e:
                status_label.config(text=f"Launch error: {e}")
                print(f"Launch error: {e}")
                import traceback
                traceback.print_exc()
        
        def test_simple():
            # Just test that the LaunchManager can be created
            status_label.config(text="LaunchManager created successfully")
        
        ttk.Button(button_frame, text="Test Simple", command=test_simple).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Test Launch", command=test_launch).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=root.destroy).grid(row=0, column=2)
        
        print("LaunchManager component created successfully!")
        
        # Test simple creation
        test_simple()
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating LaunchManager: {e}")
        import traceback
        traceback.print_exc()
        ttk.Label(main_frame, text=f"Error: {e}").grid(row=3, column=0, columnspan=3)
        root.mainloop()

if __name__ == "__main__":
    test_launch_manager()

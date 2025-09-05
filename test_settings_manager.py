#!/usr/bin/env python3
"""
Test script for SettingsManager component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.settings_manager import SettingsManager
    print("Successfully imported SettingsManager")
except ImportError as e:
    print(f"Failed to import SettingsManager: {e}")
    sys.exit(1)

def test_settings_manager():
    root = tk.Tk()
    root.title("SettingsManager Component Test")
    root.geometry("600x500")
    
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
    
    def on_settings_changed():
        print("Settings changed")
        config = settings_manager.get_config()
        status_label.config(text=f"Config: {config}")
    
    try:
        # Create SettingsManager component
        settings_manager = SettingsManager(main_frame, get_language)
        settings_manager.setup_ui()
        
        # Add test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        def test_config():
            config = settings_manager.get_config()
            print(f"Current config: {config}")
            status_label.config(text=f"Config: {config}")
        
        def test_performance_mode():
            settings_manager.performance_mode.set(not settings_manager.performance_mode.get())
            test_config()
        
        ttk.Button(button_frame, text="Get Config", command=test_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Toggle Performance", command=test_performance_mode).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=root.destroy).grid(row=0, column=2)
        
        print("SettingsManager component created successfully!")
        
        # Test initial config
        test_config()
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating SettingsManager: {e}")
        import traceback
        traceback.print_exc()
        ttk.Label(main_frame, text=f"Error: {e}").grid(row=3, column=0, columnspan=3)
        root.mainloop()

if __name__ == "__main__":
    test_settings_manager()

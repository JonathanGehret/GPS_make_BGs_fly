#!/usr/bin/env python3
"""
Test script for ModeSelector component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.mode_selector import ModeSelector
    print("Successfully imported ModeSelector")
except ImportError as e:
    print(f"Failed to import ModeSelector: {e}")
    sys.exit(1)

def test_mode_selector():
    root = tk.Tk()
    root.title("ModeSelector Component Test")
    root.geometry("600x400")
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Status label
    status_label = ttk.Label(main_frame, text="Status: Ready")
    status_label.grid(row=1, column=0, pady=5, sticky="ew")
    
    def get_language():
        return 'en'
    
    def on_mode_changed(mode_key, mode_info):
        print(f"Mode changed to: {mode_key} - {mode_info['display_name']}")
        status_label.config(text=f"Selected: {mode_info['display_name']} -> {mode_info['script']}")
    
    try:
        # Create ModeSelector component
        mode_selector = ModeSelector(main_frame, get_language)
        mode_selector.set_mode_change_callback(on_mode_changed)
        mode_selector.setup_ui()
        
        # Add test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        def test_get_mode():
            mode = mode_selector.get_selected_mode()
            script = mode_selector.get_selected_script()
            mode_info = mode_selector.get_selected_mode_info()
            print(f"Current mode: {mode}")
            print(f"Script: {script}")
            print(f"Info: {mode_info}")
            status_label.config(text=f"Mode: {mode}, Script: {script}")
        
        def test_set_mobile():
            mode_selector.set_mode('mobile_animation')
        
        def test_set_3d():
            mode_selector.set_mode('3d_animation')
        
        def test_add_custom():
            mode_selector.add_mode(
                'custom_mode', 
                'Custom Animation', 
                'Custom animation mode for testing',
                'custom_script.py',
                '🔧'
            )
            print("Added custom mode")
        
        ttk.Button(button_frame, text="Get Mode Info", command=test_get_mode).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Set Mobile", command=test_set_mobile).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Set 3D", command=test_set_3d).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Add Custom", command=test_add_custom).grid(row=0, column=3, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=root.destroy).grid(row=0, column=4)
        
        print("ModeSelector component created successfully!")
        
        # Test initial mode
        test_get_mode()
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating ModeSelector: {e}")
        import traceback
        traceback.print_exc()
        ttk.Label(main_frame, text=f"Error: {e}").grid(row=3, column=0, columnspan=5)
        root.mainloop()

if __name__ == "__main__":
    test_mode_selector()

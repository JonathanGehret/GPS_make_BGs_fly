#!/usr/bin/env python3
"""
Test script for DataPreview component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.data_preview import DataPreview
    print("Successfully imported DataPreview")
except ImportError as e:
    print(f"Failed to import DataPreview: {e}")
    sys.exit(1)

def test_data_preview():
    root = tk.Tk()
    root.title("DataPreview Component Test")
    root.geometry("800x600")
    
    # Configure root grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=1)  # Make data_preview expandable
    
    # Status label
    status_label = ttk.Label(main_frame, text="Status: Ready")
    status_label.grid(row=0, column=0, pady=5, sticky="ew")
    
    def get_language():
        return 'en'
    
    def on_data_changed():
        print("Data preview changed")
        file_count = data_preview.get_file_count()
        total_points = data_preview.get_total_points()
        status_label.config(text=f"Files: {file_count}, Points: {total_points}")
    
    try:
        # Create DataPreview component
        data_preview = DataPreview(main_frame, get_language)
        
        # Set up data folder variable
        data_folder_var = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "data"))
        data_preview.set_data_folder_var(data_folder_var)
        
        data_preview.setup_ui()
        
        # Add some test buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10, sticky="ew")
        
        def test_refresh():
            # Test refresh with current data folder
            data_preview.refresh_preview()
            on_data_changed()
        
        def change_folder():
            # Test changing folder
            new_folder = os.path.join(os.path.dirname(__file__), "data")
            if os.path.exists(new_folder):
                data_folder_var.set(new_folder)
                test_refresh()
            else:
                status_label.config(text="No data folder found")
        
        ttk.Button(button_frame, text="Refresh Preview", command=test_refresh).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="Change Folder", command=change_folder).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=root.destroy).grid(row=0, column=2)
        
        print("DataPreview component created successfully!")
        
        # Test initial refresh
        test_refresh()
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating DataPreview: {e}")
        import traceback
        traceback.print_exc()
        ttk.Label(main_frame, text=f"Error: {e}").grid(row=3, column=0, columnspan=2)
        root.mainloop()

if __name__ == "__main__":
    test_data_preview()

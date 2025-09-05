#!/usr/bin/env python3
"""
Test FolderManager component in isolation
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.folder_manager import FolderManager
    print("Successfully imported FolderManager")
except ImportError as e:
    print(f"Failed to import FolderManager: {e}")
    sys.exit(1)

def test_folder_manager():
    root = tk.Tk()
    root.title("FolderManager Component Test")
    root.geometry("600x400")
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    # Configure grid weights for main frame
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    status_label = ttk.Label(main_frame, text="Status: Ready")
    status_label.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
    
    def on_folders_changed(data_folder, output_folder):
        print(f"Folders changed - Data: {data_folder}, Output: {output_folder}")
        status_label.config(text=f"Data: {data_folder or 'None'}, Output: {output_folder or 'None'}")
    
    def get_language():
        return 'en'
    
    try:
        folder_manager = FolderManager(main_frame, get_language)
        # Set up folder change callback
        folder_manager.set_data_folder_callback(lambda directory: on_folders_changed(
            directory, 
            folder_manager.output_folder.get()
        ))
        folder_manager.setup_ui()
        
        def test_folders():
            if folder_manager.validate_folders():
                print("Folders are valid!")
                status_label.config(text="Status: Folders validated successfully!")
            else:
                print("Folder validation failed")
                status_label.config(text="Status: Folder validation failed!")
        
        # Add test button using grid below the FolderManager (which uses row 0)
        ttk.Button(main_frame, text="Test Folders", command=test_folders).grid(row=2, column=0, columnspan=2, pady=10)
        
        print("FolderManager component created successfully!")
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating FolderManager: {e}")
        import traceback
        traceback.print_exc()
        ttk.Label(main_frame, text=f"Error: {e}").grid(row=3, column=0, columnspan=2)

if __name__ == "__main__":
    test_folder_manager()

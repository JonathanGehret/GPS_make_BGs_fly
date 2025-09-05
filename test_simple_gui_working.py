#!/usr/bin/env python3
"""
Simple GUI based on the working test pattern
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path to import components (same as working test)
gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

try:
    from components.folder_manager import FolderManager
    print("Successfully imported FolderManager")
except ImportError as e:
    print(f"Failed to import FolderManager: {e}")
    sys.exit(1)

def create_simple_gui():
    root = tk.Tk()
    root.title("2D Live Map - Simple Integration")
    root.geometry("600x400")
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    # Configure grid weights
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Title
    title_label = ttk.Label(main_frame, text="🗺️ 2D Live Map - Step 1: FolderManager", 
                           font=("Arial", 16, "bold"))
    title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
    
    # Status label
    status_label = ttk.Label(main_frame, text="Status: Ready")
    status_label.grid(row=1, column=0, pady=5, sticky="ew")
    
    def on_data_folder_changed(directory):
        print(f"Data folder changed to: {directory}")
        status_label.config(text=f"Data folder: {directory}")
    
    def get_language():
        return 'en'
    
    # Create FolderManager (exactly like working test)
    folder_manager = FolderManager(main_frame, get_language)
    folder_manager.set_data_folder_callback(on_data_folder_changed)
    folder_manager.setup_ui()
    
    # Settings section
    settings_frame = ttk.LabelFrame(main_frame, text="⚡ Settings", padding="10")
    settings_frame.grid(row=3, column=0, sticky="ew", pady=10)
    
    performance_mode = tk.BooleanVar(value=True)
    ttk.Checkbutton(settings_frame, text="Enable Performance Mode", 
                   variable=performance_mode).grid(row=0, column=0, sticky="w")
    
    # Buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=4, column=0, pady=20)
    
    def launch_action():
        data_folder = folder_manager.get_data_folder()
        output_folder = folder_manager.get_output_folder()
        print(f"Launch clicked - Data: {data_folder}, Output: {output_folder}")
        status_label.config(text=f"Data: {data_folder}, Output: {output_folder}")
    
    ttk.Button(button_frame, text="🚀 Launch", command=launch_action).grid(row=0, column=0, padx=(0, 10))
    ttk.Button(button_frame, text="❌ Close", command=root.destroy).grid(row=0, column=1)
    
    print("GUI created successfully - starting mainloop")
    root.mainloop()
    print("GUI closed")

if __name__ == "__main__":
    create_simple_gui()

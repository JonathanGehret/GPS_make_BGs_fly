#!/usr/bin/env python3
"""
Minimal test to isolate grid conflict
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

gui_path = os.path.join(os.path.dirname(__file__), "gui")
sys.path.insert(0, gui_path)

from components.folder_manager import FolderManager
from components.mode_selector import ModeSelector

def test_conflict():
    root = tk.Tk()
    root.title("Grid Conflict Test")
    root.geometry("600x400")
    
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_columnconfigure(0, weight=1)
    
    def get_language():
        return 'en'
    
    print("Creating ModeSelector...")
    mode_selector = ModeSelector(main_frame, get_language)
    mode_selector.setup_ui()
    print("ModeSelector created at row 0")
    
    print("Creating FolderManager...")
    folder_manager = FolderManager(main_frame, get_language)
    folder_manager.setup_ui() 
    print("FolderManager created at row 0 - CONFLICT!")
    
    print("Both components created - testing...")
    root.mainloop()

if __name__ == "__main__":
    test_conflict()

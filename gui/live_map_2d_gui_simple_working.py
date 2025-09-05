#!/usr/bin/env python3
"""
Simple modular 2D Live Map GUI - Working version with FolderManager
Based on successful integration test
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path for component imports (same as working test)
gui_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, gui_path)

try:
    from components.folder_manager import FolderManager
    print("Successfully imported FolderManager in simple GUI")
except ImportError as e:
    print(f"Failed to import FolderManager: {e}")
    sys.exit(1)


class SimpleGUI:
    """Simplified GUI for testing - Step 1: Integrating FolderManager"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Step 1: FolderManager")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"
        
        # Components
        self.folder_manager = None
        self.performance_mode = None
        self.status_var = None
        self.status_label = None
        
        self.setup_ui()
        self.center_window()
    
    def get_language(self):
        """Get current language"""
        return self.language
    
    def on_data_folder_changed(self, directory):
        """Callback when data folder changes"""
        print(f"Data folder changed to: {directory}")
        if self.status_var:
            self.status_var.set(f"Data folder: {directory}")
    
    def setup_ui(self):
        """Set up a simple UI with FolderManager component using grid layout"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(main_frame, text="🗺️ 2D Live Map - Step 1: FolderManager", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Integrate FolderManager component
        self.folder_manager = FolderManager(main_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # Simple settings (use grid layout)
        settings_frame = ttk.LabelFrame(main_frame, text="⚡ Settings", padding="10")
        settings_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.performance_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Enable Performance Mode", 
                       variable=self.performance_mode).grid(row=0, column=0, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=20)
        
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_map).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=self.root.destroy).grid(row=0, column=1)
    
    def launch_map(self):
        """Simple launch function - now with FolderManager data"""
        if self.folder_manager:
            data_folder = self.folder_manager.get_data_folder()
            output_folder = self.folder_manager.get_output_folder()
            print(f"Launch clicked - Data: {data_folder}, Output: {output_folder}")
            self.status_var.set(f"Data: {data_folder}, Output: {output_folder}")
        else:
            self.status_var.set("FolderManager not available")
        print("Launch button clicked with FolderManager!")
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    print("Starting Simple GUI with FolderManager integration...")
    app = SimpleGUI()
    app.run()
    print("Simple GUI closed.")


if __name__ == "__main__":
    main()

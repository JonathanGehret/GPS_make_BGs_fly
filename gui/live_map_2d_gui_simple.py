#!/usr/bin/env python3
"""
Simple modular 2D Live Map GUI - Gradual component integration
Step 1: Adding FolderManager component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path for component imports (use same approach as working test)
gui_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, gui_path)

# Import components gradually
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
        
        self.root.title("2D Live Map - Step 1")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"  # Start with English for simplicity
        
        # Components
        self.folder_manager = None
        
        self.setup_ui()
        self.center_window()
    
    def get_language(self):
        """Get current language"""
        return self.language
    
    def on_data_folder_changed(self, directory):
        """Callback when data folder changes"""
        print(f"Data folder changed to: {directory}")
        # Could trigger data preview refresh here
    
    def setup_ui(self):
        """Set up a simple UI with FolderManager component"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="🗺️ 2D Live Map - Step 1: FolderManager", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Integrate FolderManager component with grid container
        folder_container = ttk.Frame(main_frame)
        folder_container.pack(fill=tk.X, pady=(0, 10))
        folder_container.columnconfigure(0, weight=1)
        
        self.folder_manager = FolderManager(folder_container, self.get_language)
        # Set up folder change callback
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # Simple settings (keep original for now)
        settings_frame = ttk.LabelFrame(main_frame, text="⚡ Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.performance_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Enable Performance Mode", 
                       variable=self.performance_mode).pack(anchor=tk.W)
        
        # Status and buttons
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_var = tk.StringVar(value="Ready - FolderManager integrated")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W, pady=(0, 10))
        
        button_frame = ttk.Frame(status_frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_map).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=self.root.destroy).pack(side=tk.LEFT)
    
    def launch_map(self):
        """Simple launch function - now with FolderManager data"""
        if self.folder_manager:
            data_folder = self.folder_manager.get_data_folder()
            output_folder = self.folder_manager.get_output_folder()
            self.status_var.set(f"Data: {data_folder}, Output: {output_folder}")
        else:
            self.status_var.set("This would launch the map...")
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
    app = SimpleGUI()
    app.run()


if __name__ == "__main__":
    main()

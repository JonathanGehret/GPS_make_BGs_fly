#!/usr/bin/env python3
"""
Simple modular 2D Live Map GUI - Step 2: Adding DataPreview component
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path for component imports
gui_path = os.path.join(os.path.dirname(__file__))
sys.path.insert(0, gui_path)

try:
    from components.folder_manager import FolderManager
    from components.data_preview import DataPreview
    print("Successfully imported FolderManager and DataPreview")
except ImportError as e:
    print(f"Failed to import components: {e}")
    sys.exit(1)


class SimpleGUI:
    """Simplified GUI - Step 2: FolderManager + DataPreview"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Step 2: FolderManager + DataPreview")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"
        
        # Components
        self.folder_manager = None
        self.data_preview = None
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
        
        # Refresh data preview when folder changes
        if self.data_preview:
            self.data_preview.refresh_preview()
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            self.status_var.set(f"Data: {directory} | Files: {file_count}, Points: {total_points}")
    
    def setup_ui(self):
        """Set up UI with FolderManager and DataPreview components"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # Make data preview expandable
        
        # Title
        title = ttk.Label(main_frame, text="🗺️ 2D Live Map - Step 2: FolderManager + DataPreview", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5, sticky="ew")
        
        # FolderManager component
        self.folder_manager = FolderManager(main_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # DataPreview component
        self.data_preview = DataPreview(main_frame, self.get_language)
        # Connect data preview to folder manager's data folder variable
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        self.data_preview.setup_ui()
        
        # Simple settings
        settings_frame = ttk.LabelFrame(main_frame, text="⚡ Settings", padding="10")
        settings_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        self.performance_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Enable Performance Mode", 
                       variable=self.performance_mode).grid(row=0, column=0, sticky="w")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=20)
        
        ttk.Button(button_frame, text="🔄 Refresh Data", command=self.refresh_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_map).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", command=self.root.destroy).grid(row=0, column=2)
    
    def refresh_data(self):
        """Manually refresh data preview"""
        if self.data_preview:
            self.data_preview.refresh_preview()
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            data_folder = self.folder_manager.get_data_folder()
            self.status_var.set(f"Refreshed | Files: {file_count}, Points: {total_points} in {data_folder}")
    
    def launch_map(self):
        """Launch function with both components"""
        if self.folder_manager and self.data_preview:
            data_folder = self.folder_manager.get_data_folder()
            output_folder = self.folder_manager.get_output_folder()
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            
            print(f"Launch with: {file_count} files, {total_points} points")
            print(f"Data: {data_folder}, Output: {output_folder}")
            
            self.status_var.set(f"Ready to launch: {file_count} files, {total_points} points")
        else:
            self.status_var.set("Components not ready")
        print("Launch button clicked with FolderManager + DataPreview!")
    
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
    print("Starting Simple GUI with FolderManager + DataPreview integration...")
    app = SimpleGUI()
    app.run()
    print("Simple GUI closed.")


if __name__ == "__main__":
    main()

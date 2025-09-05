#!/usr/bin/env python3
"""
Simple modular 2D Live Map GUI - Final Step: All components integrated
FolderManager + DataPreview + SettingsManager + LaunchManager
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
    from components.settings_manager import SettingsManager
    from components.launch_manager import LaunchManager
    print("Successfully imported all components")
except ImportError as e:
    print(f"Failed to import components: {e}")
    sys.exit(1)


class SimpleGUI:
    """Complete modular GUI with all components"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Complete Modular GUI")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"
        
        # Components
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.launch_manager = None
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
            self.update_status()
    
    def update_status(self):
        """Update status with current data and settings"""
        if self.data_preview and self.folder_manager:
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            data_folder = os.path.basename(self.folder_manager.get_data_folder())
            self.status_var.set(f"Ready | {file_count} files, {total_points} points in {data_folder}")
    
    def setup_ui(self):
        """Set up complete UI with all components"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # Make data preview expandable
        
        # Title
        title = ttk.Label(main_frame, text="🗺️ 2D Live Map - Complete Modular GUI", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Component 1: FolderManager
        self.folder_manager = FolderManager(main_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # Component 2: DataPreview
        self.data_preview = DataPreview(main_frame, self.get_language)
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        self.data_preview.setup_ui()
        
        # Component 3: SettingsManager
        self.settings_manager = SettingsManager(main_frame, self.get_language)
        self.settings_manager.setup_ui()
        
        # Component 4: LaunchManager (no UI setup needed - it's just the launch logic)
        self.launch_manager = LaunchManager(self.get_language)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=20)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch Map", command=self.launch_map).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=self.root.destroy).grid(row=0, column=2)
    
    def refresh_data(self):
        """Manually refresh all data"""
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
    
    def launch_map(self):
        """Launch the map using all components"""
        if not all([self.folder_manager, self.data_preview, self.settings_manager, self.launch_manager]):
            self.status_var.set("Error: Not all components are ready")
            return
        
        try:
            # Update status before launch
            self.status_var.set("Launching map...")
            self.root.update()
            
            # Use LaunchManager with real components
            result = self.launch_manager.launch_map(self.folder_manager, self.settings_manager)
            
            if result:
                file_count = self.data_preview.get_file_count()
                total_points = self.data_preview.get_total_points()
                self.status_var.set(f"Launch successful! ({file_count} files, {total_points} points)")
            else:
                self.status_var.set("Launch failed - check configuration")
                
        except Exception as e:
            print(f"Launch error: {e}")
            import traceback
            traceback.print_exc()
            self.status_var.set(f"Launch error: {str(e)}")
    
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
        # Initial data refresh
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
        
        self.root.mainloop()


def main():
    print("Starting Complete Modular GUI with all components...")
    app = SimpleGUI()
    app.run()
    print("Complete GUI closed.")


if __name__ == "__main__":
    main()

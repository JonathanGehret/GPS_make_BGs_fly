#!/usr/bin/env python3
"""
Simple approach: add mode selector as a dropdown in the title area
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
    print("Successfully imported core components")
except ImportError as e:
    print(f"Failed to import components: {e}")
    sys.exit(1)


class SimpleGUIWithModeDropdown:
    """Simple GUI with inline mode dropdown (no separate component)"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - With Mode Dropdown")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"
        
        # Mode selection
        self.selected_mode = tk.StringVar(value="2d_live_map")
        self.modes = {
            "2d_live_map": {"name": "2D Live Map", "script": "animate_live_map.py"},
            "mobile_animation": {"name": "Mobile Animation", "script": "mobile_animation.py"},
            "3d_animation": {"name": "3D Animation", "script": "animation_3d.py"}
        }
        
        # Components
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.launch_manager = None
        self.status_var = None
        self.status_label = None
        self.mode_dropdown = None
        
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
    
    def on_mode_changed(self, event=None):
        """Callback when mode dropdown changes"""
        mode_key = self.selected_mode.get()
        mode_info = self.modes[mode_key]
        print(f"Mode changed to: {mode_info['name']}")
        self.update_status()
    
    def update_status(self):
        """Update status with current data and settings"""
        if self.data_preview and self.folder_manager:
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            data_folder = os.path.basename(self.folder_manager.get_data_folder())
            mode_name = self.modes[self.selected_mode.get()]['name']
            
            self.status_var.set(f"Ready | {file_count} files, {total_points} points | Mode: {mode_name}")
    
    def setup_ui(self):
        """Set up UI with inline mode dropdown"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)  # Make data preview expandable (moved to row 4)
        
        # Title with mode dropdown
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title = ttk.Label(title_frame, text="🗺️ GPS Animation Suite", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, sticky="w")
        
        # Mode dropdown in title area
        mode_frame = ttk.Frame(title_frame)
        mode_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Label(mode_frame, text="Mode:").grid(row=0, column=0, padx=(0, 5))
        
        mode_options = [f"🗺️ {self.modes['2d_live_map']['name']}", 
                       f"📱 {self.modes['mobile_animation']['name']}", 
                       f"🌍 {self.modes['3d_animation']['name']}"]
        
        self.mode_dropdown = ttk.Combobox(mode_frame, values=mode_options, state="readonly", width=20)
        self.mode_dropdown.grid(row=0, column=1)
        self.mode_dropdown.set(mode_options[0])  # Default to 2D Live Map
        self.mode_dropdown.bind('<<ComboboxSelected>>', self.on_mode_changed)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Create a container frame for components so they don't override the title
        components_frame = ttk.Frame(main_frame)
        components_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        components_frame.grid_columnconfigure(0, weight=1)
        components_frame.grid_rowconfigure(1, weight=1)  # Make data preview expandable
        
        # FolderManager (now in components_frame)
        self.folder_manager = FolderManager(components_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # DataPreview (now in components_frame)
        self.data_preview = DataPreview(components_frame, self.get_language)
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        self.data_preview.setup_ui()
        
        # SettingsManager (now in components_frame)
        self.settings_manager = SettingsManager(components_frame, self.get_language)
        self.settings_manager.setup_ui()
        
        # LaunchManager (same as working version)
        self.launch_manager = LaunchManager(self.get_language)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=20)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🎯 Mode Info", command=self.show_mode_info).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_selected_mode).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=self.root.destroy).grid(row=0, column=3)
    
    def refresh_data(self):
        """Manually refresh all data"""
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
    
    def show_mode_info(self):
        """Show current mode information"""
        mode_key = self.selected_mode.get()
        mode_info = self.modes[mode_key]
        print(f"Current mode: {mode_info['name']}")
        print(f"Script: {mode_info['script']}")
        self.status_var.set(f"Mode: {mode_info['name']} -> scripts/{mode_info['script']}")
    
    def launch_selected_mode(self):
        """Launch based on selected mode"""
        try:
            # Parse dropdown selection to get mode key
            selected_text = self.mode_dropdown.get()
            if "2D Live Map" in selected_text:
                mode_key = "2d_live_map"
            elif "Mobile Animation" in selected_text:
                mode_key = "mobile_animation"
            elif "3D Animation" in selected_text:
                mode_key = "3d_animation"
            else:
                mode_key = "2d_live_map"  # fallback
            
            self.selected_mode.set(mode_key)
            mode_info = self.modes[mode_key]
            
            self.status_var.set(f"Launching {mode_info['name']}...")
            self.root.update()
            
            if mode_key == "2d_live_map":
                # Use existing LaunchManager for 2D maps
                result = self.launch_manager.launch_map(self.folder_manager, self.settings_manager)
                status = "2D Live Map launched!" if result else "2D Live Map launch failed"
            else:
                # For mobile_animation and 3d_animation
                result = self.launch_script(mode_info['script'])
                status = f"{mode_info['name']} launched!" if result else f"{mode_info['name']} launch failed"
            
            self.status_var.set(status)
            
        except Exception as e:
            print(f"Launch error: {e}")
            self.status_var.set(f"Launch error: {str(e)}")
    
    def launch_script(self, script_name):
        """Launch a script directly"""
        import subprocess
        
        try:
            script_path = os.path.join("scripts", script_name)
            if os.path.exists(script_path):
                print(f"Launching {script_path}")
                subprocess.Popen(["python3", script_path])
                return True
            else:
                print(f"Script not found: {script_path}")
                return False
        except Exception as e:
            print(f"Error launching script: {e}")
            return False
    
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
    print("Starting GUI with Mode Dropdown...")
    app = SimpleGUIWithModeDropdown()
    app.run()
    print("GUI closed.")


if __name__ == "__main__":
    main()

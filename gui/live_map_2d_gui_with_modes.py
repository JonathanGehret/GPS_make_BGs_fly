#!/usr/bin/env python3
"""
Complete modular 2D Live Map GUI - With Mode Selection
FolderManager + DataPreview + SettingsManager + ModeSelector + LaunchManager
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
    from components.mode_selector import ModeSelector
    from components.launch_manager import LaunchManager
    print("Successfully imported all components including ModeSelector")
except ImportError as e:
    print(f"Failed to import components: {e}")
    sys.exit(1)


class CompleteGUI:
    """Complete modular GUI with mode selection"""
    
    def __init__(self, parent=None):
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Complete GUI with Mode Selection")
        self.root.geometry("800x800")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"
        
        # Components
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.mode_selector = None
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
    
    def on_mode_changed(self, mode_key, mode_info):
        """Callback when animation mode changes"""
        print(f"Animation mode changed to: {mode_info['display_name']} ({mode_key})")
        self.update_status()
    
    def update_status(self):
        """Update status with current data and settings"""
        if self.data_preview and self.folder_manager and self.mode_selector:
            file_count = self.data_preview.get_file_count()
            total_points = self.data_preview.get_total_points()
            data_folder = os.path.basename(self.folder_manager.get_data_folder())
            mode_info = self.mode_selector.get_selected_mode_info()
            
            self.status_var.set(f"Ready | {file_count} files, {total_points} points in {data_folder} | Mode: {mode_info['display_name']}")
    
    def setup_ui(self):
        """Set up complete UI with all components including mode selection"""
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)  # Make data preview expandable
        
        # Title
        title = ttk.Label(main_frame, text="🗺️ 2D Live Map - Complete GUI with Mode Selection", 
                         font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, pady=5, sticky="ew")
        
        # Component 1: ModeSelector (at the top - most important choice)
        self.mode_selector = ModeSelector(main_frame, self.get_language)
        self.mode_selector.set_mode_change_callback(self.on_mode_changed)
        self.mode_selector.setup_ui()
        
        # Component 2: FolderManager
        self.folder_manager = FolderManager(main_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        self.folder_manager.setup_ui()
        
        # Component 3: DataPreview
        self.data_preview = DataPreview(main_frame, self.get_language)
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        self.data_preview.setup_ui()
        
        # Component 4: SettingsManager
        self.settings_manager = SettingsManager(main_frame, self.get_language)
        self.settings_manager.setup_ui()
        
        # Component 5: LaunchManager (no UI setup needed - it's just the launch logic)
        self.launch_manager = LaunchManager(self.get_language)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, pady=20)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="🎯 Test Mode", command=self.test_mode).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_animation).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=self.root.destroy).grid(row=0, column=3)
    
    def refresh_data(self):
        """Manually refresh all data"""
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
    
    def test_mode(self):
        """Test current mode selection"""
        mode_key = self.mode_selector.get_selected_mode()
        mode_info = self.mode_selector.get_selected_mode_info()
        script = self.mode_selector.get_selected_script()
        
        print(f"Current mode test:")
        print(f"  Mode: {mode_key}")
        print(f"  Display: {mode_info['display_name']}")
        print(f"  Script: {script}")
        print(f"  Description: {mode_info['description']}")
        
        self.status_var.set(f"Mode test: {mode_info['display_name']} -> {script}")
    
    def launch_animation(self):
        """Launch the animation using the selected mode"""
        if not all([self.folder_manager, self.data_preview, self.settings_manager, self.mode_selector]):
            self.status_var.set("Error: Not all components are ready")
            return
        
        try:
            # Get current mode
            mode_info = self.mode_selector.get_selected_mode_info()
            script_name = mode_info['script']
            
            # Update status before launch
            self.status_var.set(f"Launching {mode_info['display_name']}...")
            self.root.update()
            
            print(f"Launching animation mode: {mode_info['display_name']}")
            print(f"Using script: {script_name}")
            
            # Check if it's the standard 2D live map mode (uses LaunchManager)
            if self.mode_selector.get_selected_mode() == "2d_live_map":
                # Use existing LaunchManager for 2D live map
                result = self.launch_manager.launch_map(self.folder_manager, self.settings_manager)
                if result:
                    file_count = self.data_preview.get_file_count()
                    total_points = self.data_preview.get_total_points()
                    self.status_var.set(f"2D Live Map launched! ({file_count} files, {total_points} points)")
                else:
                    self.status_var.set("2D Live Map launch failed - check configuration")
            else:
                # For other modes (mobile_animation, 3d_animation), launch the specific script
                result = self.launch_custom_script(script_name, mode_info)
                if result:
                    self.status_var.set(f"{mode_info['display_name']} launched successfully!")
                else:
                    self.status_var.set(f"{mode_info['display_name']} launch failed")
                
        except Exception as e:
            print(f"Launch error: {e}")
            import traceback
            traceback.print_exc()
            self.status_var.set(f"Launch error: {str(e)}")
    
    def launch_custom_script(self, script_name, mode_info):
        """Launch a custom animation script"""
        import subprocess
        
        try:
            # Get folders from folder manager
            data_folder = self.folder_manager.get_data_folder()
            output_folder = self.folder_manager.get_output_folder()
            
            # Build script path
            script_path = os.path.join("scripts", script_name)
            
            if not os.path.exists(script_path):
                print(f"Warning: Script {script_path} not found")
                self.status_var.set(f"Script not found: {script_name}")
                return False
            
            print(f"Executing: python3 {script_path}")
            print(f"Data folder: {data_folder}")
            print(f"Output folder: {output_folder}")
            
            # Set environment variables for the script
            env = os.environ.copy()
            env['GPS_DATA_FOLDER'] = data_folder
            env['GPS_OUTPUT_FOLDER'] = output_folder
            
            # Launch the script
            process = subprocess.Popen(
                ["python3", script_path],
                env=env,
                cwd=os.getcwd()
            )
            
            print(f"{mode_info['display_name']} script launched with PID: {process.pid}")
            return True
            
        except Exception as e:
            print(f"Error launching {script_name}: {e}")
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
    print("Starting Complete GUI with Mode Selection...")
    app = CompleteGUI()
    app.run()
    print("Complete GUI closed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GPS Live Map 2D Clean GUI - New Modular version using helper classes
"""

import tkinter as tk
import os
import sys

# Add paths for importing components
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, parent_dir])

# Import helper modules
from helpers.scrollable_frame import ScrollableFrame
from helpers.mode_manager import ModeManager
from helpers.point_calculator import PointCalculator
from helpers.gui_sections import GUISections
from helpers.launcher import AnimationLauncher

print("Successfully imported modular components")


class ScrollableGUI:
    """Main GPS Animation Suite GUI using modular helper classes"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPS Animation Suite")
        self.root.geometry("600x700")
        
        # Language setting
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'en')
        
        # Initialize helper components
        self.mode_manager = ModeManager()
        self.point_calculator = PointCalculator()
        self.gui_sections = GUISections(self.get_language)
        self.launcher = AnimationLauncher(self.get_language)
        
        # Component references
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.status_var = None
        
        self.setup_gui()
        self.center_window()
    
    def get_language(self):
        """Get current language"""
        return self.language
    
    def setup_gui(self):
        """Setup the complete GUI using helper classes"""
        # Create scrollable frame
        scrollable_frame = ScrollableFrame(self.root)
        content_frame = scrollable_frame.get_content_frame()
        
        # Status variable
        self.status_var = tk.StringVar(value="Ready")
        
        # Set up mode manager callback
        self.mode_manager.set_status_callback(self.update_status)
        
        # Create all GUI sections
        self.gui_sections.create_title_section(content_frame, self.mode_manager)
        self.gui_sections.create_status_section(content_frame, self.status_var)
        
        # Create folders section with callback
        self.folder_manager = self.gui_sections.create_folders_section(
            content_frame, 
            self.on_data_folder_changed
        )
        
        # Create data preview section
        self.data_preview = self.gui_sections.create_data_preview_section(
            content_frame, 
            self.folder_manager.data_folder
        )
        
        # Set up point calculator
        self.point_calculator.set_data_folder_var(self.folder_manager.data_folder)
        
        # Create settings section
        self.settings_manager = self.gui_sections.create_settings_section(
            content_frame, 
            self.point_calculator
        )
        
        # Create buttons section
        self.gui_sections.create_buttons_section(
            content_frame,
            self.launch_selected_mode,
            self.root.destroy
        )
    
    def on_data_folder_changed(self, directory):
        """Callback when data folder changes"""
        print(f"Data folder changed to: {directory}")
        if self.status_var:
            self.status_var.set(f"Data folder: {directory}")
        
        # Refresh data preview when folder changes
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
        
        # Update point count calculation
        self.point_calculator.update_point_count_calculation()
    
    def update_status(self):
        """Update status based on folder manager state"""
        if not self.data_preview:
            return
        
        file_count = self.data_preview.get_file_count()
        if file_count > 0:
            total_points = self.data_preview.get_total_points()
            mode_info = self.mode_manager.get_selected_mode_info()
            self.status_var.set(f"Ready | {file_count} files, {total_points} points | Mode: {mode_info['name']}")
        else:
            self.status_var.set("No GPS data files found")
    
    def launch_selected_mode(self):
        """Launch the selected animation mode"""
        def status_callback(message):
            if self.status_var:
                self.status_var.set(message)
                self.root.update()
        
        self.launcher.launch_selected_mode(
            self.mode_manager,
            self.folder_manager, 
            self.settings_manager,
            status_callback
        )
    
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
        
        # Initial point count calculation
        self.point_calculator.update_point_count_calculation()
        
        self.root.mainloop()


def main():
    print("Starting modular GPS Animation Suite...")
    app = ScrollableGUI()
    app.run()
    print("GUI closed.")


if __name__ == "__main__":
    main()

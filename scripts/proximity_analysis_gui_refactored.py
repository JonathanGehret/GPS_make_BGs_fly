#!/usr/bin/env python3
"""
Proximity Analysis GUI Application - Refactored

Professional graphical interface for vulture proximity analysis.
Makes the analysis accessible to non-technical users through an intuitive interface.

This is the refactored version that uses modular components for better maintainability.
"""

import sys
import os
import tkinter as tk

# Add the scripts directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import modular components
try:
    from gui.proximity_analysis.config import ProximityGUIConfig
    from gui.proximity_analysis.i18n_handler import ProximityI18nHandler
    from gui.proximity_analysis.event_handlers import ProximityEventHandler
    from gui.proximity_analysis.ui_builder import ProximityUIBuilder
except ImportError as e:
    print(f"❌ ERROR: Could not import modular components: {e}")
    sys.exit(1)

# Import required dependencies
try:
    from i18n import get_translator
except ImportError:
    print("❌ ERROR: Could not import i18n")
    get_translator = None


class ProximityAnalysisGUI:
    """Professional GUI for Vulture Proximity Analysis - Refactored Version"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize configuration
        self.config = ProximityGUIConfig(root)
        
        # Initialize translator
        if get_translator:
            translator = get_translator()
            self.config.translator = translator
        else:
            translator = None
        
        # Initialize handlers
        self.i18n_handler = ProximityI18nHandler(self.config, translator)
        self.event_handler = ProximityEventHandler(self.config, self.i18n_handler)
        self.ui_builder = ProximityUIBuilder(self.config, self.event_handler, self.i18n_handler)
        
        # Set up the user interface
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main user interface"""
        self.ui_builder.setup_ui()
    
    # Delegate methods for backwards compatibility
    def change_language_dropdown(self, event=None):
        """Handle language dropdown change event"""
        return self.i18n_handler.change_language_dropdown(event)
    
    def switch_language(self, new_lang='en'):
        """Switch to a new language and update all UI text"""
        return self.i18n_handler.switch_language(new_lang)
    
    def update_ui_text(self):
        """Update all UI elements with current language"""
        return self.i18n_handler.update_ui_text()
    
    def browse_folder(self):
        """Handle data folder browsing"""
        return self.event_handler.browse_folder()
    
    def browse_output_folder(self):
        """Handle output folder browsing"""
        return self.event_handler.browse_output_folder()
    
    def refresh_data_preview(self):
        """Refresh the data preview display"""
        return self.event_handler.refresh_data_preview()
    
    def toggle_animation_options(self):
        """Handle animation options toggle"""
        return self.event_handler.toggle_animation_options()
    
    def run_analysis(self):
        """Start the proximity analysis in a background thread"""
        return self.event_handler.run_analysis()
    
    def stop_analysis(self):
        """Stop the running analysis"""
        return self.event_handler.stop_analysis()
    
    def open_selected_file(self, event=None):
        """Open selected result file in browser"""
        return self.event_handler.open_selected_file(event)
    
    def show_in_folder(self):
        """Show results in file manager"""
        return self.event_handler.show_in_folder()
    
    def open_results_folder(self):
        """Open the results folder"""
        return self.event_handler.open_results_folder()
    
    def show_help(self):
        """Show help documentation"""
        return self.event_handler.show_help()
    
    def log(self, message):
        """Add message to log queue"""
        return self.event_handler.log(message)
    
    def clear_log(self):
        """Clear the log display"""
        return self.event_handler.clear_log()
    
    def save_log(self):
        """Save log to file"""
        return self.event_handler.save_log()
    
    # Expose configuration for external access
    @property
    def data_folder(self):
        return self.config.data_folder
    
    @property
    def output_folder(self):
        return self.config.output_folder
    
    @property
    def proximity_threshold(self):
        return self.config.proximity_threshold
    
    @property
    def time_threshold(self):
        return self.config.time_threshold
    
    @property
    def generate_animations(self):
        return self.config.generate_animations
    
    @property
    def time_buffer(self):
        return self.config.time_buffer
    
    @property
    def trail_length(self):
        return self.config.trail_length
    
    @property
    def time_step(self):
        return self.config.time_step
    
    @property
    def limit_encounters(self):
        return self.config.limit_encounters


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ProximityAnalysisGUI(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\\nApplication interrupted by user")
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

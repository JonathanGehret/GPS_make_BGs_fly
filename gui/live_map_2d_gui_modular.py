#!/usr/bin/env python3
"""
Modular 2D Live Map GUI
Streamlined main GUI using component-based architecture
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the gui directory to the path for component imports
sys.path.append(os.path.dirname(__file__))

# Import our modular components
from components.folder_manager import FolderManager
from components.data_preview import DataPreview
from components.settings_manager import SettingsManager
from components.launch_manager import LaunchManager


class LiveMap2DGUI:
    """Main GUI controller for 2D Live Map - now modular and maintainable"""
    
    def __init__(self, parent=None):
        # Create root window
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Configuration")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'de')
        
        # Initialize components
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.launch_manager = None
        
        # UI elements
        self.lang_var = None
        self.status_var = None
        self.launch_btn = None
        self.cancel_btn = None
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Set up the modular user interface"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with scrolling
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create scrollable content area
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header with title and language selection
        self.setup_header(scrollable_frame)
        
        # Initialize components with their respective frames
        self.setup_components(scrollable_frame)
        
        # Bottom section with status and buttons
        self.setup_bottom_section(main_frame, canvas, scrollbar)
        
        # Configure scrolling
        self.setup_scrolling(canvas)
        
        # Set initial language texts
        self.update_all_languages()
    
    def setup_header(self, parent):
        """Set up the header with title and language selection"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🗺️ 2D Live Map", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Language selection
        lang_frame = ttk.Frame(header_frame)
        lang_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(lang_frame, text="🌐", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 5))
        
        self.lang_var = tk.StringVar(value=self.language)
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["en", "de"], state="readonly", width=6)
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
    
    def setup_components(self, parent):
        """Initialize and set up all modular components"""
        row = 1  # Start after header
        
        # Folder Manager Component
        folder_frame = ttk.Frame(parent)
        folder_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_manager = FolderManager(folder_frame, self.get_language)
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        row += 1
        
        # Data Preview Component
        preview_frame = ttk.Frame(parent)
        preview_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        
        self.data_preview = DataPreview(preview_frame, self.get_language)
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        row += 1
        
        # Settings Manager Component
        settings_frame = ttk.Frame(parent)
        settings_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(0, weight=1)
        
        self.settings_manager = SettingsManager(settings_frame, self.get_language)
        self.settings_manager.update_data_folder(self.folder_manager.data_folder)
        row += 1
        
        # Launch Manager (no UI, just logic)
        self.launch_manager = LaunchManager(self.get_language)
        
        # Trigger initial data preview
        self.root.after_idle(self.data_preview.refresh_preview)
    
    def setup_bottom_section(self, main_frame, canvas, scrollbar):
        """Set up the bottom section with status bar and buttons"""
        # Pack canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bottom frame
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(bottom_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9))
        status_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=1, column=0, columnspan=2)
        
        # Launch button
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch 2D Map", 
                                    command=self.launch_map)
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        self.cancel_btn = ttk.Button(button_frame, text="❌ Cancel", 
                                    command=self.root.destroy)
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Configure button style
        style = ttk.Style()
        style.configure("Launch.TButton", font=("Arial", 11, "bold"))
        self.launch_btn.configure(style="Launch.TButton")
        
        # Configure grid weights for main frame
        main_frame.rowconfigure(0, weight=1)
    
    def setup_scrolling(self, canvas):
        """Set up mouse wheel scrolling"""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def get_language(self):
        """Get the current language setting"""
        return self.language
    
    def change_language(self, event=None):
        """Change the interface language"""
        self.language = self.lang_var.get()
        self.update_all_languages()
    
    def update_all_languages(self):
        """Update language for all components"""
        # Update main window
        if self.language == "de":
            self.root.title("2D Live Karte - Konfiguration")
            self.launch_btn.config(text="🚀 2D Live Karte starten")
            self.cancel_btn.config(text="❌ Abbrechen")
            self.status_var.set("Bereit")
        else:
            self.root.title("2D Live Map - Configuration")
            self.launch_btn.config(text="🚀 Launch 2D Live Map")
            self.cancel_btn.config(text="❌ Cancel")
            self.status_var.set("Ready")
        
        # Update all components
        if self.folder_manager:
            self.folder_manager.update_language(self.language)
        if self.data_preview:
            self.data_preview.update_language(self.language)
        if self.settings_manager:
            self.settings_manager.update_language(self.language)
    
    def on_data_folder_changed(self, new_folder):
        """Called when data folder changes - refresh preview"""
        if self.data_preview:
            self.data_preview.refresh_preview()
        if self.settings_manager:
            self.settings_manager.update_data_folder(self.folder_manager.data_folder)
    
    def launch_map(self):
        """Launch the 2D live map using the launch manager"""
        try:
            self.status_var.set("Launching..." if self.language == "en" else "Wird gestartet...")
            self.root.update()
            
            success = self.launch_manager.launch_map(self.folder_manager, self.settings_manager)
            
            if success:
                self.status_var.set("Completed" if self.language == "en" else "Abgeschlossen")
            else:
                self.status_var.set("Failed" if self.language == "en" else "Fehlgeschlagen")
                
        except Exception as e:
            print(f"Error in launch_map: {e}")
            self.status_var.set("Error" if self.language == "en" else "Fehler")
        finally:
            # Reset status after a delay
            self.root.after(3000, lambda: self.status_var.set("Ready" if self.language == "en" else "Bereit"))
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main function for standalone execution"""
    app = LiveMap2DGUI()
    app.run()


if __name__ == "__main__":
    main()

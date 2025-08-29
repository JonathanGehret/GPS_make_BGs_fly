#!/usr/bin/env python3
"""
3D Visualization GUI Launcher
GUI wrapper for the 3D terrain visualization with animation controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import sys
import os
from pathlib import Path

# Import shared animation controls
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
try:
    from utils.animation_controls import AnimationControlsFrame
except ImportError:
    # Fallback if the shared component doesn't exist yet
    AnimationControlsFrame = None

class Visualization3DGUI:
    def __init__(self, parent=None):
        # Create root window - use parent if provided, otherwise create new Tk
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("3D Visualization - Configuration")
        self.root.geometry("750x650")
        self.root.resizable(True, True)
        
        # Language setting - check environment first, then default to German
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'de')  # Default to German
        
        # Configuration variables
        self.data_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.output_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "visualizations"))
        self.terrain_quality = tk.StringVar(value="medium")
        self.show_elevation = tk.BooleanVar(value=True)
        self.show_markers = tk.BooleanVar(value=True)
        
        # Animation controls will be created in setup_ui
        self.animation_controls = None
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Set up the user interface with animation controls"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with scrollable content
        main_frame = ttk.Frame(self.root, padding="15")  # Reduced padding
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Create a scrollable frame
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Title and language (more compact)
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🎯 3D Visualization", 
                               font=("Arial", 14, "bold"))  # Smaller font
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Language selection
        lang_frame = ttk.Frame(header_frame)
        lang_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(lang_frame, text="🌐", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 3))
        
        self.lang_var = tk.StringVar(value=self.language)  # Use environment language
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["en", "de"], state="readonly", width=6)
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Data and Output folders (compact)
        self.folders_frame = ttk.LabelFrame(scrollable_frame, text="📁 Folders", padding="10")
        self.folders_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folders_frame.columnconfigure(1, weight=1)
        
        # Data folder
        self.data_label = ttk.Label(self.folders_frame, text="Data:")
        self.data_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.folders_frame, textvariable=self.data_folder, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 3))
        self.browse_data_button = ttk.Button(self.folders_frame, text="📁", command=self.browse_data_folder, width=3)
        self.browse_data_button.grid(row=0, column=2, pady=2)
        
        # Output folder
        self.output_label = ttk.Label(self.folders_frame, text="Output:")
        self.output_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(self.folders_frame, textvariable=self.output_folder, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 3))
        self.browse_output_button = ttk.Button(self.folders_frame, text="📁", command=self.browse_output_folder, width=3)
        self.browse_output_button.grid(row=1, column=2, pady=2)
        
        # 3D Settings
        self.settings_frame = ttk.LabelFrame(scrollable_frame, text="🎯 3D Settings", padding="10")
        self.settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.settings_frame.columnconfigure(1, weight=1)
        
        # Terrain quality
        self.terrain_label = ttk.Label(self.settings_frame, text="Terrain Quality:")
        self.terrain_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        quality_combo = ttk.Combobox(self.settings_frame, textvariable=self.terrain_quality, 
                                   values=["low", "medium", "high"], state="readonly", width=15)
        quality_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=2)
        
        # Options
        self.options_frame = ttk.LabelFrame(scrollable_frame, text="🔧 Display Options", padding="10")
        self.options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.elevation_check = ttk.Checkbutton(self.options_frame, text="Show Elevation Data", 
                                              variable=self.show_elevation)
        self.elevation_check.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.markers_check = ttk.Checkbutton(self.options_frame, text="Show Position Markers", 
                                            variable=self.show_markers)
        self.markers_check.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Animation controls frame (more compact)
        self.animation_frame = ttk.LabelFrame(scrollable_frame, text="🎬 Animation Settings", padding="10")
        self.animation_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.animation_frame.columnconfigure(0, weight=1)
        
        # Create the shared animation controls (without time buffer, without encounter limit)
        if AnimationControlsFrame:
            self.animation_controls = AnimationControlsFrame(
                self.animation_frame, 
                include_time_buffer=False,  # 3D visualization don't need time buffer
                include_encounter_limit=False,  # 3D visualization don't limit encounters
                data_folder=self.data_folder  # Pass data folder for point count calculations
            )
        else:
            # Fallback: create basic controls manually
            self.create_fallback_animation_controls(self.animation_frame)
        
        # Canvas and scrollbar setup
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bottom frame (outside scroll area)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Bereit" if self.language == "de" else "Ready")
        status_bar = ttk.Label(bottom_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 8))
        status_bar.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=1, column=1)
        
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch 3D Viz", 
                                    command=self.launch_visualization, style="Launch.TButton")
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.cancel_btn = ttk.Button(button_frame, text="❌ Cancel", command=self.root.destroy)
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Configure button style
        style.configure("Launch.TButton", font=("Arial", 11, "bold"), padding=8)
        
        # Configure scrolling
        main_frame.rowconfigure(0, weight=1)
        scrollable_frame.columnconfigure(0, weight=1)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Set initial texts
        self.update_texts()
    
    def change_language(self, event=None):
        """Change the interface language"""
        self.language = self.lang_var.get()
        self.update_texts()
    
    def update_texts(self):
        """Update all texts based on selected language"""
        if self.language == "de":
            self.root.title("3D Visualisierung - Konfiguration")
            self.launch_btn.config(text="🚀 3D Viz starten")
            self.cancel_btn.config(text="❌ Abbrechen")
            self.status_var.set("Bereit")
            
            # Update frame labels
            self.folders_frame.config(text="📁 Ordner")
            self.settings_frame.config(text="🎯 3D Einstellungen")
            self.options_frame.config(text="🔧 Anzeigeoptionen")
            self.animation_frame.config(text="🎬 Animation-Einstellungen")
            
            # Update field labels
            self.data_label.config(text="Daten:")
            self.output_label.config(text="Ausgabe:")
            self.terrain_label.config(text="Gelände-Qualität:")
            
            # Update checkboxes
            self.elevation_check.config(text="Höhendaten anzeigen")
            self.markers_check.config(text="Positionsmarkierungen anzeigen")
            
        else:
            self.root.title("3D Visualization - Configuration")
            self.launch_btn.config(text="🚀 Launch 3D Viz")
            self.cancel_btn.config(text="❌ Cancel")
            self.status_var.set("Ready")
            
            # Update frame labels
            self.folders_frame.config(text="📁 Folders")
            self.settings_frame.config(text="🎯 3D Settings")
            self.options_frame.config(text="🔧 Display Options")
            self.animation_frame.config(text="🎬 Animation Settings")
            
            # Update field labels
            self.data_label.config(text="Data:")
            self.output_label.config(text="Output:")
            self.terrain_label.config(text="Terrain Quality:")
            
            # Update checkboxes
            self.elevation_check.config(text="Show Elevation Data")
            self.markers_check.config(text="Show Position Markers")
    
    def browse_data_folder(self):
        """Browse for data directory"""
        title = "GPS-Datenverzeichnis auswählen" if self.language == "de" else "Select GPS Data Directory"
        directory = filedialog.askdirectory(
            title=title,
            initialdir=self.data_folder.get()
        )
        if directory:
            self.data_folder.set(directory)
            # Update point count in animation controls
            if hasattr(self, 'animation_controls'):
                self.animation_controls.update_data_folder(self.data_folder)
    
    def browse_output_folder(self):
        """Browse for output directory"""
        title = "Ausgabeordner auswählen" if self.language == "de" else "Select Output Directory"
        directory = filedialog.askdirectory(
            title=title,
            initialdir=self.output_folder.get()
        )
        if directory:
            self.output_folder.set(directory)
    
    def create_fallback_animation_controls(self, parent_frame):
        """Create simple animation controls if shared component not available"""
        # Simple fallback variables
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        
        # Trail length
        ttk.Label(parent_frame, text="Trail Length (hours):").grid(row=0, column=0, sticky=tk.W, pady=10)
        trail_scale = ttk.Scale(parent_frame, from_=0.1, to=6.0, 
                               variable=self.trail_length, orient=tk.HORIZONTAL)
        trail_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=10)
        self.trail_label = ttk.Label(parent_frame, text="2.0 hours")
        self.trail_label.grid(row=0, column=2, pady=10)
        trail_scale.configure(command=self.update_trail_label_fallback)
        
        # Time step
        ttk.Label(parent_frame, text="Time Step:").grid(row=1, column=0, sticky=tk.W, pady=10)
        time_step_combo = ttk.Combobox(parent_frame, textvariable=self.time_step, 
                                      values=['1s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '1h'],
                                      state='readonly', width=10)
        time_step_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=10)
        
        parent_frame.columnconfigure(1, weight=1)
        
        # Create a simple config object for compatibility
        class SimpleConfig:
            def get_config(self):
                return {
                    'trail_length': self.trail_length.get(),
                    'time_step': self.time_step.get()
                }
        
        self.animation_controls = SimpleConfig()
        self.animation_controls.trail_length = self.trail_length
        self.animation_controls.time_step = self.time_step
    
    def update_trail_label_fallback(self, value):
        """Update trail length label for fallback controls"""
        if hasattr(self, 'trail_label'):
            self.trail_label.config(text=f"{float(value):.1f} hours")
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def launch_visualization(self):
        """Launch the 3D visualization with configuration"""
        if not os.path.exists(self.data_folder.get()):
            if self.language == "de":
                messagebox.showerror("Fehler", "Datenverzeichnis existiert nicht!")
            else:
                messagebox.showerror("Error", "Data directory does not exist!")
            return
        
        # Create output directory if it doesn't exist
        try:
            os.makedirs(self.output_folder.get(), exist_ok=True)
        except Exception as e:
            if self.language == "de":
                messagebox.showerror("Fehler", f"Ausgabeordner kann nicht erstellt werden: {e}")
            else:
                messagebox.showerror("Error", f"Cannot create output directory: {e}")
            return
        
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "animation_3d.py")
        if not os.path.exists(script_path):
            if self.language == "de":
                messagebox.showerror("Fehler", f"Skript nicht gefunden: {script_path}")
            else:
                messagebox.showerror("Error", f"Script not found: {script_path}")
            return
        
        try:
            # Get animation configuration
            if hasattr(self.animation_controls, 'get_config'):
                config = self.animation_controls.get_config()
            else:
                # Fallback for simple config
                config = {
                    'trail_length': self.trail_length.get(),
                    'time_step': self.time_step.get()
                }
            
            # Set environment variables for configuration
            env = os.environ.copy()
            env['GPS_DATA_DIR'] = self.data_folder.get()
            env['OUTPUT_DIR'] = self.output_folder.get()
            env['TERRAIN_QUALITY'] = self.terrain_quality.get()
            env['TRAIL_LENGTH_HOURS'] = str(config['trail_length'])
            env['TIME_STEP'] = config['time_step']
            env['SHOW_ELEVATION'] = str(self.show_elevation.get())
            env['SHOW_MARKERS'] = str(self.show_markers.get())
            
            # Launch the script
            subprocess.Popen([sys.executable, script_path], env=env)
            
            if self.language == "de":
                messagebox.showinfo("Erfolg", f"3D Visualisierung gestartet!\nAusgabe: {self.output_folder.get()}")
            else:
                messagebox.showinfo("Success", f"3D Visualization launched!\nOutput: {self.output_folder.get()}")
            
            self.root.destroy()
            
        except Exception as e:
            if self.language == "de":
                messagebox.showerror("Fehler", f"Fehler beim Starten: {str(e)}")
            else:
                messagebox.showerror("Error", f"Error launching: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = Visualization3DGUI()
    app.run()

if __name__ == "__main__":
    main()

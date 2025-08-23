#!/usr/bin/env python3
"""
3D Visualization GUI Launcher
GUI wrapper for the 3D terrain visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os

class Visualization3DGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Visualization - Configuration")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"  # Default to English
        
        # Configuration variables
        self.data_dir = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.terrain_quality = tk.StringVar(value="medium")
        self.animation_speed = tk.IntVar(value=100)
        self.show_elevation = tk.BooleanVar(value=True)
        self.show_markers = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 3D Visualization Configuration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Language selection
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=1, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        ttk.Label(lang_frame, text="Language / Sprache:").grid(row=0, column=0, padx=(0, 10))
        
        self.lang_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["en", "de"], state="readonly", width=10)
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        config_frame.columnconfigure(1, weight=1)
        
        # Data directory selection
        ttk.Label(config_frame, text="Data Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_frame, textvariable=self.data_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(config_frame, text="Browse", command=self.browse_data_dir).grid(row=0, column=2, pady=5)
        
        # Terrain quality
        ttk.Label(config_frame, text="Terrain Quality:").grid(row=1, column=0, sticky=tk.W, pady=5)
        quality_combo = ttk.Combobox(config_frame, textvariable=self.terrain_quality, 
                                   values=["low", "medium", "high"], state="readonly")
        quality_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Animation speed
        ttk.Label(config_frame, text="Animation Speed (ms):").grid(row=2, column=0, sticky=tk.W, pady=5)
        speed_frame = ttk.Frame(config_frame)
        speed_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Scale(speed_frame, from_=50, to=500, variable=self.animation_speed, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(speed_frame, textvariable=self.animation_speed).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Options
        options_frame = ttk.LabelFrame(config_frame, text="Options", padding="5")
        options_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Checkbutton(options_frame, text="Show Elevation Data", variable=self.show_elevation).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Show Position Markers", variable=self.show_markers).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Description
        desc_frame = ttk.LabelFrame(main_frame, text="Description", padding="10")
        desc_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.desc_text = tk.Text(desc_frame, height=7, wrap=tk.WORD, state=tk.DISABLED)
        self.desc_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)
        
        # Scrollbar for description
        desc_scroll = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.desc_text.yview)
        desc_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.desc_text.configure(yscrollcommand=desc_scroll.set)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch 3D Visualization", 
                                    command=self.launch_visualization, style="Large.TButton")
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).pack(side=tk.LEFT)
        
        # Configure button style
        style = ttk.Style()
        style.configure("Large.TButton", font=("Arial", 11, "bold"), padding=10)
        
        # Set initial description
        self.update_description()
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(3, weight=1)
    
    def change_language(self, event=None):
        """Change the interface language"""
        self.language = self.lang_var.get()
        self.update_texts()
        self.update_description()
    
    def update_texts(self):
        """Update all texts based on selected language"""
        if self.language == "de":
            self.root.title("3D Visualisierung - Konfiguration")
            self.launch_btn.config(text="🚀 3D Visualisierung starten")
        else:
            self.root.title("3D Visualization - Configuration")
            self.launch_btn.config(text="🚀 Launch 3D Visualization")
    
    def update_description(self):
        """Update the description text"""
        if self.language == "de":
            description = """🎯 3D Terrain Visualisierung

Diese Anwendung erstellt eine immersive 3D-Visualisierung von Geierflugpfaden mit realen Geländedaten.

Funktionen:
• 3D-Flugpfad-Visualisierung mit Höhendaten
• Realistische Geländedarstellung
• Interaktive 3D-Navigation (Zoomen, Drehen, Neigen)
• Konfigurierbare Geländequalität
• Animierte Flugsequenzen
• Höhenprofile und Positionsmarker

Konfiguration:
• Datenverzeichnis: Ordner mit GPS CSV-Dateien
• Geländequalität: Low/Medium/High (beeinflusst Ladezeit)
• Animationsgeschwindigkeit: Verzögerung zwischen Frames
• Optionen: Höhendaten und Positionsmarker ein-/ausschalten

Systemanforderungen:
• WebGL-fähiger Browser für optimale Darstellung
• Internetverbindung für Geländedaten"""
        else:
            description = """🎯 3D Terrain Visualization

This application creates an immersive 3D visualization of vulture flight paths with real terrain data.

Features:
• 3D flight path visualization with elevation data
• Realistic terrain rendering
• Interactive 3D navigation (zoom, rotate, tilt)
• Configurable terrain quality
• Animated flight sequences
• Elevation profiles and position markers

Configuration:
• Data Directory: Folder containing GPS CSV files
• Terrain Quality: Low/Medium/High (affects loading time)
• Animation Speed: Delay between frames in milliseconds
• Options: Toggle elevation data and position markers

System Requirements:
• WebGL-capable browser for optimal rendering
• Internet connection for terrain data"""
        
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, description)
        self.desc_text.config(state=tk.DISABLED)
    
    def browse_data_dir(self):
        """Browse for data directory"""
        directory = filedialog.askdirectory(
            title="Select GPS Data Directory" if self.language == "en" else "GPS-Datenverzeichnis auswählen",
            initialdir=self.data_dir.get()
        )
        if directory:
            self.data_dir.set(directory)
    
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
        if not os.path.exists(self.data_dir.get()):
            if self.language == "de":
                messagebox.showerror("Fehler", "Datenverzeichnis existiert nicht!")
            else:
                messagebox.showerror("Error", "Data directory does not exist!")
            return
        
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "animation_3d.py")
        if not os.path.exists(script_path):
            if self.language == "de":
                messagebox.showerror("Fehler", f"Skript nicht gefunden: {script_path}")
            else:
                messagebox.showerror("Error", f"Script not found: {script_path}")
            return
        
        try:
            # Set environment variables for configuration
            env = os.environ.copy()
            env['GPS_DATA_DIR'] = self.data_dir.get()
            env['TERRAIN_QUALITY'] = self.terrain_quality.get()
            env['ANIMATION_SPEED'] = str(self.animation_speed.get())
            env['SHOW_ELEVATION'] = str(self.show_elevation.get())
            env['SHOW_MARKERS'] = str(self.show_markers.get())
            
            # Launch the script
            subprocess.Popen([sys.executable, script_path], env=env)
            
            if self.language == "de":
                messagebox.showinfo("Erfolg", "3D Visualisierung erfolgreich gestartet!")
            else:
                messagebox.showinfo("Success", "3D Visualization launched successfully!")
            
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

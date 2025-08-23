#!/usr/bin/env python3
"""
2D Live Map GUI Launcher
GUI wrapper for the 2D live map visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os

class LiveMap2DGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("2D Live Map - Configuration")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"  # Default to English
        
        # Configuration variables
        self.data_dir = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.trail_length = tk.IntVar(value=50)
        self.animation_speed = tk.IntVar(value=100)
        
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
        title_label = ttk.Label(main_frame, text="🗺️ 2D Live Map Configuration", 
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
        
        # Trail length
        ttk.Label(config_frame, text="Trail Length:").grid(row=1, column=0, sticky=tk.W, pady=5)
        trail_frame = ttk.Frame(config_frame)
        trail_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Scale(trail_frame, from_=10, to=200, variable=self.trail_length, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(trail_frame, textvariable=self.trail_length).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Animation speed
        ttk.Label(config_frame, text="Animation Speed (ms):").grid(row=2, column=0, sticky=tk.W, pady=5)
        speed_frame = ttk.Frame(config_frame)
        speed_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Scale(speed_frame, from_=50, to=500, variable=self.animation_speed, orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(speed_frame, textvariable=self.animation_speed).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Description
        desc_frame = ttk.LabelFrame(main_frame, text="Description", padding="10")
        desc_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.desc_text = tk.Text(desc_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
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
        
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch 2D Live Map", 
                                    command=self.launch_map, style="Large.TButton")
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
            self.root.title("2D Live Karte - Konfiguration")
            self.launch_btn.config(text="🚀 2D Live Karte starten")
        else:
            self.root.title("2D Live Map - Configuration")
            self.launch_btn.config(text="🚀 Launch 2D Live Map")
    
    def update_description(self):
        """Update the description text"""
        if self.language == "de":
            description = """🗺️ 2D Live Karte Visualisierung

Diese Anwendung erstellt eine interaktive 2D-Karte, die GPS-Verfolgungsdaten von Geiern in Echtzeit anzeigt.

Funktionen:
• Interaktive Kartenvisualisierung mit OpenStreetMap
• Konfigurierbare Spurlänge für Flugpfade
• Echtzeit-Animation der Geierbewegungen
• Professionelle Datenverarbeitung
• Responsive Design für alle Bildschirmgrößen

Konfiguration:
• Datenverzeichnis: Ordner mit GPS CSV-Dateien
• Spurlänge: Anzahl der Punkte im Flugpfad (10-200)
• Animationsgeschwindigkeit: Verzögerung zwischen Frames in Millisekunden"""
        else:
            description = """🗺️ 2D Live Map Visualization

This application creates an interactive 2D map showing real-time GPS tracking data of vultures.

Features:
• Interactive map visualization with OpenStreetMap
• Configurable trail length for flight paths
• Real-time animation of vulture movements
• Professional-grade data processing
• Responsive design for all screen sizes

Configuration:
• Data Directory: Folder containing GPS CSV files
• Trail Length: Number of points in flight path (10-200)
• Animation Speed: Delay between frames in milliseconds"""
        
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
    
    def launch_map(self):
        """Launch the 2D live map with configuration"""
        if not os.path.exists(self.data_dir.get()):
            if self.language == "de":
                messagebox.showerror("Fehler", "Datenverzeichnis existiert nicht!")
            else:
                messagebox.showerror("Error", "Data directory does not exist!")
            return
        
        script_path = os.path.join(os.path.dirname(__file__), "animate_live_map.py")
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
            env['TRAIL_LENGTH'] = str(self.trail_length.get())
            env['ANIMATION_SPEED'] = str(self.animation_speed.get())
            
            # Launch the script
            subprocess.Popen([sys.executable, script_path], env=env)
            
            if self.language == "de":
                messagebox.showinfo("Erfolg", "2D Live Karte erfolgreich gestartet!")
            else:
                messagebox.showinfo("Success", "2D Live Map launched successfully!")
            
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
    app = LiveMap2DGUI()
    app.run()

if __name__ == "__main__":
    main()

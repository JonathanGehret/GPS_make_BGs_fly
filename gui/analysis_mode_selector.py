#!/usr/bin/env python3
"""
GPS Analysis Mode Selection GUI
Hauptmenü für verschiedene GPS-Analysemodi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class AnalysisModeSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPS Analysis - Mode Selection")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Language setting
        self.language = "en"  # Default to English
        
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
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="GPS Analysis Suite", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Language selection
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=1, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        
        ttk.Label(lang_frame, text="Language / Sprache:").grid(row=0, column=0, padx=(0, 10))
        
        self.lang_var = tk.StringVar(value="en")
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                 values=["en", "de"], state="readonly", width=10)
        lang_combo.grid(row=0, column=1)
        lang_combo.bind("<<ComboboxSelected>>", self.change_language)
        
        # Mode selection buttons
        self.setup_mode_buttons(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready / Bereit")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
    
    def setup_mode_buttons(self, parent):
        """Setup the analysis mode selection buttons"""
        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, pady=20, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        # Mode 1: Proximity Analysis
        self.btn1 = ttk.Button(button_frame, text="🔍 Proximity Analysis", 
                              command=self.launch_proximity_analysis,
                              style="Large.TButton")
        self.btn1.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.desc1 = ttk.Label(button_frame, 
                              text="Analyze GPS proximity between vultures",
                              font=("Arial", 9), foreground="gray")
        self.desc1.grid(row=1, column=0, pady=(0, 15))
        
        # Mode 2: 2D Live Map
        self.btn2 = ttk.Button(button_frame, text="🗺️ 2D Live Map", 
                              command=self.launch_2d_map,
                              style="Large.TButton")
        self.btn2.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.desc2 = ttk.Label(button_frame, 
                              text="Interactive 2D map with real-time tracking",
                              font=("Arial", 9), foreground="gray")
        self.desc2.grid(row=3, column=0, pady=(0, 15))
        
        # Mode 3: 3D Visualization
        self.btn3 = ttk.Button(button_frame, text="🎯 3D Visualization", 
                              command=self.launch_3d_visualization,
                              style="Large.TButton")
        self.btn3.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.desc3 = ttk.Label(button_frame, 
                              text="3D flight path visualization with terrain",
                              font=("Arial", 9), foreground="gray")
        self.desc3.grid(row=5, column=0, pady=(0, 15))
        
        # Configure button style
        style = ttk.Style()
        style.configure("Large.TButton", font=("Arial", 11, "bold"), padding=10)
    
    def change_language(self, event=None):
        """Change the interface language"""
        self.language = self.lang_var.get()
        self.update_texts()
    
    def update_texts(self):
        """Update all texts based on selected language"""
        if self.language == "de":
            self.root.title("GPS Analyse - Modus Auswahl")
            self.btn1.config(text="🔍 Näherungsanalyse")
            self.desc1.config(text="GPS-Näherungsanalyse zwischen Geiern")
            
            self.btn2.config(text="🗺️ 2D Live Karte")
            self.desc2.config(text="Interaktive 2D-Karte mit Echtzeit-Verfolgung")
            
            self.btn3.config(text="🎯 3D Visualisierung")
            self.desc3.config(text="3D-Flugpfad-Visualisierung mit Gelände")
            
            self.status_var.set("Bereit")
        else:
            self.root.title("GPS Analysis - Mode Selection")
            self.btn1.config(text="🔍 Proximity Analysis")
            self.desc1.config(text="Analyze GPS proximity between vultures")
            
            self.btn2.config(text="🗺️ 2D Live Map")
            self.desc2.config(text="Interactive 2D map with real-time tracking")
            
            self.btn3.config(text="🎯 3D Visualization")
            self.desc3.config(text="3D flight path visualization with terrain")
            
            self.status_var.set("Ready")
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def launch_proximity_analysis(self):
        """Launch the proximity analysis GUI"""
        self.update_status("Launching Proximity Analysis..." if self.language == "en" 
                          else "Starte Näherungsanalyse...")
        
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "proximity_analysis_gui.py")
        if os.path.exists(script_path):
            try:
                subprocess.Popen([sys.executable, script_path])
                if self.language == "en":
                    self.update_status("Proximity Analysis launched successfully")
                else:
                    self.update_status("Näherungsanalyse erfolgreich gestartet")
            except Exception as e:
                self.show_error(f"Error launching proximity analysis: {str(e)}")
        else:
            self.show_error(f"proximity_analysis_gui.py not found at: {script_path}")
    
    def launch_2d_map(self):
        """Launch the 2D live map"""
        self.update_status("Launching 2D Live Map..." if self.language == "en" 
                          else "Starte 2D Live Karte...")
        
        script_path = os.path.join(os.path.dirname(__file__), "live_map_2d_gui.py")
        if os.path.exists(script_path):
            try:
                subprocess.Popen([sys.executable, script_path])
                if self.language == "en":
                    self.update_status("2D Live Map GUI launched successfully")
                else:
                    self.update_status("2D Live Karte GUI erfolgreich gestartet")
            except Exception as e:
                self.show_error(f"Error launching 2D map GUI: {str(e)}")
        else:
            self.show_error(f"live_map_2d_gui.py not found at: {script_path}")
    
    def launch_3d_visualization(self):
        """Launch the 3D visualization"""
        self.update_status("Launching 3D Visualization..." if self.language == "en" 
                          else "Starte 3D Visualisierung...")
        
        script_path = os.path.join(os.path.dirname(__file__), "visualization_3d_gui.py")
        if os.path.exists(script_path):
            try:
                subprocess.Popen([sys.executable, script_path])
                if self.language == "en":
                    self.update_status("3D Visualization GUI launched successfully")
                else:
                    self.update_status("3D Visualisierung GUI erfolgreich gestartet")
            except Exception as e:
                self.show_error(f"Error launching 3D visualization GUI: {str(e)}")
        else:
            self.show_error(f"visualization_3d_gui.py not found at: {script_path}")
    
    def update_status(self, message):
        """Update the status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_error(self, message):
        """Show an error message"""
        if self.language == "de":
            messagebox.showerror("Fehler", message)
        else:
            messagebox.showerror("Error", message)
        
        self.update_status("Error occurred" if self.language == "en" else "Fehler aufgetreten")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = AnalysisModeSelector()
    app.run()

if __name__ == "__main__":
    main()

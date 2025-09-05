#!/usr/bin/env python3
"""
2D Live Map GUI Launcher
GUI wrapper for the 2D live map visualization with animation controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os
from pathlib import Path

# Try to import shared animation controls
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
try:
    # Try multiple import paths to ensure compatibility
    try:
        from scripts.utils.animation_controls import AnimationControlsFrame
    except ImportError:
        from utils.animation_controls import AnimationControlsFrame
except ImportError:
    # Fallback if the shared component doesn't exist yet
    AnimationControlsFrame = None

class LiveMap2DGUI:
    def __init__(self, parent=None):
        # Create root window - use parent if provided, otherwise create new Tk
        if parent:
            self.root = tk.Toplevel(parent)
        else:
            self.root = tk.Tk()
        
        self.root.title("2D Live Map - Configuration")
        self.root.geometry("700x550")  # Reduced size
        self.root.resizable(True, True)
        
        # Language setting - check environment first, then default to German
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'de')  # Default to German
        
        # Configuration variables
        self.data_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "data"))
        self.output_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "visualizations"))
        
        # Performance mode setting
        self.performance_mode = None  # Will be initialized in setup_ui
        
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
        title_label = ttk.Label(header_frame, text="🗺️ 2D Live Map", 
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
        
        # Store labels for translation
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
        
        # Data preview (smaller)
        self.preview_frame = ttk.LabelFrame(scrollable_frame, text="📊 Data Preview", padding="8")
        self.preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.preview_frame.columnconfigure(0, weight=1)
        
        self.data_preview = tk.Text(self.preview_frame, height=3, width=60, wrap=tk.WORD, font=("Arial", 8))
        self.data_preview.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.refresh_button = ttk.Button(self.preview_frame, text="🔄 Refresh", 
                                        command=self.refresh_data_preview)
        self.refresh_button.grid(row=1, column=0, sticky=tk.W)
        
        # Animation controls frame (more compact)
        self.animation_frame = ttk.LabelFrame(scrollable_frame, text="🎬 Animation Settings", padding="10")
        self.animation_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.animation_frame.columnconfigure(0, weight=1)
        
        # Create the shared animation controls (without time buffer, without encounter limit)
        if AnimationControlsFrame:
            self.animation_controls = AnimationControlsFrame(
                self.animation_frame, 
                include_time_buffer=False,  # 2D maps don't need time buffer
                include_encounter_limit=False,  # 2D maps don't limit encounters
                data_folder=self.data_folder  # Pass data folder for point count calculations
            )
        else:
            # Fallback: create basic controls manually
            self.create_fallback_animation_controls(self.animation_frame)
        
        # Performance mode section
        self.performance_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Performance Settings", padding="10")
        self.performance_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.performance_frame.columnconfigure(0, weight=1)
        
        # Performance mode checkbox
        self.performance_mode = tk.BooleanVar(value=True)
        self.performance_checkbox = ttk.Checkbutton(
            self.performance_frame, 
            text="Enable Performance Mode",
            variable=self.performance_mode,
            command=self.update_performance_info
        )
        self.performance_checkbox.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Performance mode explanation
        self.performance_info = ttk.Label(
            self.performance_frame, 
            text="📝 Standard mode: Fading markers with smooth transitions\n⚡ Performance mode: Line+head rendering with adaptive LOD for large datasets",
            font=("Arial", 8),
            foreground="gray50"
        )
        self.performance_info.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status and buttons (fixed at bottom)
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
        
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch 2D Map", 
                                    command=self.launch_map, style="Launch.TButton")
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
        
        # Initial data preview
        self.refresh_data_preview()
        
        # Set initial texts
        self.update_texts()
    
    def change_language(self, event=None):
        """Change the interface language"""
        self.language = self.lang_var.get()
        self.update_texts()
    
    def update_performance_info(self):
        """Update performance mode information display"""
        if self.performance_mode.get():
            if self.language == "de":
                info_text = "⚡ Aktiviert: Linie+Kopf-Rendering mit adaptiver LOD für große Datensätze"
            else:
                info_text = "⚡ Enabled: Line+head rendering with adaptive LOD for large datasets"
        else:
            if self.language == "de":
                info_text = "📝 Standard: Verblassende Marker mit glatten Übergängen"
            else:
                info_text = "📝 Standard: Fading markers with smooth transitions"
        
        self.performance_info.config(text=info_text)
    
    def update_texts(self):
        """Update all texts based on selected language"""
        if self.language == "de":
            self.root.title("2D Live Karte - Konfiguration")
            self.launch_btn.config(text="🚀 2D Live Karte starten")
            self.cancel_btn.config(text="❌ Abbrechen")
            self.status_var.set("Bereit")
            
            # Update frame labels
            self.folders_frame.config(text="📁 Ordner")
            self.preview_frame.config(text="📊 Datenvorschau")
            self.animation_frame.config(text="🎬 Animation-Einstellungen")
            self.performance_frame.config(text="⚡ Performance-Einstellungen")
            
            # Update field labels
            self.data_label.config(text="Daten:")
            self.output_label.config(text="Ausgabe:")
            self.refresh_button.config(text="🔄 Aktualisieren")
            
            # Update performance mode elements
            self.performance_checkbox.config(text="Performance-Modus aktivieren")
            
        else:
            self.root.title("2D Live Map - Configuration")
            self.launch_btn.config(text="🚀 Launch 2D Live Map")
            self.cancel_btn.config(text="❌ Cancel")
            self.status_var.set("Ready")
            
            # Update frame labels
            self.folders_frame.config(text="📁 Folders")
            self.preview_frame.config(text="📊 Data Preview")
            self.animation_frame.config(text="🎬 Animation Settings")
            self.performance_frame.config(text="⚡ Performance Settings")
            
            # Update field labels
            self.data_label.config(text="Data:")
            self.output_label.config(text="Output:")
            self.refresh_button.config(text="🔄 Refresh")
            
            # Update performance mode elements
            self.performance_checkbox.config(text="Enable Performance Mode")
        
        # Update performance info text
        self.update_performance_info()
    
    def _update_widget_texts_de(self, widget):
        """Recursively update widget texts to German"""
        try:
            widget_class = widget.winfo_class()
            if widget_class == "Label":
                current_text = widget.cget("text")
                # Update specific labels
                if "Data:" in current_text:
                    widget.config(text="Daten:")
                elif "Output:" in current_text:
                    widget.config(text="Ausgabe:")
                elif "🔄 Refresh" in current_text:
                    widget.config(text="🔄 Aktualisieren")
            elif widget_class == "Labelframe":
                current_text = widget.cget("text")
                if "📁 Folders" in current_text:
                    widget.config(text="📁 Ordner")
                elif "📊 Data Preview" in current_text:
                    widget.config(text="📊 Datenvorschau")
                elif "🎬 Animation Settings" in current_text:
                    widget.config(text="🎬 Animation-Einstellungen")
            elif widget_class == "Button":
                current_text = widget.cget("text")
                if "❌ Cancel" in current_text:
                    widget.config(text="❌ Abbrechen")
            
            # Recursively check children
            for child in widget.winfo_children():
                self._update_widget_texts_de(child)
        except Exception:
            pass
    
    def _update_widget_texts_en(self, widget):
        """Recursively update widget texts to English"""
        try:
            widget_class = widget.winfo_class()
            if widget_class == "Label":
                current_text = widget.cget("text")
                # Update specific labels
                if "Daten:" in current_text:
                    widget.config(text="Data:")
                elif "Ausgabe:" in current_text:
                    widget.config(text="Output:")
                elif "🔄 Aktualisieren" in current_text:
                    widget.config(text="🔄 Refresh")
            elif widget_class == "Labelframe":
                current_text = widget.cget("text")
                if "📁 Ordner" in current_text:
                    widget.config(text="📁 Folders")
                elif "📊 Datenvorschau" in current_text:
                    widget.config(text="📊 Data Preview")
                elif "🎬 Animation-Einstellungen" in current_text:
                    widget.config(text="🎬 Animation Settings")
            elif widget_class == "Button":
                current_text = widget.cget("text")
                if "❌ Abbrechen" in current_text:
                    widget.config(text="❌ Cancel")
            
            # Recursively check children
            for child in widget.winfo_children():
                self._update_widget_texts_en(child)
        except Exception:
            pass
    
    def browse_data_folder(self):
        """Browse for data directory"""
        title = "GPS-Datenverzeichnis auswählen" if self.language == "de" else "Select GPS Data Directory"
        directory = filedialog.askdirectory(
            title=title,
            initialdir=self.data_folder.get()
        )
        if directory:
            self.data_folder.set(directory)
            self.refresh_data_preview()
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
    
    def refresh_data_preview(self):
        """Refresh the data preview"""
        self.data_preview.delete(1.0, tk.END)
        
        try:
            folder = self.data_folder.get()
            if not os.path.exists(folder):
                self.data_preview.insert(tk.END, f"❌ Folder not found: {folder}\n")
                return
                
            csv_files = list(Path(folder).glob("*.csv"))
            
            if not csv_files:
                self.data_preview.insert(tk.END, f"⚠️  No CSV files found in: {folder}\n")
                return
                
            self.data_preview.insert(tk.END, f"📁 Data folder: {folder}\n")
            self.data_preview.insert(tk.END, f"📊 Found {len(csv_files)} CSV file(s)\n\n")
            
            for csv_file in csv_files:
                try:
                    # Try to read basic info without importing pandas
                    with open(csv_file, 'r') as f:
                        lines = sum(1 for _ in f) - 1  # Subtract header
                    self.data_preview.insert(tk.END, f"✅ {csv_file.name}: ~{lines} data points\n")
                except Exception:
                    self.data_preview.insert(tk.END, f"❌ {csv_file.name}: Error reading file\n")
                    
        except Exception as e:
            self.data_preview.insert(tk.END, f"❌ Error reading folder: {e}\n")
    
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
    
    def show_success_dialog(self, output_folder, html_file_path=None):
        """Show a custom success dialog with buttons to open output folder and HTML file"""
        # Create custom dialog window
        dialog = tk.Toplevel(self.root)
        if self.language == "de":
            dialog.title("Erfolg")
            message = "2D Live Karte erfolgreich erstellt!"
            folder_text = f"Ausgabeordner: {output_folder}"
            open_folder_btn_text = "📁 Ordner öffnen"
            open_html_btn_text = "🌐 HTML öffnen"
            close_btn_text = "Schließen"
        else:
            dialog.title("Success")
            message = "2D Live Map created successfully!"
            folder_text = f"Output folder: {output_folder}"
            open_folder_btn_text = "📁 Open Folder"
            open_html_btn_text = "🌐 Open HTML"
            close_btn_text = "Close"
        
        dialog.geometry("550x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Success icon and message
        icon_label = ttk.Label(main_frame, text="✅", font=("Arial", 24))
        icon_label.pack(pady=(0, 10))
        
        message_label = ttk.Label(main_frame, text=message, font=("Arial", 12, "bold"))
        message_label.pack(pady=(0, 5))
        
        folder_label = ttk.Label(main_frame, text=folder_text, font=("Arial", 9))
        folder_label.pack(pady=(0, 10))
        
        # Show HTML file path if available
        if html_file_path:
            html_filename = os.path.basename(html_file_path) if html_file_path else "Unknown"
            if self.language == "de":
                html_text = f"HTML-Datei: {html_filename}"
            else:
                html_text = f"HTML file: {html_filename}"
            html_label = ttk.Label(main_frame, text=html_text, font=("Arial", 9), foreground="blue")
            html_label.pack(pady=(0, 20))
        else:
            ttk.Label(main_frame, text="", font=("Arial", 2)).pack(pady=(0, 10))  # Spacer
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=(10, 0))
        
        # Function to close dialog only (keep main window open)
        def close_dialog_only():
            dialog.destroy()
        
        # Open folder button
        open_folder_btn = ttk.Button(
            buttons_frame, 
            text=open_folder_btn_text,
            command=lambda: self.open_output_folder(output_folder)
        )
        open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open HTML button (only if HTML file path is available)
        if html_file_path:
            open_html_btn = ttk.Button(
                buttons_frame, 
                text=open_html_btn_text,
                command=lambda: self.open_html_file(html_file_path)
            )
            open_html_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button - this will only close the dialog, keeping main window open
        close_btn = ttk.Button(buttons_frame, text=close_btn_text, command=close_dialog_only)
        close_btn.pack(side=tk.LEFT)
        
        # Set focus to close button
        close_btn.focus_set()
        
        # Bind Enter key and window close to close only the dialog
        dialog.bind('<Return>', lambda e: close_dialog_only())
        dialog.bind('<Escape>', lambda e: close_dialog_only())
        dialog.protocol("WM_DELETE_WINDOW", close_dialog_only)
    
    def open_html_file(self, html_file_path):
        """Open the generated HTML file directly in the default browser"""
        try:
            if html_file_path and os.path.exists(html_file_path):
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(html_file_path)}")
                print(f"🌐 Opened HTML file: {html_file_path}")
            else:
                if self.language == "de":
                    messagebox.showerror("Fehler", f"HTML-Datei nicht gefunden: {html_file_path}")
                else:
                    messagebox.showerror("Error", f"HTML file not found: {html_file_path}")
        except Exception as e:
            if self.language == "de":
                messagebox.showerror("Fehler", f"Fehler beim Öffnen der HTML-Datei: {e}")
            else:
                messagebox.showerror("Error", f"Failed to open HTML file: {e}")
    
    def open_output_folder(self, folder_path):
        """Open the output folder in the system file manager"""
        try:
            if os.path.exists(folder_path):
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(folder_path)}")
                print(f"📁 Opened output folder: {folder_path}")
            else:
                if self.language == "de":
                    messagebox.showerror("Fehler", f"Ordner nicht gefunden: {folder_path}")
                else:
                    messagebox.showerror("Error", f"Folder not found: {folder_path}")
        except Exception as e:
            if self.language == "de":
                messagebox.showerror("Fehler", f"Fehler beim Öffnen des Ordners: {e}")
            else:
                messagebox.showerror("Error", f"Failed to open folder: {e}")
    
    def launch_map(self):
        """Launch the 2D live map with configuration"""
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
        
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "animate_live_map.py")
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
            env['TRAIL_LENGTH_HOURS'] = str(config['trail_length'])
            env['TIME_STEP'] = config['time_step']
            env['PLAYBACK_SPEED'] = str(config.get('playback_speed', 1.0))
            env['PERFORMANCE_MODE'] = '1' if self.performance_mode.get() else '0'
            
            # Launch the animation script and wait for completion to get the HTML file path
            try:
                if getattr(sys, '_MEIPASS', False):
                    # In bundle mode, we need to find the Python interpreter
                    bundle_dir = sys._MEIPASS
                    
                    # Try to find python executable in the bundle
                    python_exe = None
                    possible_python_paths = [
                        os.path.join(bundle_dir, 'python'),
                        os.path.join(bundle_dir, 'python3'),
                        'python3',  # System python
                        'python'    # Fallback
                    ]
                    
                    for py_path in possible_python_paths:
                        if os.path.exists(py_path) or py_path in ['python3', 'python']:
                            python_exe = py_path
                            break
                    
                    if python_exe:
                        # Launch the script with the found Python interpreter
                        process = subprocess.run([python_exe, script_path], env=env, 
                                               capture_output=True, text=True, timeout=300)
                    else:
                        # Fallback: try to run script directly (might work on some systems)
                        process = subprocess.run([script_path], env=env, 
                                               capture_output=True, text=True, timeout=300)
                else:
                    # Development mode - use system Python
                    process = subprocess.run([sys.executable, script_path], env=env, 
                                           capture_output=True, text=True, timeout=300)
                
                # Parse the output to find the generated HTML file path
                html_file_path = None
                if process.stdout:
                    for line in process.stdout.split('\n'):
                        if 'Saved:' in line and '.html' in line:
                            # Extract the path after "Saved: "
                            html_file_path = line.split('Saved: ')[-1].strip()
                            break
                
                if self.language == "de":
                    self.show_success_dialog(self.output_folder.get(), html_file_path)
                else:
                    self.show_success_dialog(self.output_folder.get(), html_file_path)
                
                # Note: The main window will stay open when the success dialog is closed
                
            except subprocess.TimeoutExpired:
                if self.language == "de":
                    messagebox.showerror("Fehler", "Zeitüberschreitung beim Erstellen der Animation (5 Minuten)")
                else:
                    messagebox.showerror("Error", "Timeout while creating animation (5 minutes)")
            except Exception as launch_error:
                if self.language == "de":
                    messagebox.showerror("Fehler", f"Fehler beim Erstellen der Animation: {launch_error}")
                else:
                    messagebox.showerror("Error", f"Error creating animation: {launch_error}")
            
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

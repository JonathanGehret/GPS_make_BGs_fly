#!/usr/bin/env python3
"""
GUI Sections Creator for GPS Animation Suite
Creates individual GUI sections like title, folders, data preview, etc.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from datetime import datetime


class GUISections:
    """Creates and manages individual GUI sections"""
    
    def __init__(self, get_language_func):
        self.get_language = get_language_func
        
    def create_title_section(self, parent, mode_manager):
        """Create title and mode dropdown section"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 10))
        
        # Title on the left
        title = ttk.Label(title_frame, text="🗺️ GPS Animation Suite", 
                         font=("Arial", 16, "bold"))
        title.pack(side="left")
        
        # Mode dropdown on the right
        mode_frame = ttk.Frame(title_frame)
        mode_frame.pack(side="right")
        
        ttk.Label(mode_frame, text="Mode:").pack(side="left", padx=(0, 5))
        
        mode_options = mode_manager.get_mode_options()
        mode_manager.mode_dropdown = ttk.Combobox(mode_frame, values=mode_options, state="readonly", width=20)
        mode_manager.mode_dropdown.pack(side="left")
        mode_manager.mode_dropdown.set(mode_options[0])  # Default to 2D Live Map
        mode_manager.mode_dropdown.bind('<<ComboboxSelected>>', mode_manager.on_mode_changed)
        
        return title_frame
    
    def create_status_section(self, parent, status_var):
        """Create status bar section"""
        status_label = ttk.Label(parent, textvariable=status_var, 
                               relief="sunken", anchor="w", padding="5")
        status_label.pack(fill="x", pady=(0, 10))
        return status_label
    
    def create_folders_section(self, parent, data_folder_callback=None):
        """Create folders section with browse buttons"""
        folder_frame = ttk.LabelFrame(parent, text="📁 Folders", padding="10")
        folder_frame.pack(fill="x", pady=(0, 10))
        # Initialize folder variables (prefill from environment if provided)
        # Fall back to project-root-relative defaults for stability across different CWDs
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        default_data = os.environ.get('GPS_DATA_DIR', os.path.join(project_root, "assets", "data"))
        default_output = os.environ.get('OUTPUT_DIR', os.path.join(project_root, "visualizations"))
        data_folder = tk.StringVar(value=default_data)
        output_folder = tk.StringVar(value=default_output)
        
        # Browse methods
        def browse_data_folder():
            language = self.get_language()
            title = "GPS-Datenverzeichnis auswählen" if language == "de" else "Select GPS Data Directory"
            directory = filedialog.askdirectory(title=title, initialdir=data_folder.get())
            if directory:
                data_folder.set(directory)
                if data_folder_callback:
                    data_folder_callback(directory)
        
        def browse_output_folder():
            language = self.get_language()
            title = "Ausgabeverzeichnis auswählen" if language == "de" else "Select Output Directory"
            directory = filedialog.askdirectory(title=title, initialdir=output_folder.get())
            if directory:
                output_folder.set(directory)
        
        # Data folder
        data_frame = ttk.Frame(folder_frame)
        data_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(data_frame, text="Data:").pack(side="left")
        data_entry = ttk.Entry(data_frame, textvariable=data_folder, width=50)
        data_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        ttk.Button(data_frame, text="📁", command=browse_data_folder, width=3).pack(side="right")
        
        # Output folder
        output_frame = ttk.Frame(folder_frame)
        output_frame.pack(fill="x")
        
        ttk.Label(output_frame, text="Output:").pack(side="left")
        output_entry = ttk.Entry(output_frame, textvariable=output_folder, width=50)
        output_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        ttk.Button(output_frame, text="📁", command=browse_output_folder, width=3).pack(side="right")
        
        # Create folder manager object to return
        class FolderManager:
            def __init__(self):
                self.data_folder = data_folder
                self.output_folder = output_folder
                
            def get_data_folder(self):
                return self.data_folder.get()
                
            def get_output_folder(self):
                return self.output_folder.get()
                
            def validate_folders(self):
                issues = []
                data_dir = self.data_folder.get()
                output_dir = self.output_folder.get()
                
                if not data_dir or not os.path.exists(data_dir):
                    issues.append("Data folder does not exist")
                if not output_dir:
                    issues.append("Output folder not specified")
                
                return issues
        
        return FolderManager()
    
    def create_data_preview_section(self, parent, data_folder_var):
        """Create data preview section"""
        preview_frame = ttk.LabelFrame(parent, text="📊 Data Preview", padding="10")
        preview_frame.pack(fill="x", pady=(0, 10))
        
        # Preview text area
        data_preview_text = tk.Text(preview_frame, height=4, width=60, wrap=tk.WORD, font=("Arial", 8))
        data_preview_text.pack(fill="x", pady=(0, 5))
        
        def refresh_preview():
            if not data_folder_var:
                return
            
            data_folder = data_folder_var.get()
            if not data_folder or not os.path.exists(data_folder):
                data_preview_text.delete("1.0", tk.END)
                data_preview_text.insert("1.0", "No data folder selected or folder doesn't exist")
                return
            
            # Count CSV files
            csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
            if not csv_files:
                data_preview_text.delete("1.0", tk.END)
                data_preview_text.insert("1.0", "No CSV files found in data folder")
                return
            
            # Show preview - list all files
            preview_text = f"Found {len(csv_files)} GPS data files:\\n\\n"
            total_points = 0
            for filename in csv_files:  # Show all files
                filepath = os.path.join(data_folder, filename)
                try:
                    import pandas as pd
                    df = pd.read_csv(filepath, sep=';')
                    points = len(df)
                    total_points += points
                    preview_text += f"📄 {filename}: {points} points\\n"
                except Exception:
                    preview_text += f"📄 {filename}: Error reading file\\n"
            
            preview_text += f"\\nTotal estimated points: {total_points}"
            
            data_preview_text.delete("1.0", tk.END)
            data_preview_text.insert("1.0", preview_text)
        
        # Create data preview manager object
        class DataPreview:
            def __init__(self):
                self.data_preview = data_preview_text
                self.data_folder_var = data_folder_var
                
            def refresh_preview(self):
                refresh_preview()
                
            def get_file_count(self):
                if not self.data_folder_var:
                    return 0
                data_folder = self.data_folder_var.get()
                if not data_folder or not os.path.exists(data_folder):
                    return 0
                return len([f for f in os.listdir(data_folder) if f.endswith('.csv')])
            
            def get_total_points(self):
                return self.get_file_count() * 40  # Rough estimate

            def get_time_range(self):
                """Scan CSV files in the data folder and return (min_dt, max_dt) or None.

                Expects timestamp column header containing 'timestamp' (case-insensitive)
                and timestamps in formats like '15.06.2024 08:02:00'.
                """
                if not self.data_folder_var:
                    return None
                data_folder = self.data_folder_var.get()
                if not data_folder or not os.path.exists(data_folder):
                    return None

                csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
                if not csv_files:
                    return None

                import csv

                min_dt = None
                max_dt = None

                # Candidate formats; add more if needed
                formats = ['%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S']

                for filename in csv_files:
                    path = os.path.join(data_folder, filename)
                    try:
                        with open(path, 'r', encoding='utf-8') as fh:
                            reader = csv.reader(fh, delimiter=';')
                            headers = next(reader, None)
                            if not headers:
                                continue

                            # Find timestamp column
                            ts_idx = None
                            for i, h in enumerate(headers):
                                if h and 'timestamp' in h.lower():
                                    ts_idx = i
                                    break
                            if ts_idx is None:
                                ts_idx = 0

                            for row in reader:
                                if len(row) <= ts_idx:
                                    continue
                                s = row[ts_idx].strip()
                                if not s:
                                    continue
                                dt = None
                                for fmt in formats:
                                    try:
                                        dt = datetime.strptime(s, fmt)
                                        break
                                    except Exception:
                                        dt = None

                                if dt is None:
                                    # Try ISO parse as fallback
                                    try:
                                        dt = datetime.fromisoformat(s)
                                    except Exception:
                                        dt = None

                                if dt:
                                    if min_dt is None or dt < min_dt:
                                        min_dt = dt
                                    if max_dt is None or dt > max_dt:
                                        max_dt = dt
                    except Exception:
                        # ignore file read/parse errors per-file
                        continue

                if min_dt and max_dt:
                    return (min_dt, max_dt)
                return None
        
        return DataPreview()
    
    def create_settings_section(self, parent, point_calculator):
        """Create animation settings section"""
        animation_frame = ttk.LabelFrame(parent, text="🎬 Animation Settings", padding="10")
        animation_frame.pack(fill="x", pady=(0, 10))
        
        # Trail length
        trail_frame = ttk.Frame(animation_frame)
        trail_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(trail_frame, text="Trail Length (hours):").pack(side="left")
        trail_length = tk.DoubleVar(value=2.0)
        trail_scale = ttk.Scale(trail_frame, from_=0.5, to=12.0, variable=trail_length, orient="horizontal")
        trail_scale.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        trail_label = ttk.Label(trail_frame, text="2.0 hours")
        trail_label.pack(side="right")
        
        def update_trail_label(value):
            trail_label.config(text=f"{float(value):.1f} hours")
        trail_scale.config(command=update_trail_label)
        
        # Time step
        time_frame = ttk.Frame(animation_frame)
        time_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(time_frame, text="Time Step:").pack(side="left")
        time_step = tk.StringVar(value="1m")
        time_step_combo = ttk.Combobox(time_frame, textvariable=time_step, 
                                      values=["1s", "10s", "30s", "1m", "5m", "10m"], state="readonly", width=10)
        time_step_combo.pack(side="left", padx=(10, 0))
        
        # Point count calculation display
        point_count_label = ttk.Label(time_frame, text="Point count calculated when data is loaded", 
                                      font=("Arial", 9), foreground="blue")
        point_count_label.pack(side="left", padx=(20, 0))
        
        # Set up point calculator
        point_calculator.set_point_count_label(point_count_label)
        point_calculator.set_time_step_var(time_step)
        
        # Bind time step change to update point count
        def on_time_step_change(event=None):
            point_calculator.update_point_count_calculation()
        time_step_combo.bind('<<ComboboxSelected>>', on_time_step_change)
        
        # Performance settings
        performance_frame = ttk.LabelFrame(parent, text="⚡ Performance Settings", padding="10")
        performance_frame.pack(fill="x", pady=(0, 10))
        
        performance_mode = tk.BooleanVar(value=True)
        performance_checkbox = ttk.Checkbutton(performance_frame, text="Enable Performance Mode", 
                                              variable=performance_mode)
        performance_checkbox.pack(anchor="w", pady=(0, 5))
        
        ttk.Label(performance_frame, text="• Enabled: Line+head rendering with adaptive LOD for large datasets", 
                 font=("Arial", 8), foreground="gray").pack(anchor="w")
        
        # Create settings manager object
        class SettingsManager:
            def __init__(self):
                self.performance_mode = performance_mode
                self.trail_length = trail_length
                self.time_step = time_step
                
            def get_config(self):
                cfg = {
                    'performance_mode': self.performance_mode.get(),
                    'trail_length': self.trail_length.get(),
                    'time_step': self.time_step.get(),
                    'playback_speed': 1.0
                }
                # Include optional animation time range if present as attributes
                try:
                    if hasattr(self, 'animation_start_time') and getattr(self, 'animation_start_time'):
                        cfg['animation_start_time'] = getattr(self, 'animation_start_time')
                    if hasattr(self, 'animation_end_time') and getattr(self, 'animation_end_time'):
                        cfg['animation_end_time'] = getattr(self, 'animation_end_time')
                except Exception:
                    pass
                return cfg
        
        return SettingsManager()
    
    def create_buttons_section(self, parent, launch_callback, close_callback):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=20)
        
        ttk.Button(button_frame, text="🚀 Launch", command=launch_callback).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=close_callback).pack(side="left")
        
        return button_frame

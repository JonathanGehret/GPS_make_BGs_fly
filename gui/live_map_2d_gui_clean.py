#!/usr/bin/env python3
"""
GPS Live Map 2D Clean GUI - Scrollable version with mode dropdown and point count calculation
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import pandas as pd

# Add paths for importing components
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.extend([current_dir, parent_dir])

# Import components
try:
    from components.folder_manager import FolderManager
    from components.data_preview import DataPreview
    from components.settings_manager import SettingsManager
    from components.launch_manager import LaunchManager
    print("Successfully imported core components")
except ImportError as e:
    print(f"Import error for components: {e}")
    # For now, we'll create simplified versions inline

class ScrollableGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPS Animation Suite")
        self.root.geometry("600x700")
        
        # Language setting
        self.language = os.environ.get('GPS_ANALYSIS_LANGUAGE', 'en')
        
        # Mode configuration
        self.modes = {
            '2d_live_map': {'name': '2D Live Map', 'script': 'animate_live_map.py'},
            'mobile_animation': {'name': 'Mobile Animation', 'script': 'mobile_animation.py'},
            '3d_animation': {'name': '3D Animation', 'script': 'animation_3d.py'}
        }
        
        self.selected_mode = tk.StringVar(value='2d_live_map')
        
        # Component references
        self.folder_manager = None
        self.data_preview = None
        self.settings_manager = None
        self.launch_manager = None
        self.status_var = None
        
        self.setup_scrollable_ui()
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
        
        # Update point count calculation
        self.update_point_count_calculation()
    
    def update_status(self):
        """Update status based on folder manager state"""
        if not self.data_preview:
            return
        
        file_count = self.data_preview.get_file_count()
        if file_count > 0:
            total_points = self.data_preview.get_total_points()
            mode_name = self.modes[self.selected_mode.get()]['name']
            self.status_var.set(f"Ready | {file_count} files, {total_points} points | Mode: {mode_name}")
        else:
            self.status_var.set("No GPS data files found")
    
    def on_mode_changed(self, event=None):
        """Handle mode dropdown change"""
        selected_display = self.mode_dropdown.get()
        
        # Extract mode key from display string  
        for mode_key, mode_info in self.modes.items():
            if mode_info['name'] in selected_display:
                self.selected_mode.set(mode_key)
                print(f"Mode changed to: {mode_key} -> {mode_info['name']}")
                break
        
        self.update_status()
    
    def setup_scrollable_ui(self):
        """Setup scrollable UI with all components"""
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create all sections
        self.create_title_section(scrollable_frame)
        self.create_status_section(scrollable_frame)
        self.create_folders_section(scrollable_frame)
        self.create_data_preview_section(scrollable_frame)
        self.create_settings_sections(scrollable_frame)
        self.create_buttons_section(scrollable_frame)
    
    def create_title_section(self, parent):
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
        
        mode_options = [f"🗺️ {self.modes['2d_live_map']['name']}", 
                       f"📱 {self.modes['mobile_animation']['name']}", 
                       f"🌍 {self.modes['3d_animation']['name']}"]
        
        self.mode_dropdown = ttk.Combobox(mode_frame, values=mode_options, state="readonly", width=20)
        self.mode_dropdown.pack(side="left")
        self.mode_dropdown.set(mode_options[0])  # Default to 2D Live Map
        self.mode_dropdown.bind('<<ComboboxSelected>>', self.on_mode_changed)
    
    def create_status_section(self, parent):
        """Create status bar section"""
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(parent, textvariable=self.status_var, 
                               relief="sunken", anchor="w", padding="5")
        status_label.pack(fill="x", pady=(0, 10))
    
    def create_folders_section(self, parent):
        """Create folders section with browse buttons"""
        folder_frame = ttk.LabelFrame(parent, text="📁 Folders", padding="10")
        folder_frame.pack(fill="x", pady=(0, 10))
        
        # Create folder manager without calling setup_ui
        self.folder_manager = FolderManager.__new__(FolderManager)  # Create without __init__
        self.folder_manager.parent_frame = None
        self.folder_manager.get_language = self.get_language
        
        # Initialize folder manager variables manually
        self.folder_manager.data_folder = tk.StringVar(value=os.path.join(os.getcwd(), "data"))
        self.folder_manager.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), "visualizations"))
        
        # Set up callback mechanism
        self.folder_manager.data_folder_callback = None
        
        # Create browse methods manually
        def browse_data_folder():
            from tkinter import filedialog
            language = self.get_language()
            title = "GPS-Datenverzeichnis auswählen" if language == "de" else "Select GPS Data Directory"
            directory = filedialog.askdirectory(title=title, initialdir=self.folder_manager.data_folder.get())
            if directory:
                self.folder_manager.data_folder.set(directory)
                if self.folder_manager.data_folder_callback:
                    self.folder_manager.data_folder_callback(directory)
        
        def browse_output_folder():
            from tkinter import filedialog
            language = self.get_language()
            title = "Ausgabeverzeichnis auswählen" if language == "de" else "Select Output Directory"
            directory = filedialog.askdirectory(title=title, initialdir=self.folder_manager.output_folder.get())
            if directory:
                self.folder_manager.output_folder.set(directory)
        
        # Add validation method
        def validate_folders():
            issues = []
            data_folder = self.folder_manager.data_folder.get()
            output_folder = self.folder_manager.output_folder.get()
            
            if not data_folder or not os.path.exists(data_folder):
                issues.append("Data folder does not exist")
            if not output_folder:
                issues.append("Output folder not specified")
            
            return issues
        
        def get_data_folder():
            return self.folder_manager.data_folder.get()
        
        def get_output_folder():
            return self.folder_manager.output_folder.get()
        
        def set_data_folder_callback(callback):
            self.folder_manager.data_folder_callback = callback
        
        # Attach methods to folder manager
        self.folder_manager.browse_data_folder = browse_data_folder
        self.folder_manager.browse_output_folder = browse_output_folder
        self.folder_manager.validate_folders = validate_folders
        self.folder_manager.get_data_folder = get_data_folder
        self.folder_manager.get_output_folder = get_output_folder
        self.folder_manager.set_data_folder_callback = set_data_folder_callback
        
        # Set up callback
        self.folder_manager.set_data_folder_callback(self.on_data_folder_changed)
        
        # Data folder
        data_frame = ttk.Frame(folder_frame)
        data_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(data_frame, text="Data:").pack(side="left")
        data_entry = ttk.Entry(data_frame, textvariable=self.folder_manager.data_folder, width=50)
        data_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        ttk.Button(data_frame, text="📁", command=self.folder_manager.browse_data_folder, width=3).pack(side="right")
        
        # Output folder
        output_frame = ttk.Frame(folder_frame)
        output_frame.pack(fill="x")
        
        ttk.Label(output_frame, text="Output:").pack(side="left")
        output_entry = ttk.Entry(output_frame, textvariable=self.folder_manager.output_folder, width=50)
        output_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        ttk.Button(output_frame, text="📁", command=self.folder_manager.browse_output_folder, width=3).pack(side="right")
    
    def create_data_preview_section(self, parent):
        """Create data preview section"""
        preview_frame = ttk.LabelFrame(parent, text="📊 Data Preview", padding="10")
        preview_frame.pack(fill="x", pady=(0, 10))
        
        # Create data preview without calling setup_ui
        self.data_preview = DataPreview.__new__(DataPreview)  # Create without __init__
        self.data_preview.parent_frame = None
        self.data_preview.get_language = self.get_language
        
        # Initialize data preview variables manually
        self.data_preview.data_folder_var = None
        
        # Preview text area
        self.data_preview.data_preview = tk.Text(preview_frame, height=4, width=60, wrap=tk.WORD, font=("Arial", 8))
        self.data_preview.data_preview.pack(fill="x", pady=(0, 5))
        
        # Create methods manually
        def set_data_folder_var(folder_var):
            self.data_preview.data_folder_var = folder_var
        
        def refresh_preview():
            if not self.data_preview.data_folder_var:
                return
            
            data_folder = self.data_preview.data_folder_var.get()
            if not data_folder or not os.path.exists(data_folder):
                self.data_preview.data_preview.delete("1.0", tk.END)
                self.data_preview.data_preview.insert("1.0", "No data folder selected or folder doesn't exist")
                return
            
            # Count CSV files
            csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
            if not csv_files:
                self.data_preview.data_preview.delete("1.0", tk.END)
                self.data_preview.data_preview.insert("1.0", "No CSV files found in data folder")
                return
            
            # Show preview
            preview_text = f"Found {len(csv_files)} GPS data files:\\n\\n"
            total_points = 0
            for i, filename in enumerate(csv_files[:5]):  # Show first 5 files
                filepath = os.path.join(data_folder, filename)
                try:
                    import pandas as pd
                    df = pd.read_csv(filepath, sep=';')
                    points = len(df)
                    total_points += points
                    preview_text += f"📄 {filename}: {points} points\\n"
                except Exception as e:
                    preview_text += f"📄 {filename}: Error reading file\\n"
            
            if len(csv_files) > 5:
                preview_text += f"... and {len(csv_files) - 5} more files\\n"
            
            preview_text += f"\\nTotal estimated points: {total_points}"
            
            self.data_preview.data_preview.delete("1.0", tk.END)
            self.data_preview.data_preview.insert("1.0", preview_text)
        
        def get_file_count():
            if not self.data_preview.data_folder_var:
                return 0
            data_folder = self.data_preview.data_folder_var.get()
            if not data_folder or not os.path.exists(data_folder):
                return 0
            return len([f for f in os.listdir(data_folder) if f.endswith('.csv')])
        
        def get_total_points():
            # For now, return a simple estimate
            return get_file_count() * 40  # Rough estimate
        
        # Attach methods to data preview
        self.data_preview.set_data_folder_var = set_data_folder_var
        self.data_preview.refresh_preview = refresh_preview
        self.data_preview.get_file_count = get_file_count
        self.data_preview.get_total_points = get_total_points
        
        # Set up with folder manager
        self.data_preview.set_data_folder_var(self.folder_manager.data_folder)
        
        # Refresh button
        ttk.Button(preview_frame, text="🔄 Refresh", command=self.data_preview.refresh_preview).pack(anchor="w")
    
    def create_settings_sections(self, parent):
        """Create settings sections"""
        # Create settings manager without calling setup_ui
        self.settings_manager = SettingsManager.__new__(SettingsManager)  # Create without __init__
        self.settings_manager.parent_frame = None
        self.settings_manager.get_language = self.get_language
        
        # Initialize settings variables manually
        self.settings_manager.performance_mode = tk.BooleanVar(value=True)
        self.settings_manager.trail_length = tk.DoubleVar(value=2.0)
        self.settings_manager.time_step = tk.StringVar(value="1m")
        
        # Create get_config method
        def get_config():
            return {
                'performance_mode': self.settings_manager.performance_mode.get(),
                'trail_length': self.settings_manager.trail_length.get(),
                'time_step': self.settings_manager.time_step.get(),
                'playback_speed': 1.0
            }
        
        # Attach method to settings manager
        self.settings_manager.get_config = get_config
        
        # Animation settings
        animation_frame = ttk.LabelFrame(parent, text="🎬 Animation Settings", padding="10")
        animation_frame.pack(fill="x", pady=(0, 10))
        
        # Trail length
        trail_frame = ttk.Frame(animation_frame)
        trail_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(trail_frame, text="Trail Length (hours):").pack(side="left")
        self.settings_manager.trail_length = tk.DoubleVar(value=2.0)
        trail_scale = ttk.Scale(trail_frame, from_=0.5, to=12.0, variable=self.settings_manager.trail_length, orient="horizontal")
        trail_scale.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        self.trail_label = ttk.Label(trail_frame, text="2.0 hours")
        self.trail_label.pack(side="right")
        
        def update_trail_label(value):
            self.trail_label.config(text=f"{float(value):.1f} hours")
        trail_scale.config(command=update_trail_label)
        
        # Time step
        time_frame = ttk.Frame(animation_frame)
        time_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(time_frame, text="Time Step:").pack(side="left")
        self.settings_manager.time_step = tk.StringVar(value="1m")
        time_step_combo = ttk.Combobox(time_frame, textvariable=self.settings_manager.time_step, 
                                      values=["1s", "10s", "30s", "1m", "5m", "10m"], state="readonly", width=10)
        time_step_combo.pack(side="left", padx=(10, 0))
        
        # Point count calculation display
        self.point_count_label = ttk.Label(time_frame, text="Point count calculated when data is loaded", 
                                          font=("Arial", 9), foreground="blue")
        self.point_count_label.pack(side="left", padx=(20, 0))
        
        # Bind time step change to update point count
        def on_time_step_change(event=None):
            self.update_point_count_calculation()
        time_step_combo.bind('<<ComboboxSelected>>', on_time_step_change)
        
        # Performance settings
        performance_frame = ttk.LabelFrame(parent, text="⚡ Performance Settings", padding="10")
        performance_frame.pack(fill="x", pady=(0, 10))
        
        performance_checkbox = ttk.Checkbutton(performance_frame, text="Enable Performance Mode", 
                                              variable=self.settings_manager.performance_mode)
        performance_checkbox.pack(anchor="w", pady=(0, 5))
        
        ttk.Label(performance_frame, text="• Enabled: Line+head rendering with adaptive LOD for large datasets", 
                 font=("Arial", 8), foreground="gray").pack(anchor="w")
    
    def create_buttons_section(self, parent):
        """Create buttons section"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=20)
        
        # Create launch manager
        self.launch_manager = LaunchManager(self.get_language)
        
        ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_data).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🎯 Mode Info", command=self.show_mode_info).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch", command=self.launch_selected_mode).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="❌ Close", command=self.root.destroy).pack(side="left")
    
    def refresh_data(self):
        """Manually refresh all data"""
        if self.data_preview:
            self.data_preview.refresh_preview()
            self.update_status()
        self.update_point_count_calculation()
    
    def show_mode_info(self):
        """Show current mode information"""
        mode_key = self.selected_mode.get()
        mode_info = self.modes[mode_key]
        print(f"Current mode: {mode_info['name']}")
        print(f"Script: {mode_info['script']}")
        self.status_var.set(f"Mode: {mode_info['name']} -> scripts/{mode_info['script']}")
    
    def launch_selected_mode(self):
        """Launch based on selected mode"""
        try:
            mode_key = self.selected_mode.get()
            mode_info = self.modes[mode_key]
            
            self.status_var.set(f"Launching {mode_info['name']}...")
            self.root.update()
            
            if mode_key == "2d_live_map":
                # Use existing LaunchManager for 2D maps
                result = self.launch_manager.launch_map(self.folder_manager, self.settings_manager)
                status = "2D Live Map launched!" if result else "2D Live Map launch failed"
            else:
                # For mobile_animation and 3d_animation
                result = self.launch_script(mode_info['script'])
                status = f"{mode_info['name']} launched!" if result else f"{mode_info['name']} launch failed"
            
            self.status_var.set(status)
            
        except Exception as e:
            print(f"Launch error: {e}")
            self.status_var.set(f"Launch error: {str(e)}")
    
    def launch_script(self, script_name):
        """Launch a script with proper configuration"""
        import subprocess
        
        try:
            # Validate folders first
            issues = self.folder_manager.validate_folders()
            if issues:
                print(f"Folder validation issues: {issues}")
                self.status_var.set(f"Error: {issues[0]}")
                return False
            
            # Get configuration
            config = self.settings_manager.get_config()
            data_folder = self.folder_manager.get_data_folder()
            output_folder = self.folder_manager.get_output_folder()
            
            script_path = os.path.join("scripts", script_name)
            if os.path.exists(script_path):
                print(f"Launching {script_path} with configuration:")
                print(f"  Data folder: {data_folder}")
                print(f"  Output folder: {output_folder}")
                print(f"  Trail length: {config['trail_length']} hours")
                print(f"  Time step: {config['time_step']}")
                print(f"  Performance mode: {config['performance_mode']}")
                
                # Set environment variables for configuration
                env = os.environ.copy()
                env['GPS_DATA_DIR'] = data_folder
                env['OUTPUT_DIR'] = output_folder
                env['TRAIL_LENGTH_HOURS'] = str(config['trail_length'])
                env['TIME_STEP'] = config['time_step']
                env['PLAYBACK_SPEED'] = str(config.get('playback_speed', 1.0))
                env['PERFORMANCE_MODE'] = '1' if config['performance_mode'] else '0'
                
                # Launch the script with environment variables
                subprocess.Popen(["python3", script_path], env=env)
                return True
            else:
                print(f"Script not found: {script_path}")
                return False
        except Exception as e:
            print(f"Error launching script: {e}")
            return False
    
    def update_point_count_calculation(self):
        """Update the point count display based on current time step and loaded data"""
        try:
            # Get the currently selected folder and its CSV files
            data_folder = self.folder_manager.data_folder.get()
            if not data_folder or not os.path.exists(data_folder):
                self.point_count_label.config(text="Point count calculated when data is loaded")
                return
            
            # Find CSV files in the folder
            csv_files = [f for f in os.listdir(data_folder) 
                        if f.endswith('.csv') and not f.startswith('.')]
            
            if not csv_files:
                self.point_count_label.config(text="No CSV files found in selected folder")
                return
            
            # Read first CSV file to get data structure
            first_csv = os.path.join(data_folder, csv_files[0])
            try:
                import pandas as pd
                df = pd.read_csv(first_csv, sep=';')
                
                # Look for timestamp column with different possible names
                timestamp_col = None
                possible_timestamp_cols = ['timestamp', 'Timestamp', 'Timestamp [UTC]', 'time', 'Time', 'datetime', 'DateTime']
                
                for col in possible_timestamp_cols:
                    if col in df.columns:
                        timestamp_col = col
                        break
                
                if not timestamp_col:
                    self.point_count_label.config(text="No timestamp column found in CSV file")
                    return
                
                # Convert time step to seconds for calculation
                time_step_str = self.settings_manager.time_step.get()
                time_step_seconds = self.convert_time_step_to_seconds(time_step_str)
                
                # Calculate total timespan
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], format='%d.%m.%Y %H:%M:%S', errors='coerce')
                
                # Drop rows where timestamp conversion failed
                df = df.dropna(subset=[timestamp_col])
                
                if len(df) == 0:
                    self.point_count_label.config(text="Cannot parse timestamp format in CSV file")
                    return
                
                # Get original number of points in the file
                original_points = len(df)
                
                total_duration = (df[timestamp_col].max() - df[timestamp_col].min()).total_seconds()
                
                # Calculate expected number of points
                if total_duration > 0:
                    estimated_points = int(total_duration / time_step_seconds) + 1
                    total_files = len(csv_files)
                    
                    # Calculate percentage reduction
                    if original_points > 0:
                        reduction_percent = ((original_points - estimated_points) / original_points) * 100
                        
                        if reduction_percent > 0:
                            self.point_count_label.config(
                                text=f"≈ {estimated_points:,} points per file (was {original_points:,}, {reduction_percent:.1f}% reduction) • {total_files} files • {time_step_str} steps",
                                foreground="darkgreen"
                            )
                        else:
                            # If estimated points >= original points (very fine time step)
                            increase_percent = ((estimated_points - original_points) / original_points) * 100
                            self.point_count_label.config(
                                text=f"≈ {estimated_points:,} points per file (was {original_points:,}, {increase_percent:.1f}% increase) • {total_files} files • {time_step_str} steps",
                                foreground="darkorange"
                            )
                    else:
                        self.point_count_label.config(
                            text=f"≈ {estimated_points:,} points per file ({total_files} files) with {time_step_str} steps",
                            foreground="darkgreen"
                        )
                else:
                    self.point_count_label.config(text="Cannot calculate: insufficient time data")
                    
            except Exception as e:
                self.point_count_label.config(text=f"Error calculating points: {str(e)[:30]}...")
                
        except Exception as e:
            self.point_count_label.config(text="Point count calculated when data is loaded")
    
    def convert_time_step_to_seconds(self, time_step_str):
        """Convert time step string to seconds"""
        if time_step_str.endswith('s'):
            return int(time_step_str[:-1])
        elif time_step_str.endswith('m'):
            return int(time_step_str[:-1]) * 60
        elif time_step_str.endswith('h'):
            return int(time_step_str[:-1]) * 3600
        else:
            return 60  # Default to 1 minute
    
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
        self.update_point_count_calculation()
        
        self.root.mainloop()


def main():
    print("Starting scrollable GUI with mode dropdown...")
    app = ScrollableGUI()
    app.run()
    print("GUI closed.")


if __name__ == "__main__":
    main()

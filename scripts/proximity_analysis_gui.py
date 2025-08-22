#!/usr/bin/env python3
"""
Proximity Analysis GUI Application

Professional graphical interface for vulture proximity analysis.
Makes the analysis accessible to non-technical users through an intuitive interface.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import webbrowser
from pathlib import Path
import pandas as pd

# Add the scripts directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import DataLoader
from core.proximity_engine import ProximityEngine
from visualization.proximity_plots import ProximityVisualizer
from animate_live_map import LiveMapAnimator
from proximity_analysis import group_proximity_events, parse_time_step


class ProximityAnalysisGUI:
    """Professional GUI for Vulture Proximity Analysis"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🦅 Vulture Proximity Analysis - Professional Edition")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Analysis state
        self.data_folder = tk.StringVar(value="data")
        self.proximity_threshold = tk.DoubleVar(value=2.0)
        self.time_threshold = tk.IntVar(value=5)
        self.generate_animations = tk.BooleanVar(value=False)
        self.time_buffer = tk.DoubleVar(value=2.0)
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        self.limit_encounters = tk.IntVar(value=0)
        
        # Results storage
        self.results = {}
        self.output_files = []
        
        # Thread management
        self.analysis_thread = None
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.check_log_queue()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🦅 Vulture Proximity Analysis", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Setup tabs
        self.setup_data_tab()
        self.setup_analysis_tab()
        self.setup_animation_tab()
        self.setup_results_tab()
        self.setup_log_tab()
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.run_button = ttk.Button(button_frame, text="🚀 Run Analysis", 
                                    command=self.run_analysis, style='Accent.TButton')
        self.run_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹ Stop", 
                                     command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Open Results Folder", 
                  command=self.open_results_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="❓ Help", 
                  command=self.show_help).pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to analyze vulture GPS data")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_data_tab(self):
        """Setup data configuration tab"""
        data_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(data_frame, text="📁 Data")
        
        # Data folder selection
        ttk.Label(data_frame, text="GPS Data Folder:", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        folder_frame = ttk.Frame(data_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(0, weight=1)
        
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.data_folder, width=50)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(folder_frame, text="Browse...", 
                  command=self.browse_folder).grid(row=0, column=1)
        
        # Data preview
        ttk.Label(data_frame, text="Data Preview:", font=('Arial', 11, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.data_preview = scrolledtext.ScrolledText(data_frame, height=15, width=70)
        self.data_preview.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        data_frame.rowconfigure(3, weight=1)
        data_frame.columnconfigure(0, weight=1)
        
        ttk.Button(data_frame, text="🔄 Refresh Data Preview", 
                  command=self.refresh_data_preview).grid(row=4, column=0, pady=(10, 0))
        
    def setup_analysis_tab(self):
        """Setup analysis parameters tab"""
        analysis_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(analysis_frame, text="⚙️ Analysis")
        
        # Proximity threshold
        ttk.Label(analysis_frame, text="Proximity Analysis Parameters:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        param_frame = ttk.LabelFrame(analysis_frame, text="Detection Parameters", padding="15")
        param_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(param_frame, text="Proximity Threshold (km):").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))
        proximity_scale = ttk.Scale(param_frame, from_=0.1, to=10.0, 
                                   variable=self.proximity_threshold, orient=tk.HORIZONTAL)
        proximity_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 10))
        self.proximity_label = ttk.Label(param_frame, text="2.0 km")
        self.proximity_label.grid(row=0, column=2, pady=(0, 10))
        proximity_scale.configure(command=self.update_proximity_label)
        
        ttk.Label(param_frame, text="Time Threshold (minutes):").grid(
            row=1, column=0, sticky=tk.W)
        time_scale = ttk.Scale(param_frame, from_=1, to=60, 
                              variable=self.time_threshold, orient=tk.HORIZONTAL)
        time_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.time_label = ttk.Label(param_frame, text="5 min")
        self.time_label.grid(row=1, column=2)
        time_scale.configure(command=self.update_time_label)
        
        param_frame.columnconfigure(1, weight=1)
        
        # Analysis options
        options_frame = ttk.LabelFrame(analysis_frame, text="Analysis Options", padding="15")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Checkbutton(options_frame, text="Generate encounter animations", 
                       variable=self.generate_animations,
                       command=self.toggle_animation_options).grid(row=0, column=0, sticky=tk.W)
        
        # Help text
        help_frame = ttk.LabelFrame(analysis_frame, text="Parameter Guide", padding="15")
        help_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        help_text = """
        • Proximity Threshold: Maximum distance between vultures to count as a proximity event
        • Time Threshold: Minimum duration for a proximity event to be recorded
        • Encounter Animations: Creates interactive maps showing vulture interactions
        """
        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        analysis_frame.columnconfigure(0, weight=1)
        
    def setup_animation_tab(self):
        """Setup animation parameters tab"""
        animation_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(animation_frame, text="🎬 Animation")
        
        # Animation settings
        ttk.Label(animation_frame, text="Animation Configuration:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Time buffer
        buffer_frame = ttk.LabelFrame(animation_frame, text="Data Range", padding="15")
        buffer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(buffer_frame, text="Time Buffer (hours):").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        buffer_scale = ttk.Scale(buffer_frame, from_=0.5, to=12.0, 
                                variable=self.time_buffer, orient=tk.HORIZONTAL)
        buffer_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 10))
        self.buffer_label = ttk.Label(buffer_frame, text="2.0 hours")
        self.buffer_label.grid(row=0, column=2, pady=(0, 10))
        buffer_scale.configure(command=self.update_buffer_label)
        
        # Trail length
        ttk.Label(buffer_frame, text="Trail Length (hours):").grid(row=1, column=0, sticky=tk.W)
        trail_scale = ttk.Scale(buffer_frame, from_=0.1, to=6.0, 
                               variable=self.trail_length, orient=tk.HORIZONTAL)
        trail_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.trail_label = ttk.Label(buffer_frame, text="2.0 hours")
        self.trail_label.grid(row=1, column=2)
        trail_scale.configure(command=self.update_trail_label)
        
        buffer_frame.columnconfigure(1, weight=1)
        
        # Time step
        step_frame = ttk.LabelFrame(animation_frame, text="Animation Quality", padding="15")
        step_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(step_frame, text="Time Step:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        time_step_combo = ttk.Combobox(step_frame, textvariable=self.time_step, 
                                      values=['1s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '1h'],
                                      state='readonly', width=10)
        time_step_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        ttk.Label(step_frame, text="Quality Guide:", font=('Arial', 9, 'italic')).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        ttk.Label(step_frame, text="• 1s-30s: Ultra-smooth (slower processing)", 
                 font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 1m-5m: Balanced quality and speed", 
                 font=('Arial', 8)).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 10m-1h: Fast processing (less detail)", 
                 font=('Arial', 8)).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        # Performance options
        perf_frame = ttk.LabelFrame(animation_frame, text="Performance Options", padding="15")
        perf_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(perf_frame, text="Limit Encounters (0 = all):").grid(row=0, column=0, sticky=tk.W)
        limit_scale = ttk.Scale(perf_frame, from_=0, to=50, 
                               variable=self.limit_encounters, orient=tk.HORIZONTAL)
        limit_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.limit_label = ttk.Label(perf_frame, text="No limit")
        self.limit_label.grid(row=0, column=2)
        limit_scale.configure(command=self.update_limit_label)
        
        perf_frame.columnconfigure(1, weight=1)
        animation_frame.columnconfigure(0, weight=1)
        
    def setup_results_tab(self):
        """Setup results display tab"""
        results_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(results_frame, text="📊 Results")
        
        # Results summary
        ttk.Label(results_frame, text="Analysis Results:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=70)
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Output files
        files_frame = ttk.LabelFrame(results_frame, text="Generated Files", padding="10")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.files_listbox = tk.Listbox(files_frame, height=6)
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.files_listbox.bind('<Double-1>', self.open_selected_file)
        
        files_buttons = ttk.Frame(files_frame)
        files_buttons.grid(row=0, column=1, sticky=(tk.N))
        
        ttk.Button(files_buttons, text="📂 Open", 
                  command=self.open_selected_file).pack(pady=(0, 5))
        ttk.Button(files_buttons, text="📁 Show in Folder", 
                  command=self.show_in_folder).pack()
        
        files_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
    def setup_log_tab(self):
        """Setup log display tab"""
        log_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(log_frame, text="📝 Log")
        
        ttk.Label(log_frame, text="Analysis Log:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=25, width=80)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_buttons = ttk.Frame(log_frame)
        log_buttons.grid(row=2, column=0, pady=(10, 0))
        
        ttk.Button(log_buttons, text="🗑 Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_buttons, text="💾 Save Log", 
                  command=self.save_log).pack(side=tk.LEFT)
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(1, weight=1)
        
    def update_proximity_label(self, value):
        """Update proximity threshold label"""
        self.proximity_label.config(text=f"{float(value):.1f} km")
        
    def update_time_label(self, value):
        """Update time threshold label"""
        self.time_label.config(text=f"{int(float(value))} min")
        
    def update_buffer_label(self, value):
        """Update time buffer label"""
        self.buffer_label.config(text=f"{float(value):.1f} hours")
        
    def update_trail_label(self, value):
        """Update trail length label"""
        self.trail_label.config(text=f"{float(value):.1f} hours")
        
    def update_limit_label(self, value):
        """Update encounter limit label"""
        limit = int(float(value))
        self.limit_label.config(text="No limit" if limit == 0 else f"{limit} encounters")
        
    def toggle_animation_options(self):
        """Enable/disable animation tab based on checkbox"""
        if self.generate_animations.get():
            self.notebook.tab(2, state='normal')  # Enable animation tab
        else:
            self.notebook.tab(2, state='disabled')  # Disable animation tab
            
    def browse_folder(self):
        """Browse for data folder"""
        folder = filedialog.askdirectory(title="Select GPS Data Folder", 
                                        initialdir=self.data_folder.get())
        if folder:
            self.data_folder.set(folder)
            self.refresh_data_preview()
            
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
                self.data_preview.insert(tk.END, f"⚠️ No CSV files found in: {folder}\n")
                return
                
            self.data_preview.insert(tk.END, f"📁 Data Folder: {folder}\n")
            self.data_preview.insert(tk.END, f"📄 Found {len(csv_files)} CSV file(s):\n\n")
            
            total_points = 0
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    points = len(df)
                    total_points += points
                    self.data_preview.insert(tk.END, f"  ✅ {csv_file.name:<30} ({points:,} GPS points)\n")
                except Exception as e:
                    self.data_preview.insert(tk.END, f"  ❌ {csv_file.name:<30} (Error: {e})\n")
            
            self.data_preview.insert(tk.END, f"\n📊 Total GPS points: {total_points:,}\n")
            
            if total_points > 100000:
                self.data_preview.insert(tk.END, "\n⚠️  Large dataset detected. Consider using larger time steps for animations.\n")
                
        except Exception as e:
            self.data_preview.insert(tk.END, f"❌ Error reading data folder: {e}\n")
            
    def log(self, message):
        """Add message to log queue"""
        self.log_queue.put(message)
        
    def check_log_queue(self):
        """Check for new log messages"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_log_queue)
            
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Log File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
                
    def run_analysis(self):
        """Run the proximity analysis in a separate thread"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showwarning("Warning", "Analysis is already running!")
            return
            
        # Validate inputs
        if not os.path.exists(self.data_folder.get()):
            messagebox.showerror("Error", "Please select a valid data folder!")
            return
            
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.files_listbox.delete(0, tk.END)
        self.output_files.clear()
        self.clear_log()
        
        # Update UI state
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Running proximity analysis...")
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._run_analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def stop_analysis(self):
        """Stop the running analysis"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            # Note: This is a graceful stop - the thread will finish current operation
            self.log("🛑 Stop requested by user...")
            self.status_var.set("Stopping analysis...")
            
    def _run_analysis_worker(self):
        """Worker function for analysis thread"""
        try:
            self.log("🚀 Starting Vulture Proximity Analysis...")
            self.log(f"📁 Data folder: {self.data_folder.get()}")
            
            # Load data
            self.log("📊 Loading GPS data...")
            data_loader = DataLoader()
            data_loader.data_folder = self.data_folder.get()
            
            dataframes = data_loader.load_all_csv_files()
            
            if not dataframes:
                self.log("❌ No GPS data found!")
                return False
                
            self.log(f"✅ Loaded {len(dataframes)} GPS data files")
            
            # Initialize proximity engine
            proximity_engine = ProximityEngine()
            proximity_engine.load_dataframes(dataframes)
            
            # Set parameters
            proximity_engine.proximity_threshold_km = self.proximity_threshold.get()
            proximity_engine.min_duration_minutes = self.time_threshold.get()
            
            self.log(f"⚙️  Proximity threshold: {self.proximity_threshold.get()} km")
            self.log(f"⚙️  Time threshold: {self.time_threshold.get()} minutes")
            
            # Run proximity analysis
            self.log("🔍 Analyzing proximity events...")
            events = proximity_engine.analyze_proximity()
            
            if not events:
                self.log("⚠️  No proximity events found with current parameters")
                self.log("💡 Try increasing the proximity threshold or check your data")
                self._update_results("No proximity events found")
                return True
                
            self.log(f"✅ Found {len(events)} proximity events!")
            
            # Generate encounters animations if requested
            if self.generate_animations.get():
                self.log("🎬 Creating encounter animations...")
                self._create_animations(events, proximity_engine.gps_data)
            
            # Calculate statistics
            self.log("📊 Calculating statistics...")
            statistics = proximity_engine.calculate_statistics()
            
            # Create visualizations
            self.log("📈 Creating visualizations...")
            visualizer = ProximityVisualizer()
            visualizer.create_all_visualizations(events, statistics)
            
            # Export results
            self.log("💾 Exporting results...")
            events_df = proximity_engine.get_events_dataframe()
            
            from gps_utils import get_numbered_output_path
            output_path = get_numbered_output_path('proximity_events', 'analysis')
            output_path = output_path.replace('.html', '.csv')
            events_df.to_csv(output_path, index=False)
            self.output_files.append(output_path)
            self.log(f"📄 Events data saved to: {output_path}")
            
            # Update results display
            self._update_results_display(statistics, events)
            
            self.log("🎉 Proximity analysis completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"❌ Analysis failed: {e}")
            return False
        finally:
            # Reset UI state
            self.root.after(0, self._analysis_finished)
            
    def _create_animations(self, events, gps_data):
        """Create encounter animations"""
        try:
            # Group events into encounters
            encounters = group_proximity_events(events)
            
            if not encounters:
                self.log("⚠️  No encounter groups found")
                return
                
            self.log(f"🎬 Found {len(encounters)} encounter group(s) to animate")
            
            # Apply encounter limit if set
            limit = self.limit_encounters.get()
            if limit > 0 and limit < len(encounters):
                encounters = encounters[:limit]
                self.log(f"⚡ Limited to first {limit} encounters for performance")
            
            # Parse time step
            time_step_seconds = parse_time_step(self.time_step.get())
            if time_step_seconds is None:
                time_step_seconds = 60  # Default to 1 minute
                
            animated_count = 0
            
            for i, encounter in enumerate(encounters, 1):
                try:
                    self.log(f"🎨 Creating animation for encounter {i}/{len(encounters)}...")
                    
                    # Create encounter dataset
                    from proximity_analysis import create_encounter_dataset
                    encounter_data = create_encounter_dataset(
                        encounter, gps_data, self.time_buffer.get()
                    )
                    
                    if encounter_data is None or len(encounter_data) == 0:
                        self.log(f"⚠️  No GPS data found for encounter {i}, skipping...")
                        continue
                    
                    # Create LiveMapAnimator with encounter data
                    animator = LiveMapAnimator()
                    animator.dataframes = encounter_data
                    animator.combined_data = pd.concat(encounter_data, ignore_index=True)
                    
                    # Configure for encounter animation
                    animator.selected_time_step = time_step_seconds
                    animator.trail_system.trail_length_minutes = self.trail_length.get() * 60
                    
                    # Create the visualization
                    success = animator.create_visualization()
                    
                    if success:
                        animated_count += 1
                        duration = encounter['duration_minutes']
                        vultures = ', '.join(encounter['vultures'])
                        self.log(f"✅ Encounter {i} animated: {vultures} ({duration:.1f} min)")
                        
                        # Add to output files list
                        # Note: Would need to get the actual output path from animator
                        
                    else:
                        self.log(f"⚠️  Failed to animate encounter {i}")
                        
                except KeyboardInterrupt:
                    self.log(f"⚠️  Animation interrupted at encounter {i}")
                    break
                except Exception as e:
                    self.log(f"❌ Error animating encounter {i}: {e}")
                    continue
            
            if animated_count > 0:
                self.log(f"🎉 Successfully created {animated_count} encounter animations!")
            else:
                self.log("⚠️  No encounter animations were created")
                
        except Exception as e:
            self.log(f"❌ Animation creation failed: {e}")
            
    def _update_results_display(self, statistics, events):
        """Update the results display"""
        try:
            results_text = f"""
🦅 VULTURE PROXIMITY ANALYSIS RESULTS
{'='*50}

📊 SUMMARY STATISTICS:
• Total proximity events: {statistics.total_events:,}
• Unique vulture pairs: {statistics.unique_pairs}
• Average distance: {statistics.average_distance_km:.2f} km
• Closest encounter: {statistics.closest_distance_km:.2f} km
• Total proximity time: {statistics.total_duration_hours:.1f} hours
• Most active pair: {statistics.most_active_pair}
• Peak activity hour: {statistics.peak_activity_hour}:00

🦅 EVENTS BY VULTURE:
"""
            for vulture, count in statistics.events_by_vulture.items():
                results_text += f"• {vulture}: {count} events\n"
                
            results_text += "\n⏰ EVENTS BY HOUR:\n"
            for hour in sorted(statistics.events_by_hour.keys()):
                count = statistics.events_by_hour[hour]
                results_text += f"• {hour:02d}:00: {count} events\n"
                
            # Update results in main thread
            self.root.after(0, lambda: self.results_text.insert(tk.END, results_text))
            
        except Exception as e:
            self.log(f"❌ Error updating results display: {e}")
            
    def _update_results(self, message):
        """Update results with a simple message"""
        self.root.after(0, lambda: self.results_text.insert(tk.END, message))
        
    def _analysis_finished(self):
        """Called when analysis is finished"""
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Analysis completed")
        
        # Update file list
        for file_path in self.output_files:
            self.files_listbox.insert(tk.END, os.path.basename(file_path))
            
    def open_selected_file(self, event=None):
        """Open the selected file"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.output_files):
                file_path = self.output_files[index]
                try:
                    webbrowser.open(f"file://{os.path.abspath(file_path)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")
                    
    def show_in_folder(self):
        """Show selected file in folder"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.output_files):
                file_path = self.output_files[index]
                try:
                    folder_path = os.path.dirname(file_path)
                    webbrowser.open(f"file://{folder_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open folder: {e}")
                    
    def open_results_folder(self):
        """Open the results folder"""
        try:
            results_folder = os.path.join(os.path.dirname(__file__), '..', 'visualizations')
            results_folder = os.path.abspath(results_folder)
            webbrowser.open(f"file://{results_folder}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open results folder: {e}")
            
    def show_help(self):
        """Show help dialog"""
        help_text = """
🦅 Vulture Proximity Analysis - Help

OVERVIEW:
This application analyzes GPS tracking data to identify when vultures are in close proximity to each other.

TABS:
📁 Data: Select your GPS data folder and preview files
⚙️ Analysis: Configure proximity detection parameters  
🎬 Animation: Configure encounter animation settings
📊 Results: View analysis results and statistics
📝 Log: Monitor analysis progress and messages

QUICK START:
1. Select your GPS data folder in the Data tab
2. Adjust proximity and time thresholds in Analysis tab
3. Optionally enable encounter animations
4. Click "Run Analysis" to start

TIPS:
• Use larger proximity thresholds for initial exploration
• Enable animations only for smaller datasets initially
• Check the log for detailed progress information
• Results are saved in the visualizations folder

For more information, visit the project documentation.
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Vulture Proximity Analysis")
        help_window.geometry("600x500")
        help_window.configure(bg='#f0f0f0')
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    ProximityAnalysisGUI(root)
    
    # Set window icon if available
    try:
        # You could add an icon file here
        # root.iconbitmap('vulture_icon.ico')
        pass
    except Exception:
        pass
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()

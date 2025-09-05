#!/usr/bin/env python3
"""
Proximity Analysis GUI - Event Handlers

Handles user interactions like button clicks, file browsing, and validation.
"""

import os
import threading
import queue
import subprocess
import platform
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


class ProximityEventHandler:
    """Handles user events and interactions for the Proximity Analysis GUI"""
    
    def __init__(self, config, i18n_handler=None):
        self.config = config
        self.i18n_handler = i18n_handler
        
        # Initialize logging queue
        self.config.log_queue = queue.Queue()
        
        # Start log queue checking
        self._start_log_queue_checker()
    
    def browse_folder(self):
        """Handle data folder browsing"""
        folder = filedialog.askdirectory(
            title="Select Data Folder",
            initialdir=self.config.data_folder.get()
        )
        if folder:
            self.config.data_folder.set(folder)
            self.refresh_data_preview()
    
    def browse_output_folder(self):
        """Handle output folder browsing"""
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.config.output_folder.get()
        )
        if folder:
            self.config.output_folder.set(folder)
    
    def refresh_data_preview(self):
        """Refresh the data preview display"""
        if not self.config.data_preview:
            return
            
        try:
            # Import here to avoid circular imports
            from core.gps_utils import DataLoader
            
            # Clear existing preview
            for item in self.config.data_preview.get_children():
                self.config.data_preview.delete(item)
            
            # Load data files
            data_loader = DataLoader(self.config.data_folder.get())
            csv_files = data_loader.find_csv_files()
            
            if not csv_files:
                self.config.data_preview.insert('', 'end', values=('No CSV files found', '', ''))
                return
            
            # Preview each file
            for file_path in csv_files:
                try:
                    df = data_loader.load_single_csv(file_path, validate=False)
                    if df is not None:
                        filename = os.path.basename(file_path)
                        num_records = len(df)
                        vulture_id = df['vulture_id'].iloc[0] if 'vulture_id' in df.columns else 'Unknown'
                        self.config.data_preview.insert('', 'end', values=(filename, vulture_id, f"{num_records} records"))
                    else:
                        filename = os.path.basename(file_path)
                        self.config.data_preview.insert('', 'end', values=(filename, 'Error', 'Failed to load'))
                except Exception as e:
                    filename = os.path.basename(file_path)
                    self.config.data_preview.insert('', 'end', values=(filename, 'Error', str(e)[:50]))
                    
        except Exception as e:
            self.log(f"Error refreshing data preview: {e}")
    
    def toggle_animation_options(self):
        """Handle animation options toggle"""
        # This would be implemented by the UI builder that creates the animation controls
        pass
    
    def run_analysis(self):
        """Start the proximity analysis in a background thread"""
        if self.config.analysis_running:
            return
        
        # Validate configuration
        is_valid, errors = self.config.is_valid_configuration()
        if not is_valid:
            messagebox.showerror("Configuration Error", "\\n".join(errors))
            return
        
        # Check if data folder exists and has files
        try:
            from core.gps_utils import DataLoader
            data_loader = DataLoader(self.config.data_folder.get())
            csv_files = data_loader.find_csv_files()
            if not csv_files:
                messagebox.showerror("Data Error", "No CSV files found in the selected data folder.")
                return
        except Exception as e:
            messagebox.showerror("Data Error", f"Error accessing data folder: {e}")
            return
        
        # Update UI state
        self.config.analysis_running = True
        if self.config.run_button:
            self.config.run_button.config(state='disabled')
        if self.config.stop_button:
            self.config.stop_button.config(state='normal')
        
        translator = self.config.translator
        status_text = "Running analysis..." if not translator else translator.t("status_running")
        self.config.status_var.set(status_text)

        # Clear previous results
        self.config.results = {}
        self.config.timeline = []
        self.config.result_files = {}

        # Start analysis thread
        self.config.analysis_thread = threading.Thread(target=self._run_analysis_worker, daemon=True)
        self.config.analysis_thread.start()
    
    def stop_analysis(self):
        """Stop the running analysis"""
        if self.config.analysis_running:
            self.config.analysis_running = False
            translator = self.config.translator
            status_text = "Analysis stopped" if not translator else translator.t("status_stopped")
            self.config.status_var.set(status_text)
            self._analysis_finished()
    
    def _run_analysis_worker(self):
        """Worker function that runs the analysis in background"""
        try:
            # Import analysis functions
            from core.gps_utils import DataLoader, get_numbered_output_path
            from core.analysis.proximity_engine import ProximityEngine
            
            # Get parameters
            params = self.config.get_analysis_parameters()
            
            # Log start
            self.log("Starting proximity analysis...")
            
            # Load GPS data
            self.log("Loading GPS data...")
            data_loader = DataLoader(params['data_folder'])
            dataframes = data_loader.load_all_csv_files()
            
            if not dataframes:
                self.log("❌ No valid GPS data found")
                return
            
            self.log(f"✅ Loaded {len(dataframes)} vulture datasets")
            
            # Initialize and configure proximity engine
            self.log("Configuring proximity engine...")
            engine = ProximityEngine()
            engine.load_dataframes(dataframes)
            engine.proximity_threshold_km = float(params['proximity_threshold'])
            engine.min_duration_minutes = float(params['time_threshold'])

            self.log(f"⚙️ Proximity threshold: {engine.proximity_threshold_km} km")
            self.log(f"⚙️ Time threshold: {engine.min_duration_minutes} minutes")

            # Run proximity analysis
            self.log("Analyzing proximity events...")
            events = engine.analyze_proximity()

            if not events:
                self.log("⚠️ No proximity events found with current parameters")
                self.config.results = {
                    'total_events': 0,
                    'unique_pairs': 0,
                    'avg_distance_km': 0.0,
                    'closest_distance_km': 0.0,
                }
                self.config.timeline = []
                self._update_results_display()
                return

            self.log(f"✅ Found {len(events)} proximity events!")

            # Calculate statistics (without generating visualizations here)
            self.log("Calculating statistics...")
            stats = engine.calculate_statistics()

            # Export events dataframe to CSV in the selected output folder
            try:
                # Respect the configured output folder using OUTPUT_DIR for helpers
                output_dir = params['output_folder']
                if output_dir:
                    os.environ['OUTPUT_DIR'] = output_dir
                events_df = engine.get_events_dataframe()
                csv_path = get_numbered_output_path('proximity_events', 'analysis').replace('.html', '.csv')
                events_df.to_csv(csv_path, index=False)
                self.log(f"📄 Events CSV saved to: {csv_path}")
                # Track result file
                self.config.result_files = self.config.result_files or {}
                self.config.result_files['events_csv'] = csv_path
            except Exception as e:
                self.log(f"⚠️ Failed to export events CSV: {e}")

            # Populate results for display
            self.config.results = {
                'total_events': stats.total_events,
                'unique_pairs': stats.unique_pairs,
                'avg_distance_km': getattr(stats, 'average_distance_km', 0.0),
                'closest_distance_km': getattr(stats, 'closest_distance_km', 0.0),
            }

            # Create the same HTML visualizations as before (timeline, map, dashboard)
            try:
                from utils.proximity_plots import ProximityVisualizer
                if output_dir:
                    os.environ['OUTPUT_DIR'] = output_dir  # ensure visualizer saves to chosen folder
                self.log("📈 Creating visualizations (timeline, map, dashboard)...")
                viz = ProximityVisualizer()
                viz.create_all_visualizations(events, stats)
                self.log("✨ Visualizations created.")
            except Exception as ve:
                self.log(f"⚠️ Visualization creation failed: {ve}")

            # Build a simple timeline from events (start=end=timestamp)
            self.config.timeline = []
            for idx, ev in enumerate(events, start=1):
                ts = ev.timestamp
                # Use a nominal end equal to start (engine doesn't group durations here)
                self.config.timeline.append({
                    'id': idx,
                    'start': ts,
                    'end': ts,  # no duration info at this stage
                    'pair': (ev.vulture1, ev.vulture2),
                })

            self.log("✅ Analysis completed successfully!")

            # Update results display
            self._update_results_display()
            
        except Exception as e:
            self.log(f"❌ Analysis failed: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            if self.config.analysis_running:
                self._analysis_finished()
    
    def _update_results_display(self):
        """Update the results display with analysis results"""
        if not self.config.results_tree or not self.config.results:
            return
        
        try:
            # Clear existing results
            for item in self.config.results_tree.get_children():
                self.config.results_tree.delete(item)
            
            # Add results
            results = self.config.results
            self.config.results_tree.insert('', 'end', values=('Total Events', results.get('total_events', 0)))
            self.config.results_tree.insert('', 'end', values=('Unique Pairs', results.get('unique_pairs', 0)))
            if 'avg_distance_km' in results:
                self.config.results_tree.insert('', 'end', values=('Average Distance (km)', f"{results.get('avg_distance_km', 0.0):.2f}"))
            if 'closest_distance_km' in results:
                self.config.results_tree.insert('', 'end', values=('Closest Distance (km)', f"{results.get('closest_distance_km', 0.0):.2f}"))

            # If timeline is available, add a small summary row
            if getattr(self.config, 'timeline', None):
                self.config.results_tree.insert('', 'end', values=('Timeline Events', len(self.config.timeline)))
            
            # Add exported files if available
            if getattr(self.config, 'result_files', None):
                for label, path in self.config.result_files.items():
                    self.config.results_tree.insert('', 'end', values=(label.replace('_', ' ').title(), path))
            
        except Exception as e:
            self.log(f"Error updating results display: {e}")
    
    def _analysis_finished(self):
        """Handle analysis completion"""
        self.config.analysis_running = False
        
        # Update UI state
        if self.config.run_button:
            self.config.run_button.config(state='normal')
        if self.config.stop_button:
            self.config.stop_button.config(state='disabled')
        
        translator = self.config.translator
        if self.config.results:
            status_text = "Analysis completed" if not translator else translator.t("status_completed")
        else:
            status_text = "Analysis stopped" if not translator else translator.t("status_stopped")
        
        self.config.status_var.set(status_text)
    
    def open_selected_file(self, event=None):
        """Open selected result file in browser"""
        if not self.config.results_tree:
            return
            
        selection = self.config.results_tree.selection()
        if selection:
            item_id = selection[0]
            values = self.config.results_tree.item(item_id, 'values')
            if not values or len(values) < 2:
                return
            path = values[1]
            if isinstance(path, str) and os.path.exists(path):
                try:
                    import webbrowser
                    webbrowser.open(f"file://{os.path.abspath(path)}")
                    self.log(f"Opening file: {path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")

    def view_timeline(self):
        """Open a simple timeline viewer dialog showing detected events"""
        if not getattr(self.config, 'timeline', None):
            messagebox.showinfo("Timeline", "No timeline data available. Run analysis first.")
            return

        # Create a window with a simple listbox of events
        win = tk.Toplevel(self.config.root)
        win.title("Proximity Timeline")
        win.geometry("500x300")

        lb = tk.Listbox(win)
        lb.pack(fill='both', expand=True, padx=10, pady=10)

        for ev in self.config.timeline:
            start = ev['start'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(ev['start'], 'strftime') else str(ev['start'])
            end = ev['end'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(ev['end'], 'strftime') else str(ev['end'])
            pair = ", ".join(ev.get('pair', []))
            lb.insert('end', f"Event {ev.get('id')}: {pair} — {start} → {end}")

    def generate_map_for_timeframe(self):
        """Prompt user for start/end time and launch the map generator for that timeframe"""
        if not getattr(self.config, 'timeline', None):
            messagebox.showinfo("Generate Map", "No timeline available. Run analysis first.")
            return

        # Simple dialog: ask for start and end timestamps (ISO or relative simple input)
        from tkinter.simpledialog import askstring
        start = askstring("Start Time (UTC)", "Enter start time (YYYY-MM-DD HH:MM:SS) or leave blank to use earliest event:")
        if start is None:
            return
        end = askstring("End Time (UTC)", "Enter end time (YYYY-MM-DD HH:MM:SS) or leave blank to use latest event:")
        if end is None:
            return

        # Determine window from inputs or fallback to timeline bounds
        def parse_or_none(s):
            if not s or not s.strip():
                return None
            from datetime import datetime
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(s.strip(), fmt)
                except Exception:
                    continue
            return None

        start_dt = parse_or_none(start)
        end_dt = parse_or_none(end)

        if start_dt is None:
            start_dt = min(ev['start'] for ev in self.config.timeline)
        if end_dt is None:
            end_dt = max(ev['end'] for ev in self.config.timeline)

        # Save to environment variables read by the LiveMapAnimator
        os.environ['TIME_WINDOW_START'] = start_dt.strftime('%Y-%m-%dT%H:%M:%S')
        os.environ['TIME_WINDOW_END'] = end_dt.strftime('%Y-%m-%dT%H:%M:%S')

        # Launch live map animator script in a subprocess using same mechanism as live_map GUI
        try:
            script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'animation', 'animate_live_map.py')
            if not os.path.exists(script_path):
                messagebox.showerror("Error", f"Map generator script not found: {script_path}")
                return

            # Use system python to run animator as a separate process
            subprocess.Popen([sys.executable, script_path], env=os.environ.copy())
            messagebox.showinfo("Map Generation", f"Map generation launched for {start_dt} → {end_dt}.")
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch map generator: {e}")
    
    def show_in_folder(self):
        """Show results in file manager"""
        output_folder = self.config.output_folder.get()
        if output_folder and os.path.exists(output_folder):
            self._open_file_manager(output_folder)
    
    def open_results_folder(self):
        """Open the results folder"""
        output_folder = self.config.output_folder.get()
        if output_folder and os.path.exists(output_folder):
            self._open_file_manager(output_folder)
        else:
            messagebox.showwarning("Folder Not Found", "Results folder does not exist yet.")
    
    def _open_file_manager(self, path):
        """Open file manager at specified path"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['explorer', path], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', path], check=True)
        except Exception as e:
            self.log(f"Could not open file manager: {e}")
    
    def show_help(self):
        """Show help documentation"""
        help_text = """
Vulture Proximity Analysis Help

This application analyzes GPS tracking data to identify when vultures come into close proximity with each other.

Data Tab:
- Select the folder containing your GPS CSV files
- Preview the data files that will be analyzed

- Set proximity threshold (kilometers)
- Set time threshold (minutes)
- Configure other analysis parameters

Animation Tab:
- Enable/disable animation generation
- Configure animation parameters

Results Tab:
- View analysis results
- Open generated files
- Access results folder

For more detailed help, visit: https://github.com/YourRepo/GPS_make_BGs_fly
        """
        
        # Create help window
        help_window = tk.Toplevel(self.config.root)
        help_window.title("Help - Vulture Proximity Analysis")
        help_window.geometry("600x400")
        
        # Add help text
        import tkinter.scrolledtext as scrolledtext
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=10, pady=10)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def log(self, message):
        """Add message to log queue"""
        if self.config.log_queue:
            self.config.log_queue.put(message)
    
    def _start_log_queue_checker(self):
        """Start checking log queue for new messages"""
        self.check_log_queue()
    
    def check_log_queue(self):
        """Check log queue and update log display"""
        try:
            while True:
                message = self.config.log_queue.get_nowait()
                if self.config.log_text:
                    self.config.log_text.config(state='normal')
                    self.config.log_text.insert('end', f"{message}\\n")
                    self.config.log_text.see('end')
                    self.config.log_text.config(state='disabled')
        except queue.Empty:
            pass
        
        # Schedule next check
        if self.config.root:
            self.config.root.after(100, self.check_log_queue)
    
    def clear_log(self):
        """Clear the log display"""
        if self.config.log_text:
            self.config.log_text.config(state='normal')
            self.config.log_text.delete('1.0', 'end')
            self.config.log_text.config(state='disabled')
    
    def save_log(self):
        """Save log to file"""
        if not self.config.log_text:
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.config.log_text.get('1.0', 'end-1c')
                with open(filename, 'w') as f:
                    f.write(content)
                self.log(f"Log saved to: {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save log: {e}")
    
    def open_timeline_viz(self):
        """Open the latest timeline visualization file in browser"""
        self._open_latest_viz_file("proximity_timeline")
    
    def open_map_viz(self):
        """Open the latest map visualization file in browser"""
        self._open_latest_viz_file("proximity_map")
    
    def open_dashboard_viz(self):
        """Open the latest dashboard visualization file in browser"""
        self._open_latest_viz_file("proximity_dashboard")
    
    def _open_latest_viz_file(self, file_prefix):
        """Open the latest visualization file with the given prefix"""
        output_folder = self.config.output_folder.get()
        if not output_folder or not os.path.exists(output_folder):
            messagebox.showwarning("No Results", "No output folder found. Run analysis first.")
            return
        
        # Look for visualization files in the output directory and visualizations folder
        search_dirs = [output_folder]
        
        # Also check the main visualizations folder
        viz_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'visualizations')
        if os.path.exists(viz_folder):
            search_dirs.append(viz_folder)
        
        latest_file = None
        latest_time = 0
        
        for search_dir in search_dirs:
            try:
                for filename in os.listdir(search_dir):
                    if filename.startswith(file_prefix) and filename.endswith('.html'):
                        file_path = os.path.join(search_dir, filename)
                        file_time = os.path.getmtime(file_path)
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = file_path
            except OSError:
                continue
        
        if latest_file:
            self._open_file_in_browser(latest_file)
            self.log(f"📊 Opened {file_prefix} visualization: {os.path.basename(latest_file)}")
        else:
            messagebox.showinfo("No Visualization", f"No {file_prefix} visualization found. Run analysis first to generate visualizations.")
    
    def open_2d_map_gui(self):
        """Open the 2D Map Live GUI"""
        try:
            # Prefill the 2D GUI with current dataset and output folder
            env = os.environ.copy()
            data_folder = self.config.data_folder.get()
            output_folder = self.config.output_folder.get()
            if data_folder:
                env['GPS_DATA_DIR'] = data_folder
            if output_folder:
                env['OUTPUT_DIR'] = output_folder
            # Ensure full time window is used (let 2D GUI detect bounds)
            env.pop('ANIMATION_START_TIME', None)
            env.pop('ANIMATION_END_TIME', None)
            env.pop('TIME_WINDOW_START', None)
            env.pop('TIME_WINDOW_END', None)

            # Launch as a separate process (Tk must run in main thread, not a background thread)
            base_dir = os.path.dirname(__file__)
            gui_script = os.path.abspath(os.path.join(base_dir, '..', 'live_map_2d_gui.py'))
            if not os.path.exists(gui_script):
                raise FileNotFoundError(f"2D GUI script not found at {gui_script}")
            subprocess.Popen([sys.executable, gui_script], env=env)
            self.log("🗺️ Opening 2D Map Live GUI with current dataset (full range) in a new window...")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open 2D Map GUI: {e}")
            self.log(f"❌ Failed to open 2D Map GUI: {e}")

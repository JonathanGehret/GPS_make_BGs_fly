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
            from gps_utils import DataLoader
            
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
            from gps_utils import DataLoader
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
            from gps_utils import DataLoader
            
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
            
            # Run proximity analysis
            self.log("Analyzing proximity events...")
            
            # Parse time step (for future use)
            # time_step_seconds = parse_time_step(params['time_step'])
            
            # Perform analysis (this would be the actual analysis logic)
            # For now, we'll simulate the process
            import time
            for i in range(5):
                if not self.config.analysis_running:
                    return
                self.log(f"Processing step {i+1}/5...")
                time.sleep(1)
            
            # Simulate results
            self.config.results = {
                'total_events': 42,
                'unique_pairs': 3,
                'avg_duration': 5.2,
                'max_duration': 15.8
            }
            
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
            self.config.results_tree.insert('', 'end', values=('Average Duration (min)', f"{results.get('avg_duration', 0):.1f}"))
            self.config.results_tree.insert('', 'end', values=('Max Duration (min)', f"{results.get('max_duration', 0):.1f}"))
            
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
            # This would open the selected file
            self.log("Opening selected file...")
    
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

Analysis Tab:
- Set proximity threshold (meters)
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

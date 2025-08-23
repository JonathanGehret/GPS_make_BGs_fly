#!/usr/bin/env python3
"""
Shared Animation Controls Component

Provides reusable animation parameter controls that can be used
across different GUI applications (2D maps, 3D visualization, proximity analysis).
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Add scripts directory to path to import performance optimizer
scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, scripts_dir)

try:
    from utils.performance_optimizer import PerformanceOptimizer
    from gps_utils import DataLoader
except ImportError:
    PerformanceOptimizer = None
    DataLoader = None


class AnimationControlsFrame:
    """Reusable frame containing animation parameter controls"""
    
    def __init__(self, parent_frame, include_time_buffer=True, include_encounter_limit=False, data_folder=None):
        """
        Initialize animation controls frame
        
        Args:
            parent_frame: Parent tkinter frame to contain the controls
            include_time_buffer: Whether to include time buffer control (for proximity analysis)
            include_encounter_limit: Whether to include encounter limit control (for proximity analysis)
            data_folder: Optional data folder for point count calculations
        """
        self.parent_frame = parent_frame
        self.include_time_buffer = include_time_buffer
        self.include_encounter_limit = include_encounter_limit
        self.data_folder = data_folder
        
        # Animation variables
        self.time_buffer = tk.DoubleVar(value=2.0)
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        self.limit_encounters = tk.IntVar(value=0)
        
        # Point count tracking
        self.dataframes = []
        self.point_count_label = None
        
        # Labels for dynamic updates
        self.buffer_label = None
        self.trail_label = None
        self.limit_label = None
        
        self._load_data_if_available()
        self.setup_controls()
    
    def _load_data_if_available(self):
        """Load GPS data if data folder is available for point count calculations"""
        if self.data_folder and DataLoader:
            try:
                data_loader = DataLoader(self.data_folder.get() if hasattr(self.data_folder, 'get') else self.data_folder)
                self.dataframes = data_loader.load_all_csv_files()
            except Exception:
                self.dataframes = []
    
    def update_data_folder(self, data_folder):
        """Update data folder and reload data for point count calculations"""
        self.data_folder = data_folder
        self._load_data_if_available()
        self.update_point_count()
    
    def _convert_time_step_to_seconds(self, time_step_str):
        """Convert time step string to seconds"""
        time_step_str = time_step_str.lower().strip()
        
        if time_step_str.endswith('s'):
            return int(time_step_str[:-1])
        elif time_step_str.endswith('m'):
            return int(time_step_str[:-1]) * 60
        elif time_step_str.endswith('h'):
            return int(time_step_str[:-1]) * 3600
        else:
            return 60  # Default to 1 minute
    
    def update_point_count(self):
        """Update point count display based on current time step"""
        if not self.point_count_label or not self.dataframes or not PerformanceOptimizer:
            return
        
        try:
            time_step_seconds = self._convert_time_step_to_seconds(self.time_step.get())
            original, filtered = PerformanceOptimizer.estimate_data_points(self.dataframes, time_step_seconds)
            rating = PerformanceOptimizer.get_performance_rating(filtered)
            reduction = ((original - filtered) / original * 100) if original > 0 else 0
            
            count_text = f"{rating} {filtered:,} points ({reduction:.1f}% reduction from {original:,})"
            self.point_count_label.config(text=count_text)
        except Exception:
            self.point_count_label.config(text="Point count unavailable")
    
    def setup_controls(self):
        """Setup the animation control widgets"""
        # Main animation frame
        animation_frame = self.parent_frame
        
        # Animation settings title
        ttk.Label(animation_frame, text="Animation Configuration:", 
                 font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Data range frame
        buffer_frame = ttk.LabelFrame(animation_frame, text="Data Range", padding="15")
        buffer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        current_row = 0
        
        # Time buffer (only for proximity analysis)
        if self.include_time_buffer:
            ttk.Label(buffer_frame, text="Time Buffer (hours):").grid(row=current_row, column=0, sticky=tk.W, pady=(0, 10))
            buffer_scale = ttk.Scale(buffer_frame, from_=0.5, to=12.0, 
                                    variable=self.time_buffer, orient=tk.HORIZONTAL)
            buffer_scale.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(0, 10))
            self.buffer_label = ttk.Label(buffer_frame, text="2.0 hours")
            self.buffer_label.grid(row=current_row, column=2, pady=(0, 10))
            buffer_scale.configure(command=self.update_buffer_label)
            current_row += 1
        
        # Trail length
        ttk.Label(buffer_frame, text="Trail Length (hours):").grid(row=current_row, column=0, sticky=tk.W)
        trail_scale = ttk.Scale(buffer_frame, from_=0.1, to=6.0, 
                               variable=self.trail_length, orient=tk.HORIZONTAL)
        trail_scale.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        self.trail_label = ttk.Label(buffer_frame, text="2.0 hours")
        self.trail_label.grid(row=current_row, column=2)
        trail_scale.configure(command=self.update_trail_label)
        
        buffer_frame.columnconfigure(1, weight=1)
        
        # Time step frame
        step_frame = ttk.LabelFrame(animation_frame, text="Animation Quality", padding="15")
        step_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(step_frame, text="Time Step:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        time_step_combo = ttk.Combobox(step_frame, textvariable=self.time_step, 
                                      values=['1s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '1h'],
                                      state='readonly', width=10)
        time_step_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        time_step_combo.bind('<<ComboboxSelected>>', lambda e: self.update_point_count())
        
        # Point count display
        self.point_count_label = ttk.Label(step_frame, text="📊 Point count will be calculated when data is loaded", 
                                          font=('Arial', 9), foreground='blue')
        self.point_count_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Initial point count calculation
        self.after_widget_creation()
        
        ttk.Label(step_frame, text="Quality Guide:", font=('Arial', 9, 'italic')).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        ttk.Label(step_frame, text="• 1s-30s: Ultra-smooth (slower processing)", 
                 font=('Arial', 8)).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 1m-5m: Balanced quality and speed", 
                 font=('Arial', 8)).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 10m-1h: Fast processing (less detail)", 
                 font=('Arial', 8)).grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
        # Performance options (only for proximity analysis with encounter limiting)
        if self.include_encounter_limit:
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
    
    def after_widget_creation(self):
        """Called after widget creation to trigger initial calculations"""
        # Schedule initial point count calculation
        if self.point_count_label:
            # Use after_idle to ensure all widgets are properly created
            self.point_count_label.after_idle(self.update_point_count)
    
    def update_buffer_label(self, value):
        """Update time buffer label"""
        if self.buffer_label:
            self.buffer_label.config(text=f"{float(value):.1f} hours")
    
    def update_trail_label(self, value):
        """Update trail length label"""
        if self.trail_label:
            self.trail_label.config(text=f"{float(value):.1f} hours")
    
    def update_limit_label(self, value):
        """Update encounter limit label"""
        if self.limit_label:
            limit = int(float(value))
            self.limit_label.config(text="No limit" if limit == 0 else f"{limit} encounters")
    
    def get_config(self):
        """Get current animation configuration as dictionary"""
        config = {
            'trail_length': self.trail_length.get(),
            'time_step': self.time_step.get(),
        }
        
        if self.include_time_buffer:
            config['time_buffer'] = self.time_buffer.get()
        
        if self.include_encounter_limit:
            config['limit_encounters'] = self.limit_encounters.get()
        
        return config
    
    def set_config(self, config):
        """Set animation configuration from dictionary"""
        if 'trail_length' in config:
            self.trail_length.set(config['trail_length'])
            self.update_trail_label(config['trail_length'])
        
        if 'time_step' in config:
            self.time_step.set(config['time_step'])
        
        if 'time_buffer' in config and self.include_time_buffer:
            self.time_buffer.set(config['time_buffer'])
            self.update_buffer_label(config['time_buffer'])
        
        if 'limit_encounters' in config and self.include_encounter_limit:
            self.limit_encounters.set(config['limit_encounters'])
            self.update_limit_label(config['limit_encounters'])

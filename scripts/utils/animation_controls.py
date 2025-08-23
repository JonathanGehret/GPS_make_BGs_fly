#!/usr/bin/env python3
"""
Shared Animation Controls Component

Provides reusable animation parameter controls that can be used
across different GUI applications (2D maps, 3D visualization, proximity analysis).
"""

import tkinter as tk
from tkinter import ttk


class AnimationControlsFrame:
    """Reusable frame containing animation parameter controls"""
    
    def __init__(self, parent_frame, include_time_buffer=True, include_encounter_limit=False):
        """
        Initialize animation controls frame
        
        Args:
            parent_frame: Parent tkinter frame to contain the controls
            include_time_buffer: Whether to include time buffer control (for proximity analysis)
            include_encounter_limit: Whether to include encounter limit control (for proximity analysis)
        """
        self.parent_frame = parent_frame
        self.include_time_buffer = include_time_buffer
        self.include_encounter_limit = include_encounter_limit
        
        # Animation variables
        self.time_buffer = tk.DoubleVar(value=2.0)
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        self.limit_encounters = tk.IntVar(value=0)
        
        # Labels for dynamic updates
        self.buffer_label = None
        self.trail_label = None
        self.limit_label = None
        
        self.setup_controls()
    
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
        
        ttk.Label(step_frame, text="Quality Guide:", font=('Arial', 9, 'italic')).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        ttk.Label(step_frame, text="• 1s-30s: Ultra-smooth (slower processing)", 
                 font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 1m-5m: Balanced quality and speed", 
                 font=('Arial', 8)).grid(row=3, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(step_frame, text="• 10m-1h: Fast processing (less detail)", 
                 font=('Arial', 8)).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
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

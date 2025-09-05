#!/usr/bin/env python3
"""
Proximity Analysis GUI - Core Configuration and State Management

Handles the main GUI state, configuration variables, and core initialization.
"""

import tkinter as tk
from tkinter import ttk


class ProximityGUIConfig:
    """Configuration and state management for the Proximity Analysis GUI"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize translator (will be set by main GUI)
        self.translator = None
        
        # Configure main window
        self.root.title("Vulture Proximity Analysis")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Analysis configuration variables
        self.data_folder = tk.StringVar(value="/assets/data")
        self.output_folder = tk.StringVar(value="visualizations")
        self.proximity_threshold = tk.DoubleVar(value=2.0)
        self.time_threshold = tk.IntVar(value=5)
        self.generate_animations = tk.BooleanVar(value=False)
        self.time_buffer = tk.DoubleVar(value=2.0)
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        self.limit_encounters = tk.IntVar(value=0)
        
        # UI state variables
        self.status_var = tk.StringVar(value="Ready to analyze proximity events")
        self.progress_var = tk.DoubleVar()
        
        # Results storage
        self.results = {}
        # Timeline (list of proximity events) and other result file references
        self.timeline = []
        self.result_files = {}
        self.analysis_running = False
        self.analysis_thread = None

        # UI component references (will be set by UI builders)
        self.notebook = None
        self.title_label = None
        self.run_button = None
        self.stop_button = None
        self.open_results_button = None
        self.help_button = None
        self.browse_output_button = None
        
        # Log components
        self.log_queue = None
        self.log_text = None
        self.data_preview = None
        self.results_tree = None
    
    def get_analysis_parameters(self):
        """Get current analysis parameters as a dictionary"""
        return {
            'data_folder': self.data_folder.get(),
            'output_folder': self.output_folder.get(),
            'proximity_threshold': self.proximity_threshold.get(),
            'time_threshold': self.time_threshold.get(),
            'generate_animations': self.generate_animations.get(),
            'time_buffer': self.time_buffer.get(),
            'trail_length': self.trail_length.get(),
            'time_step': self.time_step.get(),
            'limit_encounters': self.limit_encounters.get()
        }
    
    def set_analysis_parameters(self, params):
        """Set analysis parameters from a dictionary"""
        if 'data_folder' in params:
            self.data_folder.set(params['data_folder'])
        if 'output_folder' in params:
            self.output_folder.set(params['output_folder'])
        if 'proximity_threshold' in params:
            self.proximity_threshold.set(params['proximity_threshold'])
        if 'time_threshold' in params:
            self.time_threshold.set(params['time_threshold'])
        if 'generate_animations' in params:
            self.generate_animations.set(params['generate_animations'])
        if 'time_buffer' in params:
            self.time_buffer.set(params['time_buffer'])
        if 'trail_length' in params:
            self.trail_length.set(params['trail_length'])
        if 'time_step' in params:
            self.time_step.set(params['time_step'])
        if 'limit_encounters' in params:
            self.limit_encounters.set(params['limit_encounters'])
    
    def reset_to_defaults(self):
        """Reset all parameters to default values"""
        self.data_folder.set("/assets/data")
        self.output_folder.set("visualizations")
        self.proximity_threshold.set(2.0)
        self.time_threshold.set(5)
        self.generate_animations.set(False)
        self.time_buffer.set(2.0)
        self.trail_length.set(2.0)
        self.time_step.set("1m")
        self.limit_encounters.set(0)
    
    def is_valid_configuration(self):
        """Check if current configuration is valid for analysis"""
        errors = []
        
        if not self.data_folder.get().strip():
            errors.append("Data folder is required")
        
        if not self.output_folder.get().strip():
            errors.append("Output folder is required")
        
        if self.proximity_threshold.get() <= 0:
            errors.append("Proximity threshold must be positive")
        
        if self.time_threshold.get() <= 0:
            errors.append("Time threshold must be positive")
        
    # Note: animation/map generation is now an on-demand operation after analysis
    # so animation-specific parameters are not required to run the proximity analysis.
        
        return len(errors) == 0, errors

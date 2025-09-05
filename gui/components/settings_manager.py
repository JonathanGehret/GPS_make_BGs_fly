#!/usr/bin/env python3
"""
Settings Component for 2D Live Map GUI
Handles performance mode and animation settings
"""

import tkinter as tk
from tkinter import ttk
import os
import sys


class SettingsManager:
    """Manages performance and animation settings"""
    
    def __init__(self, parent_frame, language_callback=None):
        self.parent_frame = parent_frame
        self.get_language = language_callback or (lambda: 'en')
        
        # Settings variables
        self.performance_mode = tk.BooleanVar(value=True)
        
        # UI elements
        self.animation_frame = None
        self.performance_frame = None
        self.performance_checkbox = None
        self.performance_info = None
        
        # Animation controls
        self.animation_controls = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the settings UI"""
        # Animation settings frame
        self.animation_frame = ttk.LabelFrame(self.parent_frame, text="🎬 Animation Settings", padding="10")
        self.animation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.animation_frame.columnconfigure(0, weight=1)
        
        # Try to load shared animation controls
        self.setup_animation_controls()
        
        # Performance settings frame
        self.performance_frame = ttk.LabelFrame(self.parent_frame, text="⚡ Performance Settings", padding="10")
        self.performance_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.performance_frame.columnconfigure(0, weight=1)
        
        # Performance mode checkbox
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
        
        # Initialize performance info
        self.update_performance_info()
    
    def setup_animation_controls(self):
        """Set up animation controls (with fallback if shared component not available)"""
        # Try to import shared animation controls
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
            try:
                from scripts.utils.animation_controls import AnimationControlsFrame
            except ImportError:
                from utils.animation_controls import AnimationControlsFrame
            
            # Create the shared animation controls
            self.animation_controls = AnimationControlsFrame(
                self.animation_frame, 
                include_time_buffer=False,  # 2D maps don't need time buffer
                include_encounter_limit=False,  # 2D maps don't limit encounters
                data_folder=None  # Will be set later
            )
        except ImportError:
            # Fallback: create basic controls manually
            self.create_fallback_animation_controls()
    
    def create_fallback_animation_controls(self):
        """Create simple animation controls if shared component not available"""
        # Simple fallback variables
        self.trail_length = tk.DoubleVar(value=2.0)
        self.time_step = tk.StringVar(value="1m")
        
        # Trail length
        ttk.Label(self.animation_frame, text="Trail Length (hours):").grid(row=0, column=0, sticky=tk.W, pady=10)
        trail_scale = ttk.Scale(self.animation_frame, from_=0.1, to=6.0, 
                               variable=self.trail_length, orient=tk.HORIZONTAL)
        trail_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=10)
        self.trail_label = ttk.Label(self.animation_frame, text="2.0 hours")
        self.trail_label.grid(row=0, column=2, pady=10)
        trail_scale.configure(command=self.update_trail_label_fallback)
        
        # Time step
        ttk.Label(self.animation_frame, text="Time Step:").grid(row=1, column=0, sticky=tk.W, pady=10)
        time_step_combo = ttk.Combobox(self.animation_frame, textvariable=self.time_step, 
                                      values=['1s', '5s', '10s', '30s', '1m', '2m', '5m', '10m', '30m', '1h'],
                                      state='readonly', width=10)
        time_step_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=10)
        
        self.animation_frame.columnconfigure(1, weight=1)
        
        # Create a simple config object for compatibility
        class SimpleConfig:
            def __init__(self, trail_length, time_step):
                self.trail_length = trail_length
                self.time_step = time_step
            
            def get_config(self):
                return {
                    'trail_length': self.trail_length.get(),
                    'time_step': self.time_step.get()
                }
        
        self.animation_controls = SimpleConfig(self.trail_length, self.time_step)
    
    def update_trail_label_fallback(self, value):
        """Update trail length label for fallback controls"""
        if hasattr(self, 'trail_label'):
            self.trail_label.config(text=f"{float(value):.1f} hours")
    
    def update_performance_info(self):
        """Update performance mode information display"""
        language = self.get_language()
        
        if self.performance_mode.get():
            if language == "de":
                info_text = "⚡ Aktiviert: Linie+Kopf-Rendering mit adaptiver LOD für große Datensätze"
            else:
                info_text = "⚡ Enabled: Line+head rendering with adaptive LOD for large datasets"
        else:
            if language == "de":
                info_text = "📝 Standard: Verblassende Marker mit glatten Übergängen"
            else:
                info_text = "📝 Standard: Fading markers with smooth transitions"
        
        self.performance_info.config(text=info_text)
    
    def update_language(self, language):
        """Update UI text for the specified language"""
        if language == "de":
            self.animation_frame.config(text="🎬 Animation-Einstellungen")
            self.performance_frame.config(text="⚡ Performance-Einstellungen")
            self.performance_checkbox.config(text="Performance-Modus aktivieren")
        else:
            self.animation_frame.config(text="🎬 Animation Settings")
            self.performance_frame.config(text="⚡ Performance Settings")
            self.performance_checkbox.config(text="Enable Performance Mode")
        
        # Update performance info text
        self.update_performance_info()
    
    def get_config(self):
        """Get the current animation configuration"""
        if hasattr(self.animation_controls, 'get_config'):
            config = self.animation_controls.get_config()
        else:
            # Fallback for simple config
            config = {
                'trail_length': getattr(self, 'trail_length', tk.DoubleVar(value=2.0)).get(),
                'time_step': getattr(self, 'time_step', tk.StringVar(value="1m")).get()
            }
        
        # Add performance mode to config
        config['performance_mode'] = self.performance_mode.get()
        return config
    
    def update_data_folder(self, data_folder_var):
        """Update the data folder for animation controls"""
        if hasattr(self.animation_controls, 'update_data_folder'):
            self.animation_controls.update_data_folder(data_folder_var)

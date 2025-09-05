#!/usr/bin/env python3
"""
Mode Selector Component for 2D Live Map GUI
Handles switching between different animation modes (2D Live Map, Mobile Animation, etc.)
"""

import tkinter as tk
from tkinter import ttk
import os
import sys


class ModeSelector:
    """Manages animation mode selection (2D Live Map, Mobile Animation, etc.)"""
    
    def __init__(self, parent_frame, language_callback=None):
        self.parent_frame = parent_frame
        self.get_language = language_callback or (lambda: 'en')
        
        # Mode selection variable
        self.selected_mode = tk.StringVar(value="2d_live_map")
        
        # Available modes
        self.modes = {
            "2d_live_map": {
                "display_name": "2D Live Map",
                "description": "Standard 2D map visualization with animation controls",
                "script": "animate_live_map.py",
                "icon": "🗺️"
            },
            "mobile_animation": {
                "display_name": "Mobile Animation",
                "description": "Mobile-optimized animation with touch-friendly controls",
                "script": "mobile_animation.py", 
                "icon": "📱"
            },
            "3d_animation": {
                "display_name": "3D Animation",
                "description": "3D flight path visualization",
                "script": "animation_3d.py",
                "icon": "🌍"
            }
        }
        
        # UI elements
        self.mode_frame = None
        self.mode_dropdown = None
        self.description_label = None
        
    def setup_ui(self):
        """Set up the mode selector UI"""
        # Main mode frame
        self.mode_frame = ttk.LabelFrame(self.parent_frame, text="🎯 Animation Mode", padding="10")
        self.mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.mode_frame.columnconfigure(1, weight=1)
        
        # Mode selection label
        mode_label = ttk.Label(self.mode_frame, text="Select Mode:")
        mode_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Mode dropdown
        mode_options = [f"{info['icon']} {info['display_name']}" for mode_key, info in self.modes.items()]
        self.mode_dropdown = ttk.Combobox(
            self.mode_frame,
            values=mode_options,
            state="readonly",
            width=25
        )
        self.mode_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.mode_dropdown.bind('<<ComboboxSelected>>', self.on_mode_changed)
        
        # Set initial selection
        initial_display = f"{self.modes['2d_live_map']['icon']} {self.modes['2d_live_map']['display_name']}"
        self.mode_dropdown.set(initial_display)
        
        # Description label
        self.description_label = ttk.Label(
            self.mode_frame, 
            text=self.modes['2d_live_map']['description'],
            foreground="gray"
        )
        self.description_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def on_mode_changed(self, event=None):
        """Handle mode selection change"""
        selected_display = self.mode_dropdown.get()
        
        # Find the mode key based on display name
        selected_mode_key = None
        for mode_key, info in self.modes.items():
            if f"{info['icon']} {info['display_name']}" == selected_display:
                selected_mode_key = mode_key
                break
        
        if selected_mode_key:
            self.selected_mode.set(selected_mode_key)
            mode_info = self.modes[selected_mode_key]
            
            # Update description
            self.description_label.config(text=mode_info['description'])
            
            print(f"Mode changed to: {mode_info['display_name']} ({selected_mode_key})")
            
            # Trigger callback if set
            if hasattr(self, 'on_mode_change_callback') and self.on_mode_change_callback:
                self.on_mode_change_callback(selected_mode_key, mode_info)
    
    def get_selected_mode(self):
        """Get the currently selected mode key"""
        return self.selected_mode.get()
    
    def get_selected_mode_info(self):
        """Get the full info for the currently selected mode"""
        mode_key = self.selected_mode.get()
        return self.modes.get(mode_key, self.modes['2d_live_map'])
    
    def get_selected_script(self):
        """Get the script filename for the selected mode"""
        mode_info = self.get_selected_mode_info()
        return mode_info['script']
    
    def set_mode_change_callback(self, callback):
        """Set callback function for mode changes"""
        self.on_mode_change_callback = callback
    
    def add_mode(self, mode_key, display_name, description, script, icon="🎯"):
        """Add a new mode to the selector"""
        self.modes[mode_key] = {
            "display_name": display_name,
            "description": description,
            "script": script,
            "icon": icon
        }
        
        # Update dropdown if it exists
        if self.mode_dropdown:
            mode_options = [f"{info['icon']} {info['display_name']}" for mode_key, info in self.modes.items()]
            self.mode_dropdown.configure(values=mode_options)
    
    def set_mode(self, mode_key):
        """Programmatically set the selected mode"""
        if mode_key in self.modes:
            self.selected_mode.set(mode_key)
            mode_info = self.modes[mode_key]
            
            if self.mode_dropdown:
                display_text = f"{mode_info['icon']} {mode_info['display_name']}"
                self.mode_dropdown.set(display_text)
            
            if self.description_label:
                self.description_label.config(text=mode_info['description'])
            
            # Trigger callback
            if hasattr(self, 'on_mode_change_callback') and self.on_mode_change_callback:
                self.on_mode_change_callback(mode_key, mode_info)

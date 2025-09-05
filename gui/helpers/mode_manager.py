#!/usr/bin/env python3
"""
Mode Manager for GPS Animation Suite
Handles mode selection and configuration
"""

import tkinter as tk


class ModeManager:
    """Manages animation mode selection and configuration"""
    
    def __init__(self):
        self.modes = {
            '2d_live_map': {'name': '2D Live Map', 'script': 'animate_live_map.py'},
            'mobile_animation': {'name': 'Mobile Animation', 'script': 'mobile_animation.py'},
            '3d_animation': {'name': '3D Animation', 'script': 'animation_3d.py'}
        }
        
        self.selected_mode = tk.StringVar(value='2d_live_map')
        self.mode_dropdown = None
        self.status_callback = None
    
    def get_mode_options(self):
        """Get formatted mode options for dropdown"""
        return [f"🗺️ {self.modes['2d_live_map']['name']}", 
                f"📱 {self.modes['mobile_animation']['name']}", 
                f"🌍 {self.modes['3d_animation']['name']}"]
    
    def set_status_callback(self, callback):
        """Set callback function for status updates"""
        self.status_callback = callback
    
    def on_mode_changed(self, event=None):
        """Handle mode dropdown change"""
        if not self.mode_dropdown:
            return
            
        selected_display = self.mode_dropdown.get()
        
        # Extract mode key from display string  
        for mode_key, mode_info in self.modes.items():
            if mode_info['name'] in selected_display:
                self.selected_mode.set(mode_key)
                print(f"Mode changed to: {mode_key} -> {mode_info['name']}")
                break
        
        # Update status if callback is set
        if self.status_callback:
            self.status_callback()
    
    def get_selected_mode_key(self):
        """Get the currently selected mode key"""
        return self.selected_mode.get()
    
    def get_selected_mode_info(self):
        """Get the currently selected mode information"""
        mode_key = self.selected_mode.get()
        return self.modes[mode_key]
    
    def get_all_modes(self):
        """Get all available modes"""
        return self.modes

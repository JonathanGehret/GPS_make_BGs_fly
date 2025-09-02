#!/usr/bin/env python3
"""
Test script to demonstrate the playback speed controls in a GUI window.
This shows how the slider and controls work before launching full animations.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from utils.animation_controls import AnimationControlsFrame

def test_gui():
    """Create a test window with animation controls."""
    root = tk.Tk()
    root.title("Playback Speed Test")
    root.geometry("400x200")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Add title
    title_label = ttk.Label(main_frame, text="Animation Playback Speed Controls", 
                           font=("Arial", 12, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
    
    # Create animation controls
    controls = AnimationControlsFrame(main_frame)
    controls.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
    
    # Add current values display
    values_frame = ttk.Frame(main_frame)
    values_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
    
    current_speed_var = tk.StringVar()
    frame_duration_2d_var = tk.StringVar()
    frame_duration_3d_var = tk.StringVar()
    
    ttk.Label(values_frame, text="Current Speed:").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(values_frame, textvariable=current_speed_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
    
    ttk.Label(values_frame, text="2D Frame Duration:").grid(row=1, column=0, sticky=tk.W)
    ttk.Label(values_frame, textvariable=frame_duration_2d_var).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    ttk.Label(values_frame, text="3D Frame Duration:").grid(row=2, column=0, sticky=tk.W)
    ttk.Label(values_frame, textvariable=frame_duration_3d_var).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
    
    def update_display():
        """Update the display with current values."""
        speed = controls.get_config()['playback_speed']
        current_speed_var.set(f"{speed:.1f}x")
        
        # Calculate frame durations (2D uses 600ms base, 3D uses 800ms base)
        frame_2d = int(600 / speed)
        frame_3d = int(800 / speed)
        
        frame_duration_2d_var.set(f"{frame_2d}ms")
        frame_duration_3d_var.set(f"{frame_3d}ms")
    
    # Initial update
    update_display()
    
    # Update display when speed changes
    def on_speed_change(*args):
        update_display()
    
    controls.playback_speed.trace('w', on_speed_change)
    
    # Add instructions
    instructions = ttk.Label(main_frame, 
                           text="Move the slider to test different playback speeds.\n"
                                "This slider will appear in both 2D and 3D animation GUIs.",
                           justify=tk.CENTER)
    instructions.grid(row=3, column=0, columnspan=2, pady=10)
    
    # Configure grid weights
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    
    print("🎮 Playback Speed Test GUI opened!")
    print("📍 Use the slider to test different speeds")
    print("📊 Watch how frame durations change for 2D and 3D animations")
    
    root.mainloop()

if __name__ == "__main__":
    test_gui()

#!/usr/bin/env python3
"""
Simple demo to show the mode dropdown location and functionality
"""

import tkinter as tk
from tkinter import ttk
import os

def demo_mode_dropdown_location():
    """Create a simple demo showing where the mode dropdown appears"""
    
    root = tk.Tk()
    root.title("Mode Dropdown Location Demo")
    root.geometry("600x200")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill="both", expand=True)
    
    # Title with mode dropdown (same layout as live_map_2d_gui_final.py)
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill="x", pady=(0, 20))
    
    # Title on the left
    title = ttk.Label(title_frame, text="🗺️ GPS Animation Suite", 
                     font=("Arial", 16, "bold"))
    title.pack(side="left")
    
    # Mode dropdown on the right
    mode_frame = ttk.Frame(title_frame)
    mode_frame.pack(side="right")
    
    ttk.Label(mode_frame, text="Mode:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
    
    mode_options = [
        "🗺️ 2D Live Map", 
        "📱 Mobile Animation", 
        "🌍 3D Animation"
    ]
    
    mode_var = tk.StringVar(value=mode_options[0])
    mode_dropdown = ttk.Combobox(mode_frame, textvariable=mode_var, 
                                values=mode_options, state="readonly", width=20)
    mode_dropdown.pack(side="left")
    
    # Status to show mode changes
    status_var = tk.StringVar(value="Mode: 2D Live Map (Default)")
    status_label = ttk.Label(main_frame, textvariable=status_var, 
                            font=("Arial", 10), foreground="blue")
    status_label.pack(pady=10)
    
    def on_mode_change(event=None):
        selected = mode_var.get()
        status_var.set(f"Mode: {selected}")
        print(f"Mode changed to: {selected}")
    
    mode_dropdown.bind('<<ComboboxSelected>>', on_mode_change)
    
    # Instructions
    instructions = ttk.Label(main_frame, 
                           text="👆 The mode dropdown is in the TOP-RIGHT corner\n"
                                "Try selecting different modes from the dropdown!",
                           font=("Arial", 11), justify="center")
    instructions.pack(pady=20)
    
    # Arrow pointing to dropdown
    arrow_frame = ttk.Frame(title_frame)
    arrow_frame.pack(side="right", padx=(10, 0))
    
    arrow_label = ttk.Label(arrow_frame, text="← MODE DROPDOWN", 
                           font=("Arial", 9, "bold"), foreground="red")
    arrow_label.pack()
    
    print("Mode dropdown demo is running!")
    print("The dropdown should be visible in the top-right corner of the window.")
    print("Try selecting different modes:")
    for i, mode in enumerate(mode_options):
        print(f"  {i+1}. {mode}")
    
    root.mainloop()

if __name__ == "__main__":
    demo_mode_dropdown_location()

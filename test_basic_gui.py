#!/usr/bin/env python3
"""
Minimal test for modular GUI
"""

import tkinter as tk
from tkinter import ttk

def test_basic_gui():
    root = tk.Tk()
    root.title("Test GUI")
    root.geometry("400x300")
    
    # Simple label
    label = ttk.Label(root, text="Test GUI is working!")
    label.pack(pady=20)
    
    # Button to close
    button = ttk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)
    
    print("GUI created successfully")
    root.mainloop()

if __name__ == "__main__":
    test_basic_gui()

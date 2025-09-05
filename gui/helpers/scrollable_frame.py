#!/usr/bin/env python3
"""
Scrollable Frame Helper for GPS Animation Suite
Provides scrollable canvas functionality with mousewheel support
"""

import tkinter as tk
from tkinter import ttk


class ScrollableFrame:
    """A scrollable frame widget with canvas and scrollbar"""
    
    def __init__(self, parent):
        self.parent = parent
        self.setup_scrollable_frame()
    
    def setup_scrollable_frame(self):
        """Create scrollable frame with canvas and scrollbar"""
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def get_content_frame(self):
        """Get the frame where content should be added"""
        return self.scrollable_frame

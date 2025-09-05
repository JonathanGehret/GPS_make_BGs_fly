#!/usr/bin/env python3
"""
Data Preview Component for 2D Live Map GUI
Handles data preview and validation
"""

import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path


class DataPreview:
    """Manages data preview and file information display"""
    
    def __init__(self, parent_frame, language_callback=None):
        self.parent_frame = parent_frame
        self.get_language = language_callback or (lambda: 'en')
        
        # UI elements
        self.preview_frame = None
        self.data_preview = None
        self.refresh_button = None
        
        # Data folder reference (will be set by main GUI)
        self.data_folder_var = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the data preview UI"""
        # Data preview frame
        self.preview_frame = ttk.LabelFrame(self.parent_frame, text="📊 Data Preview", padding="8")
        self.preview_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.preview_frame.columnconfigure(0, weight=1)
        
        # Text widget for preview
        self.data_preview = tk.Text(self.preview_frame, height=4, width=60, wrap=tk.WORD, font=("Arial", 8))
        self.data_preview.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Refresh button
        self.refresh_button = ttk.Button(self.preview_frame, text="🔄 Refresh", 
                                        command=self.refresh_preview)
        self.refresh_button.grid(row=1, column=0, sticky=tk.W)
    
    def set_data_folder_var(self, data_folder_var):
        """Set the data folder variable to monitor"""
        self.data_folder_var = data_folder_var
    
    def refresh_preview(self):
        """Refresh the data preview"""
        self.data_preview.delete(1.0, tk.END)
        
        if not self.data_folder_var:
            self.data_preview.insert(tk.END, "❌ No data folder configured\n")
            return
        
        try:
            folder = self.data_folder_var.get()
            if not os.path.exists(folder):
                self.data_preview.insert(tk.END, f"❌ Folder not found: {folder}\n")
                return
            
            csv_files = list(Path(folder).glob("*.csv"))
            
            if not csv_files:
                self.data_preview.insert(tk.END, f"⚠️  No CSV files found in: {folder}\n")
                return
            
            self.data_preview.insert(tk.END, f"📁 Data folder: {folder}\n")
            self.data_preview.insert(tk.END, f"📊 Found {len(csv_files)} CSV file(s)\n\n")
            
            # Show file details
            total_points = 0
            for csv_file in csv_files:
                try:
                    # Count lines efficiently
                    with open(csv_file, 'r') as f:
                        line_count = sum(1 for _ in f) - 1  # Subtract header
                    total_points += line_count
                    self.data_preview.insert(tk.END, f"✅ {csv_file.name}: ~{line_count} data points\n")
                except Exception:
                    self.data_preview.insert(tk.END, f"❌ {csv_file.name}: Error reading file\n")
            
            if total_points > 0:
                self.data_preview.insert(tk.END, f"\n📈 Total data points: ~{total_points}\n")
                
        except Exception as e:
            self.data_preview.insert(tk.END, f"❌ Error reading folder: {e}\n")
    
    def update_language(self, language):
        """Update UI text for the specified language"""
        if language == "de":
            self.preview_frame.config(text="📊 Datenvorschau")
            self.refresh_button.config(text="🔄 Aktualisieren")
        else:
            self.preview_frame.config(text="📊 Data Preview")
            self.refresh_button.config(text="🔄 Refresh")
    
    def get_file_count(self):
        """Get the number of CSV files in the current data folder"""
        if not self.data_folder_var:
            return 0
        
        folder = self.data_folder_var.get()
        if not os.path.exists(folder):
            return 0
        
        csv_files = list(Path(folder).glob("*.csv"))
        return len(csv_files)
    
    def get_total_points(self):
        """Get the estimated total number of data points"""
        if not self.data_folder_var:
            return 0
        
        folder = self.data_folder_var.get()
        if not os.path.exists(folder):
            return 0
        
        csv_files = list(Path(folder).glob("*.csv"))
        total_points = 0
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r') as f:
                    line_count = sum(1 for _ in f) - 1  # Subtract header
                total_points += line_count
            except Exception:
                continue
        
        return total_points

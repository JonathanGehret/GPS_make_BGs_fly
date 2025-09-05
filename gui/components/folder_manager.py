#!/usr/bin/env python3
"""
Folder Management Component for 2D Live Map GUI
Handles data and output folder selection
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from pathlib import Path


class FolderManager:
    """Manages data and output folder selection and validation"""
    
    def __init__(self, parent_frame, language_callback=None):
        self.parent_frame = parent_frame
        self.get_language = language_callback or (lambda: 'en')
        
        # Folder variables
        self.data_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        self.output_folder = tk.StringVar(value=os.path.join(os.path.dirname(__file__), "..", "..", "visualizations"))
        
        # UI elements (will be set by setup_ui)
        self.folder_frame = None
        self.data_label = None
        self.output_label = None
        self.browse_data_button = None
        self.browse_output_button = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the folder management UI"""
        # Main folder frame
        self.folder_frame = ttk.LabelFrame(self.parent_frame, text="📁 Folders", padding="10")
        self.folder_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.folder_frame.columnconfigure(1, weight=1)
        
        # Data folder
        self.data_label = ttk.Label(self.folder_frame, text="Data:")
        self.data_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        data_entry = ttk.Entry(self.folder_frame, textvariable=self.data_folder, width=40)
        data_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 3))
        
        self.browse_data_button = ttk.Button(self.folder_frame, text="📁", 
                                           command=self.browse_data_folder, width=3)
        self.browse_data_button.grid(row=0, column=2, pady=2)
        
        # Output folder
        self.output_label = ttk.Label(self.folder_frame, text="Output:")
        self.output_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        output_entry = ttk.Entry(self.folder_frame, textvariable=self.output_folder, width=40)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 3))
        
        self.browse_output_button = ttk.Button(self.folder_frame, text="📁", 
                                             command=self.browse_output_folder, width=3)
        self.browse_output_button.grid(row=1, column=2, pady=2)
    
    def browse_data_folder(self):
        """Browse for data directory"""
        language = self.get_language()
        title = "GPS-Datenverzeichnis auswählen" if language == "de" else "Select GPS Data Directory"
        
        directory = filedialog.askdirectory(
            title=title,
            initialdir=self.data_folder.get()
        )
        if directory:
            self.data_folder.set(directory)
            # Trigger any callbacks that might be registered
            if hasattr(self, 'on_data_folder_changed'):
                self.on_data_folder_changed(directory)
    
    def browse_output_folder(self):
        """Browse for output directory"""
        language = self.get_language()
        title = "Ausgabeordner auswählen" if language == "de" else "Select Output Directory"
        
        directory = filedialog.askdirectory(
            title=title,
            initialdir=self.output_folder.get()
        )
        if directory:
            self.output_folder.set(directory)
    
    def validate_folders(self):
        """Validate that the selected folders exist and are accessible"""
        data_path = self.data_folder.get()
        output_path = self.output_folder.get()
        
        issues = []
        
        # Check data folder
        if not os.path.exists(data_path):
            language = self.get_language()
            msg = "Datenverzeichnis existiert nicht!" if language == "de" else "Data directory does not exist!"
            issues.append(msg)
        else:
            # Check for CSV files
            csv_files = list(Path(data_path).glob("*.csv"))
            if not csv_files:
                language = self.get_language()
                msg = "Keine CSV-Dateien im Datenverzeichnis gefunden!" if language == "de" else "No CSV files found in data directory!"
                issues.append(msg)
        
        # Check output folder (create if it doesn't exist)
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            language = self.get_language()
            msg = f"Ausgabeordner kann nicht erstellt werden: {e}" if language == "de" else f"Cannot create output directory: {e}"
            issues.append(msg)
        
        return issues
    
    def update_language(self, language):
        """Update UI text for the specified language"""
        if language == "de":
            self.folder_frame.config(text="📁 Ordner")
            self.data_label.config(text="Daten:")
            self.output_label.config(text="Ausgabe:")
        else:
            self.folder_frame.config(text="📁 Folders")
            self.data_label.config(text="Data:")
            self.output_label.config(text="Output:")
    
    def get_data_folder(self):
        """Get the current data folder path"""
        return self.data_folder.get()
    
    def get_output_folder(self):
        """Get the current output folder path"""
        return self.output_folder.get()
    
    def set_data_folder_callback(self, callback):
        """Set a callback function to be called when data folder changes"""
        self.on_data_folder_changed = callback

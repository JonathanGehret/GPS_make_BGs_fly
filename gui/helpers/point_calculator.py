#!/usr/bin/env python3
"""
Point Calculator for GPS Animation Suite
Handles point count calculations and time step conversions
"""

import os
import pandas as pd
import tkinter as tk


class PointCalculator:
    """Calculates point counts based on time steps and data"""
    
    def __init__(self):
        self.point_count_label = None
        self.data_folder_var = None
        self.time_step_var = None
    
    def set_point_count_label(self, label):
        """Set the label widget for displaying point count"""
        self.point_count_label = label
    
    def set_data_folder_var(self, folder_var):
        """Set the data folder variable"""
        self.data_folder_var = folder_var
    
    def set_time_step_var(self, time_step_var):
        """Set the time step variable"""
        self.time_step_var = time_step_var
    
    def convert_time_step_to_seconds(self, time_step_str):
        """Convert time step string to seconds"""
        if time_step_str.endswith('s'):
            return int(time_step_str[:-1])
        elif time_step_str.endswith('m'):
            return int(time_step_str[:-1]) * 60
        elif time_step_str.endswith('h'):
            return int(time_step_str[:-1]) * 3600
        else:
            return 60  # Default to 1 minute
    
    def update_point_count_calculation(self):
        """Update the point count display based on current time step and loaded data"""
        if not self.point_count_label or not self.data_folder_var or not self.time_step_var:
            return
        
        try:
            # Get the currently selected folder and its CSV files
            data_folder = self.data_folder_var.get()
            if not data_folder or not os.path.exists(data_folder):
                self.point_count_label.config(text="Point count calculated when data is loaded")
                return
            
            # Find CSV files in the folder
            csv_files = [f for f in os.listdir(data_folder) 
                        if f.endswith('.csv') and not f.startswith('.')]
            
            if not csv_files:
                self.point_count_label.config(text="No CSV files found in selected folder")
                return
            
            # Read first CSV file to get data structure
            first_csv = os.path.join(data_folder, csv_files[0])
            try:
                df = pd.read_csv(first_csv, sep=';')
                
                # Look for timestamp column with different possible names
                timestamp_col = None
                possible_timestamp_cols = ['timestamp', 'Timestamp', 'Timestamp [UTC]', 'time', 'Time', 'datetime', 'DateTime']
                
                for col in possible_timestamp_cols:
                    if col in df.columns:
                        timestamp_col = col
                        break
                
                if not timestamp_col:
                    self.point_count_label.config(text="No timestamp column found in CSV file")
                    return
                
                # Convert time step to seconds for calculation
                time_step_str = self.time_step_var.get()
                time_step_seconds = self.convert_time_step_to_seconds(time_step_str)
                
                # Calculate total timespan
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], format='%d.%m.%Y %H:%M:%S', errors='coerce')
                
                # Drop rows where timestamp conversion failed
                df = df.dropna(subset=[timestamp_col])
                
                if len(df) == 0:
                    self.point_count_label.config(text="Cannot parse timestamp format in CSV file")
                    return
                
                # Get original number of points in the file
                original_points = len(df)
                
                total_duration = (df[timestamp_col].max() - df[timestamp_col].min()).total_seconds()
                
                # Calculate expected number of points
                if total_duration > 0:
                    estimated_points = int(total_duration / time_step_seconds) + 1
                    total_files = len(csv_files)
                    
                    # Calculate percentage reduction
                    if original_points > 0:
                        reduction_percent = ((original_points - estimated_points) / original_points) * 100
                        
                        if reduction_percent > 0:
                            self.point_count_label.config(
                                text=f"≈ {estimated_points:,} points per file (was {original_points:,}, {reduction_percent:.1f}% reduction) • {total_files} files • {time_step_str} steps",
                                foreground="darkgreen"
                            )
                        else:
                            # If estimated points >= original points (very fine time step)
                            increase_percent = ((estimated_points - original_points) / original_points) * 100
                            self.point_count_label.config(
                                text=f"≈ {estimated_points:,} points per file (was {original_points:,}, {increase_percent:.1f}% increase) • {total_files} files • {time_step_str} steps",
                                foreground="darkorange"
                            )
                    else:
                        self.point_count_label.config(
                            text=f"≈ {estimated_points:,} points per file ({total_files} files) with {time_step_str} steps",
                            foreground="darkgreen"
                        )
                else:
                    self.point_count_label.config(text="Cannot calculate: insufficient time data")
                    
            except Exception:
                self.point_count_label.config(text=f"Error calculating points: CSV format issue")
                
        except Exception:
            self.point_count_label.config(text="Point count calculated when data is loaded")

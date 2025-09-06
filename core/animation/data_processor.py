"""
Data Processing Pipeline

Handles data loading, filtering, analysis, and preparation for visualization.
"""

import os
from pathlib import Path
from typing import List, Optional
import pandas as pd
import plotly.express as px

from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.gps_utils import DataLoader
from core.animation.precipitation_manager import PrecipitationManager


class DataProcessor:
    """Handles data loading, processing, and preparation for visualization."""

    def __init__(self, ui: UserInterface):
        self.ui = ui
        self.data_loader = DataLoader()
        self.optimizer = PerformanceOptimizer()
        self.precipitation_manager = PrecipitationManager(ui)
        self.selected_time_step: Optional[int] = None
        self.dataframes: List[pd.DataFrame] = []
        self.combined_data: Optional[pd.DataFrame] = None

    def analyze_data(self) -> bool:
        """Analyze CSV files and load data"""
        self.ui.print_section("📊 DATA ANALYSIS")
        try:
            csv_files = self.data_loader.find_csv_files()
            if not csv_files:
                self.ui.print_error("No CSV files found in data directory!")
                self.ui.print_info("Please add GPS data files to the 'data/' folder")
                return False
            total_points = 0
            print(f"Found {len(csv_files)} GPS data file(s):")

            # Check for an optional time window to limit data (set by GUI)
            time_window_start = os.environ.get('TIME_WINDOW_START')
            time_window_end = os.environ.get('TIME_WINDOW_END')
            start_ts = None
            end_ts = None
            if time_window_start:
                try:
                    start_ts = pd.to_datetime(time_window_start, utc=True)
                    self.ui.print_info(f"Applying time window start: {start_ts.isoformat()}")
                except Exception:
                    self.ui.print_warning(f"Invalid TIME_WINDOW_START: {time_window_start}")
            if time_window_end:
                try:
                    end_ts = pd.to_datetime(time_window_end, utc=True)
                    self.ui.print_info(f"Applying time window end: {end_ts.isoformat()}")
                except Exception:
                    self.ui.print_warning(f"Invalid TIME_WINDOW_END: {time_window_end}")

            for i, csv_file in enumerate(csv_files, 1):
                try:
                    df = self.data_loader.load_single_csv(csv_file)
                    if df is not None:
                        # If a time window was provided, attempt to filter by the Timestamp [UTC] column
                        if (start_ts is not None) or (end_ts is not None):
                            if 'Timestamp [UTC]' in df.columns:
                                try:
                                    ts = pd.to_datetime(df['Timestamp [UTC]'], utc=True)
                                    df['Timestamp [UTC]'] = ts
                                    mask = pd.Series(True, index=df.index)
                                    if start_ts is not None:
                                        mask &= ts >= start_ts
                                    if end_ts is not None:
                                        mask &= ts <= end_ts
                                    df = df[mask]
                                except Exception:
                                    self.ui.print_warning(f"Could not apply time window filter to {Path(csv_file).name}")
                            else:
                                self.ui.print_warning(f"No 'Timestamp [UTC]' column to filter in {Path(csv_file).name}")

                        points = len(df)
                        total_points += points
                        print(f"    {i}. {Path(csv_file).name:<25} ({points:4d} GPS points)")
                        self.dataframes.append(df)
                except Exception as e:
                    self.ui.print_warning(f"Could not analyze {Path(csv_file).name}: {e}")
            if not self.dataframes:
                self.ui.print_error("No valid GPS data found!")
                return False
            print(f"\n📈 Total GPS points available: {total_points}")
            return True
        except Exception as e:
            self.ui.print_error(f"Failed to analyze data: {e}")
            return False

    def configure_performance(self) -> bool:
        """Configure time step and performance settings"""
        time_step_env = os.environ.get('TIME_STEP')
        if time_step_env:
            try:
                self.selected_time_step = self._parse_time_step_from_gui(time_step_env)
                self.ui.print_success(f"Using GUI time step: {time_step_env} ({self.selected_time_step}s)")
                return True
            except Exception:
                self.ui.print_warning(f"Invalid time step from GUI: {time_step_env}, falling back to manual selection")
        self.ui.print_info("Using default 1 minute time step for testing")
        self.selected_time_step = 60
        return True

    def _parse_time_step_from_gui(self, time_step_str: str) -> int:
        """Parse time step string from GUI"""
        s = time_step_str.lower().strip()
        if s.endswith('seconds') or s.endswith('second'):
            return int(s.split()[0])
        elif s.endswith('minutes') or s.endswith('minute'):
            return int(s.split()[0]) * 60
        elif s.endswith('hours') or s.endswith('hour'):
            return int(s.split()[0]) * 3600
        elif s.endswith('s'):
            return int(s[:-1])
        elif s.endswith('m'):
            return int(s[:-1]) * 60
        elif s.endswith('h'):
            return int(s[:-1]) * 3600
        else:
            return int(s)

    def process_data(self) -> bool:
        """Process and filter data"""
        self.ui.print_section("🔄 DATA PROCESSING")
        print(f"Applying {self.selected_time_step/60:.1f} minute time step filter...")
        print()
        try:
            processed: List[pd.DataFrame] = []
            for i, df in enumerate(self.dataframes):
                filename = df['source_file'].iloc[0] if 'source_file' in df.columns else f"File {i+1}"
                print(f"   📁 Processing {filename}...")
                original_count = len(df)
                filtered_df = self.optimizer.filter_by_time_step(df, self.selected_time_step)
                filtered_count = len(filtered_df)
                if filtered_count == 0:
                    self.ui.print_warning(f"No data points remain after filtering {filename}")
                    continue
                reduction = ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0
                print(f"   ✅ Filtered: {original_count} → {filtered_count} points ({reduction:.1f}% reduction)")
                filtered_df = filtered_df.copy()
                filtered_df['color'] = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]

                # Add precipitation data if enabled
                if self.precipitation_manager.enable_precipitation:
                    print(f"   🌧️ Adding precipitation data for {filename}...")
                    filtered_df = self.precipitation_manager.add_precipitation_data_to_dataframe(filtered_df)

                processed.append(filtered_df)
            if not processed:
                self.ui.print_error("No data remained after processing!")
                return False
            self.combined_data = pd.concat(processed, ignore_index=True)
            total_points = len(self.combined_data)
            rating = self.optimizer.get_performance_rating(total_points)
            print(f"\n✅ Total processed data points: {total_points}")
            print(f"⚡ Expected performance: {rating}")
            return True
        except Exception as e:
            self.ui.print_error(f"Failed to process data: {e}")
            return False

    def get_combined_data(self) -> Optional[pd.DataFrame]:
        """Get the processed combined data"""
        return self.combined_data

    def get_dataframes(self) -> List[pd.DataFrame]:
        """Get the list of loaded dataframes"""
        return self.dataframes

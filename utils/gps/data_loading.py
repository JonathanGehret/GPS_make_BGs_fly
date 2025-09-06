#!/usr/bin/env python3
"""
Data Loading for GPS Data

Handles loading, processing, and cleaning of GPS CSV files.
"""

import os
import glob
import logging
import pandas as pd
from typing import List, Optional
from .constants import DATA_DIR, CSV_SEPARATOR, TIMESTAMP_FORMAT, PROJECT_ROOT
from .validation import DataValidator


class DataLoader:
    """Handles loading and preprocessing of GPS data"""
    
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__ + '.DataLoader')
    
    def find_csv_files(self) -> List[str]:
        """Find all CSV files in known data locations.

        Search order (first non-empty wins unless ALWAYS_MERGE_DATA_DIRS=1):
          1. Explicit self.data_dir (DATA_DIR or injected path)
          2. Environment override GPS_DATA_DIR
          3. assets/rain_test_data
          4. assets/data/rain_test_data
          5. assets/data
          6. assets
        If ALWAYS_MERGE_DATA_DIRS=1 then we aggregate unique CSVs from all.
        """
        project_root = PROJECT_ROOT
        env_dir = os.environ.get('GPS_DATA_DIR')
        candidate_dirs: List[str] = []
        seen = set()

        def add(d: Optional[str]):
            if not d:
                return
            if d in seen:
                return
            if os.path.isdir(d):
                seen.add(d)
                candidate_dirs.append(d)

        force_rain = os.environ.get('RAIN_TEST_DATA', '0') == '1'
        rain_dir_primary = os.path.join(project_root, 'assets', 'rain_test_data')
        if force_rain:
            add(rain_dir_primary)
        add(self.data_dir)
        add(env_dir)
        if not force_rain:
            add(rain_dir_primary)
        add(os.path.join(project_root, 'assets', 'data', 'rain_test_data'))
        add(os.path.join(project_root, 'assets', 'data'))
        add(os.path.join(project_root, 'assets'))

        merge = os.environ.get('ALWAYS_MERGE_DATA_DIRS', '0') == '1'
        collected: List[str] = []
        for d in candidate_dirs:
            pattern = os.path.join(d, '*.csv')
            files = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith('.')]
            if files:
                if force_rain and d == rain_dir_primary:
                    return sorted(files)
                if merge:
                    collected.extend(files)
                else:
                    return sorted(files)
        if merge and collected:
            collected = sorted(list({os.path.abspath(f) for f in collected}))
        return collected
    
    def load_single_csv(self, file_path: str, validate: bool = True) -> Optional[pd.DataFrame]:
        """
        Load and validate a single CSV file
        Now more robust - cleans bad data instead of rejecting files
        
        Args:
            file_path: Path to the CSV file
            validate: Whether to validate the data format
            
        Returns:
            DataFrame or None if loading failed
        """
        try:
            # Load CSV with proper separator
            df = pd.read_csv(file_path, sep=CSV_SEPARATOR)
            
            # Filter for display=1 records
            if 'display' in df.columns:
                df = df[df['display'] == 1].copy()
            
            # Validate and clean if requested
            if validate:
                is_valid, messages = DataValidator.validate_csv_format(df)
                if not is_valid:
                    self.logger.error(f"Critical validation errors in {file_path}: {messages}")
                    return None
                elif messages:
                    # Log warnings but continue
                    for msg in messages:
                        self.logger.warning(f"Data issue in {file_path}: {msg}")
            
            # Clean data by removing rows with invalid coordinates
            initial_count = len(df)
            
            # Remove rows with NaN coordinates (but keep rows with NaN height)
            if 'Longitude' in df.columns and 'Latitude' in df.columns:
                df = df.dropna(subset=['Longitude', 'Latitude'])
                
                # Additional safety check for coordinate ranges
                valid_coords = (
                    (df['Longitude'].between(-180, 180)) & 
                    (df['Latitude'].between(-90, 90))
                )
                df = df[valid_coords]
            
            cleaned_count = len(df)
            if cleaned_count < initial_count:
                self.logger.info(f"Cleaned data: removed {initial_count - cleaned_count} invalid GPS points from {os.path.basename(file_path)}")
            
            if df.empty:
                self.logger.warning(f"No valid GPS data remaining in {file_path} after cleaning")
                return None
            
            # Parse timestamps with better error handling
            if 'Timestamp [UTC]' in df.columns:
                try:
                    df['Timestamp [UTC]'] = pd.to_datetime(
                        df['Timestamp [UTC]'], 
                        format=TIMESTAMP_FORMAT,
                        errors='coerce'  # Convert invalid timestamps to NaT
                    )
                    
                    # Remove rows with invalid timestamps
                    timestamp_invalid = df['Timestamp [UTC]'].isna()
                    if timestamp_invalid.any():
                        self.logger.warning(f"Removed {timestamp_invalid.sum()} rows with invalid timestamps from {os.path.basename(file_path)}")
                        df = df[~timestamp_invalid]
                    
                    if df.empty:
                        self.logger.warning(f"No valid timestamps remaining in {file_path}")
                        return None
                        
                except Exception as e:
                    self.logger.error(f"Failed to parse timestamps in {file_path}: {e}")
                    return None
            
            # Add metadata
            filename = os.path.basename(file_path)
            df['source_file'] = filename
            df['vulture_id'] = filename.replace('.csv', '').replace('_', ' ').title()
            
            self.logger.info(f"Successfully loaded {len(df)} valid records from {filename}")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load {file_path}: {e}")
            return None
    
    def load_all_csv_files(self, validate: bool = True) -> List[pd.DataFrame]:
        """Load all CSV files in the data directory"""
        csv_files = self.find_csv_files()
        
        if not csv_files:
            self.logger.warning("No CSV files found in data directory")
            return []
        
        dataframes = []
        for file_path in csv_files:
            df = self.load_single_csv(file_path, validate)
            if df is not None:
                dataframes.append(df)
        
        return dataframes

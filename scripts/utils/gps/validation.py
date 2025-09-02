#!/usr/bin/env python3
"""
Data Validation for GPS Data

Validates GPS data format, content, and data quality.
"""

import pandas as pd
from typing import List, Tuple
from .constants import REQUIRED_COLUMNS, TIMESTAMP_FORMAT


class DataValidator:
    """Validates GPS data format and content"""
    
    @staticmethod
    def validate_csv_format(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that DataFrame has required columns and proper format
        Now more lenient - cleans bad data instead of rejecting files
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns (still critical)
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return False, errors  # This is still a critical error
        
        # Check for empty DataFrame (still critical)
        if df.empty:
            errors.append("CSV file is empty")
            return False, errors
        
        # For other validation, we'll now be more lenient and just warn
        warnings = []
        
        # Clean and validate coordinates
        if 'Longitude' in df.columns:
            try:
                # Convert to numeric, replacing errors with NaN
                df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
                invalid_lon = ~df['Longitude'].between(-180, 180)
                if invalid_lon.any():
                    warnings.append(f"Found {invalid_lon.sum()} invalid longitude values (will be excluded)")
            except Exception as e:
                warnings.append(f"Longitude column has formatting issues: {e}")
        
        if 'Latitude' in df.columns:
            try:
                # Convert to numeric, replacing errors with NaN
                df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
                invalid_lat = ~df['Latitude'].between(-90, 90)
                if invalid_lat.any():
                    warnings.append(f"Found {invalid_lat.sum()} invalid latitude values (will be excluded)")
            except Exception as e:
                warnings.append(f"Latitude column has formatting issues: {e}")
        
        if 'Height' in df.columns:
            try:
                # Convert to numeric, replacing errors with NaN
                df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
                # Replace unrealistic heights with NaN (will show as "no height data")
                invalid_height = (df['Height'] < 0) | (df['Height'] > 10000)
                if invalid_height.any():
                    df.loc[invalid_height, 'Height'] = float('nan')
                    warnings.append(f"Found {invalid_height.sum()} unrealistic height values (0-10000m range) - will show as 'no height data'")
            except Exception as e:
                warnings.append(f"Height column has formatting issues: {e}")
        
        # Log warnings but don't reject the file
        if warnings:
            errors.extend(warnings)
        
        return True, errors  # Always return True now, just log issues
    
    @staticmethod
    def validate_timestamp_format(timestamp_series: pd.Series) -> bool:
        """Validate timestamp format"""
        try:
            pd.to_datetime(timestamp_series, format=TIMESTAMP_FORMAT)
            return True
        except Exception:
            return False


# ===========================
# EXCEPTION CLASSES
# ===========================

class GPSVisualizationError(Exception):
    """Base exception for GPS visualization errors"""
    pass


class DataLoadError(GPSVisualizationError):
    """Raised when data loading fails"""
    pass


class ValidationError(GPSVisualizationError):
    """Raised when data validation fails"""
    pass


class VisualizationError(GPSVisualizationError):
    """Raised when visualization creation fails"""
    pass

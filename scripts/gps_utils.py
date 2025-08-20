#!/usr/bin/env python3
"""
Common utilities and shared functionality for GPS Vulture Visualization
This module contains reusable functions, constants, and classes used across the project.

Best Practices Implemented:
- Type hints for better code documentation
- Comprehensive error handling
- Consistent logging and user feedback
- Performance optimization
- Clean code principles
"""

import pandas as pd
import plotly.express as px
import os
import glob
import logging
from typing import List, Dict, Tuple, Optional
import numpy as np

# ===========================
# CONSTANTS AND CONFIGURATION
# ===========================

# Project configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
VISUALIZATIONS_DIR = os.path.join(PROJECT_ROOT, 'visualizations')
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')

# Data format constants
CSV_SEPARATOR = ';'
TIMESTAMP_FORMAT = '%d.%m.%Y %H:%M:%S'
TIMESTAMP_MOBILE_FORMAT = '%d.%m %H:%M'

# Visualization constants
DEFAULT_COLORS = px.colors.qualitative.Set1
# MapLibre GL JS configuration (successor to deprecated Mapbox GL JS)
DEFAULT_MAPLIBRE_STYLE = "open-street-map"  # OpenStreetMap style works with MapLibre
MAPLIBRE_STYLES = {
    "open-street-map": "open-street-map",  # Default OpenStreetMap
    "carto-positron": "carto-positron",    # Light theme
    "carto-darkmatter": "carto-darkmatter", # Dark theme  
    "stamen-terrain": "stamen-terrain",    # Terrain view
    "stamen-toner": "stamen-toner",        # High contrast
    "white-bg": "white-bg"                 # White background
}
EARTH_RADIUS_KM = 6371

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'ultra_fast': 50,
    'very_fast': 100,
    'fast': 300,
    'moderate': 500,
    'slow': 1000
}

# ===========================
# LOGGING CONFIGURATION
# ===========================

def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ===========================
# DATA VALIDATION AND LOADING
# ===========================

class DataValidator:
    """Validates GPS data format and content"""
    
    REQUIRED_COLUMNS = ['Timestamp [UTC]', 'Longitude', 'Latitude', 'Height', 'display']
    
    @staticmethod
    def validate_csv_format(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that DataFrame has required columns and proper format
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns
        missing_cols = [col for col in DataValidator.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        
        # Check data types and ranges
        if 'Longitude' in df.columns:
            if not df['Longitude'].between(-180, 180).all():
                errors.append("Longitude values must be between -180 and 180")
        
        if 'Latitude' in df.columns:
            if not df['Latitude'].between(-90, 90).all():
                errors.append("Latitude values must be between -90 and 90")
        
        if 'Height' in df.columns:
            if df['Height'].min() < -500 or df['Height'].max() > 10000:
                errors.append("Height values seem unrealistic (should be between -500m and 10,000m)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_timestamp_format(timestamp_series: pd.Series) -> bool:
        """Validate timestamp format"""
        try:
            pd.to_datetime(timestamp_series, format=TIMESTAMP_FORMAT)
            return True
        except Exception:
            return False

class DataLoader:
    """Handles loading and preprocessing of GPS data"""
    
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__ + '.DataLoader')
    
    def find_csv_files(self) -> List[str]:
        """Find all CSV files in the data directory"""
        pattern = os.path.join(self.data_dir, '*.csv')
        csv_files = glob.glob(pattern)
        # Filter out .gitkeep and other non-data files
        csv_files = [f for f in csv_files if not os.path.basename(f).startswith('.')]
        return csv_files
    
    def load_single_csv(self, file_path: str, validate: bool = True) -> Optional[pd.DataFrame]:
        """
        Load and validate a single CSV file
        
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
            
            # Validate if requested
            if validate:
                is_valid, errors = DataValidator.validate_csv_format(df)
                if not is_valid:
                    self.logger.warning(f"Validation errors in {file_path}: {errors}")
                    return None
            
            # Parse timestamps
            if 'Timestamp [UTC]' in df.columns:
                try:
                    df['Timestamp [UTC]'] = pd.to_datetime(
                        df['Timestamp [UTC]'], 
                        format=TIMESTAMP_FORMAT
                    )
                except Exception as e:
                    self.logger.error(f"Failed to parse timestamps in {file_path}: {e}")
                    return None
            
            # Add metadata
            filename = os.path.basename(file_path)
            df['source_file'] = filename
            df['vulture_id'] = filename.replace('.csv', '').replace('_', ' ').title()
            
            self.logger.info(f"Loaded {len(df)} records from {filename}")
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

# ===========================
# PERFORMANCE OPTIMIZATION
# ===========================

class PerformanceOptimizer:
    """Handles performance optimization through data filtering"""
    
    TIME_STEP_OPTIONS = {
        "1s": {"seconds": 1, "label": "1 second", "description": "Ultra-high detail"},
        "30s": {"seconds": 30, "label": "30 seconds", "description": "Very high detail"},
        "1m": {"seconds": 60, "label": "1 minute", "description": "High detail"},
        "2m": {"seconds": 120, "label": "2 minutes", "description": "Good balance"},
        "5m": {"seconds": 300, "label": "5 minutes", "description": "Faster loading"},
        "10m": {"seconds": 600, "label": "10 minutes", "description": "Quick overview"},
        "20m": {"seconds": 1200, "label": "20 minutes", "description": "Fast loading"},
        "30m": {"seconds": 1800, "label": "30 minutes", "description": "Fastest loading"},
        "60m": {"seconds": 3600, "label": "1 hour", "description": "Summary only"}
    }
    
    @staticmethod
    def estimate_data_points(dataframes: List[pd.DataFrame], time_step_seconds: int) -> Tuple[int, int]:
        """
        Estimate data points before and after filtering
        
        Returns:
            Tuple of (original_count, estimated_filtered_count)
        """
        total_original = sum(len(df) for df in dataframes)
        total_filtered = 0
        
        for df in dataframes:
            if len(df) <= 1:
                total_filtered += len(df)
                continue
            
            time_span = (df['Timestamp [UTC]'].max() - df['Timestamp [UTC]'].min()).total_seconds()
            estimated_points = max(1, int(time_span / time_step_seconds))
            total_filtered += min(estimated_points, len(df))
        
        return total_original, total_filtered
    
    @staticmethod
    def filter_by_time_step(df: pd.DataFrame, time_step_seconds: int) -> pd.DataFrame:
        """
        Filter DataFrame to include only points at specified time intervals
        
        Args:
            df: DataFrame with 'Timestamp [UTC]' column
            time_step_seconds: Minimum seconds between points
            
        Returns:
            Filtered DataFrame
        """
        if len(df) == 0 or time_step_seconds <= 1:
            return df
        
        df_sorted = df.sort_values('Timestamp [UTC]').copy()
        filtered_rows = []
        last_time = None
        
        for _, row in df_sorted.iterrows():
            current_time = row['Timestamp [UTC]']
            
            if last_time is None or (current_time - last_time).total_seconds() >= time_step_seconds:
                filtered_rows.append(row)
                last_time = current_time
        
        return pd.DataFrame(filtered_rows)
    
    @staticmethod
    def get_performance_rating(point_count: int) -> str:
        """Get performance rating emoji based on point count"""
        if point_count < PERFORMANCE_THRESHOLDS['ultra_fast']:
            return "🔥"
        elif point_count < PERFORMANCE_THRESHOLDS['very_fast']:
            return "🚀"
        elif point_count < PERFORMANCE_THRESHOLDS['fast']:
            return "⚡"
        elif point_count < PERFORMANCE_THRESHOLDS['moderate']:
            return "⏱️"
        else:
            return "🐌"

# ===========================
# VISUALIZATION UTILITIES
# ===========================

class VisualizationHelper:
    """Helper functions for creating consistent visualizations"""
    
    @staticmethod
    def setup_maplibre_layout(df: pd.DataFrame, height: int = 600, zoom: int = 12) -> Dict:
        """Create standard MapLibre layout configuration (successor to Mapbox)"""
        return {
            'mapbox': {  # Note: Plotly still uses 'mapbox' key but with MapLibre backend
                'style': DEFAULT_MAPLIBRE_STYLE,
                'center': {
                    'lat': df['Latitude'].mean(),
                    'lon': df['Longitude'].mean()
                },
                'zoom': zoom
            },
            'height': height,
            'margin': {'r': 0, 'l': 0, 't': 30, 'b': 0},
            'showlegend': True
        }
    
    @staticmethod
    def create_hover_template(include_time: bool = True, mobile_format: bool = False) -> str:
        """Create consistent hover template"""
        if include_time:
            return (
                "<b>%{hovertext}</b><br>"
                "Time: %{customdata[0]}<br>"
                "Lat: %{lat:.4f}°<br>"
                "Lon: %{lon:.4f}°<br>"
                "Alt: %{customdata[1]}m"
                "<extra></extra>"
            )
        else:
            return (
                "<b>%{hovertext}</b><br>"
                "Lat: %{lat:.4f}°<br>"
                "Lon: %{lon:.4f}°<br>"
                "Alt: %{customdata[0]}m"
                "<extra></extra>"
            )
    
    @staticmethod
    def assign_colors(dataframes: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Assign consistent colors to vultures"""
        for i, df in enumerate(dataframes):
            df['color'] = DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        return dataframes

# ===========================
# GEOGRAPHIC UTILITIES
# ===========================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth
    
    Args:
        lat1, lon1: First point coordinates in decimal degrees
        lat2, lon2: Second point coordinates in decimal degrees
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return c * EARTH_RADIUS_KM

# ===========================
# DIRECTORY MANAGEMENT
# ===========================

def ensure_output_directories():
    """Create output directories if they don't exist"""
    for directory in [VISUALIZATIONS_DIR, ANALYSIS_DIR]:
        os.makedirs(directory, exist_ok=True)

def get_output_path(filename: str, output_type: str = 'visualizations') -> str:
    """
    Get the full path for an output file
    
    Args:
        filename: Name of the output file
        output_type: 'visualizations' or 'analysis'
        
    Returns:
        Full path to the output file
    """
    if output_type == 'visualizations':
        base_dir = VISUALIZATIONS_DIR
    elif output_type == 'analysis':
        base_dir = ANALYSIS_DIR
    else:
        raise ValueError(f"Unknown output_type: {output_type}")
    
    ensure_output_directories()
    return os.path.join(base_dir, filename)

# ===========================
# USER INTERFACE UTILITIES
# ===========================

class UserInterface:
    """Utilities for consistent user interaction"""
    
    @staticmethod
    def print_header(title: str, width: int = 80):
        """Print a formatted header"""
        print("\n" + "=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
    
    @staticmethod
    def print_section(title: str, width: int = 50):
        """Print a formatted section header"""
        print(f"\n{title}")
        print("-" * width)
    
    @staticmethod
    def print_success(message: str):
        """Print a success message"""
        print(f"✅ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message"""
        print(f"⚠️  {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message"""
        print(f"❌ {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message"""
        print(f"ℹ️  {message}")

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

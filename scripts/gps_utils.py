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
        Now more lenient - cleans bad data instead of rejecting files
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns (still critical)
        missing_cols = [col for col in DataValidator.REQUIRED_COLUMNS if col not in df.columns]
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
    def calculate_map_bounds(df: pd.DataFrame, padding_percent: float = 0.1) -> Dict:
        """Calculate optimal map center and zoom to fit all data points"""
        if df.empty:
            logger.warning("Empty dataframe provided to calculate_map_bounds, using default bounds")
            return {'center': {'lat': 47.57, 'lon': 12.98}, 'zoom': 12}
        
        # Calculate bounding box
        lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
        lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
        
        # Add padding to ensure points aren't right at the edge
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        
        lat_padding = lat_range * padding_percent
        lon_padding = lon_range * padding_percent
        
        # Calculate center point
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        
        # Calculate appropriate zoom level based on data spread
        # This is an approximation - MapLibre will adjust as needed
        max_range = max(lat_range, lon_range)
        if max_range == 0:
            zoom = 15  # Very local data
        elif max_range < 0.01:  # < ~1km
            zoom = 14
        elif max_range < 0.05:  # < ~5km  
            zoom = 12
        elif max_range < 0.1:   # < ~10km
            zoom = 11
        elif max_range < 0.5:   # < ~50km
            zoom = 9
        else:
            zoom = 8
        
        # Log the calculated bounds for debugging
        logger.info(f"Smart bounds calculated: center=({center_lat:.4f}, {center_lon:.4f}), zoom={zoom}")
        logger.info(f"Data range: lat {lat_min:.4f} to {lat_max:.4f}, lon {lon_min:.4f} to {lon_max:.4f}")
            
        return {
            'center': {'lat': center_lat, 'lon': center_lon},
            'zoom': zoom,
            'bounds': {
                'lat_min': lat_min - lat_padding,
                'lat_max': lat_max + lat_padding, 
                'lon_min': lon_min - lon_padding,
                'lon_max': lon_max + lon_padding
            }
        }
    
    @staticmethod
    def setup_maplibre_layout(df: pd.DataFrame, height: int = 600, auto_fit: bool = True) -> Dict:
        """Create standard MapLibre layout configuration with smart bounds"""
        if auto_fit:
            map_config = VisualizationHelper.calculate_map_bounds(df)
            center = map_config['center']
            zoom = map_config['zoom']
        else:
            # Fallback to simple center calculation
            center = {
                'lat': df['Latitude'].mean() if not df.empty else 47.57,
                'lon': df['Longitude'].mean() if not df.empty else 12.98
            }
            zoom = 12
            
        return {
            'mapbox': {  # Note: Plotly still uses 'mapbox' key but with MapLibre backend
                'style': DEFAULT_MAPLIBRE_STYLE,
                'center': center,
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


def get_numbered_output_path(base_filename: str, output_type: str = 'visualizations') -> str:
    """
    Get the full path for an output file with consecutive numbering
    
    This function automatically finds the next available number and creates
    a filename like: base_name_01.html, base_name_02.html, etc.
    
    Args:
        base_filename: Base name of the output file (without extension)
        output_type: 'visualizations' or 'analysis'
        
    Returns:
        Full path to the numbered output file
    """
    if output_type == 'visualizations':
        base_dir = VISUALIZATIONS_DIR
        extension = '.html'
    elif output_type == 'analysis':
        base_dir = ANALYSIS_DIR
        extension = '.html'
    else:
        raise ValueError(f"Unknown output_type: {output_type}")
    
    ensure_output_directories()
    
    # Find the next available number
    existing_numbers = []
    
    if os.path.exists(base_dir):
        for file in os.listdir(base_dir):
            if file.startswith(base_filename) and file.endswith(extension):
                # Extract number from filename like "base_name_03.html"
                try:
                    # Remove base filename and extension
                    remaining = file[len(base_filename):]
                    if remaining.startswith('_') and remaining.endswith(extension):
                        number_part = remaining[1:-len(extension)]  # Remove _ and .html
                        if number_part.isdigit():
                            existing_numbers.append(int(number_part))
                except (ValueError, IndexError):
                    continue
    
    # Find next available number
    next_number = 1
    if existing_numbers:
        next_number = max(existing_numbers) + 1
    
    # Create numbered filename
    numbered_filename = f"{base_filename}_{next_number:02d}{extension}"
    
    return os.path.join(base_dir, numbered_filename)

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


# ===========================
# UTILITY FUNCTIONS
# ===========================

def format_height_display(height_value) -> str:
    """
    Format height value for display in tooltips, handling NaN values gracefully.
    
    Args:
        height_value: Height value (can be float, int, or NaN)
        
    Returns:
        str: Formatted height string for display
    """
    try:
        # Check if the value is NaN or None
        if pd.isna(height_value) or height_value is None:
            return "No height data"
        
        # Convert to numeric if it's a string
        if isinstance(height_value, str):
            try:
                height_value = float(height_value)
            except (ValueError, TypeError):
                return "No height data"
        
        # Format the numeric value
        return f"{height_value:.1f}m"
        
    except Exception:
        return "No height data"

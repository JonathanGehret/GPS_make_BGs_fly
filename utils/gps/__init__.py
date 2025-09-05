#!/usr/bin/env python3
"""
GPS Utilities Package

Modular GPS utilities for vulture visualization and analysis.
This package provides a clean, organized structure for all GPS-related functionality.
"""

# Import main classes and functions for easy access
from .constants import (
    DATA_DIR, VISUALIZATIONS_DIR, ANALYSIS_DIR,
    CSV_SEPARATOR, TIMESTAMP_FORMAT, TIMESTAMP_MOBILE_FORMAT,
    DEFAULT_COLORS, DEFAULT_MAPLIBRE_STYLE, MAPLIBRE_STYLES,
    EARTH_RADIUS_KM, PERFORMANCE_THRESHOLDS, TIME_STEP_OPTIONS
)

from .calculations import haversine_distance, format_height_display

from .validation import (
    DataValidator, GPSVisualizationError, DataLoadError, 
    ValidationError, VisualizationError
)

from .data_loading import DataLoader

from .performance import PerformanceOptimizer

from .visualization_helpers import VisualizationHelper

from .directory_utils import (
    ensure_output_directories, get_output_path, get_numbered_output_path
)

from .ui_utils import setup_logging, UserInterface, logger

# Version info
__version__ = "1.0.0"
__author__ = "GPS Vulture Visualization Project"

# Export main components for backwards compatibility
__all__ = [
    # Constants
    'DATA_DIR', 'VISUALIZATIONS_DIR', 'ANALYSIS_DIR',
    'CSV_SEPARATOR', 'TIMESTAMP_FORMAT', 'TIMESTAMP_MOBILE_FORMAT',
    'DEFAULT_COLORS', 'DEFAULT_MAPLIBRE_STYLE', 'MAPLIBRE_STYLES',
    'EARTH_RADIUS_KM', 'PERFORMANCE_THRESHOLDS', 'TIME_STEP_OPTIONS',
    
    # Main classes
    'DataValidator', 'DataLoader', 'PerformanceOptimizer', 
    'VisualizationHelper', 'UserInterface',
    
    # Functions
    'haversine_distance', 'format_height_display',
    'ensure_output_directories', 'get_output_path', 'get_numbered_output_path',
    'setup_logging',
    
    # Exceptions
    'GPSVisualizationError', 'DataLoadError', 'ValidationError', 'VisualizationError',
    
    # Logger
    'logger'
]

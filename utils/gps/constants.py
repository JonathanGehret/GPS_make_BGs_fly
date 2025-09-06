#!/usr/bin/env python3
"""
Constants and Configuration for GPS Vulture Visualization

Centralized configuration for all GPS visualization components.
"""

import os
import plotly.express as px

# ===========================
# PROJECT CONFIGURATION
# ===========================

# Project paths
# Determine project root robustly: this file is at <root>/utils/gps/constants.py
# So go up three levels instead of four.
_THIS_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_THIS_FILE)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
VISUALIZATIONS_DIR = os.path.join(PROJECT_ROOT, 'visualizations')
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, 'analysis')

# ===========================
# DATA FORMAT CONSTANTS
# ===========================

# CSV format configuration
CSV_SEPARATOR = ';'
TIMESTAMP_FORMAT = '%d.%m.%Y %H:%M:%S'
TIMESTAMP_MOBILE_FORMAT = '%d.%m %H:%M'

# Required columns for GPS data
REQUIRED_COLUMNS = ['Timestamp [UTC]', 'Longitude', 'Latitude', 'Height', 'display']

# ===========================
# VISUALIZATION CONSTANTS
# ===========================

# Color configuration
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

# ===========================
# GEOGRAPHIC CONSTANTS
# ===========================

# Earth radius for distance calculations
EARTH_RADIUS_KM = 6371

# ===========================
# PERFORMANCE CONFIGURATION
# ===========================

# Performance thresholds for point count ratings
PERFORMANCE_THRESHOLDS = {
    'ultra_fast': 50,
    'very_fast': 100,
    'fast': 300,
    'moderate': 500,
    'slow': 1000
}

# Time step options for performance optimization
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

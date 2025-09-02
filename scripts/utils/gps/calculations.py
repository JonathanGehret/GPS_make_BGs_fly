#!/usr/bin/env python3
"""
GPS Calculations and Geographic Utilities

Functions for distance calculations and geographic computations.
"""

import numpy as np
from .constants import EARTH_RADIUS_KM


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


def format_height_display(height_value) -> str:
    """
    Format height value for display in tooltips, handling NaN values gracefully.
    
    Args:
        height_value: Height value (can be float, int, or NaN)
        
    Returns:
        str: Formatted height string for display
    """
    import pandas as pd
    
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

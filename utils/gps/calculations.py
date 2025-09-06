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


def calculate_velocity(lat1: float, lon1: float, lat2: float, lon2: float, time_diff_seconds: float) -> float:
    """
    Calculate velocity between two GPS points
    
    Args:
        lat1, lon1: First point coordinates in decimal degrees
        lat2, lon2: Second point coordinates in decimal degrees
        time_diff_seconds: Time difference between points in seconds
        
    Returns:
        Velocity in m/s, or 0 if time_diff is 0 or invalid
    """
    if time_diff_seconds <= 0:
        return 0.0
    
    # Calculate distance in kilometers
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Convert to meters
    distance_m = distance_km * 1000
    
    # Calculate velocity in m/s
    velocity = distance_m / time_diff_seconds
    
    return velocity


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


def format_velocity_display(velocity_value) -> str:
    """
    Format velocity value for display in tooltips
    
    Args:
        velocity_value: Velocity value in m/s
        
    Returns:
        str: Formatted velocity string for display
    """
    import pandas as pd
    
    try:
        # Check if the value is NaN or None
        if pd.isna(velocity_value) or velocity_value is None:
            return "No velocity data"
        
        # Convert to numeric if it's a string
        if isinstance(velocity_value, str):
            try:
                velocity_value = float(velocity_value)
            except (ValueError, TypeError):
                return "No velocity data"
        
        # Format the numeric value
        return f"{velocity_value:.1f} m/s"
        
    except Exception:
        return "No velocity data"

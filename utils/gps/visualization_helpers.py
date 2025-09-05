#!/usr/bin/env python3
"""
Visualization Helper Functions

Utilities for creating consistent and well-formatted visualizations.
"""

import logging
import pandas as pd
from typing import Dict, List
from .constants import DEFAULT_COLORS, DEFAULT_MAPLIBRE_STYLE

logger = logging.getLogger(__name__)


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

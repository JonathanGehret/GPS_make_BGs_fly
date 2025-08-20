"""
Performance Optimizer Module

Handles performance optimization through data filtering and time step management.
"""

import pandas as pd
from typing import List, Tuple

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'ultra_fast': 50,
    'very_fast': 100,
    'fast': 300,
    'moderate': 500,
    'slow': 1000
}


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

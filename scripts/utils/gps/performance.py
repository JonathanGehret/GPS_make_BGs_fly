#!/usr/bin/env python3
"""
Performance Optimization Utilities

Handles data filtering and performance optimization for large GPS datasets.
"""

import pandas as pd
from typing import List, Tuple
from .constants import TIME_STEP_OPTIONS, PERFORMANCE_THRESHOLDS


class PerformanceOptimizer:
    """Handles performance optimization through data filtering"""
    
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
    
    @staticmethod
    def get_time_step_options():
        """Get available time step options"""
        return TIME_STEP_OPTIONS

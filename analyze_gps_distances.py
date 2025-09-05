#!/usr/bin/env python3
"""
Quick check of GPS data to understand vulture distances
"""

import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.gps_utils import DataLoader, haversine_distance

def analyze_gps_data():
    """Analyze the GPS data to understand distances"""
    print("🔍 Analyzing GPS data distances...")
    
    data_loader = DataLoader("assets/data")
    dataframes = data_loader.load_all_csv_files()
    
    if len(dataframes) < 2:
        print("Need at least 2 vultures for distance analysis")
        return
    
    df1 = dataframes[0]
    df2 = dataframes[1]
    
    v1_name = df1['vulture_id'].iloc[0] if 'vulture_id' in df1.columns else "Vulture 1"
    v2_name = df2['vulture_id'].iloc[0] if 'vulture_id' in df2.columns else "Vulture 2"
    
    print(f"Comparing {v1_name} vs {v2_name}")
    print(f"{v1_name}: {len(df1)} records")
    print(f"{v2_name}: {len(df2)} records")
    
    # Convert timestamps to datetime if needed
    if 'timestamp' in df1.columns:
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])
    if 'timestamp' in df2.columns:  
        df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    
    # Find overlapping time range
    if 'timestamp' in df1.columns and 'timestamp' in df2.columns:
        start_time = max(df1['timestamp'].min(), df2['timestamp'].min())
        end_time = min(df1['timestamp'].max(), df2['timestamp'].max())
        print(f"Overlapping time range: {start_time} to {end_time}")
        
        # Sample some distances at different times
        sample_times = pd.date_range(start_time, end_time, periods=10)
        
        distances = []
        for t in sample_times:
            # Find closest records to this time
            idx1 = df1.iloc[(df1['timestamp'] - t).abs().argsort()[:1]].index[0]
            idx2 = df2.iloc[(df2['timestamp'] - t).abs().argsort()[:1]].index[0]
            
            lat1, lon1 = df1.loc[idx1, 'latitude'], df1.loc[idx1, 'longitude']
            lat2, lon2 = df2.loc[idx2, 'latitude'], df2.loc[idx2, 'longitude']
            
            dist = haversine_distance(lat1, lon1, lat2, lon2)
            distances.append(dist)
            
            print(f"  {t.strftime('%H:%M:%S')}: {dist:.2f}km apart")
        
        min_dist = min(distances)
        max_dist = max(distances)
        avg_dist = sum(distances) / len(distances)
        
        print(f"\nDistance statistics:")
        print(f"  Minimum: {min_dist:.2f}km")
        print(f"  Maximum: {max_dist:.2f}km") 
        print(f"  Average: {avg_dist:.2f}km")
        
        print(f"\nRecommended settings:")
        print(f"  Proximity threshold: {min_dist * 1.5:.1f}km (to catch closest approaches)")
        print(f"  Time threshold: 1-2 minutes (for test data)")
    
    else:
        print("No timestamp columns found for temporal analysis")

if __name__ == "__main__":
    analyze_gps_data()

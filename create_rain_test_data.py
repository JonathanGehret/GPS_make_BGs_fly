#!/usr/bin/env python3
"""
Create synthetic GPS data for testing precipitation overlay.
Uses a known heavy rain event location and time.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


def create_synthetic_rain_test_data():
    """
    Create synthetic GPS data for London during Hurricane Ciaran (November 2, 2023)
    This was a major storm with heavy rainfall across the UK.
    """
    # London coordinates during Hurricane Ciaran
    center_lat = 51.5074  # London
    center_lon = -0.1278
    
    # Hurricane Ciaran date - known heavy rain event
    start_time = datetime(2023, 11, 2, 6, 0, 0)  # 6 AM UTC
    
    # Create GPS tracks for 2 "vultures" moving around London
    data_vulture1 = []
    data_vulture2 = []
    
    # Generate 4 hours of data (6 AM to 10 AM during peak storm)
    for i in range(240):  # 240 minutes = 4 hours
        current_time = start_time + timedelta(minutes=i)
        
        # Vulture 1: Circular pattern around London
        angle1 = (i * 2 * np.pi) / 120  # Complete circle every 2 hours
        lat1 = center_lat + 0.05 * np.cos(angle1) + np.random.normal(0, 0.002)
        lon1 = center_lon + 0.05 * np.sin(angle1) + np.random.normal(0, 0.002)
        
        # Vulture 2: Figure-8 pattern
        angle2 = (i * 2 * np.pi) / 90  # Faster movement
        lat2 = center_lat + 0.03 * np.cos(angle2) + 0.02 * np.cos(2 * angle2) + np.random.normal(0, 0.002)
        lon2 = center_lon + 0.03 * np.sin(angle2) + np.random.normal(0, 0.002)
        
        # Random altitude and speed
        altitude1 = 150 + 50 * np.sin(angle1) + np.random.normal(0, 10)
        altitude2 = 180 + 40 * np.cos(angle2) + np.random.normal(0, 10)
        speed1 = 25 + 10 * np.random.random()
        speed2 = 30 + 10 * np.random.random()
        
        data_vulture1.append({
            'Timestamp [UTC]': current_time.strftime('%d.%m.%Y %H:%M:%S'),
            'Latitude': round(lat1, 6),
            'Longitude': round(lon1, 6),
            'Height': round(altitude1, 1),
            'Speed': round(speed1, 1),
            'Heading': round((angle1 * 180 / np.pi) % 360, 1),
            'display': 1
        })
        
        data_vulture2.append({
            'Timestamp [UTC]': current_time.strftime('%d.%m.%Y %H:%M:%S'),
            'Latitude': round(lat2, 6),
            'Longitude': round(lon2, 6),
            'Height': round(altitude2, 1),
            'Speed': round(speed2, 1),
            'Heading': round((angle2 * 180 / np.pi) % 360, 1),
            'display': 1
        })
    
    # Create DataFrames
    df1 = pd.DataFrame(data_vulture1)
    df2 = pd.DataFrame(data_vulture2)
    
    # Create rain test data directory
    rain_test_dir = os.path.join(os.getcwd(), 'assets', 'rain_test_data')
    os.makedirs(rain_test_dir, exist_ok=True)
    
    # Save CSV files
    csv1_path = os.path.join(rain_test_dir, 'hurricane_vulture_01.csv')
    csv2_path = os.path.join(rain_test_dir, 'hurricane_vulture_02.csv')
    
    df1.to_csv(csv1_path, sep=';', index=False)
    df2.to_csv(csv2_path, sep=';', index=False)
    
    print(f"✅ Created rain test data:")
    print(f"   📁 Directory: {rain_test_dir}")
    print(f"   📄 File 1: {csv1_path} ({len(df1)} points)")
    print(f"   📄 File 2: {csv2_path} ({len(df2)} points)")
    print(f"   📅 Time range: {start_time} to {start_time + timedelta(hours=4)}")
    print(f"   🌍 Location: London (Hurricane Ciaran event)")
    print(f"   🌧️ Expected: Heavy precipitation during this storm")
    print()
    print("To test precipitation overlay:")
    print(f"   export GPS_DATA_DIR='{rain_test_dir}'")
    print("   export PRECIP_ENABLE=1 PRECIP_ZMAX=5")
    print("   python3 core/animation/animate_live_map.py")
    
    return rain_test_dir, [csv1_path, csv2_path]


if __name__ == "__main__":
    create_synthetic_rain_test_data()

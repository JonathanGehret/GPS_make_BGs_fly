import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate the same synthetic data as in animate_3d.py
np.random.seed(42)
start_time = 1
end_time = 50

# Base datetime for timestamps
base_datetime = datetime(2024, 6, 15, 8, 0, 0)  # Start at 8:00 AM

# Vulture A: 50 points - flying around the lake
timestamps_a = np.linspace(start_time, end_time, 50, dtype=int)
latitudes_a = np.linspace(47.54, 47.58, 50) + np.random.normal(0, 0.001, 50)
longitudes_a = np.linspace(12.96, 13.00, 50) + np.random.normal(0, 0.001, 50)
altitudes_a = np.linspace(800, 1800, 50) + np.random.normal(0, 20, 50)

# Vulture B: 30 points - flying higher around mountain peaks
timestamps_b = np.sort(np.random.choice(np.arange(start_time, end_time+1), 30, replace=False))
latitudes_b = np.linspace(47.56, 47.60, 30) + np.random.normal(0, 0.001, 30)
longitudes_b = np.linspace(12.98, 13.02, 30) + np.random.normal(0, 0.001, 30)
altitudes_b = np.linspace(1200, 2200, 30) + np.random.normal(0, 30, 30)

# Create DataFrames for each vulture
def create_vulture_df(timestamps, latitudes, longitudes, altitudes):
    data = []
    for i, ts in enumerate(timestamps):
        # Convert timestamp to datetime format
        dt = base_datetime + timedelta(minutes=int(ts)*2)  # 2 minutes per timestamp unit
        timestamp_str = dt.strftime("%d.%m.%Y %H:%M:%S")
        
        data.append({
            'Timestamp [UTC]': timestamp_str,
            'Longitude': f"{longitudes[i]:.15f}",
            'Latitude': f"{latitudes[i]:.15f}", 
            'Height': f"{int(altitudes[i])}",
            'display': '1'
        })
    return pd.DataFrame(data)

# Create DataFrames
df_vulture_a = create_vulture_df(timestamps_a, latitudes_a, longitudes_a, altitudes_a)
df_vulture_b = create_vulture_df(timestamps_b, latitudes_b, longitudes_b, altitudes_b)

# Export to CSV files
df_vulture_a.to_csv('data/test_vulture_01.csv', sep=';', index=False)
df_vulture_b.to_csv('data/test_vulture_02.csv', sep=';', index=False)

print("Exported synthetic vulture data to:")
print("- data/test_vulture_01.csv (50 data points)")
print("- data/test_vulture_02.csv (30 data points)")

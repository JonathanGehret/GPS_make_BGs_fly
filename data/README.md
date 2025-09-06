# Test Data Documentation

This directory contains test GPS data files for local debugging and development.

## Test Files

### test_vulture_A.csv
- **Vulture ID**: Bartgeier_A
- **Time Range**: 2024-08-15 08:00:00 - 08:15:00 UTC (16 data points)
- **Location**: Austrian Alps region (47.57°N, 12.98°E)
- **Flight Pattern**: Gradual northeastern movement with altitude gain
- **Height Range**: 2150m - 2225m

### test_vulture_B.csv
- **Vulture ID**: Bartgeier_B
- **Time Range**: 2024-08-15 08:05:00 - 08:20:00 UTC (16 data points)
- **Location**: Austrian Alps region (47.57°N, 12.98°E)
- **Flight Pattern**: Steady northeastern movement with consistent altitude gain
- **Height Range**: 2140m - 2215m

### test_vulture_C.csv
- **Vulture ID**: Bartgeier_C
- **Time Range**: 2024-08-15 08:03:00 - 08:18:00 UTC (16 data points)
- **Location**: Austrian Alps region (47.57°N, 12.98°E)
- **Flight Pattern**: Slow northeastern movement with steady altitude gain
- **Height Range**: 2180m - 2255m

## Data Format

All CSV files use the same format:
```
Timestamp [UTC],Longitude,Latitude,Height,vulture_id,display
2024-08-15 08:00:00,12.9800,47.5700,2150,Bartgeier_A,1
```

**Important**: The `display` column must contain `1` for visible data points that should be included in analysis.

## Usage in Analysis

These test files can be used to:

1. **Proximity Analysis**: Test vulture interactions and distance calculations
2. **2D Live Map**: Demonstrate real-time tracking visualization
3. **3D Visualization**: Show flight paths with altitude changes

## Overlapping Time Windows

The vultures have overlapping observation times (08:05-08:15) which allows for:
- Proximity analysis between pairs
- Multi-vulture tracking scenarios
- Interaction detection algorithms

## Coordinate System

- **Coordinate System**: WGS84 (GPS standard)
- **Altitude**: Meters above sea level
- **Region**: Austrian Alps (Hohe Tauern National Park area)
- **Precision**: ~11m horizontal accuracy (5 decimal places)

## Test Scenarios

1. **Close Proximity**: Vultures A and B have closest approach around 08:10-08:15
2. **Altitude Differences**: Vulture C flies at higher altitudes
3. **Time Overlap**: All three vultures tracked simultaneously 08:05-08:15
4. **Movement Patterns**: Different flight speeds and directions for variety

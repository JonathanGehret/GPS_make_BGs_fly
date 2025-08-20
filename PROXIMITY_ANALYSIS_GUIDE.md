# Vulture Proximity Analysis Tool

## Overview
This tool analyzes GPS tracking data from multiple vultures to identify when they are in close proximity to each other. This is valuable for understanding:
- Social behavior patterns
- Feeding site locations (where multiple vultures gather)
- Flight path interactions
- Territorial behaviors
- Seasonal patterns

## Features

### 🔍 **Core Analysis**
- **Proximity Detection**: Finds when 2+ vultures are within configurable distance (default: 2km)
- **Time Window Matching**: Accounts for GPS timestamp differences (default: ±30 minutes)
- **Haversine Distance**: Accurate great-circle distance calculations
- **Large Dataset Support**: Handles weeks, months, or years of data

### 📊 **Statistics Generated**
- **Total proximity events** found
- **Pair-wise interaction counts** (A-B, A-C, B-C, etc.)
- **Distance statistics** (average, min, max proximity distances)
- **Temporal patterns** (hourly activity, monthly trends)
- **Geographic hotspots** (clustering of events)

### 📈 **Visualizations Created**
- **Interactive Timeline**: Events over time with distance coloring
- **Proximity Map**: Geographic visualization of encounter locations
- **Hotspot Analysis**: Clusters of frequent encounters

## Usage

### Basic Usage
```bash
# Run analysis with default settings (2km threshold, 30min time window)
python3 scripts/proximity_analysis.py
```

### Results Generated
The tool creates these files in the `analysis/` folder:
- `proximity_timeline.html` - Interactive timeline visualization
- `proximity_map.html` - Interactive map of proximity events
- `proximity_analysis_results.json` - Detailed raw results

### Customization
You can modify the analysis parameters by editing the script:

```python
# Change proximity threshold (kilometers)
analyzer = VultureProximityAnalyzer(proximity_threshold_km=1.5)

# Change time window for matching GPS records (minutes)
proximity_events = analyzer.find_proximity_events(time_window_minutes=15)
```

## Sample Output

```
VULTURE PROXIMITY ANALYSIS REPORT
============================================================

📊 OVERVIEW:
  • Total proximity events: 37
  • Unique vulture pairs: 1 (A-B)
  • Analysis period: 0 days
  • Events per day: 37.00
  • Proximity threshold: 2.0 km

📏 DISTANCE STATISTICS:
  • Average proximity distance: 1.79 km
  • Closest encounter: 1.431 km
  • Furthest proximity: 1.99 km

🦅 PAIR-WISE INTERACTIONS:
  • A-B: 37 events, avg 1.79km apart
    └─ Closest: 1.431km

🕒 TEMPORAL PATTERNS:
  • Peak activity hour: 8:00 (26 events)

📍 GEOGRAPHIC HOTSPOTS:
  • Hotspot 1: 16 events at 47.5553°N, 12.9752°E
  • Hotspot 2: 11 events at 47.5810°N, 13.0005°E
  • Hotspot 3: 10 events at 47.5680°N, 12.9874°E
```

## Interpretation Guide

### 🎯 **What Proximity Events Indicate**
- **Feeding Sites**: Clusters of events often indicate carcass locations
- **Roosting Areas**: Regular morning/evening encounters suggest shared roosting
- **Thermal Sharing**: Proximity during flight hours indicates shared thermals
- **Social Interactions**: Close encounters may indicate territorial or social behavior

### 📍 **Geographic Hotspots**
- **High Event Count**: Popular feeding or roosting locations
- **Low Average Distance**: Indicates very close interactions (< 1km)
- **Seasonal Clusters**: Different hotspots may be active in different seasons

### 🕒 **Temporal Patterns**
- **Morning Peaks**: Often indicate roosting site departures
- **Midday Activity**: May indicate thermal sharing or feeding
- **Evening Peaks**: Could suggest return to roosting areas

## Data Requirements

### CSV Format
The tool expects CSV files in the `data/` folder with this format:
```
Timestamp [UTC];Longitude;Latitude;Height;display
15.06.2024 08:02:00;12.9650;47.5450;850;1
15.06.2024 08:05:00;12.9680;47.5470;920;1
```

### Scaling
- **Small datasets**: 50-100 GPS points per vulture
- **Medium datasets**: 1,000-10,000 points per vulture (weeks/months)
- **Large datasets**: 50,000+ points per vulture (years)

## Advanced Features

### Customizable Thresholds
```python
# Analyze very close encounters (under 500m)
analyzer = VultureProximityAnalyzer(proximity_threshold_km=0.5)

# Analyze broader regional co-occurrence (within 5km)
analyzer = VultureProximityAnalyzer(proximity_threshold_km=5.0)
```

### Export Results
All results are saved as JSON for further analysis:
```python
import json
with open('analysis/proximity_analysis_results.json', 'r') as f:
    results = json.load(f)
    
# Access proximity events
events = results['proximity_events']
```

## Scientific Applications

### 🔬 **Research Questions This Tool Can Help Answer**
- Do vultures share feeding sites?
- Are there preferred communal roosting locations?
- How do flight paths intersect throughout the day?
- Do vultures follow each other to food sources?
- Are there territorial boundaries between individuals?
- How does proximity behavior change seasonally?

### 📋 **Recommended Analysis Workflow**
1. **Run basic analysis** with 2km threshold
2. **Examine hotspots** for potential feeding/roosting sites
3. **Analyze temporal patterns** for behavioral insights
4. **Adjust thresholds** for detailed analysis (0.5km for feeding, 5km for regional)
5. **Cross-reference with field observations** of carcass locations
6. **Seasonal comparison** with multi-month datasets

This tool provides a powerful foundation for vulture behavioral ecology research!

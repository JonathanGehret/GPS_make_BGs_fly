# 🦅 Bearded Vulture GPS Flight Path Visualization

A comprehensive Python toolkit for visualizing GPS flight paths of bearded vultures with real-world mapping, advanced behavioral analysis, and professional-grade performance optimization.

## 🌟 Features

### 🗺️ Interactive Visualizations
- **Live Map Integration**: Real-time OpenStreetMap tiles with authentic geographic context
- **Flight Path Animation**: Smooth animated tracking of vulture movements over time
- **Multi-Vulture Support**: Simultaneous visualization of multiple birds with color coding
- **Real Geographic Data**: Königssee, Berchtesgaden National Park coordinates

### ⚡ Performance Optimization
- **Configurable Time Steps**: Choose from 1 second to 60 minutes for optimal performance
- **Smart Data Filtering**: Intelligent reduction for older computers (e.g., 80 → 31 points)
- **Mobile Optimization**: Touch-friendly controls and responsive design

### 🔍 Advanced Analysis
- **Proximity Detection**: Identify when vultures are in close proximity
- **Behavioral Analysis**: Statistical analysis of flight patterns
- **Multiple Export Formats**: JSON, CSV, and HTML visualizations
- **Comprehensive Reports**: Timeline, map, and dashboard views

### 🛠️ Professional Architecture
- **Type Safety**: Full type hints throughout codebase
- **Error Handling**: Comprehensive error management and logging
- **Modular Design**: Clean separation of concerns with `gps_utils.py`
- **Best Practices**: Following Python coding standards and conventions

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Professional Scripts

#### 🖥️ Desktop Version (Recommended)
```bash
python3 scripts/animate_live_map_professional.py
```
**Features:**
- Guided workflow with performance optimization
- Interactive map with real-time tile loading
- Professional data processing with type safety
- Configurable time-step filtering (1s to 60m)
- Responsive design for all screen sizes

#### 📱 Mobile Version
```bash
python3 scripts/animate_mobile_map_professional.py
```
**Features:**
- Touch-friendly controls and larger markers
- Mobile-optimized interface and performance
- Landscape mode support with pinch-to-zoom
- Compact design for smaller screens

#### 🔍 Advanced Analysis
```bash
python3 scripts/proximity_analysis_professional.py
```
**Features:**
- Behavioral analysis and proximity detection
- Statistical analysis with comprehensive exports
- Multiple visualization types (timeline, map, dashboard)
- JSON and CSV exports for further analysis

## CSV Data Format
To use your own GPS data, place CSV files in the `data/` folder with this format:
```
Timestamp [UTC];Longitude;Latitude;Height;display
15.06.2024 08:00:00;13.046297834691827;47.128937182739124;2000;1
15.06.2024 08:02:00;13.047123456789012;47.129876543210987;2050;1
```
- Separator: semicolon (;)
- Timestamp format: DD.MM.YYYY HH:mm:ss
- Longitude/Latitude: decimal degrees (high precision)
- Height: meters above sea level
- display: always 1

Example files: `data/test_vulture_01.csv`, `data/test_vulture_02.csv`## Next Steps
- Animated 2D flight paths (video format)
- Animated 3D flight paths (interactive web format)

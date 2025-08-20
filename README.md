# 🦅 Bearded Vulture GPS Flight Path Visualization

A comprehensive Python toolkit for visualizing GPS flight paths of bearded vultures with real-world mapping, advanced behavioral analysis, and professional-grade performance optimization.

## 🌟 Features

### 🗺️ Interactive Visualizations
- **Live Map Integration**: Real-time OpenStreetMap tiles with MapLibre GL JS (modern successor to Mapbox)
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

## 📊 CSV Data Format

To use your own GPS data, place CSV files in the `data/` folder with this format:

```csv
Timestamp [UTC];Longitude;Latitude;Height;display
15.06.2024 08:00:00;13.046297834691827;47.128937182739124;2000;1
15.06.2024 08:02:00;13.047123456789012;47.129876543210987;2050;1
```

**Format Requirements:**
- **Separator**: Semicolon (`;`)
- **Timestamp**: `DD.MM.YYYY HH:mm:ss` format in UTC
- **Coordinates**: Decimal degrees with high precision
- **Height**: Meters above sea level
- **Display**: Always `1` (legacy field)

**Example Files:** 
- `data/test_vulture_01.csv` (50 GPS points)
- `data/test_vulture_02.csv` (30 GPS points)

## 🏗️ Project Structure

```
GPS_make_BGs_fly/
├── data/                          # GPS datasets
│   ├── test_vulture_01.csv       # Sample data for vulture 1
│   └── test_vulture_02.csv       # Sample data for vulture 2
├── scripts/                       # Professional scripts
│   ├── gps_utils.py              # Core utilities module
│   ├── animate_live_map_professional.py    # Desktop visualization
│   ├── animate_mobile_map_professional.py  # Mobile optimization
│   └── proximity_analysis_professional.py  # Behavioral analysis
├── old_scripts/                   # Legacy scripts (archived)
├── visualizations/                # Generated outputs
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Technical Details

### Dependencies
- **Python 3.8+** with modern async/await support
- **Plotly 6.3.0+** for interactive visualizations with MapLibre GL JS
- **Pandas** for data processing
- **NumPy** for numerical computations
- **Requests** for live map tile loading
- **Scikit-learn** for proximity clustering
- **Pillow** for image processing

### Core Architecture
- **`gps_utils.py`**: Shared functionality with professional class design
  - `DataLoader`: CSV processing with validation
  - `PerformanceOptimizer`: Time-step filtering system
  - `VisualizationHelper`: UI and display utilities
  - Type hints and comprehensive error handling

### Performance Optimization
The system includes intelligent performance optimization:

- **Time-Step Filtering**: Reduce data points while preserving flight pattern
- **Smart Estimation**: Interpolate between filtered points for accuracy
- **Performance Indicators**: 🚀 (fast) to 🔥 (ultra-fast) loading
- **Configurable Thresholds**: Adapt to different hardware capabilities

**Example Performance Gains:**
- Original: 80 data points
- 5-minute filter: 31 points (61% reduction)
- 10-minute filter: 18 points (77% reduction)

## 🎯 Use Cases

### Research Applications
- **Migration Tracking**: Long-term vulture movement patterns
- **Territory Analysis**: Understanding habitat preferences
- **Behavioral Studies**: Social interactions and proximity events
- **Conservation Planning**: Identifying critical flight corridors

### Educational Use
- **Interactive Learning**: Engaging wildlife education tools
- **Data Visualization**: Teaching GPS data analysis techniques
- **Geographic Awareness**: Real-world coordinate understanding

### Technical Applications
- **Performance Benchmarking**: Optimize for different hardware
- **Mobile Development**: Touch-friendly interface design
- **Data Processing**: Large-scale GPS dataset handling

## 🛠️ Development Notes

### Code Quality Standards
- **Type Hints**: Full typing for better IDE support and error detection
- **Error Handling**: Comprehensive exception management
- **Logging**: Professional logging for debugging and monitoring
- **Documentation**: Extensive inline documentation and docstrings

### Legacy Code
Historical scripts have been moved to `old_scripts/` folder:
- Basic plotting scripts (`plot_2d.py`, `plot_3d.py`)
- Early animation attempts (`animate_2d.py`, `animate_3d_fast.py`)
- Previous optimization versions

See `old_scripts/README.md` for migration guidance.

## 🐛 Troubleshooting

### Common Issues

**Invisible Flight Paths**: If vultures and flight paths don't appear:
- Ensure you're using the professional scripts
- Check that CSV data files are in the correct format
- See `VISUALIZATION_FIXES.md` for technical details

**Performance Issues**: For slow loading on older computers:
- Use larger time steps (10m, 20m, or 60m)
- Try the mobile version for lighter resource usage
- Check available memory and processing power

**Data Loading Errors**: If CSV files won't load:
- Verify semicolon separation and UTF-8 encoding
- Check timestamp format: `DD.MM.YYYY HH:mm:ss`
- Ensure coordinate precision is sufficient

## 🤝 Contributing

This project uses professional Python development practices:
- Follow PEP 8 style guidelines
- Include type hints for all functions
- Add comprehensive error handling
- Write descriptive docstrings
- Test with sample data before submitting

## 📄 License

Open source project for educational and research purposes.

## 🙏 Acknowledgments

- **Bearded Vulture Research**: Real-world GPS tracking data
- **OpenStreetMap**: High-quality geographic map tiles
- **Plotly Community**: Excellent visualization framework
- **Python Ecosystem**: Robust scientific computing libraries

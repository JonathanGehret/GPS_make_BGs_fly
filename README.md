# 🦅 GPS Bearded Vulture Flight Analysis

Professional GPS proximity analysis and visualization system for bearded vulture research. This is the **clean, optimized version** with enhanced legends, bird names in filenames, and comprehensive bilingual support.

## 🌟 Features

- **📊 Proximity Analysis**: Detect when vultures come close to each other
- **🎬 Interactive Animations**: Live map animations with enhanced legends and bird names
- **🌐 Bilingual GUI**: German/English interface with German as default
- **📱 Mobile Optimized**: Touch-friendly visualizations for field work
- **🏔️ 3D Terrain**: Real elevation data for accurate flight path analysis
- **📈 Statistical Reports**: Comprehensive analysis with professional visualizations
- **🏷️ Enhanced Output**: Bird names in filenames and comprehensive legend displays

## 🚀 Quick Start

### For Non-Technical Users (German Interface)
1. **Double-click `launch_gui.py`** to start the GUI application
2. **Select your GPS data folder** in the Data tab
3. **Configure analysis parameters** in the Analysis tab  
4. **Enable animations** for encounter mapping (optional)
5. **Run analysis** and view results

### For Technical Users
```bash
# Install minimal required dependencies
pip install -r requirements.txt

# Run proximity analysis
python3 scripts/proximity_analysis.py

# Launch bilingual GUI application  
python3 scripts/proximity_analysis_gui.py
```

## 📦 Dependencies

**Minimal requirements** for optimal performance:
- **pandas**: Data processing and analysis
- **numpy**: Numerical computations  
- **plotly**: Interactive visualizations with MapLibre GL JS
- **requests**: Elevation data fetching
- **tkinter**: GUI interface (included with Python)

*All unnecessary dependencies removed for cleaner installation.*

## 📁 Project Structure

```
GPS_make_BGs_fly/
├── launch_gui.py                    # GUI launcher
├── VultureProximityAnalysis.desktop # Desktop shortcut
├── scripts/
│   ├── proximity_analysis.py        # Core analysis engine
│   ├── proximity_analysis_gui.py    # Bilingual GUI application
│   ├── animate_live_map.py          # Interactive map animations
│   ├── mobile_animation.py          # Mobile-optimized animations
│   ├── i18n.py                      # German/English translations
│   ├── core/                        # Core analysis engines
│   ├── utils/                       # Utility functions
│   └── visualization/               # Visualization components
├── data/                            # Place GPS CSV files here
├── visualizations/                  # Generated maps and animations
└── analysis/                        # Analysis results and reports
```

## 📊 Data Format

Your GPS CSV files should contain:
- **Timestamp**: Date/time in UTC
- **Latitude**: Decimal degrees  
- **Longitude**: Decimal degrees
- **Vulture ID**: Identifier for each individual
- **Altitude/Height**: Optional elevation data

## 🎯 Analysis Types

### 📍 Proximity Detection
- Configurable distance thresholds
- Time-based filtering
- Statistical analysis of encounters

### 🎬 Encounter Animations  
- Interactive map visualizations
- Trail effects showing flight paths
- Mobile-optimized versions

### 📊 Visualization Options
- 2D interactive maps with OpenStreetMap
- 3D terrain visualizations with real elevation
- Statistical dashboards and timelines
- Mobile-friendly touch interfaces

## 🌐 Language Support

- **Default**: German interface for German-speaking colleagues
- **Alternative**: English for international collaboration
- **Switching**: Click "🌐 Language/Sprache" at top-right
- **Persistence**: Language choice remembered

## 🧹 Project Maintenance

### Keeping the Project Clean
This project has been optimized and cleaned of deprecated files. To prevent VS Code or other editors from recreating unwanted files:

- **✅ Enhanced `.gitignore`**: Prevents restoration of deprecated scripts
- **✅ Modular Architecture**: Only essential files remain
- **✅ Protected File Patterns**: Auto-generated files are ignored
- **⚠️ VS Code Settings**: Disable auto-recovery features if files keep reappearing

### If Unwanted Files Reappear:
```bash
# Quick cleanup of deprecated patterns
find scripts/ -name "*_professional.py" -delete
find scripts/ -name "*_optimized.py" -delete  
find scripts/ -name "animate_2d.py" -delete
find scripts/ -name "plot_*.py" -delete
```

## 🆘 Support

For detailed documentation:
- **GUI Guide**: `README_GUI.md` (English) / `README_GUI_DE.md` (German)
- **Documentation**: `docs/` folder
- **Examples**: Check `data/` folder for sample datasets

## 📜 License

Research use - GPS tracking data analysis for bearded vulture conservation.

---

🦅 **Professional GPS analysis for vulture research** - Making proximity analysis accessible to researchers worldwide.

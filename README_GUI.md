# 🦅 Vulture Proximity Analysis - GUI Edition

## Professional Graphical Interface for GPS Proximity Analysis

This GUI application makes vulture GPS proximity analysis accessible to non-technical users through an intuitive graphical interface.

## 🚀 Quick Start

### Method 1: Double-click Launch (Easiest)
1. Double-click `launch_gui.py` to start the application
2. The GUI will open automatically

### Method 2: Command Line
```bash
python3 scripts/proximity_analysis_gui.py
```

### Method 3: Desktop Shortcut (Linux)
1. Copy `VultureProximityAnalysis.desktop` to your desktop
2. Right-click and select "Allow Launching" or make it executable
3. Double-click to launch

## 📋 User Guide

### 1. Data Tab - 📁
- **Select GPS Data Folder**: Browse to your folder containing CSV files
- **Data Preview**: Shows detected CSV files and GPS point counts
- **Automatic Validation**: Checks for data issues and displays warnings

### 2. Analysis Tab - ⚙️
- **Proximity Threshold**: Distance in km for vultures to be considered "close"
  - Slider range: 0.1km to 10km
  - Recommended: 2-5km for vultures
- **Time Threshold**: Minimum duration for proximity events
  - Range: 1-60 minutes
  - Recommended: 5-15 minutes
- **Enable Animations**: Check to create interactive encounter maps

### 3. Animation Tab - 🎬 (when enabled)
- **Time Buffer**: GPS data hours before/after encounters (0.5-12 hours)
- **Trail Length**: How long flight paths stay visible (0.1-6 hours)
- **Time Step**: Animation quality vs. speed
  - Ultra-smooth: 1s-30s (slower processing)
  - Balanced: 1m-5m (recommended)
  - Fast: 10m-1h (quick processing)
- **Limit Encounters**: Process only first N encounters for testing

### 4. Results Tab - 📊
- **Analysis Summary**: Key statistics and findings
- **Generated Files**: List of output files with direct access
- **File Actions**: Open files or show in folder

### 5. Log Tab - 📝
- **Real-time Progress**: Monitor analysis as it runs
- **Error Messages**: Troubleshooting information
- **Save Log**: Export log for sharing or debugging

## 🎯 Features

### ✅ User-Friendly Interface
- **Tabbed Layout**: Organized workflow from data to results
- **Visual Feedback**: Progress bars, status updates, and color-coded messages
- **Intuitive Controls**: Sliders, dropdowns, and checkboxes
- **Real-time Validation**: Immediate feedback on settings and data

### ✅ Professional Analysis
- **Complete Proximity Detection**: Identifies when vultures are close
- **Statistical Analysis**: Comprehensive metrics and summaries
- **Interactive Visualizations**: Maps, timelines, and dashboards
- **Encounter Animations**: Professional animated maps showing interactions

### ✅ Performance & Reliability
- **Threaded Processing**: GUI remains responsive during analysis
- **Progress Monitoring**: Real-time updates and logging
- **Error Handling**: Graceful recovery from issues
- **Interrupt Support**: Stop long-running analyses safely

### ✅ Output Management
- **Multiple Formats**: HTML maps, CSV data, interactive dashboards
- **Organized Storage**: Results saved in visualizations/ folder
- **Direct Access**: Open files from within the application
- **Export Options**: Save logs and share results easily

## 📁 File Structure

```
GPS_make_BGs_fly/
├── launch_gui.py                    # Easy launcher
├── VultureProximityAnalysis.desktop # Desktop shortcut
├── scripts/
│   ├── proximity_analysis_gui.py    # Main GUI application
│   └── proximity_analysis.py        # Core analysis engine
├── data/                            # Place your GPS CSV files here
├── visualizations/                  # Generated maps and charts
└── analysis/                        # Analysis results and data
```

## 🔧 Requirements

### System Requirements
- **Python 3.7+** with tkinter (usually included)
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 2GB RAM minimum (4GB+ for large datasets)
- **Storage**: 100MB for application + space for results

### Python Dependencies
All required packages are included in the project:
- pandas (data processing)
- plotly (interactive visualizations) 
- tkinter (GUI framework - included with Python)

## 📊 Data Format

### Expected CSV Format
Your GPS data files should contain columns such as:
- **Timestamp**: Date/time in UTC
- **Latitude**: Decimal degrees
- **Longitude**: Decimal degrees
- **Vulture ID**: Identifier for each individual
- **Altitude/Height**: Optional elevation data

### Supported Variations
The application automatically handles common column name variations:
- `TIMESTAMP`, `TIME`, `Timestamp [UTC]`
- `LAT`, `LATITUDE`, `Latitude`
- `LON`, `LONGITUDE`, `Longitude`
- `VULTURE_ID`, `vulture_id`, etc.

## 🎯 Usage Tips

### For Small Datasets (< 1 week, < 3 individuals)
- Use default settings
- Enable animations with 1-2 minute time steps
- Trails: 1-2 hours

### For Medium Datasets (1-4 weeks, 3-5 individuals)
- Proximity threshold: 2-5km
- Enable animations with 5-10 minute time steps
- Trails: 2-4 hours
- Consider limiting encounters for initial testing

### For Large Datasets (> 1 month, > 5 individuals)
- Start with larger proximity thresholds (5-10km)
- Use 10-30 minute time steps for animations
- Trails: 2-6 hours
- Limit encounters to first 10-20 for performance

### Performance Optimization
- **Large datasets**: Use larger time steps and shorter trails
- **High quality**: Use smaller time steps but limit encounters
- **Testing**: Always limit encounters first, then increase
- **Memory**: Close other applications for very large datasets

## 🆘 Troubleshooting

### Common Issues

**"No CSV files found"**
- Check that CSV files are in the selected folder
- Ensure files have .csv extension
- Verify files contain GPS data

**"Analysis failed"**
- Check the Log tab for detailed error messages
- Ensure CSV files have proper column names
- Try with a smaller dataset first

**"GUI won't start"**
- Ensure Python 3.7+ is installed
- Check that tkinter is available: `python3 -c "import tkinter"`
- Try launching from command line for error messages

**"Animations taking too long"**
- Increase time step (e.g., from 1m to 10m)
- Reduce trail length
- Limit number of encounters
- Use a smaller time buffer

### Getting Help
1. Check the Log tab for detailed error messages
2. Try with the included test data first
3. Reduce dataset size for testing
4. Check that all required files are present

## 🎉 Success Indicators

When everything is working correctly, you should see:
- ✅ **Data Tab**: Shows CSV files and GPS point counts
- ✅ **Analysis**: Completes without errors in the log
- ✅ **Results**: Displays statistics and encounter summaries
- ✅ **Files**: Generated visualizations appear in the file list
- ✅ **Output**: HTML files open in your web browser

## 📈 Next Steps

After successful analysis:
1. **Review Results**: Check statistics and generated visualizations
2. **Explore Animations**: Open encounter animations in your browser
3. **Share Findings**: Export logs and results for collaboration
4. **Refine Analysis**: Adjust parameters and re-run as needed
5. **Archive Results**: Save important analyses with descriptive names

---

**🦅 Happy Analyzing!** The GUI makes professional vulture proximity analysis accessible to everyone.

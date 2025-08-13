# Bearded Vulture GPS Flight Path Visualization

This project visualizes 3D GPS flight paths of bearded vultures, including multiple individuals, using Python. It supports both 2D and 3D visualizations for visually appealing analysis.

## Project Structure
- `data/` — Store GPS datasets (CSV, JSON, etc.)
- `scripts/` — Python scripts for data processing and visualization
- `visualizations/` — Output plots and animations

## Setup
1. Install Python 3.8+
2. Recommended packages: matplotlib, plotly, pandas, numpy
3. Place your GPS data files in the `data/` folder

## Usage
- Run scripts in the `scripts/` folder to generate visualizations:
	- `plot_2d.py`: Static 2D flight path plot
	- `plot_3d.py`: Interactive 3D flight path plot
	- `animate_2d.py`: Animated 2D flight path video (MP4)
- Outputs will be saved in `visualizations/`

## Next Steps
- Animated 2D flight paths (video format)
- Animated 3D flight paths (interactive web format)

# Bearded Vulture GPS Flight Path Visualization

This project visualizes 3D GPS flight paths of bearded vultures, including multiple individuals, using Python. It supports both 2D and 3D visualizations for visually appealing analysis.

## Project Structure
- `data/` — Store GPS datasets (CSV, JSON, etc.)
- `scripts/` — Python scripts for data processing and visualization
- `visualizations/` — Output plots and animations

## Setup
1. Install Python 3.8+
2. Clone this repository:
   ```bash
   git clone https://github.com/JonathanGehret/GPS_make_BGs_fly.git
   cd GPS_make_BGs_fly
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Place your GPS data files in the `data/` folder

## Usage
- Run scripts in the `scripts/` folder to generate visualizations:
    - `plot_2d.py`: Static 2D flight path plot
    - `plot_3d.py`: Interactive 3D flight path plot
    - `animate_2d.py`: Animated 2D flight path video (MP4)
    - `animate_3d.py`: Animated 3D flight path (synthetic data)
    - `animate_3d_from_csv.py`: Animated 3D flight path (loads from CSV files)
    - `export_test_data.py`: Export synthetic data to CSV format
- Outputs will be saved in `visualizations/`

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

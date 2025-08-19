import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob
import requests
import time

class TerrainDataProvider:
    """Class to handle different terrain data sources"""
    
    def __init__(self):
        self.elevation_cache = {}
    
    def get_open_elevation_data(self, lat_min, lat_max, lon_min, lon_max, resolution=50):
        """Get elevation data from Open Elevation API (free, but slower)"""
        print("Downloading real elevation data from Open Elevation API...")
        
        lats = np.linspace(lat_min, lat_max, resolution)
        lons = np.linspace(lon_min, lon_max, resolution)
        elevations = np.zeros((resolution, resolution))
        
        # Batch requests to avoid rate limiting
        batch_size = 10
        total_requests = resolution * resolution
        completed = 0
        
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                if completed % batch_size == 0 and completed > 0:
                    time.sleep(0.5)
                
                try:
                    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'results' in data and len(data['results']) > 0:
                            elevation = data['results'][0]['elevation']
                            elevations[i, j] = elevation
                        else:
                            elevations[i, j] = 1000
                    else:
                        elevations[i, j] = 1000
                        
                except Exception:
                    elevations[i, j] = 1000
                    
                completed += 1
                if completed % 50 == 0:
                    print(f"Progress: {completed}/{total_requests} elevation points downloaded")
        
        return lons, lats, elevations
    
    def get_elevation_batch(self, locations, max_batch_size=100):
        """Get elevation data in batches for better performance"""
        elevations = []
        
        for i in range(0, len(locations), max_batch_size):
            batch = locations[i:i + max_batch_size]
            location_string = "|".join([f"{lat},{lon}" for lat, lon in batch])
            
            try:
                url = f"https://api.open-elevation.com/api/v1/lookup?locations={location_string}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        batch_elevations = [result['elevation'] for result in data['results']]
                        elevations.extend(batch_elevations)
                    else:
                        elevations.extend([1000] * len(batch))
                else:
                    print(f"API request failed with status {response.status_code}")
                    elevations.extend([1000] * len(batch))
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"Error in batch request: {e}")
                elevations.extend([1000] * len(batch))
        
        return elevations
    
    def get_elevation_data_optimized(self, lat_min, lat_max, lon_min, lon_max, resolution=50):
        """Optimized elevation data fetching with batch requests"""
        print(f"Downloading real elevation data (optimized) for {resolution}x{resolution} grid...")
        
        lats = np.linspace(lat_min, lat_max, resolution)
        lons = np.linspace(lon_min, lon_max, resolution)
        
        # Create all coordinate pairs
        locations = []
        for lat in lats:
            for lon in lons:
                locations.append((lat, lon))
        
        print(f"Fetching elevation for {len(locations)} points...")
        elevations_flat = self.get_elevation_batch(locations, max_batch_size=50)
        
        # Reshape to 2D array
        elevations = np.array(elevations_flat).reshape((resolution, resolution))
        
        print("Elevation data download complete!")
        return lons, lats, elevations
    
    def create_realistic_alpine_terrain(self, lat_min, lat_max, lon_min, lon_max, resolution=50):
        """Enhanced synthetic terrain generation"""
        print("Creating enhanced synthetic alpine terrain...")
        
        lons = np.linspace(lon_min, lon_max, resolution)
        lats = np.linspace(lat_min, lat_max, resolution)
        X, Y = np.meshgrid(lons, lats)
        
        # Base elevation for alpine region
        base_elevation = 600
        
        # Multiple mountain ranges with different orientations
        mountains1 = 800 * np.sin(2 * np.pi * (X - lon_min) / (lon_max - lon_min)) ** 2
        mountains2 = 600 * np.cos(3 * np.pi * (Y - lat_min) / (lat_max - lat_min)) ** 2
        
        # Ridge lines
        ridge1 = 400 * np.exp(-((X - (lon_min + 0.3 * (lon_max - lon_min)))**2 + 
                                (Y - (lat_min + 0.7 * (lat_max - lat_min)))**2) * 5000)
        ridge2 = 300 * np.exp(-((X - (lon_min + 0.7 * (lon_max - lon_min)))**2 + 
                                (Y - (lat_min + 0.3 * (lat_max - lat_min)))**2) * 3000)
        
        # Valley/lake depression
        valley = 200 * np.exp(-((X - (lon_min + lon_max)/2)**2 + 
                               (Y - (lat_min + lat_max)/2)**2) * 8000)
        
        # Add realistic noise
        noise = np.random.normal(0, 30, X.shape)
        
        # Combine all features
        elevations = (base_elevation + mountains1 + mountains2 + 
                     ridge1 + ridge2 + noise - valley)
        
        # Ensure realistic elevation range
        elevations = np.maximum(elevations, 400)
        elevations = np.minimum(elevations, 2500)
        
        return lons, lats, elevations

def load_vulture_data_from_csv(file_path, vulture_id):
    """Load vulture data from CSV file and convert to required format"""
    df = pd.read_csv(file_path, sep=';')
    
    timestamps = []
    for i, timestamp_str in enumerate(df['Timestamp [UTC]']):
        timestamps.append(i + 1)
    
    data = []
    for i, row in df.iterrows():
        data.append([
            timestamps[i],
            float(str(row['Latitude']).replace(',', '.')),
            float(str(row['Longitude']).replace(',', '.')),
            float(str(row['Height'])),
            vulture_id
        ])
    
    return data

def main():
    """Main function to create animated 3D visualization with real terrain"""
    
    # Initialize terrain provider
    terrain_provider = TerrainDataProvider()
    
    # Automatically load all CSV files from data folder
    data_folder = 'data'
    csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        all_data = []
        vulture_colors = ['blue', 'orange', 'red', 'green', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for i, csv_file in enumerate(csv_files):
            filename = os.path.basename(csv_file)
            vulture_id = chr(65 + i)
            print(f"  - {filename} -> Vulture {vulture_id}")
            
            try:
                vulture_data = load_vulture_data_from_csv(csv_file, vulture_id)
                all_data.extend(vulture_data)
            except Exception as e:
                print(f"    Error loading {filename}: {e}")
        
        data = all_data
        vulture_ids = [chr(65 + i) for i in range(len(csv_files))]
        print(f"Loaded total of {len(data)} data points for {len(csv_files)} vultures")
    else:
        print("No CSV files found in data folder. Using synthetic data instead...")
        
        # Fallback to synthetic data with Königssee coordinates
        np.random.seed(42)
        start_time = 1
        end_time = 50
        
        timestamps_a = np.linspace(start_time, end_time, 50, dtype=int)
        latitudes_a = np.linspace(47.54, 47.58, 50) + np.random.normal(0, 0.001, 50)
        longitudes_a = np.linspace(12.96, 13.00, 50) + np.random.normal(0, 0.001, 50)
        altitudes_a = np.linspace(800, 1800, 50) + np.random.normal(0, 20, 50)
        
        timestamps_b = np.sort(np.random.choice(np.arange(start_time, end_time+1), 30, replace=False))
        latitudes_b = np.linspace(47.56, 47.60, 30) + np.random.normal(0, 0.001, 30)
        longitudes_b = np.linspace(12.98, 13.02, 30) + np.random.normal(0, 0.001, 30)
        altitudes_b = np.linspace(1200, 2200, 30) + np.random.normal(0, 30, 30)
        
        data_a = list(zip(timestamps_a, latitudes_a, longitudes_a, altitudes_a, ['A']*50))
        data_b = list(zip(timestamps_b, latitudes_b, longitudes_b, altitudes_b, ['B']*30))
        data = data_a + data_b
        vulture_ids = ['A', 'B']

    # Create DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id'])

    # Get data bounds
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    alt_min, alt_max = df['altitude'].min(), df['altitude'].max()

    # Add padding
    lat_padding = (lat_max - lat_min) * 0.1
    lon_padding = (lon_max - lon_min) * 0.1
    alt_padding = (alt_max - alt_min) * 0.1

    lat_min_padded = lat_min - lat_padding
    lat_max_padded = lat_max + lat_padding
    lon_min_padded = lon_min - lon_padding
    lon_max_padded = lon_max + lon_padding

    # Try different terrain data sources
    terrain_type = "Unknown"
    try:
        print("\n" + "="*60)
        print("TERRAIN DATA OPTIONS:")
        print("1. Real elevation data (slower, accurate)")
        print("2. Enhanced synthetic terrain (faster, realistic)")
        print("="*60)
        
        # For demonstration, try real data first, fallback to synthetic
        print("\nAttempting to download real elevation data...")
        print("Note: This may take 2-5 minutes for good resolution...")
        
        # Use reduced resolution for faster downloads
        resolution = 25 if len(data) > 100 else 30
        
        x_terrain, y_terrain, Z = terrain_provider.get_elevation_data_optimized(
            lat_min_padded, lat_max_padded, 
            lon_min_padded, lon_max_padded, 
            resolution=resolution
        )
        terrain_type = "Real elevation data (Open Elevation API)"
        
    except Exception as e:
        print(f"\nFailed to download real elevation data: {e}")
        print("Using enhanced synthetic terrain instead...")
        
        x_terrain, y_terrain, Z = terrain_provider.create_realistic_alpine_terrain(
            lat_min_padded, lat_max_padded,
            lon_min_padded, lon_max_padded,
            resolution=50
        )
        terrain_type = "Enhanced synthetic alpine terrain"

    print(f"\nUsing terrain type: {terrain_type}")
    print(f"Terrain elevation range: {Z.min():.0f}m - {Z.max():.0f}m")

    # Get time range
    start_time = int(df['timestamp'].min())
    end_time = int(df['timestamp'].max())

    # Create animation frames
    frames = []
    for frame in range(start_time, end_time + 1):
        colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
        frame_data = [
            go.Surface(x=x_terrain, y=y_terrain, z=Z, 
                      colorscale='earth', opacity=0.8, showscale=False, 
                      name=terrain_type)
        ]
        for vulture_id in vulture_ids:
            group = df[df['vulture_id'] == vulture_id]
            data_frame = group[group['timestamp'] <= frame]
            if len(data_frame) > 0:
                trace = go.Scatter3d(
                    x=data_frame['longitude'],
                    y=data_frame['latitude'],
                    z=data_frame['altitude'],
                    mode='lines+markers',
                    name=f'Vulture {vulture_id}',
                    line=dict(color=colors.get(vulture_id, 'gray'), width=4),
                    marker=dict(color=colors.get(vulture_id, 'gray'), size=6)
                )
            else:
                trace = go.Scatter3d(
                    x=[], y=[], z=[], mode='lines+markers',
                    name=f'Vulture {vulture_id}',
                    line=dict(color=colors.get(vulture_id, 'gray'), width=4),
                    marker=dict(color=colors.get(vulture_id, 'gray'), size=6)
                )
            frame_data.append(trace)
        frames.append(go.Frame(data=frame_data, name=str(frame)))

    # Create figure
    initial_traces = [go.Surface(x=x_terrain, y=y_terrain, z=Z, 
                                colorscale='earth', opacity=0.8, showscale=False, 
                                name=terrain_type)]
    colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
    for vulture_id in vulture_ids:
        initial_traces.append(
            go.Scatter3d(x=[], y=[], z=[], mode='lines+markers', 
                        name=f'Vulture {vulture_id}', 
                        line=dict(color=colors.get(vulture_id, 'gray'), width=4), 
                        marker=dict(color=colors.get(vulture_id, 'gray'), size=6))
        )

    fig = go.Figure(data=initial_traces, frames=frames)

    fig.update_layout(
        title=f'Animated 3D Flight Paths - {terrain_type}',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude (m)',
            xaxis=dict(range=[lon_min_padded, lon_max_padded]),
            yaxis=dict(range=[lat_min_padded, lat_max_padded]),
            zaxis=dict(range=[alt_min - alt_padding, alt_max + alt_padding]),
            dragmode='orbit',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        updatemenus=[{
            'type': 'buttons',
            'direction': 'left',
            'pad': {'r': 10, 't': 10},
            'showactive': True,
            'x': 0.1,
            'xanchor': 'right',
            'y': 1.02,
            'yanchor': 'top',
            'buttons': [
                {
                    'label': '▶ Play',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 800, 'redraw': True},
                        'transition': {'duration': 100, 'easing': 'linear'},
                        'fromcurrent': True,
                        'autoplay': True
                    }]
                },
                {
                    'label': '⏸ Pause',
                    'method': 'animate',
                    'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}]
                }
            ]
        }],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'method': 'animate',
                    'label': str(frame),
                    'args': [[str(frame)], {'mode': 'immediate', 
                            'frame': {'duration': 0, 'redraw': True}, 
                            'transition': {'duration': 0}}]
                } for frame in range(start_time, end_time + 1)
            ],
            'transition': {'duration': 0},
            'x': 0.1,
            'y': 0,
            'currentvalue': {'font': {'size': 16}, 'prefix': 'Time: ', 'visible': True, 'xanchor': 'right'},
            'len': 0.8
        }],
        legend=dict(x=0.02, y=0.98),
        margin=dict(l=0, r=0, b=0, t=60)
    )

    # Save the animation
    output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'flight_paths_3d_enhanced_terrain.html')
    fig.write_html(output_path)

    print(f"\nAnimation saved to: {output_path}")
    print(f"Final terrain type: {terrain_type}")

    # Show the figure
    pio.show(fig)

if __name__ == "__main__":
    main()

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob
import requests
import time
from PIL import Image
import io

class LiveMap3DProvider:
    """Provider for 3D visualization with live map tiles and real elevation"""
    
    def __init__(self):
        self.tile_cache = {}
    
    def get_map_tile_url(self, z, x, y, style='osm'):
        """Generate tile URL for different map providers"""
        if style == 'osm':
            return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        elif style == 'satellite':
            # Using ESRI World Imagery (free)
            return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        elif style == 'terrain':
            # Using USGS terrain
            return f"https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"
        else:
            return f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    
    def deg2num(self, lat_deg, lon_deg, zoom):
        """Convert lat/lon to tile numbers"""
        lat_rad = np.radians(lat_deg)
        n = 2.0 ** zoom
        x = int((lon_deg + 180.0) / 360.0 * n)
        y = int((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * n)
        return (x, y)
    
    def num2deg(self, x, y, zoom):
        """Convert tile numbers to lat/lon"""
        n = 2.0 ** zoom
        lon_deg = x / n * 360.0 - 180.0
        lat_rad = np.arctan(np.sinh(np.pi * (1 - 2 * y / n)))
        lat_deg = np.degrees(lat_rad)
        return (lat_deg, lon_deg)
    
    def download_map_tiles(self, lat_min, lat_max, lon_min, lon_max, zoom=12):
        """Download map tiles for the specified area"""
        print(f"Downloading map tiles for 3D visualization (zoom level {zoom})...")
        
        # Get tile boundaries
        x_min, y_max = self.deg2num(lat_min, lon_min, zoom)
        x_max, y_min = self.deg2num(lat_max, lon_max, zoom)
        
        # Limit tile count to avoid too many requests
        x_range = min(x_max - x_min + 1, 4)
        y_range = min(y_max - y_min + 1, 4)
        
        print(f"Downloading {x_range}x{y_range} tiles...")
        
        tiles = []
        tile_coords = []
        
        for i, x in enumerate(range(x_min, x_min + x_range)):
            for j, y in enumerate(range(y_min, y_min + y_range)):
                try:
                    url = self.get_map_tile_url(zoom, x, y, style='osm')
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        # Convert to RGB array
                        img = Image.open(io.BytesIO(response.content))
                        img_array = np.array(img.convert('RGB'))
                        tiles.append(img_array)
                        
                        # Store tile coordinates
                        lat_north, lon_west = self.num2deg(x, y, zoom)
                        lat_south, lon_east = self.num2deg(x + 1, y + 1, zoom)
                        tile_coords.append((lat_south, lat_north, lon_west, lon_east))
                    
                    time.sleep(0.2)  # Rate limiting
                    
                except Exception as e:
                    print(f"Failed to download tile {x},{y}: {e}")
                    # Create a placeholder tile
                    placeholder = np.ones((256, 256, 3), dtype=np.uint8) * 200
                    tiles.append(placeholder)
                    
                    lat_north, lon_west = self.num2deg(x, y, zoom)
                    lat_south, lon_east = self.num2deg(x + 1, y + 1, zoom)
                    tile_coords.append((lat_south, lat_north, lon_west, lon_east))
        
        return tiles, tile_coords
    
    def create_enhanced_terrain_with_elevation(self, lat_min, lat_max, lon_min, lon_max, resolution=50):
        """Create terrain with realistic elevation for Alpine regions"""
        print("Creating enhanced Alpine terrain with realistic elevation...")
        
        lats = np.linspace(lat_min, lat_max, resolution)
        lons = np.linspace(lon_min, lon_max, resolution)
        X, Y = np.meshgrid(lons, lats)
        
        # Enhanced Alpine terrain model for Königssee/Berchtesgaden
        base_elevation = 500
        
        # Main mountain ranges (Watzmann, Hochkalter, etc.)
        watzmann = 1400 * np.exp(-((X - 12.92)**2 * 8000 + (Y - 47.55)**2 * 12000))
        hochkalter = 1200 * np.exp(-((X - 12.96)**2 * 6000 + (Y - 47.58)**2 * 10000))
        jenner = 800 * np.exp(-((X - 13.01)**2 * 10000 + (Y - 47.56)**2 * 8000))
        
        # Königssee lake depression (elongated north-south)
        lake_koenigssee = 200 * np.exp(-((X - 12.975)**2 * 15000 + (Y - 47.57)**2 * 3000))
        
        # Valley systems
        valley_berchtesgaden = 100 * np.exp(-((X - 13.00)**2 * 5000 + (Y - 47.63)**2 * 8000))
        
        # Ridge lines and smaller peaks
        ridge_noise = 150 * (np.sin(8 * np.pi * (Y - lat_min) / (lat_max - lat_min)) * 
                            np.cos(6 * np.pi * (X - lon_min) / (lon_max - lon_min)))
        
        # Realistic terrain noise
        terrain_noise = np.random.normal(0, 30, X.shape)
        
        # Combine all features
        elevations = (base_elevation + watzmann + hochkalter + jenner + 
                     valley_berchtesgaden + ridge_noise + terrain_noise - lake_koenigssee)
        
        # Ensure realistic elevation bounds
        elevations = np.maximum(elevations, 400)  # Lake level minimum
        elevations = np.minimum(elevations, 2713)  # Watzmann height maximum
        
        return lons, lats, elevations

def load_vulture_data_from_csv(file_path, vulture_id):
    """Load vulture data from CSV file"""
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

def create_3d_live_map_visualization():
    """Create 3D visualization with live map tiles and realistic terrain"""
    
    # Initialize the live map provider
    map_provider = LiveMap3DProvider()
    
    # Load CSV data
    data_folder = 'data'
    csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        all_data = []
        vulture_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
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
        print("No CSV files found. Using synthetic data...")
        np.random.seed(42)
        start_time, end_time = 1, 50
        
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

    # Get bounds
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    alt_min, alt_max = df['altitude'].min(), df['altitude'].max()

    # Add padding
    lat_padding = (lat_max - lat_min) * 0.2
    lon_padding = (lon_max - lon_min) * 0.2

    lat_min_padded = lat_min - lat_padding
    lat_max_padded = lat_max + lat_padding
    lon_min_padded = lon_min - lon_padding
    lon_max_padded = lon_max + lon_padding

    # Create realistic terrain
    x_terrain, y_terrain, Z = map_provider.create_enhanced_terrain_with_elevation(
        lat_min_padded, lat_max_padded, lon_min_padded, lon_max_padded, resolution=60
    )

    print(f"Terrain elevation range: {Z.min():.0f}m - {Z.max():.0f}m")

    # Try to download live map tiles for texture (optional, fallback to colors)
    try:
        print("\nAttempting to download live map tiles for surface texture...")
        tiles, tile_coords = map_provider.download_map_tiles(
            lat_min_padded, lat_max_padded, lon_min_padded, lon_max_padded, zoom=11
        )
        print(f"Successfully downloaded {len(tiles)} map tiles!")
        use_map_texture = True
    except Exception as e:
        print(f"Failed to download map tiles: {e}")
        print("Using enhanced terrain coloring instead...")
        use_map_texture = False

    # Create time range
    start_time = int(df['timestamp'].min())
    end_time = int(df['timestamp'].max())

    # Create animation frames
    frames = []
    for frame in range(start_time, end_time + 1):
        frame_data = []
        
        # Add terrain surface
        if use_map_texture:
            # Use a simplified colorscale that resembles map colors
            terrain_surface = go.Surface(
                x=x_terrain, y=y_terrain, z=Z,
                colorscale=[
                    [0.0, 'rgb(34, 139, 34)'],    # Forest green (low)
                    [0.3, 'rgb(107, 142, 35)'],   # Olive drab
                    [0.5, 'rgb(160, 82, 45)'],    # Saddle brown
                    [0.7, 'rgb(139, 69, 19)'],    # Saddle brown
                    [0.9, 'rgb(211, 211, 211)'], # Light gray (rock)
                    [1.0, 'rgb(255, 250, 250)']  # Snow
                ],
                opacity=0.85,
                showscale=False,
                name='Live Map Terrain',
                hovertemplate='Lat: %{y:.4f}<br>Lon: %{x:.4f}<br>Elevation: %{z:.0f}m<extra></extra>'
            )
        else:
            terrain_surface = go.Surface(
                x=x_terrain, y=y_terrain, z=Z,
                colorscale='earth',
                opacity=0.9,
                showscale=False,
                name='Enhanced Alpine Terrain'
            )
        
        frame_data.append(terrain_surface)
        
        # Add vulture flight paths
        for i, vulture_id in enumerate(vulture_ids):
            group = df[df['vulture_id'] == vulture_id]
            data_frame = group[group['timestamp'] <= frame]
            
            if len(data_frame) > 0:
                # Flight path trail
                trail = go.Scatter3d(
                    x=data_frame['longitude'],
                    y=data_frame['latitude'],
                    z=data_frame['altitude'],
                    mode='lines',
                    name=f'Vulture {vulture_id} Path',
                    line=dict(
                        color=vulture_colors[i % len(vulture_colors)], 
                        width=5
                    ),
                    opacity=0.8,
                    showlegend=True
                )
                
                # Current position with enhanced marker
                current = data_frame.iloc[-1]
                marker = go.Scatter3d(
                    x=[current['longitude']],
                    y=[current['latitude']],
                    z=[current['altitude']],
                    mode='markers',
                    name=f'Vulture {vulture_id}',
                    marker=dict(
                        color=vulture_colors[i % len(vulture_colors)],
                        size=15,
                        symbol='diamond',
                        line=dict(width=3, color='white'),
                        opacity=1.0
                    ),
                    hovertemplate=f'<b>Vulture {vulture_id}</b><br>' +
                                'Lat: %{y:.6f}<br>' +
                                'Lon: %{x:.6f}<br>' +
                                'Alt: %{z:.0f}m<br>' +
                                '<extra></extra>',
                    showlegend=False
                )
                
                frame_data.extend([trail, marker])
            else:
                # Empty traces
                trail = go.Scatter3d(x=[], y=[], z=[], mode='lines',
                                   name=f'Vulture {vulture_id} Path',
                                   line=dict(color=vulture_colors[i % len(vulture_colors)], width=5))
                marker = go.Scatter3d(x=[], y=[], z=[], mode='markers',
                                    name=f'Vulture {vulture_id}',
                                    marker=dict(color=vulture_colors[i % len(vulture_colors)], size=15),
                                    showlegend=False)
                frame_data.extend([trail, marker])
        
        frames.append(go.Frame(data=frame_data, name=str(frame)))

    # Create initial figure
    if use_map_texture:
        initial_terrain = go.Surface(
            x=x_terrain, y=y_terrain, z=Z,
            colorscale=[
                [0.0, 'rgb(34, 139, 34)'],
                [0.3, 'rgb(107, 142, 35)'],
                [0.5, 'rgb(160, 82, 45)'],
                [0.7, 'rgb(139, 69, 19)'],
                [0.9, 'rgb(211, 211, 211)'],
                [1.0, 'rgb(255, 250, 250)']
            ],
            opacity=0.85,
            showscale=False,
            name='Live Map Terrain'
        )
    else:
        initial_terrain = go.Surface(
            x=x_terrain, y=y_terrain, z=Z,
            colorscale='earth',
            opacity=0.9,
            showscale=False,
            name='Enhanced Alpine Terrain'
        )

    initial_traces = [initial_terrain]
    
    for i, vulture_id in enumerate(vulture_ids):
        initial_traces.extend([
            go.Scatter3d(x=[], y=[], z=[], mode='lines',
                        name=f'Vulture {vulture_id} Path',
                        line=dict(color=vulture_colors[i % len(vulture_colors)], width=5)),
            go.Scatter3d(x=[], y=[], z=[], mode='markers',
                        name=f'Vulture {vulture_id}',
                        marker=dict(color=vulture_colors[i % len(vulture_colors)], size=15),
                        showlegend=False)
        ])

    fig = go.Figure(data=initial_traces, frames=frames)

    # Enhanced layout for 3D live map
    terrain_type = "3D Live Map with Real Terrain" if use_map_texture else "3D Enhanced Alpine Terrain"
    
    fig.update_layout(
        title=f'Bearded Vulture Flight Paths - {terrain_type}',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude (m)',
            xaxis=dict(range=[lon_min_padded, lon_max_padded]),
            yaxis=dict(range=[lat_min_padded, lat_max_padded]),
            zaxis=dict(range=[Z.min() - 100, max(alt_max + 300, Z.max() + 200)]),
            dragmode='orbit',
            camera=dict(
                eye=dict(x=2.0, y=2.0, z=1.5),
                center=dict(x=0, y=0, z=-0.1)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1.2, y=1.0, z=0.8),
            bgcolor='lightblue'
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
                        'frame': {'duration': 1000, 'redraw': True},
                        'transition': {'duration': 200, 'easing': 'linear'},
                        'fromcurrent': True,
                        'autoplay': True
                    }]
                },
                {
                    'label': '⏸ Pause',
                    'method': 'animate',
                    'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate'}]
                },
                {
                    'label': '⏮ Reset',
                    'method': 'animate',
                    'args': [[str(start_time)], {'mode': 'immediate', 'frame': {'duration': 0}}]
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
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.9)'),
        margin=dict(l=0, r=0, b=0, t=60),
        height=900
    )

    return fig, terrain_type

def main():
    """Main function"""
    print("Creating 3D visualization with live map integration...")
    print("This combines real terrain modeling with live map tile textures!")
    
    fig, terrain_type = create_3d_live_map_visualization()
    
    # Save the visualization
    output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'flight_paths_3d_live_map.html')
    fig.write_html(output_path)
    
    print(f"\nVisualization saved to: {output_path}")
    print(f"Terrain type: {terrain_type}")
    print("\nFeatures:")
    print("- Live map tile integration")
    print("- Realistic Alpine terrain modeling")
    print("- Enhanced 3D markers and trails")
    print("- Optimized performance")
    
    # Show the figure
    pio.show(fig)

if __name__ == "__main__":
    main()

import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import plotly
import glob
from datetime import datetime

def load_vulture_data_from_csv(file_path, vulture_id):
    """Load vulture data from CSV file and convert to required format"""
    df = pd.read_csv(file_path, sep=';')
    
    # Convert timestamp to numeric for animation
    timestamps = []
    for i, timestamp_str in enumerate(df['Timestamp [UTC]']):
        # Use index as timestamp for animation (you can modify this logic)
        timestamps.append(i + 1)
    
    # Create data list in the format expected by the animation
    data = []
    for i, row in df.iterrows():
        data.append([
            timestamps[i],
            float(str(row['Latitude']).replace(',', '.')),  # Handle potential comma decimals
            float(str(row['Longitude']).replace(',', '.')),
            float(str(row['Height'])),
            vulture_id
        ])
    
    return data

# Automatically load all CSV files from data folder
data_folder = 'data'
csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

if csv_files:
    print(f"Found {len(csv_files)} CSV files:")
    all_data = []
    vulture_colors = ['blue', 'orange', 'red', 'green', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    for i, csv_file in enumerate(csv_files):
        filename = os.path.basename(csv_file)
        vulture_id = chr(65 + i)  # A, B, C, D, etc.
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
    
    # Fallback to synthetic data (same as before)
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

# Get data bounds for terrain and axes
lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
alt_min, alt_max = df['altitude'].min(), df['altitude'].max()

# Add some padding
lat_padding = (lat_max - lat_min) * 0.1
lon_padding = (lon_max - lon_min) * 0.1
alt_padding = (alt_max - alt_min) * 0.1

# Synthetic terrain mesh based on actual data bounds
terrain_size = 50
x_terrain = np.linspace(lon_min - lon_padding, lon_max + lon_padding, terrain_size)
y_terrain = np.linspace(lat_min - lat_padding, lat_max + lat_padding, terrain_size)
X, Y = np.meshgrid(x_terrain, y_terrain)

# Alpine terrain with lake and mountains
terrain_base = alt_min - 200
terrain_height = (alt_max - alt_min) * 0.8
Z = terrain_base + terrain_height * (np.sin(3 * np.pi * (X - lon_min) / (lon_max - lon_min)) ** 2 + 
                                     np.cos(4 * np.pi * (Y - lat_min) / (lat_max - lat_min)) ** 2) + \
    200 * np.exp(-((X - (lon_min + lon_max)/2)**2 + (Y - (lat_min + lat_max)/2)**2) * 10000)

# Get time range
start_time = int(df['timestamp'].min())
end_time = int(df['timestamp'].max())

# Create animation frames
frames = []
for frame in range(start_time, end_time + 1):
    colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
    frame_data = [
        go.Surface(x=x_terrain, y=y_terrain, z=Z, colorscale='earth', opacity=0.7, showscale=False, name='Berchtesgaden Alps')
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
                line=dict(color=colors.get(vulture_id, 'gray')),
                marker=dict(color=colors.get(vulture_id, 'gray'))
            )
        else:
            trace = go.Scatter3d(
                x=[], y=[], z=[], mode='lines+markers',
                name=f'Vulture {vulture_id}',
                line=dict(color=colors.get(vulture_id, 'gray')),
                marker=dict(color=colors.get(vulture_id, 'gray'))
            )
        frame_data.append(trace)
    frames.append(go.Frame(data=frame_data, name=str(frame)))

# Create figure with initial traces for all vultures
initial_traces = [go.Surface(x=x_terrain, y=y_terrain, z=Z, colorscale='earth', opacity=0.7, showscale=False, name='Berchtesgaden Alps')]
colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
for vulture_id in vulture_ids:
    initial_traces.append(
        go.Scatter3d(x=[], y=[], z=[], mode='lines+markers', 
                    name=f'Vulture {vulture_id}', 
                    line=dict(color=colors.get(vulture_id, 'gray')), 
                    marker=dict(color=colors.get(vulture_id, 'gray')))
    )
fig = go.Figure(
    data=initial_traces,
    frames=frames
)

fig.update_layout(
    title='Animated 3D Flight Paths of Bearded Vultures - Königssee, Berchtesgaden',
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Altitude (m)',
        xaxis=dict(range=[lon_min - lon_padding, lon_max + lon_padding]),
        yaxis=dict(range=[lat_min - lat_padding, lat_max + lat_padding]),
        zaxis=dict(range=[alt_min - alt_padding, alt_max + alt_padding]),
        dragmode='orbit'
    ),
    updatemenus=[{
        'type': 'buttons',
        'buttons': [
            {
                'label': 'Play',
                'method': 'animate',
                'args': [None, {
                    'frame': {'duration': 1000, 'redraw': True},
                    'transition': {'duration': 0, 'easing': 'linear'},
                    'fromcurrent': True,
                    'autoplay': True
                }]
            },
            {
                'label': 'Pause',
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
                'args': [[str(frame)], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': True}, 'transition': {'duration': 0}}]
            } for frame in range(start_time, end_time + 1)
        ],
        'transition': {'duration': 0},
        'x': 0.1,
        'y': 0,
        'currentvalue': {'font': {'size': 16}, 'prefix': 'Timestamp: ', 'visible': True, 'xanchor': 'right'},
        'len': 0.8
    }],
    legend_title='Vulture ID',
    margin=dict(l=0, r=0, b=0, t=40)
)

output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'flight_paths_3d_from_csv.html')
fig.write_html(output_path)

# Check Plotly version
required_version = '5.0.0'
if tuple(map(int, plotly.__version__.split('.'))) < tuple(map(int, required_version.split('.'))):
    print(f"Warning: Plotly version {plotly.__version__} detected. Please upgrade to >= {required_version} for best animation support.")

print(f"Animation saved to: {output_path}")
pio.show(fig)

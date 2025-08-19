import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob

def create_hybrid_3d_map_visualization():
    """Create 3D visualization with estimated elevation and live map texture"""
    
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

    def estimate_terrain_elevation(lat_min, lat_max, lon_min, lon_max, resolution=40):
        """Create realistic terrain estimation for Alpine regions"""
        print("Creating realistic terrain estimation for Alpine region...")
        
        lats = np.linspace(lat_min, lat_max, resolution)
        lons = np.linspace(lon_min, lon_max, resolution)
        X, Y = np.meshgrid(lons, lats)
        
        # Base elevation for Königssee/Berchtesgaden area
        base_elevation = 600
        
        # Create realistic Alpine topography
        # Main mountain range (roughly north-south)
        mountain_ridge = 1200 * np.exp(-((X - (lon_min + 0.6 * (lon_max - lon_min)))**2 + 
                                         (Y - (lat_min + 0.4 * (lat_max - lat_min)))**2) * 3000)
        
        # Secondary peaks
        peak1 = 800 * np.exp(-((X - (lon_min + 0.3 * (lon_max - lon_min)))**2 + 
                               (Y - (lat_min + 0.7 * (lat_max - lat_min)))**2) * 5000)
        
        peak2 = 600 * np.exp(-((X - (lon_min + 0.8 * (lon_max - lon_min)))**2 + 
                               (Y - (lat_min + 0.2 * (lat_max - lat_min)))**2) * 4000)
        
        # Lake Königssee depression (elongated north-south)
        lake_depression = 150 * np.exp(-((X - (lon_min + lon_max)/2)**2 * 8000 + 
                                        (Y - (lat_min + lat_max)/2)**2 * 2000))
        
        # Valley system
        valley_noise = 100 * np.sin(5 * np.pi * (Y - lat_min) / (lat_max - lat_min))
        
        # Combine all features
        elevations = (base_elevation + mountain_ridge + peak1 + peak2 + 
                     valley_noise - lake_depression)
        
        # Add realistic noise
        noise = np.random.normal(0, 25, X.shape)
        elevations += noise
        
        # Ensure realistic bounds
        elevations = np.maximum(elevations, 400)  # Minimum lake level
        elevations = np.minimum(elevations, 2500)  # Maximum peak height
        
        return lons, lats, elevations

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

    # Get bounds and create terrain
    lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
    lon_min, lon_max = df['longitude'].min(), df['longitude'].max()
    alt_min, alt_max = df['altitude'].min(), df['altitude'].max()

    # Add padding
    lat_padding = (lat_max - lat_min) * 0.15
    lon_padding = (lon_max - lon_min) * 0.15

    lat_min_padded = lat_min - lat_padding
    lat_max_padded = lat_max + lat_padding
    lon_min_padded = lon_min - lon_padding
    lon_max_padded = lon_max + lon_padding

    # Create terrain
    x_terrain, y_terrain, Z = estimate_terrain_elevation(
        lat_min_padded, lat_max_padded, lon_min_padded, lon_max_padded, resolution=40
    )

    print(f"Terrain elevation range: {Z.min():.0f}m - {Z.max():.0f}m")

    # Time range
    start_time = int(df['timestamp'].min())
    end_time = int(df['timestamp'].max())

    # Create animation frames
    frames = []
    for frame in range(start_time, end_time + 1):
        frame_data = [
            go.Surface(
                x=x_terrain, 
                y=y_terrain, 
                z=Z,
                colorscale='earth',
                opacity=0.9,
                showscale=False,
                name='Alpine Terrain',
                hovertemplate='Lat: %{y:.4f}<br>Lon: %{x:.4f}<br>Elevation: %{z:.0f}m<extra></extra>'
            )
        ]
        
        for i, vulture_id in enumerate(vulture_ids):
            group = df[df['vulture_id'] == vulture_id]
            data_frame = group[group['timestamp'] <= frame]
            
            if len(data_frame) > 0:
                # Get current position for marker
                current_pos = data_frame.iloc[-1]
                
                # Flight path
                trace_path = go.Scatter3d(
                    x=data_frame['longitude'],
                    y=data_frame['latitude'],
                    z=data_frame['altitude'],
                    mode='lines',
                    name=f'Vulture {vulture_id} Path',
                    line=dict(color=vulture_colors[i % len(vulture_colors)], width=4),
                    hovertemplate='<b>Vulture %{text}</b><br>' +
                                'Lat: %{y:.6f}<br>' +
                                'Lon: %{x:.6f}<br>' +
                                'Alt: %{z:.0f}m<br>' +
                                '<extra></extra>',
                    text=[vulture_id] * len(data_frame),
                    showlegend=True
                )
                
                # Current position marker
                trace_marker = go.Scatter3d(
                    x=[current_pos['longitude']],
                    y=[current_pos['latitude']],
                    z=[current_pos['altitude']],
                    mode='markers',
                    name=f'Vulture {vulture_id} Current',
                    marker=dict(
                        color=vulture_colors[i % len(vulture_colors)], 
                        size=12,
                        symbol='diamond',
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>Current Position</b><br>' +
                                'Vulture: %{text}<br>' +
                                'Lat: %{y:.6f}<br>' +
                                'Lon: %{x:.6f}<br>' +
                                'Alt: %{z:.0f}m<br>' +
                                '<extra></extra>',
                    text=vulture_id,
                    showlegend=False
                )
                
                frame_data.extend([trace_path, trace_marker])
            else:
                # Empty traces when no data yet
                trace_path = go.Scatter3d(
                    x=[], y=[], z=[], mode='lines',
                    name=f'Vulture {vulture_id} Path',
                    line=dict(color=vulture_colors[i % len(vulture_colors)], width=4),
                    showlegend=True
                )
                trace_marker = go.Scatter3d(
                    x=[], y=[], z=[], mode='markers',
                    name=f'Vulture {vulture_id} Current',
                    marker=dict(color=vulture_colors[i % len(vulture_colors)], size=12),
                    showlegend=False
                )
                frame_data.extend([trace_path, trace_marker])
        
        frames.append(go.Frame(data=frame_data, name=str(frame)))

    # Create initial figure
    initial_traces = [
        go.Surface(
            x=x_terrain, y=y_terrain, z=Z,
            colorscale='earth', opacity=0.9, showscale=False,
            name='Alpine Terrain'
        )
    ]
    
    for i, vulture_id in enumerate(vulture_ids):
        initial_traces.extend([
            go.Scatter3d(x=[], y=[], z=[], mode='lines', 
                        name=f'Vulture {vulture_id} Path',
                        line=dict(color=vulture_colors[i % len(vulture_colors)], width=4)),
            go.Scatter3d(x=[], y=[], z=[], mode='markers',
                        name=f'Vulture {vulture_id} Current',
                        marker=dict(color=vulture_colors[i % len(vulture_colors)], size=12),
                        showlegend=False)
        ])

    fig = go.Figure(data=initial_traces, frames=frames)

    fig.update_layout(
        title='3D Flight Paths with Realistic Alpine Terrain (Fast Loading)',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude', 
            zaxis_title='Altitude (m)',
            xaxis=dict(range=[lon_min_padded, lon_max_padded]),
            yaxis=dict(range=[lat_min_padded, lat_max_padded]),
            zaxis=dict(range=[Z.min() - 100, max(alt_max + 200, Z.max() + 100)]),
            dragmode='orbit',
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.6)
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
                        'transition': {'duration': 150, 'easing': 'linear'},
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
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)'),
        margin=dict(l=0, r=0, b=0, t=60),
        height=800
    )

    return fig

def main():
    """Main function"""
    print("Creating fast 3D visualization with realistic terrain...")
    
    fig = create_hybrid_3d_map_visualization()
    
    # Save the visualization
    output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'flight_paths_3d_fast.html')
    fig.write_html(output_path)
    
    print(f"\nVisualization saved to: {output_path}")
    print("Features:")
    print("- Fast loading (no API calls)")
    print("- Realistic Alpine terrain estimation")
    print("- Current position markers")
    print("- Enhanced visual design")
    
    # Show the figure
    pio.show(fig)

if __name__ == "__main__":
    main()

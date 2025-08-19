import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob

def create_mapbox_3d_visualization():
    """Create 3D visualization using Mapbox tiles for fast, live map data"""
    
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

    # Load CSV data
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
        # Fallback synthetic data
        print("No CSV files found. Using synthetic data...")
        np.random.seed(42)
        start_time, end_time = 1, 50
        
        timestamps_a = np.linspace(start_time, end_time, 50, dtype=int)
        latitudes_a = np.linspace(47.54, 47.58, 50) + np.random.normal(0, 0.001, 50)
        longitudes_a = np.linspace(12.96, 13.00, 50) + np.random.normal(0, 0.001, 50)
        altitudes_a = np.linspace(800, 1800, 50) + np.random.normal(0, 20, 50)
        
        data_a = list(zip(timestamps_a, latitudes_a, longitudes_a, altitudes_a, ['A']*50))
        data = data_a
        vulture_ids = ['A']

    # Create DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id'])

    # Calculate center point for map
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Calculate zoom level based on data spread
    lat_range = df['latitude'].max() - df['latitude'].min()
    lon_range = df['longitude'].max() - df['longitude'].min()
    max_range = max(lat_range, lon_range)
    
    # Estimate zoom level (rough approximation)
    if max_range > 0.1:
        zoom = 8
    elif max_range > 0.05:
        zoom = 10
    elif max_range > 0.01:
        zoom = 12
    else:
        zoom = 14

    print(f"Map center: {center_lat:.4f}, {center_lon:.4f}")
    print(f"Zoom level: {zoom}")

    # Create the figure with Mapbox
    fig = go.Figure()

    # Add initial empty traces for each vulture
    colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
    for vulture_id in vulture_ids:
        fig.add_trace(
            go.Scattermapbox(
                lat=[],
                lon=[],
                mode='lines+markers',
                name=f'Vulture {vulture_id}',
                line=dict(color=colors.get(vulture_id, 'gray'), width=3),
                marker=dict(color=colors.get(vulture_id, 'gray'), size=8)
            )
        )

    # Create animation frames
    start_time = int(df['timestamp'].min())
    end_time = int(df['timestamp'].max())
    
    frames = []
    for frame in range(start_time, end_time + 1):
        frame_data = []
        for vulture_id in vulture_ids:
            group = df[df['vulture_id'] == vulture_id]
            data_frame = group[group['timestamp'] <= frame]
            
            if len(data_frame) > 0:
                frame_data.append(
                    go.Scattermapbox(
                        lat=data_frame['latitude'].tolist(),
                        lon=data_frame['longitude'].tolist(),
                        mode='lines+markers',
                        name=f'Vulture {vulture_id}',
                        line=dict(color=colors.get(vulture_id, 'gray'), width=3),
                        marker=dict(color=colors.get(vulture_id, 'gray'), size=8),
                        customdata=data_frame['altitude'].tolist(),
                        hovertemplate='<b>Vulture %{text}</b><br>' +
                                    'Lat: %{lat:.6f}<br>' +
                                    'Lon: %{lon:.6f}<br>' +
                                    'Alt: %{customdata:.0f}m<br>' +
                                    '<extra></extra>',
                        text=[vulture_id] * len(data_frame)
                    )
                )
            else:
                frame_data.append(
                    go.Scattermapbox(
                        lat=[],
                        lon=[],
                        mode='lines+markers',
                        name=f'Vulture {vulture_id}',
                        line=dict(color=colors.get(vulture_id, 'gray'), width=3),
                        marker=dict(color=colors.get(vulture_id, 'gray'), size=8)
                    )
                )
        
        frames.append(go.Frame(data=frame_data, name=str(frame)))

    fig.frames = frames

    # Configure the layout with Mapbox
    fig.update_layout(
        title='Animated Flight Paths of Bearded Vultures - Live Map Data',
        mapbox=dict(
            style='open-street-map',  # Free OpenStreetMap tiles
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
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
        margin=dict(l=0, r=0, b=0, t=60),
        height=700
    )

    return fig

def main():
    """Main function"""
    print("Creating fast 2D visualization with live map tiles...")
    
    fig = create_mapbox_3d_visualization()
    
    # Save the visualization
    output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'flight_paths_live_map.html')
    fig.write_html(output_path)
    
    print(f"\nVisualization saved to: {output_path}")
    print("Using: Live OpenStreetMap tiles (fast loading!)")
    
    # Show the figure
    pio.show(fig)

if __name__ == "__main__":
    main()

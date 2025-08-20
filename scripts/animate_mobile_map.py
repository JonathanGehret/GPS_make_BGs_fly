import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import glob
from datetime import datetime

def create_mobile_optimized_map():
    """Create mobile-optimized 2D visualization with live map tiles"""
    
    def load_vulture_data_from_csv(file_path, vulture_id):
        """Load vulture data from CSV file with proper timestamp parsing"""
        df = pd.read_csv(file_path, sep=';')
        
        timestamps = []
        timestamp_strings = []
        
        for i, timestamp_str in enumerate(df['Timestamp [UTC]']):
            try:
                # Parse the timestamp (format: DD.MM.YYYY HH:mm:ss)
                dt = datetime.strptime(str(timestamp_str), '%d.%m.%Y %H:%M:%S')
                timestamps.append(i + 1)
                # Create compact time format for mobile
                timestamp_strings.append(dt.strftime('%d.%m %H:%M'))
            except Exception:
                timestamps.append(i + 1)
                timestamp_strings.append(f"Pt{i + 1}")
        
        data = []
        for i, row in df.iterrows():
            data.append([
                timestamps[i],
                float(str(row['Latitude']).replace(',', '.')),
                float(str(row['Longitude']).replace(',', '.')),
                float(str(row['Height'])),
                vulture_id,
                timestamp_strings[i]
            ])
        
        return data

    # Load CSV data
    data_folder = 'data'
    csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

    if csv_files:
        print(f"Found {len(csv_files)} CSV files:")
        all_data = []
        vulture_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
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
    else:
        print("No CSV files found. Using synthetic data...")
        # Synthetic data with compact timestamps
        np.random.seed(42)
        start_time, end_time = 1, 50
        
        timestamps_a = np.linspace(start_time, end_time, 50, dtype=int)
        latitudes_a = np.linspace(47.54, 47.58, 50) + np.random.normal(0, 0.001, 50)
        longitudes_a = np.linspace(12.96, 13.00, 50) + np.random.normal(0, 0.001, 50)
        altitudes_a = np.linspace(800, 1800, 50) + np.random.normal(0, 20, 50)
        timestamp_strings_a = [f"08:{i:02d}" for i in range(50)]
        
        data = list(zip(timestamps_a, latitudes_a, longitudes_a, altitudes_a, ['A']*50, timestamp_strings_a))
        vulture_ids = ['A']

    # Create DataFrame
    df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id', 'datetime_str'])

    # Calculate optimal map parameters for mobile
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    lat_range = df['latitude'].max() - df['latitude'].min()
    lon_range = df['longitude'].max() - df['longitude'].min()
    max_range = max(lat_range, lon_range)
    
    # Higher zoom for mobile (tighter focus)
    if max_range > 0.05:
        zoom = 12
    elif max_range > 0.01:
        zoom = 14
    else:
        zoom = 16

    print(f"Mobile-optimized map: Center {center_lat:.4f}, {center_lon:.4f}, Zoom {zoom}")

    # Create the figure
    fig = go.Figure()

    # Animation frames with mobile-optimized hover
    start_time = int(df['timestamp'].min())
    end_time = int(df['timestamp'].max())
    
    # Create datetime lookup for slider
    frame_datetime_lookup = {}
    for frame in range(start_time, end_time + 1):
        current_data = df[df['timestamp'] == frame]
        if len(current_data) > 0:
            frame_datetime_lookup[frame] = current_data.iloc[0]['datetime_str']
        else:
            frame_datetime_lookup[frame] = f"F{frame}"
    
    # Create frames
    colors = dict(zip(vulture_ids, vulture_colors[:len(vulture_ids)]))
    
    frames = []
    for frame in range(start_time, end_time + 1):
        frame_data = []
        for vulture_id in vulture_ids:
            group = df[df['vulture_id'] == vulture_id]
            data_frame = group[group['timestamp'] <= frame]
            
            if len(data_frame) > 0:
                # Mobile-friendly hover template
                hover_data = []
                for _, row in data_frame.iterrows():
                    hover_data.append([row['altitude'], row['datetime_str']])
                
                frame_data.append(
                    go.Scattermapbox(
                        lat=data_frame['latitude'].tolist(),
                        lon=data_frame['longitude'].tolist(),
                        mode='lines+markers',
                        name=f'Vulture {vulture_id}',
                        line=dict(color=colors.get(vulture_id, 'gray'), width=4),
                        marker=dict(color=colors.get(vulture_id, 'gray'), size=10),
                        customdata=hover_data,
                        hovertemplate='<b>Vulture %{text}</b><br>' +
                                    'Time: %{customdata[1]}<br>' +
                                    'Lat: %{lat:.4f}°<br>' +
                                    'Lon: %{lon:.4f}°<br>' +
                                    'Alt: %{customdata[0]:.0f}m<br>' +
                                    '<extra></extra>',
                        text=[vulture_id] * len(data_frame)
                    )
                )
            else:
                frame_data.append(
                    go.Scattermapbox(
                        lat=[], lon=[], mode='lines+markers',
                        name=f'Vulture {vulture_id}',
                        line=dict(color=colors.get(vulture_id, 'gray'), width=4),
                        marker=dict(color=colors.get(vulture_id, 'gray'), size=10)
                    )
                )
        
        frames.append(go.Frame(data=frame_data, name=str(frame)))

    # Initial traces
    initial_traces = []
    for vulture_id in vulture_ids:
        initial_traces.append(
            go.Scattermapbox(
                lat=[], lon=[], mode='lines+markers',
                name=f'Vulture {vulture_id}',
                line=dict(color=colors.get(vulture_id, 'gray'), width=4),
                marker=dict(color=colors.get(vulture_id, 'gray'), size=10)
            )
        )

    fig = go.Figure(data=initial_traces, frames=frames)

    # Mobile-optimized layout
    fig.update_layout(
        title=dict(
            text='Vulture Flight Paths - Mobile View',
            x=0.5,
            font=dict(size=14)
        ),
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
        ),
        updatemenus=[{
            'type': 'buttons',
            'direction': 'left',
            'pad': {'r': 2, 't': 2},
            'showactive': True,
            'x': 0.02,
            'xanchor': 'left',
            'y': 0.98,
            'yanchor': 'top',
            'buttons': [
                {
                    'label': '▶',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': 800, 'redraw': True},
                        'transition': {'duration': 150},
                        'fromcurrent': True,
                        'autoplay': True
                    }]
                },
                {
                    'label': '⏸',
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
                    'label': frame_datetime_lookup.get(frame, str(frame)),
                    'args': [[str(frame)], {'mode': 'immediate', 
                            'frame': {'duration': 0, 'redraw': True}, 
                            'transition': {'duration': 0}}]
                } for frame in range(start_time, end_time + 1)
            ],
            'transition': {'duration': 0},
            'x': 0.02,
            'y': 0.02,
            'currentvalue': {
                'font': {'size': 12},
                'prefix': '', 
                'visible': True, 
                'xanchor': 'left'
            },
            'len': 0.96
        }],
        legend=dict(
            x=0.02, 
            y=0.85,
            bgcolor='rgba(255,255,255,0.9)',
            font=dict(size=10),
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1
        ),
        margin=dict(l=5, r=5, b=40, t=50),
        height=500,  # Compact height for mobile
        autosize=True,
        # Note: Mobile optimizations handled by mapbox settings
        dragmode='pan'  # Better for touch screens
    )

    return fig

def main():
    """Main function"""
    print("Creating mobile-optimized 2D visualization...")
    print("Features: Compact display, touch-friendly controls, simplified UI")
    
    fig = create_mobile_optimized_map()
    
    # Save the visualization
    output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'flight_paths_mobile.html')
    fig.write_html(output_path)
    
    print(f"\nMobile visualization saved to: {output_path}")
    print("Optimizations:")
    print("- Compact time format (DD.MM HH:MM)")
    print("- Larger markers and lines for touch screens")
    print("- Simplified controls and legend")
    print("- Higher zoom level for detailed view")
    print("- Touch-friendly pan and zoom")
    
    # Show the figure
    pio.show(fig)

if __name__ == "__main__":
    main()

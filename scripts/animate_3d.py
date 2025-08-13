import plotly.graph_objects as go
import pandas as pd
import os

# Placeholder GPS data for two vultures
data = [
    [1, 46.5, 7.5, 1200, 'A'],
    [2, 46.51, 7.51, 1210, 'A'],
    [3, 46.52, 7.52, 1220, 'A'],
    [1, 46.6, 7.6, 1300, 'B'],
    [2, 46.61, 7.61, 1310, 'B'],
    [3, 46.62, 7.62, 1320, 'B'],
]
df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id'])

frames = []
max_frame = df['timestamp'].max()
for frame in range(1, max_frame + 1):
    frame_data = []
    for vulture_id, group in df.groupby('vulture_id'):
        data = group[group['timestamp'] <= frame]
        frame_data.append(go.Scatter3d(
            x=data['longitude'],
            y=data['latitude'],
            z=data['altitude'],
            mode='lines+markers',
            name=f'Vulture {vulture_id}'
        ))
    frames.append(go.Frame(data=frame_data, name=str(frame)))

fig = go.Figure(
    data=[go.Scatter3d(
        x=[], y=[], z=[], mode='lines+markers'
    )],
    frames=frames
)
fig.update_layout(
    title='Animated 3D Flight Paths of Bearded Vultures',
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Altitude (m)'
    ),
    updatemenus=[{
        'type': 'buttons',
        'buttons': [
            {
                'label': 'Play',
                'method': 'animate',
                'args': [None, {'frame': {'duration': 1000, 'redraw': True}, 'fromcurrent': True}]
            },
            {
                'label': 'Pause',
                'method': 'animate',
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}]
            }
        ]
    }],
    legend_title='Vulture ID',
    margin=dict(l=0, r=0, b=0, t=40)
)

output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'flight_paths_3d_animation.html')
fig.write_html(output_path)
fig.show()

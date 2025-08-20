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

fig = go.Figure()
for vulture_id, group in df.groupby('vulture_id'):
    fig.add_trace(go.Scatter3d(
        x=group['longitude'],
        y=group['latitude'],
        z=group['altitude'],
        mode='lines+markers',
        name=f'Vulture {vulture_id}'
    ))
fig.update_layout(
    title='3D Flight Paths of Bearded Vultures',
    scene=dict(
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        zaxis_title='Altitude (m)'
    ),
    legend_title='Vulture ID',
    margin=dict(l=0, r=0, b=0, t=40)
)
output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'flight_paths_3d.html')
fig.write_html(output_path)
fig.show()

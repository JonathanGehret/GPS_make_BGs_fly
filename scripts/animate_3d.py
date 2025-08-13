import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import plotly.io as pio
import plotly

# Placeholder GPS data for two vultures

np.random.seed(42)
start_time = 1
end_time = 50

# Generate sample data for two vultures
# Synthetic terrain mesh (mountain/valley)
terrain_size = 50
x_terrain = np.linspace(7.48, 7.82, terrain_size)
y_terrain = np.linspace(46.48, 46.82, terrain_size)
X, Y = np.meshgrid(x_terrain, y_terrain)
# Simple mountain/valley function
Z = 1250 + 100 * np.sin(2 * np.pi * (X - 7.48) / (7.82 - 7.48)) * np.cos(2 * np.pi * (Y - 46.48) / (46.82 - 46.48))
# Vulture A: 50 points
timestamps_a = np.linspace(start_time, end_time, 50, dtype=int)
latitudes_a = np.linspace(46.5, 46.7, 50) + np.random.normal(0, 0.002, 50)
longitudes_a = np.linspace(7.5, 7.7, 50) + np.random.normal(0, 0.002, 50)
altitudes_a = np.linspace(1200, 1400, 50) + np.random.normal(0, 5, 50)

# Vulture B: 30 points, random intervals within same start/end
timestamps_b = np.sort(np.random.choice(np.arange(start_time, end_time+1), 30, replace=False))
latitudes_b = np.linspace(46.6, 46.8, 30) + np.random.normal(0, 0.002, 30)
longitudes_b = np.linspace(7.6, 7.8, 30) + np.random.normal(0, 0.002, 30)
altitudes_b = np.linspace(1300, 1500, 30) + np.random.normal(0, 5, 30)

data_a = list(zip(timestamps_a, latitudes_a, longitudes_a, altitudes_a, ['A']*50))
data_b = list(zip(timestamps_b, latitudes_b, longitudes_b, altitudes_b, ['B']*30))
data = data_a + data_b

df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id'])

frames = []
max_frame = df['timestamp'].max()
for frame in range(start_time, end_time + 1):
	colors = {'A': 'blue', 'B': 'orange'}
	frame_data = [
		go.Surface(x=x_terrain, y=y_terrain, z=Z, colorscale='YlGnBu', opacity=0.6, showscale=False, name='Terrain')
	]
	for vulture_id in ['A', 'B']:
		group = df[df['vulture_id'] == vulture_id]
		data = group[group['timestamp'] <= frame]
		if len(data) > 0:
			trace = go.Scatter3d(
				x=data['longitude'],
				y=data['latitude'],
				z=data['altitude'],
				mode='lines+markers',
				name=f'Vulture {vulture_id}',
				line=dict(color=colors[vulture_id]),
				marker=dict(color=colors[vulture_id])
			)
		else:
			trace = go.Scatter3d(
				x=[], y=[], z=[], mode='lines+markers',
				name=f'Vulture {vulture_id}',
				line=dict(color=colors[vulture_id]),
				marker=dict(color=colors[vulture_id])
			)
		frame_data.append(trace)
	frames.append(go.Frame(data=frame_data, name=str(frame)))

fig = go.Figure(
	data=[
		go.Surface(x=x_terrain, y=y_terrain, z=Z, colorscale='YlGnBu', opacity=0.6, showscale=False, name='Terrain'),
		go.Scatter3d(x=[], y=[], z=[], mode='lines+markers', name='Vulture A', line=dict(color='blue'), marker=dict(color='blue')),
		go.Scatter3d(x=[], y=[], z=[], mode='lines+markers', name='Vulture B', line=dict(color='orange'), marker=dict(color='orange'))
	],
	frames=frames
)
fig.update_layout(
	title='Animated 3D Flight Paths of Bearded Vultures',
	scene=dict(
		xaxis_title='Longitude',
		yaxis_title='Latitude',
		zaxis_title='Altitude (m)',
		xaxis=dict(range=[7.48, 7.82]),
		yaxis=dict(range=[46.48, 46.82]),
		zaxis=dict(range=[1190, 1510]),
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
output_path = os.path.join(output_dir, 'flight_paths_3d_animation.html')
fig.write_html(output_path)
# Check Plotly version
required_version = '5.0.0'
if tuple(map(int, plotly.__version__.split('.'))) < tuple(map(int, required_version.split('.'))):
	print(f"Warning: Plotly version {plotly.__version__} detected. Please upgrade to >= {required_version} for best animation support.")

pio.show(fig)

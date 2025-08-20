import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import os

# Placeholder GPS data for two vultures
# Columns: timestamp, latitude, longitude, altitude, vulture_id
data = [
    [1, 46.5, 7.5, 1200, 'A'],
    [2, 46.51, 7.51, 1210, 'A'],
    [3, 46.52, 7.52, 1220, 'A'],
    [1, 46.6, 7.6, 1300, 'B'],
    [2, 46.61, 7.61, 1310, 'B'],
    [3, 46.62, 7.62, 1320, 'B'],
]
df = pd.DataFrame(data, columns=['timestamp', 'latitude', 'longitude', 'altitude', 'vulture_id'])

fig, ax = plt.subplots(figsize=(8, 6))
colors = {'A': 'blue', 'B': 'orange'}
lines = {vid: ax.plot([], [], marker='o', color=colors[vid], label=f'Vulture {vid}')[0] for vid in df['vulture_id'].unique()}
ax.set_xlim(df['longitude'].min() - 0.01, df['longitude'].max() + 0.01)
ax.set_ylim(df['latitude'].min() - 0.01, df['latitude'].max() + 0.01)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Animated 2D Flight Paths of Bearded Vultures')
ax.legend()
ax.grid(True)

# Prepare data for animation
grouped = df.groupby('vulture_id')
max_frames = df['timestamp'].max()

def init():
    for line in lines.values():
        line.set_data([], [])
    return list(lines.values())

def animate(frame):
    for vulture_id, group in grouped:
        data = group[group['timestamp'] <= frame]
        lines[vulture_id].set_data(data['longitude'].values, data['latitude'].values)
    return list(lines.values())

ani = animation.FuncAnimation(fig, animate, frames=range(1, max_frames + 1), init_func=init, blit=True, repeat=False)

output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'flight_paths_2d_animation.mp4')
ani.save(output_path, writer='ffmpeg', fps=1)
plt.show()

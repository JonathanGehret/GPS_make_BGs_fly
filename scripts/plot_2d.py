import matplotlib.pyplot as plt
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

plt.figure(figsize=(8, 6))
for vulture_id, group in df.groupby('vulture_id'):
    plt.plot(group['longitude'].values, group['latitude'].values, marker='o', label=f'Vulture {vulture_id}')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('2D Flight Paths of Bearded Vultures')
plt.legend()
plt.grid(True)
plt.tight_layout()
output_dir = os.path.join(os.path.dirname(__file__), '../visualizations')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'flight_paths_2d.png')
plt.savefig(output_path)
plt.show()

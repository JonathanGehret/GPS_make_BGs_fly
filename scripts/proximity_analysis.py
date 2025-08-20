import pandas as pd
import numpy as np
import os
import glob
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

class VultureProximityAnalyzer:
    """
    Comprehensive analysis tool for detecting when vultures are in close proximity
    Handles large datasets spanning weeks, months, or years
    """
    
    def __init__(self, proximity_threshold_km=2.0):
        self.proximity_threshold_km = proximity_threshold_km
        self.data = None
        self.proximity_events = []
        self.statistics = {}
        
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        Returns distance in kilometers
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        return c * r
    
    def load_csv_data(self, data_folder='data'):
        """Load all CSV files and combine into a single dataset"""
        csv_files = glob.glob(os.path.join(data_folder, '*.csv'))
        
        if not csv_files:
            print("No CSV files found in data folder!")
            return False
            
        all_data = []
        
        print(f"Loading {len(csv_files)} CSV files...")
        
        for i, csv_file in enumerate(csv_files):
            filename = os.path.basename(csv_file)
            vulture_id = chr(65 + i)  # A, B, C, etc.
            
            try:
                df = pd.read_csv(csv_file, sep=';')
                
                # Parse timestamps
                timestamps = []
                for timestamp_str in df['Timestamp [UTC]']:
                    try:
                        # Try to parse the timestamp (format: DD.MM.YYYY HH:mm:ss)
                        dt = datetime.strptime(str(timestamp_str), '%d.%m.%Y %H:%M:%S')
                        timestamps.append(dt)
                    except Exception:
                        # Fallback: use index as time
                        timestamps.append(datetime.now() + timedelta(hours=len(timestamps)))
                
                # Clean and convert coordinates
                latitudes = []
                longitudes = []
                altitudes = []
                
                for _, row in df.iterrows():
                    lat = float(str(row['Latitude']).replace(',', '.'))
                    lon = float(str(row['Longitude']).replace(',', '.'))
                    alt = float(str(row['Height']))
                    
                    latitudes.append(lat)
                    longitudes.append(lon)
                    altitudes.append(alt)
                
                # Create records
                for j in range(len(timestamps)):
                    all_data.append({
                        'vulture_id': vulture_id,
                        'filename': filename,
                        'timestamp': timestamps[j],
                        'latitude': latitudes[j],
                        'longitude': longitudes[j],
                        'altitude': altitudes[j]
                    })
                
                print(f"  - {filename} -> Vulture {vulture_id}: {len(timestamps)} data points")
                
            except Exception as e:
                print(f"  - Error loading {filename}: {e}")
        
        self.data = pd.DataFrame(all_data)
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)
        
        print(f"\nTotal dataset: {len(self.data)} data points across {len(csv_files)} vultures")
        print(f"Time range: {self.data['timestamp'].min()} to {self.data['timestamp'].max()}")
        
        return True
    
    def find_proximity_events(self, time_window_minutes=30):
        """
        Find all instances where 2+ vultures are within proximity threshold
        time_window_minutes: Consider records within this time window as simultaneous
        """
        if self.data is None:
            print("No data loaded. Please run load_csv_data() first.")
            return
        
        print("\nAnalyzing proximity events...")
        print(f"Proximity threshold: {self.proximity_threshold_km} km")
        print(f"Time window: ±{time_window_minutes} minutes")
        
        proximity_events = []
        
        # Group data by time windows
        self.data['time_group'] = self.data['timestamp'].dt.floor(f'{time_window_minutes}min')
        
        for time_group in self.data['time_group'].unique():
            group_data = self.data[self.data['time_group'] == time_group]
            
            # Skip if only one vulture in this time window
            if len(group_data['vulture_id'].unique()) < 2:
                continue
            
            # Calculate distances between all pairs in this time window
            vultures_in_group = group_data['vulture_id'].unique()
            
            for i, vulture1 in enumerate(vultures_in_group):
                for vulture2 in vultures_in_group[i+1:]:
                    
                    v1_data = group_data[group_data['vulture_id'] == vulture1]
                    v2_data = group_data[group_data['vulture_id'] == vulture2]
                    
                    # Find closest records in time between these two vultures
                    for _, v1_record in v1_data.iterrows():
                        for _, v2_record in v2_data.iterrows():
                            
                            time_diff = abs((v1_record['timestamp'] - v2_record['timestamp']).total_seconds() / 60)
                            
                            if time_diff <= time_window_minutes:
                                distance_km = self.haversine_distance(
                                    v1_record['latitude'], v1_record['longitude'],
                                    v2_record['latitude'], v2_record['longitude']
                                )
                                
                                if distance_km <= self.proximity_threshold_km:
                                    proximity_events.append({
                                        'timestamp': v1_record['timestamp'],
                                        'vulture1': vulture1,
                                        'vulture2': vulture2,
                                        'distance_km': distance_km,
                                        'time_diff_minutes': time_diff,
                                        'lat1': v1_record['latitude'],
                                        'lon1': v1_record['longitude'],
                                        'alt1': v1_record['altitude'],
                                        'lat2': v2_record['latitude'],
                                        'lon2': v2_record['longitude'],
                                        'alt2': v2_record['altitude'],
                                        'center_lat': (v1_record['latitude'] + v2_record['latitude']) / 2,
                                        'center_lon': (v1_record['longitude'] + v2_record['longitude']) / 2
                                    })
        
        self.proximity_events = proximity_events
        print(f"Found {len(proximity_events)} proximity events!")
        
        return proximity_events
    
    def calculate_statistics(self):
        """Calculate comprehensive statistics about proximity events"""
        if not self.proximity_events:
            print("No proximity events found. Run find_proximity_events() first.")
            return
        
        events_df = pd.DataFrame(self.proximity_events)
        vulture_ids = self.data['vulture_id'].unique()
        
        stats = {
            'total_events': len(self.proximity_events),
            'unique_pairs': len(events_df[['vulture1', 'vulture2']].drop_duplicates()),
            'average_distance_km': events_df['distance_km'].mean(),
            'min_distance_km': events_df['distance_km'].min(),
            'max_distance_km': events_df['distance_km'].max(),
            'time_span_days': (self.data['timestamp'].max() - self.data['timestamp'].min()).days,
            'events_per_day': len(self.proximity_events) / max(1, (self.data['timestamp'].max() - self.data['timestamp'].min()).days),
            'pair_statistics': {},
            'monthly_counts': {},
            'hourly_pattern': {},
            'hotspots': []
        }
        
        # Pair-wise statistics
        for vulture1 in vulture_ids:
            for vulture2 in vulture_ids:
                if vulture1 < vulture2:  # Avoid duplicates
                    pair_events = events_df[
                        ((events_df['vulture1'] == vulture1) & (events_df['vulture2'] == vulture2)) |
                        ((events_df['vulture1'] == vulture2) & (events_df['vulture2'] == vulture1))
                    ]
                    
                    if len(pair_events) > 0:
                        stats['pair_statistics'][f"{vulture1}-{vulture2}"] = {
                            'events': len(pair_events),
                            'avg_distance_km': pair_events['distance_km'].mean(),
                            'min_distance_km': pair_events['distance_km'].min(),
                            'first_encounter': pair_events['timestamp'].min(),
                            'last_encounter': pair_events['timestamp'].max()
                        }
        
        # Monthly pattern
        events_df['month'] = events_df['timestamp'].dt.to_period('M')
        monthly_counts = events_df.groupby('month').size()
        stats['monthly_counts'] = {str(month): count for month, count in monthly_counts.items()}
        
        # Hourly pattern
        events_df['hour'] = events_df['timestamp'].dt.hour
        hourly_counts = events_df.groupby('hour').size()
        stats['hourly_pattern'] = {hour: count for hour, count in hourly_counts.items()}
        
        # Geographic hotspots (cluster nearby events)
        from sklearn.cluster import DBSCAN
        
        if len(events_df) > 5:
            coords = events_df[['center_lat', 'center_lon']].values
            clustering = DBSCAN(eps=0.01, min_samples=2).fit(coords)  # ~1km clusters
            
            unique_labels = set(clustering.labels_)
            hotspots = []
            
            for label in unique_labels:
                if label != -1:  # -1 is noise
                    cluster_events = events_df[clustering.labels_ == label]
                    hotspot = {
                        'center_lat': cluster_events['center_lat'].mean(),
                        'center_lon': cluster_events['center_lon'].mean(),
                        'event_count': len(cluster_events),
                        'avg_distance_km': cluster_events['distance_km'].mean()
                    }
                    hotspots.append(hotspot)
            
            stats['hotspots'] = sorted(hotspots, key=lambda x: x['event_count'], reverse=True)
        
        self.statistics = stats
        return stats
    
    def print_summary_report(self):
        """Print a comprehensive summary report"""
        if not self.statistics:
            self.calculate_statistics()
        
        stats = self.statistics
        
        print("\n" + "="*60)
        print("VULTURE PROXIMITY ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📊 OVERVIEW:")
        print(f"  • Total proximity events: {stats['total_events']}")
        print(f"  • Unique vulture pairs: {stats['unique_pairs']}")
        print(f"  • Analysis period: {stats['time_span_days']} days")
        print(f"  • Events per day: {stats['events_per_day']:.2f}")
        print(f"  • Proximity threshold: {self.proximity_threshold_km} km")
        
        print(f"\n📏 DISTANCE STATISTICS:")
        print(f"  • Average proximity distance: {stats['average_distance_km']:.2f} km")
        print(f"  • Closest encounter: {stats['min_distance_km']:.3f} km")
        print(f"  • Furthest proximity: {stats['max_distance_km']:.2f} km")
        
        print(f"\n🦅 PAIR-WISE INTERACTIONS:")
        for pair, data in stats['pair_statistics'].items():
            print(f"  • {pair}: {data['events']} events, avg {data['avg_distance_km']:.2f}km apart")
            print(f"    └─ Closest: {data['min_distance_km']:.3f}km")
        
        print(f"\n🕒 TEMPORAL PATTERNS:")
        if stats['hourly_pattern']:
            peak_hour = max(stats['hourly_pattern'], key=stats['hourly_pattern'].get)
            print(f"  • Peak activity hour: {peak_hour}:00 ({stats['hourly_pattern'][peak_hour]} events)")
        
        print(f"\n🗓️ MONTHLY DISTRIBUTION:")
        if stats['monthly_counts']:
            for month, count in list(stats['monthly_counts'].items())[:5]:  # Show first 5 months
                print(f"  • {month}: {count} events")
        
        print(f"\n📍 GEOGRAPHIC HOTSPOTS:")
        for i, hotspot in enumerate(stats['hotspots'][:3], 1):  # Top 3 hotspots
            print(f"  • Hotspot {i}: {hotspot['event_count']} events")
            print(f"    └─ Location: {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°E")
            print(f"    └─ Avg distance: {hotspot['avg_distance_km']:.2f}km")
    
    def create_interactive_timeline(self):
        """Create an interactive timeline of proximity events"""
        if not self.proximity_events:
            print("No proximity events to visualize.")
            return None
        
        events_df = pd.DataFrame(self.proximity_events)
        
        # Create timeline plot
        fig = go.Figure()
        
        colors = {'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c', 'D': '#d62728', 'E': '#9467bd'}
        
        for _, event in events_df.iterrows():
            pair = f"{event['vulture1']}-{event['vulture2']}"
            color = colors.get(event['vulture1'], '#666666')
            
            fig.add_trace(go.Scatter(
                x=[event['timestamp']],
                y=[event['distance_km']],
                mode='markers',
                marker=dict(
                    size=10,
                    color=color,
                    line=dict(width=1, color='white')
                ),
                name=pair,
                hovertemplate=
                f"<b>{pair} Proximity Event</b><br>" +
                f"Time: %{{x}}<br>" +
                f"Distance: {event['distance_km']:.3f} km<br>" +
                f"Location: {event['center_lat']:.4f}°N, {event['center_lon']:.4f}°E<br>" +
                "<extra></extra>",
                showlegend=True
            ))
        
        fig.update_layout(
            title='Vulture Proximity Events Timeline',
            xaxis_title='Time',
            yaxis_title='Distance (km)',
            hovermode='closest',
            height=600
        )
        
        return fig
    
    def create_proximity_map(self):
        """Create an interactive map showing proximity event locations"""
        if not self.proximity_events:
            print("No proximity events to map.")
            return None
        
        events_df = pd.DataFrame(self.proximity_events)
        
        # Create map
        fig = go.Figure()
        
        # Add proximity events
        fig.add_trace(go.Scattermapbox(
            lat=events_df['center_lat'],
            lon=events_df['center_lon'],
            mode='markers',
            marker=dict(
                size=8,
                color=events_df['distance_km'],
                colorscale='RdYlBu_r',
                showscale=True,
                colorbar=dict(title="Distance (km)")
            ),
            text=[f"Vultures {row['vulture1']}-{row['vulture2']}<br>"
                  f"Distance: {row['distance_km']:.3f} km<br>"
                  f"Time: {row['timestamp']}"
                  for _, row in events_df.iterrows()],
            hovertemplate='<b>Proximity Event</b><br>%{text}<extra></extra>',
            name='Proximity Events'
        ))
        
        # Add hotspots if available
        if self.statistics and 'hotspots' in self.statistics:
            hotspots = self.statistics['hotspots']
            if hotspots:
                fig.add_trace(go.Scattermapbox(
                    lat=[h['center_lat'] for h in hotspots],
                    lon=[h['center_lon'] for h in hotspots],
                    mode='markers',
                    marker=dict(
                        size=[min(h['event_count'] * 3, 30) for h in hotspots],
                        color='red',
                        symbol='star'
                    ),
                    text=[f"Hotspot: {h['event_count']} events" for h in hotspots],
                    name='Hotspots'
                ))
        
        # Calculate map center
        center_lat = events_df['center_lat'].mean()
        center_lon = events_df['center_lon'].mean()
        
        fig.update_layout(
            title='Vulture Proximity Events Map',
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            height=700
        )
        
        return fig

def main():
    """Main analysis function"""
    print("Vulture Proximity Analysis Tool")
    print("="*40)
    
    # Initialize analyzer
    analyzer = VultureProximityAnalyzer(proximity_threshold_km=2.0)
    
    # Load data
    if not analyzer.load_csv_data():
        return
    
    # Find proximity events
    proximity_events = analyzer.find_proximity_events(time_window_minutes=30)
    
    if not proximity_events:
        print("No proximity events found with current settings.")
        return
    
    # Calculate statistics
    analyzer.calculate_statistics()
    
    # Print summary report
    analyzer.print_summary_report()
    
    # Create visualizations
    print("\nGenerating visualizations...")
    
    # Timeline
    timeline_fig = analyzer.create_interactive_timeline()
    if timeline_fig:
        output_dir = os.path.join(os.path.dirname(__file__), '../analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        timeline_path = os.path.join(output_dir, 'proximity_timeline.html')
        timeline_fig.write_html(timeline_path)
        print(f"Timeline saved to: {timeline_path}")
    
    # Map
    map_fig = analyzer.create_proximity_map()
    if map_fig:
        map_path = os.path.join(output_dir, 'proximity_map.html')
        map_fig.write_html(map_path)
        print(f"Map saved to: {map_path}")
    
    # Save detailed results
    results_path = os.path.join(output_dir, 'proximity_analysis_results.json')
    with open(results_path, 'w') as f:
        # Convert timestamps to strings for JSON serialization
        json_events = []
        for event in proximity_events:
            json_event = event.copy()
            json_event['timestamp'] = event['timestamp'].isoformat()
            json_events.append(json_event)
        
        json_stats = analyzer.statistics.copy()
        # Convert any datetime objects in stats
        for pair, data in json_stats.get('pair_statistics', {}).items():
            if 'first_encounter' in data:
                data['first_encounter'] = data['first_encounter'].isoformat()
            if 'last_encounter' in data:
                data['last_encounter'] = data['last_encounter'].isoformat()
        
        results = {
            'proximity_events': json_events,
            'statistics': json_stats,
            'settings': {
                'proximity_threshold_km': analyzer.proximity_threshold_km,
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        json.dump(results, f, indent=2)
    
    print(f"Detailed results saved to: {results_path}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()

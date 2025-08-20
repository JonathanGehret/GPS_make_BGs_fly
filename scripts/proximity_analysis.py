import pandas as pd
import numpy as np
import os
import glob
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
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
        self.encounter_groups = []
        
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
        try:
            from sklearn.cluster import DBSCAN
            sklearn_available = True
        except ImportError:
            sklearn_available = False
        
        if len(events_df) > 5 and sklearn_available:
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
        elif len(events_df) > 5:
            # Fallback: create simple hotspots by grouping nearby events manually
            hotspots = []
            processed_events = set()
            
            for i, event in events_df.iterrows():
                if i in processed_events:
                    continue
                
                # Find all events within ~1km of this event
                nearby_events = []
                center_lat, center_lon = event['center_lat'], event['center_lon']
                
                for j, other_event in events_df.iterrows():
                    if j in processed_events:
                        continue
                    
                    # Simple distance check (~1km = ~0.01 degrees)
                    lat_diff = abs(other_event['center_lat'] - center_lat)
                    lon_diff = abs(other_event['center_lon'] - center_lon)
                    
                    if lat_diff < 0.01 and lon_diff < 0.01:
                        nearby_events.append(j)
                        processed_events.add(j)
                
                if len(nearby_events) >= 2:
                    cluster_data = events_df.loc[nearby_events]
                    hotspot = {
                        'center_lat': cluster_data['center_lat'].mean(),
                        'center_lon': cluster_data['center_lon'].mean(),
                        'event_count': len(cluster_data),
                        'avg_distance_km': cluster_data['distance_km'].mean()
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
        
        print("\n📊 OVERVIEW:")
        print(f"  • Total proximity events: {stats['total_events']}")
        print(f"  • Unique vulture pairs: {stats['unique_pairs']}")
        print(f"  • Analysis period: {stats['time_span_days']} days")
        print(f"  • Events per day: {stats['events_per_day']:.2f}")
        print(f"  • Proximity threshold: {self.proximity_threshold_km} km")
        
        print("\n📏 DISTANCE STATISTICS:")
        print(f"  • Average proximity distance: {stats['average_distance_km']:.2f} km")
        print(f"  • Closest encounter: {stats['min_distance_km']:.3f} km")
        print(f"  • Furthest proximity: {stats['max_distance_km']:.2f} km")
        
        print("\n🦅 PAIR-WISE INTERACTIONS:")
        for pair, data in stats['pair_statistics'].items():
            print(f"  • {pair}: {data['events']} events, avg {data['avg_distance_km']:.2f}km apart")
            print(f"    └─ Closest: {data['min_distance_km']:.3f}km")
        
        print("\n🕒 TEMPORAL PATTERNS:")
        if stats['hourly_pattern']:
            peak_hour = max(stats['hourly_pattern'], key=stats['hourly_pattern'].get)
            print(f"  • Peak activity hour: {peak_hour}:00 ({stats['hourly_pattern'][peak_hour]} events)")
        
        print("\n🗓️ MONTHLY DISTRIBUTION:")
        if stats['monthly_counts']:
            for month, count in list(stats['monthly_counts'].items())[:5]:  # Show first 5 months
                print(f"  • {month}: {count} events")
        
        print("\n📍 GEOGRAPHIC HOTSPOTS:")
        for i, hotspot in enumerate(stats['hotspots'][:3], 1):  # Top 3 hotspots
            print(f"  • Hotspot {i}: {hotspot['event_count']} events")
            print(f"    └─ Location: {hotspot['center_lat']:.4f}°N, {hotspot['center_lon']:.4f}°E")
            print(f"    └─ Avg distance: {hotspot['avg_distance_km']:.2f}km")
    
    def generate_statistics_text(self):
        """Generate a text summary of proximity statistics"""
        if not self.proximity_events:
            return "No proximity events found."
        
        self.calculate_statistics()
        
        stats_text = []
        stats_text.append("=== VULTURE PROXIMITY ANALYSIS STATISTICS ===\n")
        
        events_df = pd.DataFrame(self.proximity_events)
        
        # Basic statistics
        stats_text.append(f"Total proximity events: {len(self.proximity_events)}")
        stats_text.append(f"Unique vulture pairs: {len(events_df[['vulture1', 'vulture2']].drop_duplicates())}")
        stats_text.append(f"Average distance: {events_df['distance_km'].mean():.3f} km")
        stats_text.append(f"Minimum distance: {events_df['distance_km'].min():.3f} km")
        stats_text.append(f"Maximum distance: {events_df['distance_km'].max():.3f} km")
        
        # Time range
        time_span = (self.data['timestamp'].max() - self.data['timestamp'].min())
        stats_text.append(f"Time span: {time_span.days} days")
        
        # Encounters
        encounters = self.group_encounters()
        stats_text.append(f"Distinct encounters: {len(encounters)}")
        
        if encounters:
            avg_duration = sum(e['duration_minutes'] for e in encounters) / len(encounters)
            stats_text.append(f"Average encounter duration: {avg_duration:.1f} minutes")
        
        # Vulture pair breakdown
        stats_text.append("\n=== VULTURE PAIR BREAKDOWN ===")
        for vulture1 in events_df['vulture1'].unique():
            for vulture2 in events_df['vulture2'].unique():
                if vulture1 < vulture2:
                    pair_events = events_df[
                        ((events_df['vulture1'] == vulture1) & (events_df['vulture2'] == vulture2)) |
                        ((events_df['vulture1'] == vulture2) & (events_df['vulture2'] == vulture1))
                    ]
                    if not pair_events.empty:
                        stats_text.append(f"{vulture1}-{vulture2}: {len(pair_events)} events, "
                                        f"avg distance: {pair_events['distance_km'].mean():.3f} km")
        
        return "\n".join(stats_text)

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
                "Time: %{x}<br>" +
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
        fig.add_trace(go.Scattermap(
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
                fig.add_trace(go.Scattermap(
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
            map=dict(
                style='open-street-map',
                center=dict(lat=center_lat, lon=center_lon),
                zoom=10
            ),
            height=700
        )
        
        return fig

    def group_encounters(self, time_gap_minutes=60):
        """
        Group proximity events into distinct encounters based on time gaps.
        
        Args:
            time_gap_minutes (int): Minimum gap in minutes to separate encounters
            
        Returns:
            list: List of encounter dictionaries with grouped events
        """
        if not self.proximity_events:
            return []
        
        # Convert events to DataFrame for easier processing
        events_df = pd.DataFrame(self.proximity_events)
        events_df = events_df.sort_values('timestamp')
        
        encounters = []
        current_encounter = []
        time_gap = pd.Timedelta(minutes=time_gap_minutes)
        
        for _, event in events_df.iterrows():
            if not current_encounter:
                # Start new encounter
                current_encounter = [event]
            else:
                # Check if this event belongs to current encounter
                last_time = current_encounter[-1]['timestamp']
                if event['timestamp'] - last_time <= time_gap:
                    current_encounter.append(event)
                else:
                    # Finalize current encounter and start new one
                    if len(current_encounter) > 0:
                        encounters.append(self._create_encounter_summary(current_encounter))
                    current_encounter = [event]
        
        # Don't forget the last encounter
        if len(current_encounter) > 0:
            encounters.append(self._create_encounter_summary(current_encounter))
        
        return encounters
    
    def _create_encounter_summary(self, events):
        """Create summary information for a group of events forming an encounter."""
        start_time = min(event['timestamp'] for event in events)
        end_time = max(event['timestamp'] for event in events)
        
        # Get all unique vultures involved
        vultures = set()
        for event in events:
            vultures.add(event['vulture1'])
            vultures.add(event['vulture2'])
        
        # Calculate center location (average of all event locations)
        center_lat = sum(event['center_lat'] for event in events) / len(events)
        center_lon = sum(event['center_lon'] for event in events) / len(events)
        
        # Calculate average distance
        avg_distance = sum(event['distance_km'] for event in events) / len(events)
        min_distance = min(event['distance_km'] for event in events)
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': (end_time - start_time).total_seconds() / 60,
            'vultures': sorted(list(vultures)),
            'num_vultures': len(vultures),
            'num_events': len(events),
            'center_lat': center_lat,
            'center_lon': center_lon,
            'avg_distance_km': avg_distance,
            'min_distance_km': min_distance,
            'events': events
        }
    
    def generate_encounter_maps(self, output_dir='output', time_buffer_hours=2):
        """
        Generate 2D maps for each encounter using the professional animation workflow.
        
        Args:
            output_dir (str): Directory to save encounter maps
            time_buffer_hours (float): Hours of data to include before/after encounter
            
        Returns:
            list: List of generated map file paths
        """
        encounters = self.group_encounters()
        if not encounters:
            print("No encounters found to generate maps for.")
            return []
        
        encounter_dir = Path(output_dir) / 'encounters'
        encounter_dir.mkdir(parents=True, exist_ok=True)
        
        generated_maps = []
        
        # Try to import the professional animation module
        try:
            import sys
            script_dir = Path(__file__).parent
            sys.path.append(str(script_dir))
            from animate_live_map_professional import LiveMapAnimator
            animation_available = True
        except ImportError as e:
            print(f"LiveMapAnimator not available: {e}")
            print("Generating simplified encounter maps instead...")
            animation_available = False
        
        for i, encounter in enumerate(encounters):
            print(f"Generating map for encounter {i+1}/{len(encounters)}...")
            
            # Create filtered dataset for this encounter
            filtered_data = self._create_encounter_dataset(encounter, time_buffer_hours)
            
            if filtered_data.empty:
                print(f"No GPS data found for encounter {i+1}, skipping...")
                continue
            
            # Generate map filename
            start_time_str = encounter['start_time'].strftime("%Y%m%d_%H%M")
            vultures_str = "_".join(encounter['vultures'])
            map_filename = f"encounter_{i+1}_{start_time_str}_{vultures_str}.html"
            map_path = encounter_dir / map_filename
            
            try:
                if animation_available:
                    # Use professional animation workflow with programmatic data
                    print("Using LiveMapAnimator with programmatic data...")
                    
                    # Create separate DataFrames for each vulture (LiveMapAnimator expects list of DFs)
                    vulture_dataframes = []
                    for vulture in encounter['vultures']:
                        vulture_data = filtered_data[filtered_data['vulture_id'] == vulture].copy()
                        if not vulture_data.empty:
                            vulture_dataframes.append(vulture_data)
                    
                    if vulture_dataframes:
                        # Create animator with programmatic data
                        animator = LiveMapAnimator(programmatic_data=vulture_dataframes)
                        
                        # Generate encounter animation
                        output_path = animator.create_encounter_animation(
                            output_file=str(map_path),
                            time_step_seconds=30,  # 30 second intervals for encounter detail
                            trail_length_minutes=5  # 5 minute trails for encounter focus
                        )
                        
                        if output_path:
                            print(f"Professional encounter animation saved: {map_path}")
                        else:
                            print("Professional animation failed, falling back to simplified map...")
                            encounter_map = self._create_simple_encounter_map(encounter, filtered_data)
                            if encounter_map:
                                encounter_map.write_html(str(map_path))
                    else:
                        print("No valid vulture data for animation, using simplified map...")
                        encounter_map = self._create_simple_encounter_map(encounter, filtered_data)
                        if encounter_map:
                            encounter_map.write_html(str(map_path))
                else:
                    # Generate a simplified encounter map using plotly
                    encounter_map = self._create_simple_encounter_map(encounter, filtered_data)
                    if encounter_map:
                        encounter_map.write_html(str(map_path))
                
                generated_maps.append(str(map_path))
                print(f"Encounter map saved: {map_path}")
                
                # Save encounter metadata
                metadata_path = encounter_dir / f"encounter_{i+1}_metadata.json"
                with open(metadata_path, 'w') as f:
                    # Convert timestamps to strings for JSON serialization
                    encounter_copy = encounter.copy()
                    encounter_copy['start_time'] = encounter_copy['start_time'].isoformat()
                    encounter_copy['end_time'] = encounter_copy['end_time'].isoformat()
                    encounter_copy['events'] = [
                        {**event, 'timestamp': event['timestamp'].isoformat() if hasattr(event['timestamp'], 'isoformat') else str(event['timestamp'])}
                        for event in encounter_copy['events']
                    ]
                    json.dump(encounter_copy, f, indent=2)
                
            except Exception as e:
                print(f"Error generating map for encounter {i+1}: {e}")
                continue
        
        print(f"Generated {len(generated_maps)} encounter maps in {encounter_dir}")
        return generated_maps
    
    def _create_simple_encounter_map(self, encounter, filtered_data):
        """Create a simple encounter map when LiveMapAnimator is not available."""
        if filtered_data.empty:
            return None
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Color scheme for different vultures
        colors = {'A': '#1f77b4', 'B': '#ff7f0e', 'C': '#2ca02c', 'D': '#d62728', 'E': '#9467bd'}
        
        # Add GPS tracks for each vulture
        for vulture in encounter['vultures']:
            vulture_data = filtered_data[filtered_data['vulture_id'] == vulture]
            if not vulture_data.empty:
                color = colors.get(vulture, '#666666')
                
                # Add track line
                fig.add_trace(go.Scattermap(
                    lat=vulture_data['latitude'],
                    lon=vulture_data['longitude'],
                    mode='lines+markers',
                    line=dict(width=3, color=color),
                    marker=dict(size=5, color=color),
                    name=f'Vulture {vulture}',
                    hovertemplate=f'<b>Vulture {vulture}</b><br>' +
                                'Lat: %{lat:.5f}<br>' +
                                'Lon: %{lon:.5f}<br>' +
                                '<extra></extra>'
                ))
        
        # Add encounter center point
        fig.add_trace(go.Scattermap(
            lat=[encounter['center_lat']],
            lon=[encounter['center_lon']],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Encounter Center',
            hovertemplate='<b>Encounter Center</b><br>' +
                         f'Duration: {encounter["duration_minutes"]:.1f} min<br>' +
                         f'Avg Distance: {encounter["avg_distance_km"]:.3f} km<br>' +
                         f'Events: {encounter["num_events"]}<br>' +
                         '<extra></extra>'
        ))
        
        # Set map layout
        fig.update_layout(
            title=f'Encounter Map: {", ".join(encounter["vultures"])} - {encounter["start_time"].strftime("%Y-%m-%d %H:%M")}',
            map=dict(
                style='open-street-map',
                center=dict(lat=encounter['center_lat'], lon=encounter['center_lon']),
                zoom=12
            ),
            height=700,
            showlegend=True
        )
        
        return fig
    
    def _create_encounter_dataset(self, encounter, time_buffer_hours):
        """
        Create a filtered GPS dataset for a specific encounter.
        
        Args:
            encounter (dict): Encounter information
            time_buffer_hours (float): Hours of data to include before/after
            
        Returns:
            pd.DataFrame: Filtered GPS data for the encounter period
        """
        buffer_time = pd.Timedelta(hours=time_buffer_hours)
        start_time = encounter['start_time'] - buffer_time
        end_time = encounter['end_time'] + buffer_time
        
        # Filter data for all vultures involved in the encounter
        filtered_data = []
        
        for vulture in encounter['vultures']:
            # Filter self.data for this vulture
            vulture_data = self.data[self.data['vulture_id'] == vulture]
            
            # Filter by time range
            time_mask = (vulture_data['timestamp'] >= start_time) & \
                       (vulture_data['timestamp'] <= end_time)
            encounter_data = vulture_data[time_mask].copy()
            
            if not encounter_data.empty:
                # Convert to LiveMapAnimator expected format
                encounter_data = encounter_data.rename(columns={
                    'timestamp': 'Timestamp [UTC]',
                    'latitude': 'Latitude',
                    'longitude': 'Longitude',
                    'altitude': 'Height'
                })
                
                # Add required columns for LiveMapAnimator
                encounter_data['display'] = 1  # All points should be displayed
                encounter_data['source_file'] = f'encounter_{vulture}.csv'
                
                # Ensure columns are in correct order
                required_columns = ['Timestamp [UTC]', 'Latitude', 'Longitude', 'Height', 'display', 'source_file', 'vulture_id']
                for col in required_columns:
                    if col not in encounter_data.columns:
                        if col == 'vulture_id':
                            encounter_data[col] = vulture
                        elif col == 'display':
                            encounter_data[col] = 1
                        elif col == 'source_file':
                            encounter_data[col] = f'encounter_{vulture}.csv'
                
                filtered_data.append(encounter_data)
        
        if filtered_data:
            combined_data = pd.concat(filtered_data, ignore_index=True)
            # Sort by timestamp for proper animation
            combined_data = combined_data.sort_values('Timestamp [UTC]')
            return combined_data
        else:
            return pd.DataFrame()

    def create_analysis_plots(self, output_dir='output', generate_encounter_maps=False, 
                            time_buffer_hours=2):
        """
        Create comprehensive analysis plots and save them to files.
        
        Args:
            output_dir (str): Directory to save output files
            generate_encounter_maps (bool): Whether to generate individual encounter maps
            time_buffer_hours (float): Hours of data for encounter maps
        """
        if not self.proximity_events:
            print("No proximity events found. Run find_proximity_events first.")
            return {}
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Create and save timeline plot
        timeline_fig = self.create_interactive_timeline()
        timeline_path = Path(output_dir) / 'proximity_timeline.html'
        timeline_fig.write_html(str(timeline_path))
        print(f"Timeline plot saved to: {timeline_path}")
        
        # Create and save map
        map_fig = self.create_proximity_map()
        map_path = Path(output_dir) / 'proximity_map.html'
        map_fig.write_html(str(map_path))
        print(f"Proximity map saved to: {map_path}")
        
        # Create statistical summary
        stats_text = self.generate_statistics_text()
        stats_path = Path(output_dir) / 'proximity_statistics.txt'
        with open(stats_path, 'w') as f:
            f.write(stats_text)
        print(f"Statistics saved to: {stats_path}")
        
        result = {
            'timeline': timeline_path,
            'map': map_path,
            'statistics': stats_path
        }
        
        # Generate encounter maps if requested
        if generate_encounter_maps:
            print("\nGenerating individual encounter maps...")
            encounter_maps = self.generate_encounter_maps(output_dir, time_buffer_hours)
            result['encounter_maps'] = encounter_maps
            
            # Create encounter summary
            encounters = self.group_encounters()
            encounter_summary_path = Path(output_dir) / 'encounter_summary.txt'
            with open(encounter_summary_path, 'w') as f:
                f.write("=== VULTURE ENCOUNTER SUMMARY ===\n\n")
                for i, encounter in enumerate(encounters):
                    f.write(f"Encounter {i+1}:\n")
                    f.write(f"  Time: {encounter['start_time']} to {encounter['end_time']}\n")
                    f.write(f"  Duration: {encounter['duration_minutes']:.1f} minutes\n")
                    f.write(f"  Vultures: {', '.join(encounter['vultures'])}\n")
                    f.write(f"  Events: {encounter['num_events']}\n")
                    f.write(f"  Avg Distance: {encounter['avg_distance_km']:.3f} km\n")
                    f.write(f"  Min Distance: {encounter['min_distance_km']:.3f} km\n")
                    f.write(f"  Location: {encounter['center_lat']:.4f}°N, {encounter['center_lon']:.4f}°E\n\n")
            
            result['encounter_summary'] = encounter_summary_path
            print(f"Encounter summary saved to: {encounter_summary_path}")
        
        return result

def main():
    """Main analysis function with enhanced encounter mapping capabilities"""
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
    
    # Ask user if they want to generate encounter maps
    print("\nGenerate individual encounter maps using professional animation workflow?")
    print("This will create detailed 2D maps for each vulture encounter.")
    response = input("Generate encounter maps? (y/n): ").lower().strip()
    generate_encounters = response in ['y', 'yes']
    
    if generate_encounters:
        print("\nHow many hours of GPS data should be included before/after each encounter?")
        try:
            time_buffer = float(input("Time buffer in hours (default 2.0): ") or "2.0")
        except ValueError:
            time_buffer = 2.0
            print("Using default time buffer of 2.0 hours")
    
    # Create comprehensive analysis with optional encounter maps
    print("\nGenerating comprehensive analysis...")
    output_dir = os.path.join(os.path.dirname(__file__), '../analysis')
    
    results = analyzer.create_analysis_plots(
        output_dir=output_dir,
        generate_encounter_maps=generate_encounters,
        time_buffer_hours=time_buffer if generate_encounters else 2.0
    )
    
    print(f"\nAnalysis complete! Results saved to: {output_dir}")
    print(f"Timeline: {results['timeline']}")
    print(f"Map: {results['map']}")
    print(f"Statistics: {results['statistics']}")
    
    if generate_encounters and 'encounter_maps' in results:
        print(f"Encounter Maps: {len(results['encounter_maps'])} maps generated")
        print(f"Encounter Summary: {results['encounter_summary']}")
    
    # Save detailed results (legacy format for compatibility)
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
        
        results_data = {
            'proximity_events': json_events,
            'statistics': json_stats,
            'settings': {
                'proximity_threshold_km': analyzer.proximity_threshold_km,
                'analysis_timestamp': datetime.now().isoformat(),
                'encounter_maps_generated': generate_encounters
            }
        }
        json.dump(results_data, f, indent=2)
    
    print(f"Detailed results saved to: {results_path}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()

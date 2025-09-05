"""
Proximity Visualization Module

Creates interactive visualizations for proximity analysis results including
timelines, maps, and statistical dashboards.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List
from core.analysis.proximity_engine import ProximityEvent, ProximityStatistics
from core.gps_utils import get_numbered_output_path
from utils.user_interface import UserInterface


class ProximityVisualizer:
    """Creates visualizations for proximity analysis results"""
    
    def __init__(self):
        self.ui = UserInterface()
    
    def create_all_visualizations(self, events: List[ProximityEvent], 
                                 statistics: ProximityStatistics) -> bool:
        """
        Create all proximity visualizations
        
        Args:
            events: List of proximity events
            statistics: Calculated statistics
            
        Returns:
            True if successful, False otherwise
        """
        if not events:
            self.ui.print_warning("No proximity events to visualize")
            return False
        
        self.ui.print_section("📊 CREATING VISUALIZATIONS")
        
        try:
            # Create timeline visualization
            self._create_timeline_visualization(events)
            
            # Create map visualization
            self._create_map_visualization(events)
            
            # Create dashboard
            self._create_dashboard(events, statistics)
            
            self.ui.print_success("All visualizations created successfully!")
            return True
            
        except Exception as e:
            self.ui.print_error(f"Visualization creation failed: {e}")
            return False
    
    def _create_timeline_visualization(self, events: List[ProximityEvent]) -> None:
        """Create timeline visualization of proximity events"""
        print("   📅 Creating timeline visualization...")
        
        # Get all unique vulture names from events
        all_vultures = set()
        for event in events:
            all_vultures.add(event.vulture1)
            all_vultures.add(event.vulture2)
        all_vultures = sorted(list(all_vultures))
        
        # Prepare data for timeline
        timeline_data = []
        for event in events:
            timeline_data.append({
                'timestamp': event.timestamp,
                'pair': f"{event.vulture1} ↔ {event.vulture2}",
                'distance': event.distance_km,
                'duration': event.duration_minutes or 2.0,  # Default duration
                'vulture1': event.vulture1,
                'vulture2': event.vulture2
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create timeline plot
        fig = px.scatter(
            timeline_df,
            x='timestamp',
            y='pair',
            size='duration',
            color='distance',
            hover_data=['distance', 'duration'],
            title='🕒 Proximity Events Timeline',
            labels={
                'timestamp': 'Date/Time',
                'pair': 'Vulture Pair',
                'distance': 'Distance (km)',
                'duration': 'Duration (min)'
            },
            color_continuous_scale='Viridis_r'
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            xaxis_title="Time",
            yaxis_title="Vulture Pairs",
            font=dict(size=12),
            title_font_size=16
        )
        
        # Generate filename with bird names
        birds_filename = "_".join(all_vultures) if len(all_vultures) <= 3 else f"{'_'.join(all_vultures[:3])}_and_{len(all_vultures)-3}_more"
        output_path = get_numbered_output_path(f'proximity_timeline_{birds_filename}')
        fig.write_html(output_path)
        print(f"      💾 Timeline saved to: {output_path}")
    
    def _create_map_visualization(self, events: List[ProximityEvent]) -> None:
        """Create map visualization of proximity events"""
        print("   🗺️  Creating map visualization...")
        
        # Get all unique vulture names from events
        all_vultures = set()
        for event in events:
            all_vultures.add(event.vulture1)
            all_vultures.add(event.vulture2)
        all_vultures = sorted(list(all_vultures))
        
        # Prepare map data - create midpoints between vultures
        map_data = []
        for event in events:
            # Calculate midpoint
            mid_lat = (event.lat1 + event.lat2) / 2
            mid_lon = (event.lon1 + event.lon2) / 2
            
            map_data.append({
                'lat': mid_lat,
                'lon': mid_lon,
                'distance': event.distance_km,
                'pair': f"{event.vulture1} ↔ {event.vulture2}",
                'timestamp': event.timestamp.strftime('%Y-%m-%d %H:%M'),
                'vulture1': event.vulture1,
                'vulture2': event.vulture2
            })
        
        map_df = pd.DataFrame(map_data)
        
        # Create map visualization
        fig = px.scatter_map(
            map_df,
            lat='lat',
            lon='lon',
            size='distance',
            color='pair',
            hover_data=['distance', 'timestamp'],
            title='🗺️ Proximity Events Map',
            map_style='open-street-map',
            size_max=15
        )
        
        fig.update_layout(
            height=600,
            title_font_size=16,
            font=dict(size=12)
        )
        
        # Generate filename with bird names
        birds_filename = "_".join(all_vultures) if len(all_vultures) <= 3 else f"{'_'.join(all_vultures[:3])}_and_{len(all_vultures)-3}_more"
        output_path = get_numbered_output_path(f'proximity_map_{birds_filename}')
        fig.write_html(output_path)
        print(f"      💾 Map saved to: {output_path}")
    
    def _create_dashboard(self, events: List[ProximityEvent], 
                         statistics: ProximityStatistics) -> None:
        """Create comprehensive dashboard visualization"""
        print("   📊 Creating analysis dashboard...")
        
        # Get all unique vulture names from events
        all_vultures = set()
        for event in events:
            all_vultures.add(event.vulture1)
            all_vultures.add(event.vulture2)
        all_vultures = sorted(list(all_vultures))
        
        # Prepare events dataframe
        events_data = []
        for event in events:
            events_data.append({
                'timestamp': event.timestamp,
                'distance': event.distance_km,
                'vulture1': event.vulture1,
                'vulture2': event.vulture2,
                'hour': event.timestamp.hour,
                'date': event.timestamp.date(),
                'pair': f"{event.vulture1}-{event.vulture2}"
            })
        
        events_df = pd.DataFrame(events_data)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Events by Hour of Day',
                'Events by Vulture',
                'Distance Distribution',
                'Daily Event Count'
            ],
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'histogram'}, {'type': 'bar'}]]
        )
        
        # 1. Events by hour
        hourly_counts = events_df['hour'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=hourly_counts.index, y=hourly_counts.values, 
                   name='Events by Hour', marker_color='lightblue'),
            row=1, col=1
        )
        
        # 2. Events by vulture (count each vulture's involvement)
        vulture_counts = {}
        for event in events:
            for vulture in [event.vulture1, event.vulture2]:
                vulture_counts[vulture] = vulture_counts.get(vulture, 0) + 1
        
        fig.add_trace(
            go.Bar(x=list(vulture_counts.keys()), y=list(vulture_counts.values()),
                   name='Events by Vulture', marker_color='lightgreen'),
            row=1, col=2
        )
        
        # 3. Distance distribution
        fig.add_trace(
            go.Histogram(x=events_df['distance'], nbinsx=20,
                        name='Distance Distribution', marker_color='salmon'),
            row=2, col=1
        )
        
        # 4. Daily event count
        daily_counts = events_df['date'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=[str(d) for d in daily_counts.index], y=daily_counts.values,
                   name='Daily Events', marker_color='gold'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text='🔍 Proximity Analysis Dashboard',
            title_font_size=16,
            showlegend=False,
            font=dict(size=11)
        )
        
        # Update axis labels
        fig.update_xaxes(title_text="Hour", row=1, col=1)
        fig.update_yaxes(title_text="Event Count", row=1, col=1)
        
        fig.update_xaxes(title_text="Vulture ID", row=1, col=2)
        fig.update_yaxes(title_text="Event Count", row=1, col=2)
        
        fig.update_xaxes(title_text="Distance (km)", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Event Count", row=2, col=2)
        
        # Add statistics text
        stats_text = f"""
        <b>📊 Summary Statistics</b><br>
        Total Events: {statistics.total_events:,}<br>
        Unique Pairs: {statistics.unique_pairs}<br>
        Avg Distance: {statistics.average_distance_km:.2f} km<br>
        Closest: {statistics.closest_distance_km:.2f} km<br>
        Total Duration: {statistics.total_duration_hours:.1f} hours<br>
        Most Active Pair: {statistics.most_active_pair}<br>
        Peak Hour: {statistics.peak_activity_hour}:00
        """
        
        fig.add_annotation(
            text=stats_text,
            x=0.02, y=0.98,
            xref="paper", yref="paper",
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="gray",
            borderwidth=1,
            font=dict(size=10)
        )
        
        # Generate filename with bird names
        birds_filename = "_".join(all_vultures) if len(all_vultures) <= 3 else f"{'_'.join(all_vultures[:3])}_and_{len(all_vultures)-3}_more"
        output_path = get_numbered_output_path(f'proximity_dashboard_{birds_filename}')
        fig.write_html(output_path)
        print(f"      💾 Dashboard saved to: {output_path}")
    
    def display_statistics(self, statistics: ProximityStatistics) -> None:
        """Display statistics in a formatted way"""
        self.ui.print_section("📊 PROXIMITY STATISTICS")
        
        print(f"Total proximity events: {statistics.total_events:,}")
        print(f"Unique vulture pairs: {statistics.unique_pairs}")
        print(f"Average distance: {statistics.average_distance_km:.2f} km")
        print(f"Closest encounter: {statistics.closest_distance_km:.2f} km")
        print(f"Total proximity time: {statistics.total_duration_hours:.1f} hours")
        print(f"Most active pair: {statistics.most_active_pair}")
        print(f"Peak activity hour: {statistics.peak_activity_hour}:00")
        
        print("\n🦅 Events by vulture:")
        for vulture, count in statistics.events_by_vulture.items():
            print(f"   {vulture}: {count} events")
        
        print("\n⏰ Events by hour:")
        for hour in sorted(statistics.events_by_hour.keys()):
            count = statistics.events_by_hour[hour]
            print(f"   {hour:02d}:00: {count} events")

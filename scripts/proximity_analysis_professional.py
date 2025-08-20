#!/usr/bin/env python3
"""
Professional Proximity Analysis for Bearded Vulture GPS Data

This script provides comprehensive proximity analysis capabilities for detecting
when vultures are in close proximity to each other, with advanced statistical
analysis, visualization, and export capabilities.

Features:
- Configurable proximity thresholds
- Temporal pattern analysis
- Statistical summaries and insights
- Interactive visualizations
- Data export capabilities
- Professional error handling and logging

Author: GPS Visualization Team
Version: 2.0
"""

import sys
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gps_utils import (
    DataLoader, UserInterface, haversine_distance, get_output_path,
    ensure_output_directories, logger
)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


@dataclass
class ProximityEvent:
    """Data class for storing proximity event information"""
    vulture1: str
    vulture2: str
    timestamp: datetime
    distance_km: float
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    altitude1: float
    altitude2: float
    duration_minutes: Optional[float] = None


@dataclass
class ProximityStatistics:
    """Data class for storing proximity analysis statistics"""
    total_events: int
    unique_pairs: int
    average_distance: float
    closest_distance: float
    total_duration_hours: float
    events_per_day: float
    most_active_pair: Tuple[str, str]
    most_active_time: str


class ProximityAnalyzer:
    """
    Professional-grade proximity analysis tool for vulture GPS data
    
    Provides comprehensive analysis of when vultures are in close proximity,
    including statistical analysis, visualization, and export capabilities.
    """
    
    def __init__(self, proximity_threshold_km: float = 2.0):
        """
        Initialize the proximity analyzer
        
        Args:
            proximity_threshold_km: Distance threshold in kilometers for proximity detection
        """
        self.proximity_threshold_km = proximity_threshold_km
        self.ui = UserInterface()
        self.data_loader = DataLoader()
        
        # Analysis results
        self.combined_data: Optional[pd.DataFrame] = None
        self.proximity_events: List[ProximityEvent] = []
        self.statistics: Optional[ProximityStatistics] = None
        
        # Configuration
        self.min_duration_minutes = 2  # Minimum duration to consider as proximity event
        self.cluster_eps_km = 0.5  # DBSCAN clustering parameter
        self.cluster_min_samples = 3  # Minimum samples for clustering
    
    def display_welcome(self) -> None:
        """Display welcome screen and analyzer information"""
        self.ui.print_header("🔍 VULTURE PROXIMITY ANALYSIS TOOL", 80)
        print("Professional GPS proximity analysis with advanced statistics")
        print()
        print("Analysis Features:")
        print(f"  📏 Proximity threshold: {self.proximity_threshold_km} km")
        print(f"  ⏱️  Minimum event duration: {self.min_duration_minutes} minutes")
        print("  📊 Statistical analysis and insights")
        print("  🗺️  Interactive visualizations")
        print("  💾 Export capabilities (JSON, CSV)")
        print()
    
    def configure_analysis(self) -> bool:
        """
        Configure analysis parameters
        
        Returns:
            True if configuration is successful, False otherwise
        """
        self.ui.print_section("⚙️ ANALYSIS CONFIGURATION")
        
        try:
            # Proximity threshold
            threshold_input = input(
                f"Proximity threshold in km (default {self.proximity_threshold_km}): "
            ).strip()
            
            if threshold_input:
                self.proximity_threshold_km = float(threshold_input)
                if self.proximity_threshold_km <= 0:
                    raise ValueError("Threshold must be positive")
            
            # Minimum duration
            duration_input = input(
                f"Minimum event duration in minutes (default {self.min_duration_minutes}): "
            ).strip()
            
            if duration_input:
                self.min_duration_minutes = float(duration_input)
                if self.min_duration_minutes < 0:
                    raise ValueError("Duration must be non-negative")
            
            self.ui.print_success("Configuration completed")
            print(f"📏 Proximity threshold: {self.proximity_threshold_km} km")
            print(f"⏱️  Minimum duration: {self.min_duration_minutes} minutes")
            
            return True
            
        except ValueError as e:
            self.ui.print_error(f"Invalid input: {e}")
            return False
        except KeyboardInterrupt:
            self.ui.print_info("Configuration cancelled")
            return False
    
    def load_and_prepare_data(self) -> bool:
        """
        Load GPS data and prepare for proximity analysis
        
        Returns:
            True if data loading is successful, False otherwise
        """
        self.ui.print_section("📊 DATA LOADING AND PREPARATION")
        
        try:
            # Load all CSV files
            dataframes = self.data_loader.load_all_csv_files()
            
            if not dataframes:
                self.ui.print_error("No valid GPS data files found!")
                return False
            
            if len(dataframes) < 2:
                self.ui.print_error("Need at least 2 vultures for proximity analysis!")
                return False
            
            # Combine data
            self.combined_data = pd.concat(dataframes, ignore_index=True)
            
            # Data summary
            vulture_counts = self.combined_data['vulture_id'].value_counts()
            total_points = len(self.combined_data)
            date_range = (
                self.combined_data['Timestamp [UTC]'].min(),
                self.combined_data['Timestamp [UTC]'].max()
            )
            
            print(f"✅ Loaded {total_points:,} GPS points")
            print(f"🦅 Vultures: {len(vulture_counts)}")
            for vulture, count in vulture_counts.items():
                print(f"   • {vulture}: {count:,} points")
            
            print(f"📅 Date range: {date_range[0].strftime('%d.%m.%Y')} to {date_range[1].strftime('%d.%m.%Y')}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Data loading failed: {e}")
            logger.exception("Data loading failed")
            return False
    
    def detect_proximity_events(self) -> bool:
        """
        Detect proximity events between vultures
        
        Returns:
            True if detection is successful, False otherwise
        """
        if self.combined_data is None:
            return False
        
        self.ui.print_section("🔍 PROXIMITY EVENT DETECTION")
        print("Analyzing GPS data for proximity events...")
        print()
        
        try:
            vultures = self.combined_data['vulture_id'].unique()
            proximity_events = []
            
            # Process each pair of vultures
            total_pairs = len(vultures) * (len(vultures) - 1) // 2
            pair_count = 0
            
            for i, vulture1 in enumerate(vultures):
                for j, vulture2 in enumerate(vultures[i+1:], i+1):
                    pair_count += 1
                    print(f"   Analyzing pair {pair_count}/{total_pairs}: {vulture1} ↔ {vulture2}")
                    
                    # Get data for each vulture
                    data1 = self.combined_data[self.combined_data['vulture_id'] == vulture1].copy()
                    data2 = self.combined_data[self.combined_data['vulture_id'] == vulture2].copy()
                    
                    # Find proximity events for this pair
                    pair_events = self._find_pair_proximity_events(data1, data2, vulture1, vulture2)
                    proximity_events.extend(pair_events)
                    
                    print(f"      Found {len(pair_events)} proximity events")
            
            self.proximity_events = proximity_events
            
            print(f"\n✅ Total proximity events detected: {len(self.proximity_events)}")
            
            if len(self.proximity_events) == 0:
                self.ui.print_warning("No proximity events found with current settings")
                self.ui.print_info("Try increasing the proximity threshold or reducing minimum duration")
                return False
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Proximity detection failed: {e}")
            logger.exception("Proximity detection failed")
            return False
    
    def _find_pair_proximity_events(
        self, 
        data1: pd.DataFrame, 
        data2: pd.DataFrame, 
        vulture1: str, 
        vulture2: str
    ) -> List[ProximityEvent]:
        """
        Find proximity events between a specific pair of vultures
        
        Args:
            data1: GPS data for first vulture
            data2: GPS data for second vulture
            vulture1: Name of first vulture
            vulture2: Name of second vulture
            
        Returns:
            List of proximity events for this pair
        """
        events = []
        
        # Sort data by timestamp
        data1 = data1.sort_values('Timestamp [UTC]')
        data2 = data2.sort_values('Timestamp [UTC]')
        
        # Find overlapping time periods
        for _, point1 in data1.iterrows():
            timestamp1 = point1['Timestamp [UTC]']
            
            # Find closest point in time from other vulture (within reasonable window)
            time_window = timedelta(minutes=30)  # Look within 30 minutes
            
            nearby_points = data2[
                (data2['Timestamp [UTC]'] >= timestamp1 - time_window) &
                (data2['Timestamp [UTC]'] <= timestamp1 + time_window)
            ]
            
            if len(nearby_points) == 0:
                continue
            
            # Find closest point in time
            time_diffs = abs(nearby_points['Timestamp [UTC]'] - timestamp1)
            closest_idx = time_diffs.idxmin()
            point2 = nearby_points.loc[closest_idx]
            
            # Calculate distance
            distance = haversine_distance(
                point1['Latitude'], point1['Longitude'],
                point2['Latitude'], point2['Longitude']
            )
            
            # Check if within proximity threshold
            if distance <= self.proximity_threshold_km:
                event = ProximityEvent(
                    vulture1=vulture1,
                    vulture2=vulture2,
                    timestamp=timestamp1,
                    distance_km=distance,
                    lat1=point1['Latitude'],
                    lon1=point1['Longitude'],
                    lat2=point2['Latitude'],
                    lon2=point2['Longitude'],
                    altitude1=point1['Height'],
                    altitude2=point2['Height']
                )
                events.append(event)
        
        # Filter events by minimum duration
        if self.min_duration_minutes > 0:
            events = self._filter_by_duration(events)
        
        return events
    
    def _filter_by_duration(self, events: List[ProximityEvent]) -> List[ProximityEvent]:
        """
        Filter proximity events by minimum duration
        
        Args:
            events: List of proximity events
            
        Returns:
            Filtered list of events meeting duration criteria
        """
        if not events:
            return events
        
        # Group consecutive events
        filtered_events = []
        current_group = [events[0]]
        
        for i in range(1, len(events)):
            time_diff = (events[i].timestamp - events[i-1].timestamp).total_seconds() / 60
            
            # If events are within reasonable time window, group them
            if time_diff <= self.min_duration_minutes * 2:
                current_group.append(events[i])
            else:
                # Process current group
                if len(current_group) >= 2:
                    duration = (current_group[-1].timestamp - current_group[0].timestamp).total_seconds() / 60
                    if duration >= self.min_duration_minutes:
                        # Add duration to events in group
                        for event in current_group:
                            event.duration_minutes = duration
                        filtered_events.extend(current_group)
                
                # Start new group
                current_group = [events[i]]
        
        # Process final group
        if len(current_group) >= 2:
            duration = (current_group[-1].timestamp - current_group[0].timestamp).total_seconds() / 60
            if duration >= self.min_duration_minutes:
                for event in current_group:
                    event.duration_minutes = duration
                filtered_events.extend(current_group)
        
        return filtered_events
    
    def calculate_statistics(self) -> bool:
        """
        Calculate comprehensive proximity statistics
        
        Returns:
            True if calculation is successful, False otherwise
        """
        if not self.proximity_events:
            return False
        
        self.ui.print_section("📈 STATISTICAL ANALYSIS")
        
        try:
            events_df = pd.DataFrame([
                {
                    'vulture1': event.vulture1,
                    'vulture2': event.vulture2,
                    'pair': f"{event.vulture1}-{event.vulture2}",
                    'timestamp': event.timestamp,
                    'distance_km': event.distance_km,
                    'duration_minutes': event.duration_minutes or 0
                }
                for event in self.proximity_events
            ])
            
            # Calculate statistics
            total_events = len(self.proximity_events)
            unique_pairs = events_df['pair'].nunique()
            average_distance = events_df['distance_km'].mean()
            closest_distance = events_df['distance_km'].min()
            total_duration_hours = events_df['duration_minutes'].sum() / 60
            
            # Time-based analysis
            events_df['date'] = events_df['timestamp'].dt.date
            days_with_events = events_df['date'].nunique()
            events_per_day = total_events / days_with_events if days_with_events > 0 else 0
            
            # Most active pair
            pair_counts = events_df['pair'].value_counts()
            most_active_pair = tuple(pair_counts.index[0].split('-')) if len(pair_counts) > 0 else ("", "")
            
            # Most active time
            events_df['hour'] = events_df['timestamp'].dt.hour
            hour_counts = events_df['hour'].value_counts()
            most_active_hour = hour_counts.index[0] if len(hour_counts) > 0 else 0
            most_active_time = f"{most_active_hour:02d}:00-{most_active_hour+1:02d}:00"
            
            # Store statistics
            self.statistics = ProximityStatistics(
                total_events=total_events,
                unique_pairs=unique_pairs,
                average_distance=average_distance,
                closest_distance=closest_distance,
                total_duration_hours=total_duration_hours,
                events_per_day=events_per_day,
                most_active_pair=most_active_pair,
                most_active_time=most_active_time
            )
            
            # Display statistics
            print("📊 PROXIMITY STATISTICS:")
            print("-" * 50)
            print(f"Total proximity events: {total_events:,}")
            print(f"Unique vulture pairs: {unique_pairs}")
            print(f"Average distance: {average_distance:.2f} km")
            print(f"Closest encounter: {closest_distance:.2f} km")
            print(f"Total proximity time: {total_duration_hours:.1f} hours")
            print(f"Events per day: {events_per_day:.1f}")
            print(f"Most active pair: {most_active_pair[0]} ↔ {most_active_pair[1]}")
            print(f"Most active time: {most_active_time}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Statistical analysis failed: {e}")
            logger.exception("Statistical analysis failed")
            return False
    
    def create_visualizations(self) -> bool:
        """
        Create comprehensive proximity visualizations
        
        Returns:
            True if visualization creation is successful, False otherwise
        """
        if not self.proximity_events:
            return False
        
        self.ui.print_section("🎨 CREATING VISUALIZATIONS")
        
        try:
            # Create timeline visualization
            self._create_timeline_visualization()
            
            # Create map visualization
            self._create_map_visualization()
            
            # Create statistical dashboard
            self._create_statistical_dashboard()
            
            self.ui.print_success("All visualizations created successfully!")
            return True
            
        except Exception as e:
            self.ui.print_error(f"Visualization creation failed: {e}")
            logger.exception("Visualization creation failed")
            return False
    
    def _create_timeline_visualization(self) -> None:
        """Create timeline visualization of proximity events"""
        print("   📅 Creating timeline visualization...")
        
        # Prepare data for timeline
        timeline_data = []
        for event in self.proximity_events:
            timeline_data.append({
                'timestamp': event.timestamp,
                'pair': f"{event.vulture1} ↔ {event.vulture2}",
                'distance': event.distance_km,
                'duration': event.duration_minutes or 0
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
            title='Proximity Events Timeline',
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
            yaxis_title="Vulture Pairs"
        )
        
        output_path = get_output_path('proximity_timeline.html')
        fig.write_html(output_path)
        print(f"      💾 Timeline saved to: {output_path}")
    
    def _create_map_visualization(self) -> None:
        """Create map visualization of proximity events"""
        print("   🗺️  Creating map visualization...")
        
        # Prepare map data
        map_data = []
        for event in self.proximity_events:
            # Midpoint between vultures
            mid_lat = (event.lat1 + event.lat2) / 2
            mid_lon = (event.lon1 + event.lon2) / 2
            
            map_data.append({
                'lat': mid_lat,
                'lon': mid_lon,
                'pair': f"{event.vulture1} ↔ {event.vulture2}",
                'distance': event.distance_km,
                'timestamp': event.timestamp.strftime('%d.%m.%Y %H:%M'),
                'altitude1': event.altitude1,
                'altitude2': event.altitude2
            })
        
        map_df = pd.DataFrame(map_data)
        
        # Create map with clustering using MapLibre (successor to deprecated Mapbox)
        fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lon',
            color='pair',
            size='distance',
            hover_data=['timestamp', 'distance', 'altitude1', 'altitude2'],
            mapbox_style='open-street-map',  # MapLibre-compatible style
            title='Proximity Events Map',
            height=700,
            zoom=10
        )
        
        fig.update_layout(
            mapbox=dict(
                center=dict(
                    lat=map_df['lat'].mean(),
                    lon=map_df['lon'].mean()
                )
            )
        )
        
        output_path = get_output_path('proximity_map.html')
        fig.write_html(output_path)
        print(f"      💾 Map saved to: {output_path}")
    
    def _create_statistical_dashboard(self) -> None:
        """Create comprehensive statistical dashboard"""
        print("   📊 Creating statistical dashboard...")
        
        # Prepare data for dashboard
        events_df = pd.DataFrame([
            {
                'pair': f"{event.vulture1}-{event.vulture2}",
                'distance_km': event.distance_km,
                'hour': event.timestamp.hour,
                'day_of_week': event.timestamp.strftime('%A'),
                'duration_minutes': event.duration_minutes or 0
            }
            for event in self.proximity_events
        ])
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Distance Distribution',
                'Events by Hour of Day',
                'Events by Vulture Pair',
                'Events by Day of Week'
            ],
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Distance distribution
        fig.add_trace(
            go.Histogram(x=events_df['distance_km'], name='Distance (km)', nbinsx=20),
            row=1, col=1
        )
        
        # Events by hour
        hourly_counts = events_df['hour'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(x=hourly_counts.index, y=hourly_counts.values, name='Events by Hour'),
            row=1, col=2
        )
        
        # Events by pair
        pair_counts = events_df['pair'].value_counts()
        fig.add_trace(
            go.Bar(x=pair_counts.index, y=pair_counts.values, name='Events by Pair'),
            row=2, col=1
        )
        
        # Events by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_counts = events_df['day_of_week'].value_counts().reindex(day_order, fill_value=0)
        fig.add_trace(
            go.Bar(x=daily_counts.index, y=daily_counts.values, name='Events by Day'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Proximity Analysis Dashboard",
            showlegend=False
        )
        
        output_path = get_output_path('proximity_dashboard.html')
        fig.write_html(output_path)
        print(f"      💾 Dashboard saved to: {output_path}")
    
    def export_results(self) -> bool:
        """
        Export analysis results to various formats
        
        Returns:
            True if export is successful, False otherwise
        """
        if not self.proximity_events:
            return False
        
        self.ui.print_section("💾 EXPORTING RESULTS")
        
        try:
            # Export to JSON
            json_data = {
                'analysis_settings': {
                    'proximity_threshold_km': self.proximity_threshold_km,
                    'min_duration_minutes': self.min_duration_minutes,
                    'analysis_date': datetime.now().isoformat()
                },
                'statistics': {
                    'total_events': self.statistics.total_events,
                    'unique_pairs': self.statistics.unique_pairs,
                    'average_distance': self.statistics.average_distance,
                    'closest_distance': self.statistics.closest_distance,
                    'total_duration_hours': self.statistics.total_duration_hours,
                    'events_per_day': self.statistics.events_per_day,
                    'most_active_pair': self.statistics.most_active_pair,
                    'most_active_time': self.statistics.most_active_time
                } if self.statistics else {},
                'events': [
                    {
                        'vulture1': event.vulture1,
                        'vulture2': event.vulture2,
                        'timestamp': event.timestamp.isoformat(),
                        'distance_km': event.distance_km,
                        'latitude1': event.lat1,
                        'longitude1': event.lon1,
                        'latitude2': event.lat2,
                        'longitude2': event.lon2,
                        'altitude1': event.altitude1,
                        'altitude2': event.altitude2,
                        'duration_minutes': event.duration_minutes
                    }
                    for event in self.proximity_events
                ]
            }
            
            json_path = get_output_path('proximity_analysis.json', 'analysis')
            with open(json_path, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"   💾 JSON export: {json_path}")
            
            # Export to CSV
            csv_data = []
            for event in self.proximity_events:
                csv_data.append({
                    'Vulture1': event.vulture1,
                    'Vulture2': event.vulture2,
                    'Timestamp': event.timestamp.strftime('%d.%m.%Y %H:%M:%S'),
                    'Distance_km': event.distance_km,
                    'Latitude1': event.lat1,
                    'Longitude1': event.lon1,
                    'Latitude2': event.lat2,
                    'Longitude2': event.lon2,
                    'Altitude1': event.altitude1,
                    'Altitude2': event.altitude2,
                    'Duration_minutes': event.duration_minutes
                })
            
            csv_df = pd.DataFrame(csv_data)
            csv_path = get_output_path('proximity_events.csv', 'analysis')
            csv_df.to_csv(csv_path, index=False)
            
            print(f"   💾 CSV export: {csv_path}")
            
            self.ui.print_success("Results exported successfully!")
            return True
            
        except Exception as e:
            self.ui.print_error(f"Export failed: {e}")
            logger.exception("Export failed")
            return False
    
    def display_completion_summary(self) -> None:
        """Display completion summary and next steps"""
        self.ui.print_section("🎉 ANALYSIS COMPLETE")
        
        if self.statistics:
            print("📊 Key Findings:")
            print(f"   • {self.statistics.total_events} proximity events detected")
            print(f"   • {self.statistics.unique_pairs} unique vulture pairs involved")
            print(f"   • Closest encounter: {self.statistics.closest_distance:.2f} km")
            print(f"   • Most active pair: {self.statistics.most_active_pair[0]} ↔ {self.statistics.most_active_pair[1]}")
            print()
        
        print("📁 Generated Files:")
        print("   • Interactive timeline visualization")
        print("   • Proximity events map")
        print("   • Statistical dashboard")
        print("   • JSON data export")
        print("   • CSV data export")
        print()
        print("💡 Next Steps:")
        print("   • Review visualizations for patterns")
        print("   • Analyze temporal clustering")
        print("   • Correlate with environmental data")
        print("   • Share results with research team")
    
    def run(self) -> bool:
        """
        Main execution method for proximity analysis
        
        Returns:
            True if analysis completes successfully, False otherwise
        """
        try:
            # Welcome and configuration
            self.display_welcome()
            
            if not self.configure_analysis():
                return False
            
            # Data loading
            if not self.load_and_prepare_data():
                return False
            
            # Proximity detection
            if not self.detect_proximity_events():
                return False
            
            # Statistical analysis
            if not self.calculate_statistics():
                return False
            
            # Visualizations
            if not self.create_visualizations():
                return False
            
            # Export results
            if not self.export_results():
                return False
            
            # Completion summary
            self.display_completion_summary()
            return True
            
        except KeyboardInterrupt:
            self.ui.print_info("\nAnalysis cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            logger.exception("Unexpected error in proximity analysis")
            return False


def main():
    """Main entry point for proximity analysis"""
    try:
        # Ensure output directories exist
        ensure_output_directories()
        
        # Create and run analyzer
        analyzer = ProximityAnalyzer()
        success = analyzer.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error in proximity analysis main")
        sys.exit(1)


if __name__ == "__main__":
    main()

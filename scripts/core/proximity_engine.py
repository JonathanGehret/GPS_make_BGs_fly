"""
Proximity Engine Module

Core proximity analysis algorithms and data structures for detecting
when vultures are in close proximity to each other.
"""

import pandas as pd
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from gps_utils import haversine_distance
from utils.user_interface import UserInterface


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
    duration_minutes: Optional[float] = None


@dataclass
class ProximityStatistics:
    """Data class for storing proximity analysis statistics"""
    total_events: int
    unique_pairs: int
    total_duration_hours: float
    average_distance_km: float
    closest_distance_km: float
    most_active_pair: str
    peak_activity_hour: int
    events_by_vulture: dict
    events_by_hour: dict


class ProximityEngine:
    """Core proximity analysis engine"""
    
    def __init__(self, proximity_threshold_km: float = 2.0, min_duration_minutes: float = 2.0):
        """
        Initialize the proximity engine
        
        Args:
            proximity_threshold_km: Distance threshold in kilometers for proximity detection
            min_duration_minutes: Minimum duration to consider as proximity event
        """
        self.proximity_threshold_km = proximity_threshold_km
        self.min_duration_minutes = min_duration_minutes
        self.ui = UserInterface()
        
        # Analysis results
        self.proximity_events: List[ProximityEvent] = []
        self.statistics: Optional[ProximityStatistics] = None
        self.gps_data: Optional[pd.DataFrame] = None
    
    def load_dataframes(self, dataframes: List[pd.DataFrame]) -> None:
        """
        Load GPS data from list of dataframes
        
        Args:
            dataframes: List of GPS dataframes to analyze
        """
        if not dataframes:
            raise ValueError("No dataframes provided")
        
        # Combine all dataframes
        combined_data = []
        for i, df in enumerate(dataframes):
            # Add source file identifier if not present
            if 'vulture_id' not in df.columns and 'VULTURE_ID' not in df.columns:
                df = df.copy()
                df['vulture_id'] = f'VULTURE_{i+1:02d}'
            combined_data.append(df)
        
        self.gps_data = pd.concat(combined_data, ignore_index=True)
        
        # Standardize column names
        self._standardize_columns()
        
        # Convert timestamp if needed
        if 'timestamp' in self.gps_data.columns:
            self.gps_data['timestamp'] = pd.to_datetime(self.gps_data['timestamp'])
        
        print(f"Loaded {len(self.gps_data):,} GPS points from {len(dataframes)} files")
    
    def load_data(self, data_path: str) -> None:
        """
        Load GPS data from CSV file (alternative method)
        
        Args:
            data_path: Path to GPS data CSV file
        """
        self.gps_data = pd.read_csv(data_path)
        self._standardize_columns()
        
        if 'timestamp' in self.gps_data.columns:
            self.gps_data['timestamp'] = pd.to_datetime(self.gps_data['timestamp'])
        
        print(f"Loaded {len(self.gps_data):,} GPS points from {data_path}")
    
    def _standardize_columns(self) -> None:
        """Standardize column names for consistent access"""
        # Map common column name variations
        column_mapping = {
            'VULTURE_ID': 'vulture_id',
            'LAT': 'latitude',
            'LON': 'longitude', 
            'LONGITUDE': 'longitude',
            'LATITUDE': 'latitude',
            'TIME': 'timestamp',
            'TIMESTAMP': 'timestamp',
            'Timestamp [UTC]': 'timestamp',
            'Latitude': 'latitude',
            'Longitude': 'longitude'
        }
        
        # Rename columns
        for old_name, new_name in column_mapping.items():
            if old_name in self.gps_data.columns:
                self.gps_data = self.gps_data.rename(columns={old_name: new_name})
    
    def configure_parameters(self) -> bool:
        """
        Configure analysis parameters through user input
        
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
    
    def analyze_proximity(self) -> List[ProximityEvent]:
        """
        Analyze proximity between vultures using loaded data
        
        Returns:
            List of proximity events
        """
        if self.gps_data is None:
            raise ValueError("No GPS data loaded. Call load_dataframes() or load_data() first.")
            
        self.ui.print_section("🔍 PROXIMITY ANALYSIS")
        print("Detecting proximity events between vultures...")
        
        # Get unique vultures
        vultures = self.gps_data['vulture_id'].unique()
        
        if len(vultures) < 2:
            self.ui.print_warning("Need at least 2 vultures for proximity analysis")
            return []
        
        print(f"Analyzing {len(vultures)} vultures: {', '.join(vultures)}")
        
        proximity_events = []
        total_pairs = len(vultures) * (len(vultures) - 1) // 2
        pair_count = 0
        
        # Analyze each pair of vultures
        for i, vulture1 in enumerate(vultures):
            for vulture2 in vultures[i+1:]:
                pair_count += 1
                print(f"   🔍 Analyzing pair {pair_count}/{total_pairs}: {vulture1} & {vulture2}")
                
                # Get data for both vultures
                data1 = self.gps_data[self.gps_data['vulture_id'] == vulture1].copy()
                data2 = self.gps_data[self.gps_data['vulture_id'] == vulture2].copy()
                
                # Find proximity events for this pair
                pair_events = self._find_proximity_events_for_pair(
                    vulture1, data1, vulture2, data2
                )
                proximity_events.extend(pair_events)
        
        print(f"\n✅ Found {len(proximity_events)} proximity events")
        self.proximity_events = proximity_events
        return proximity_events
    
    def _find_proximity_events_for_pair(self, vulture1: str, data1: pd.DataFrame, 
                                       vulture2: str, data2: pd.DataFrame) -> List[ProximityEvent]:
        """
        Find proximity events between a specific pair of vultures
        
        Args:
            vulture1: First vulture ID
            data1: GPS data for first vulture
            vulture2: Second vulture ID  
            data2: GPS data for second vulture
            
        Returns:
            List of proximity events for this pair
        """
        events = []
        
        if data1.empty or data2.empty:
            return events
        
        # Sort by timestamp
        data1 = data1.sort_values('timestamp')
        data2 = data2.sort_values('timestamp')
        
        # For each point of vulture1, find the closest point in time from vulture2
        for _, row1 in data1.iterrows():
            timestamp1 = row1['timestamp']
            lat1, lon1 = row1['latitude'], row1['longitude']
            
            # Find closest point in time from vulture2 (within reasonable time window)
            time_diffs = np.abs((data2['timestamp'] - timestamp1).dt.total_seconds())
            
            if len(time_diffs) == 0:
                continue
                
            min_time_diff_idx = time_diffs.idxmin()
            min_time_diff_value = time_diffs.loc[min_time_diff_idx]
            
            # Only consider if within 30 minutes
            if min_time_diff_value <= 1800:  # 30 minutes
                row2 = data2.loc[min_time_diff_idx]
                lat2, lon2 = row2['latitude'], row2['longitude']
                
                # Calculate distance
                distance_km = haversine_distance(lat1, lon1, lat2, lon2)
                
                # Check if within proximity threshold
                if distance_km <= self.proximity_threshold_km:
                    events.append(ProximityEvent(
                        vulture1=vulture1,
                        vulture2=vulture2,
                        timestamp=timestamp1,
                        distance_km=distance_km,
                        lat1=lat1,
                        lon1=lon1,
                        lat2=lat2,
                        lon2=lon2
                    ))
        
        return events
    
    def calculate_statistics(self) -> ProximityStatistics:
        """
        Calculate comprehensive statistics from proximity events
        
        Returns:
            ProximityStatistics object with analysis results
        """
        if not self.proximity_events:
            return ProximityStatistics(
                total_events=0, unique_pairs=0, total_duration_hours=0.0,
                average_distance_km=0.0, closest_distance_km=0.0,
                most_active_pair="None", peak_activity_hour=0,
                events_by_vulture={}, events_by_hour={}
            )
        
        # Basic statistics
        total_events = len(self.proximity_events)
        distances = [event.distance_km for event in self.proximity_events]
        average_distance = np.mean(distances)
        closest_distance = min(distances)
        
        # Unique pairs
        pairs = set()
        for event in self.proximity_events:
            pair = tuple(sorted([event.vulture1, event.vulture2]))
            pairs.add(pair)
        unique_pairs = len(pairs)
        
        # Events by vulture
        events_by_vulture = {}
        for event in self.proximity_events:
            for vulture in [event.vulture1, event.vulture2]:
                events_by_vulture[vulture] = events_by_vulture.get(vulture, 0) + 1
        
        # Events by hour
        events_by_hour = {}
        for event in self.proximity_events:
            hour = event.timestamp.hour
            events_by_hour[hour] = events_by_hour.get(hour, 0) + 1
        
        # Most active pair
        pair_counts = {}
        for event in self.proximity_events:
            pair = f"{event.vulture1} & {event.vulture2}"
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
        
        most_active_pair = max(pair_counts.items(), key=lambda x: x[1])[0] if pair_counts else "None"
        
        # Peak activity hour
        peak_activity_hour = max(events_by_hour.items(), key=lambda x: x[1])[0] if events_by_hour else 0
        
        # Estimate total duration (simplified)
        total_duration_hours = len(self.proximity_events) * (self.min_duration_minutes / 60)
        
        self.statistics = ProximityStatistics(
            total_events=total_events,
            unique_pairs=unique_pairs,
            total_duration_hours=total_duration_hours,
            average_distance_km=average_distance,
            closest_distance_km=closest_distance,
            most_active_pair=most_active_pair,
            peak_activity_hour=peak_activity_hour,
            events_by_vulture=events_by_vulture,
            events_by_hour=events_by_hour
        )
        
        return self.statistics
    
    def get_events_dataframe(self) -> pd.DataFrame:
        """
        Convert proximity events to pandas DataFrame for analysis
        
        Returns:
            DataFrame with proximity events
        """
        if not self.proximity_events:
            return pd.DataFrame()
        
        events_data = []
        for event in self.proximity_events:
            events_data.append({
                'vulture1': event.vulture1,
                'vulture2': event.vulture2,
                'timestamp': event.timestamp,
                'distance_km': event.distance_km,
                'lat1': event.lat1,
                'lon1': event.lon1,
                'lat2': event.lat2,
                'lon2': event.lon2,
                'hour': event.timestamp.hour,
                'date': event.timestamp.date()
            })
        
        return pd.DataFrame(events_data)

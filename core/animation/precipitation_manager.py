"""
Precipitation Data Manager

Handles all precipitation-related functionality including API calls,
data caching, heatmap generation, and timestamp matching.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import requests

from utils.user_interface import UserInterface


class PrecipitationManager:
    """Manages precipitation data fetching, caching, and processing."""

    def __init__(self, ui: UserInterface):
        self.ui = ui
        self.precipitation_cache = {}  # Cache for API responses
        self.enable_precipitation = os.environ.get('ENABLE_PRECIPITATION', '0') == '1'
        self.enable_precipitation_heatmap = os.environ.get('ENABLE_PRECIPITATION_HEATMAP', '0') == '1'
        self.heatmap_data = None  # Store heatmap data

    def fetch_precipitation_data(self, lat: float, lon: float, start_date: str, end_date: str) -> dict:
        """Fetch hourly precipitation data from Open-Meteo API"""
        cache_key = f"{lat:.4f}_{lon:.4f}_{start_date}_{end_date}"
        if cache_key in self.precipitation_cache:
            return self.precipitation_cache[cache_key]

        try:
            # Check if the date range is within the forecast API limits
            today = datetime.now()
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')

            # Forecast API supports up to 92 days back and 16 days forward
            forecast_start_limit = today - timedelta(days=92)

            use_historical = start_dt < forecast_start_limit

            if use_historical:
                # Use historical weather API for older dates
                url = (
                    f"https://archive-api.open-meteo.com/v1/archive?"
                    f"latitude={lat}&longitude={lon}"
                    "&hourly=precipitation"
                    "&timezone=Europe/Berlin"
                    f"&start_date={start_date}"
                    f"&end_date={end_date}"
                )
                self.ui.print_info(f"🌧️ Fetching historical precipitation data for {lat:.4f}, {lon:.4f} ({start_date} to {end_date})")
            else:
                # Use forecast API for recent dates
                url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    "&hourly=precipitation"
                    "&timezone=Europe/Berlin"
                    f"&start_date={start_date}"
                    f"&end_date={end_date}"
                )
                self.ui.print_info(f"🌧️ Fetching forecast precipitation data for {lat:.4f}, {lon:.4f} ({start_date} to {end_date})")

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.precipitation_cache[cache_key] = data

            # Debug: show sample data
            if 'hourly' in data and 'time' in data['hourly']:
                times = data['hourly']['time']
                if len(times) > 0:
                    print(f"📊 API returned {len(times)} time points, sample: {times[0]} to {times[-1]}")

            return data

        except Exception as e:
            self.ui.print_warning(f"Failed to fetch precipitation data: {e}")
            # Try fallback with past_days for very recent data
            try:
                fallback_url = (
                    f"https://api.open-meteo.com/v1/forecast?"
                    f"latitude={lat}&longitude={lon}"
                    "&hourly=precipitation"
                    "&timezone=Europe/Berlin"
                    "&past_days=7"
                )
                self.ui.print_info(f"🌧️ Fallback: Fetching recent precipitation data (past 7 days) for {lat:.4f}, {lon:.4f}")
                response = requests.get(fallback_url, timeout=30)
                response.raise_for_status()

                data = response.json()
                self.precipitation_cache[cache_key] = data
                print(f"📊 Fallback API returned {len(data['hourly']['time'])} time points")
                return data

            except Exception as fallback_e:
                self.ui.print_warning(f"Fallback also failed: {fallback_e}")
                return None

    def get_precipitation_for_timestamp(self, data: dict, timestamp: pd.Timestamp) -> float:
        """Get precipitation value for a specific timestamp"""
        if not data or 'hourly' not in data:
            return 0.0

        times = data['hourly'].get('time', [])
        precipitations = data['hourly'].get('precipitation', [])

        if not times or not precipitations:
            return 0.0

        # Convert UTC timestamp to Europe/Berlin timezone to match API data
        try:
            # Ensure timestamp is timezone-aware
            if timestamp.tz is None:
                timestamp = timestamp.tz_localize('UTC')

            # Convert to Europe/Berlin timezone
            berlin_tz = timestamp.tz_convert('Europe/Berlin')

            # For precipitation data, the value at time T represents rain during [T, T+1)
            # So we want to find the precipitation for the hour that CONTAINS our timestamp
            target_time = berlin_tz.replace(minute=0, second=0, microsecond=0)
            target_str = target_time.strftime('%Y-%m-%dT%H:%M')

            # Debug: print conversion details (only for first few calls)
            if not hasattr(self, '_debug_count'):
                self._debug_count = 0
            if self._debug_count < 3:
                print(f"🔍 UTC {timestamp} -> Berlin {berlin_tz} -> target {target_str}")
                self._debug_count += 1

            for i, time_str in enumerate(times):
                if time_str == target_str:
                    return precipitations[i]

        except Exception as e:
            print(f"⚠️ Timezone conversion error: {e}")
            # Fallback: try direct matching without timezone conversion
            target_time = timestamp.replace(minute=0, second=0, microsecond=0)
            target_str = target_time.strftime('%Y-%m-%dT%H:%M')

            for i, time_str in enumerate(times):
                if time_str == target_str:
                    return precipitations[i]

        return 0.0

    def generate_precipitation_heatmap_data(self, lat_min: float, lat_max: float, lon_min: float, lon_max: float,
                                          start_date: str, end_date: str, grid_resolution: int = 20) -> dict:
        """Generate precipitation data for a grid across the map area for heatmap visualization"""
        import numpy as np

        # Create grid of points
        lat_grid = np.linspace(lat_min, lat_max, grid_resolution)
        lon_grid = np.linspace(lon_min, lon_max, grid_resolution)

        heatmap_data = {
            'lat': [],
            'lon': [],
            'precipitation': [],
            'time_data': {}  # Store time-series data for animation
        }

        self.ui.print_info(f"🌧️ Generating precipitation heatmap grid ({grid_resolution}x{grid_resolution} = {grid_resolution**2} points)")

        # Fetch data for each grid point
        for lat in lat_grid:
            for lon in lon_grid:
                data = self.fetch_precipitation_data(lat, lon, start_date, end_date)
                if data and 'hourly' in data:
                    times = data['hourly'].get('time', [])
                    precipitations = data['hourly'].get('precipitation', [])

                    if times and precipitations:
                        # Store base precipitation (will be updated per frame)
                        avg_precip = np.mean(precipitations) if precipitations else 0
                        heatmap_data['lat'].append(lat)
                        heatmap_data['lon'].append(lon)
                        heatmap_data['precipitation'].append(avg_precip)

                        # Store time-series data for this location
                        location_key = f"{lat:.4f}_{lon:.4f}"
                        heatmap_data['time_data'][location_key] = {
                            'times': times,
                            'precipitations': precipitations
                        }

        self.ui.print_success(f"✅ Generated heatmap data for {len(heatmap_data['lat'])} grid points")
        return heatmap_data

    def get_heatmap_precipitation_for_timestamp(self, heatmap_data: dict, timestamp: pd.Timestamp) -> list:
        """Get precipitation values for all heatmap points at a specific timestamp"""
        if not heatmap_data or 'time_data' not in heatmap_data:
            return []

        # Convert UTC timestamp to Europe/Berlin timezone
        try:
            if timestamp.tz is None:
                timestamp = timestamp.tz_localize('UTC')
            berlin_tz = timestamp.tz_convert('Europe/Berlin')
            target_time = berlin_tz.replace(minute=0, second=0, microsecond=0)
            target_str = target_time.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            # Fallback
            target_time = timestamp.replace(minute=0, second=0, microsecond=0)
            target_str = target_time.strftime('%Y-%m-%dT%H:%M')

        precip_values = []
        for i, (lat, lon) in enumerate(zip(heatmap_data['lat'], heatmap_data['lon'])):
            location_key = f"{lat:.4f}_{lon:.4f}"
            if location_key in heatmap_data['time_data']:
                time_data = heatmap_data['time_data'][location_key]
                times = time_data['times']
                precipitations = time_data['precipitations']

                # Find matching time
                for j, time_str in enumerate(times):
                    if time_str == target_str:
                        precip_values.append(precipitations[j])
                        break
                else:
                    precip_values.append(0.0)  # No data for this time
            else:
                precip_values.append(0.0)

        return precip_values

    def add_precipitation_data_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add precipitation data to the dataframe"""
        if df.empty:
            return df

        # Get date range for API call (extend by 1 day on each side for safety)
        min_date = df['Timestamp [UTC]'].min()
        max_date = df['Timestamp [UTC]'].max()

        # Ensure timestamps are timezone-aware
        if min_date.tz is None:
            min_date = min_date.tz_localize('UTC')
        if max_date.tz is None:
            max_date = max_date.tz_localize('UTC')

        start_date = (min_date - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        end_date = (max_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

        print(f"📅 Precipitation data range: {start_date} to {end_date}")

        # Get unique coordinates (to minimize API calls)
        coords = df[['Latitude', 'Longitude']].drop_duplicates()

        # Fetch precipitation data for each unique coordinate
        precipitation_data = {}
        for _, row in coords.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            data = self.fetch_precipitation_data(lat, lon, start_date, end_date)
            if data:
                precipitation_data[(lat, lon)] = data
                print(f"✅ Precipitation data loaded for {lat:.4f}, {lon:.4f}")
            else:
                print(f"❌ Failed to load precipitation data for {lat:.4f}, {lon:.4f}")

        # Add precipitation column
        df = df.copy()
        df['precipitation_mm'] = 0.0

        # Match each point to precipitation data
        matched_count = 0
        for idx, row in df.iterrows():
            lat, lon = row['Latitude'], row['Longitude']
            timestamp = row['Timestamp [UTC]']

            coord_key = (lat, lon)
            if coord_key in precipitation_data:
                precip = self.get_precipitation_for_timestamp(precipitation_data[coord_key], timestamp)
                df.at[idx, 'precipitation_mm'] = precip
                if precip > 0:
                    matched_count += 1

        print(f"🌧️ Matched {matched_count} points with precipitation data")
        return df

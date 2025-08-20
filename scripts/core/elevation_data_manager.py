"""
Elevation Data Manager

Handles downloading, caching, and managing elevation models for 3D terrain visualization.
Supports multiple data sources and regional datasets with persistent caching.
"""

import pickle
import numpy as np
import requests
import time
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from pathlib import Path
from utils.user_interface import UserInterface


@dataclass
class RegionBounds:
    """Defines geographical bounds for a region"""
    name: str
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    description: str


@dataclass
class ElevationData:
    """Contains elevation data for a region"""
    region_name: str
    lons: np.ndarray
    lats: np.ndarray
    elevations: np.ndarray
    resolution: int
    bounds: RegionBounds
    download_date: str


class ElevationDataManager:
    """Manages downloading and caching of elevation data for 3D visualizations"""
    
    # Predefined regions for Austrian Alps
    PREDEFINED_REGIONS = {
        'berchtesgaden_full': RegionBounds(
            name='berchtesgaden_full',
            lat_min=47.45,  # South: Bischofshofen/Saalfelden area
            lat_max=47.75,  # North: Beyond Berchtesgaden
            lon_min=12.85,  # West: Extended Berchtesgaden
            lon_max=13.45,  # East: Tennengebirge region
            description='Full Berchtesgaden to Tennengebirge region (Bischofshofen/Saalfelden)'
        ),
        'berchtesgaden_core': RegionBounds(
            name='berchtesgaden_core',
            lat_min=47.52,
            lat_max=47.65,
            lon_min=12.94,
            lon_max=13.10,
            description='Core Berchtesgaden National Park area'
        ),
        'tennengebirge': RegionBounds(
            name='tennengebirge',
            lat_min=47.50,
            lat_max=47.68,
            lon_min=13.15,
            lon_max=13.45,
            description='Tennengebirge mountain range'
        ),
        'salzburg_south': RegionBounds(
            name='salzburg_south',
            lat_min=47.45,
            lat_max=47.60,
            lon_min=12.85,
            lon_max=13.20,
            description='Southern Salzburg region (Bischofshofen/Saalfelden)'
        )
    }
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize elevation data manager
        
        Args:
            cache_dir: Directory for caching elevation data (default: project/elevation_cache)
        """
        self.ui = UserInterface()
        
        # Set up cache directory
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.cache_dir = project_root / 'elevation_cache'
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache for loaded elevation data
        self.loaded_regions: Dict[str, ElevationData] = {}
        
        print(f"📁 Elevation cache directory: {self.cache_dir}")
    
    def list_available_regions(self) -> None:
        """Display available predefined regions"""
        self.ui.print_section("🏔️ AVAILABLE REGIONS")
        
        for region_id, bounds in self.PREDEFINED_REGIONS.items():
            cache_status = "✅ Cached" if self._is_region_cached(region_id) else "📥 Not cached"
            print(f"  {region_id}:")
            print(f"    📝 {bounds.description}")
            print(f"    🗺️  Lat: {bounds.lat_min:.3f} to {bounds.lat_max:.3f}")
            print(f"    🗺️  Lon: {bounds.lon_min:.3f} to {bounds.lon_max:.3f}")
            print(f"    💾 {cache_status}")
            print()
    
    def get_elevation_data(self, region_name: str, resolution: int = 100, 
                          force_download: bool = False) -> Optional[ElevationData]:
        """
        Get elevation data for a region (from cache or download)
        
        Args:
            region_name: Name of predefined region or 'custom'
            resolution: Grid resolution for elevation data
            force_download: Force re-download even if cached
            
        Returns:
            ElevationData object or None if failed
        """
        # Check if already loaded in memory
        cache_key = f"{region_name}_{resolution}"
        if cache_key in self.loaded_regions and not force_download:
            print(f"🔄 Using cached elevation data for {region_name}")
            return self.loaded_regions[cache_key]
        
        # Check if region exists in predefined regions
        if region_name not in self.PREDEFINED_REGIONS:
            self.ui.print_error(f"Unknown region: {region_name}")
            self.ui.print_info("Available regions: " + ", ".join(self.PREDEFINED_REGIONS.keys()))
            return None
        
        bounds = self.PREDEFINED_REGIONS[region_name]
        
        # Try to load from disk cache
        if not force_download:
            cached_data = self._load_from_cache(region_name, resolution)
            if cached_data:
                self.loaded_regions[cache_key] = cached_data
                return cached_data
        
        # Download elevation data
        self.ui.print_section(f"🏔️ DOWNLOADING ELEVATION DATA: {region_name.upper()}")
        print(f"📊 Resolution: {resolution}x{resolution} grid")
        print(f"🗺️  Area: {bounds.description}")
        print("⚠️  This may take several minutes...")
        
        elevation_data = self._download_elevation_data(bounds, resolution)
        if elevation_data:
            # Save to cache
            self._save_to_cache(elevation_data)
            self.loaded_regions[cache_key] = elevation_data
            self.ui.print_success(f"✅ Elevation data for {region_name} ready!")
            return elevation_data
        else:
            self.ui.print_error(f"Failed to download elevation data for {region_name}")
            return None
    
    def _is_region_cached(self, region_name: str, resolution: int = 100) -> bool:
        """Check if region is cached on disk"""
        cache_file = self.cache_dir / f"{region_name}_{resolution}.pkl"
        return cache_file.exists()
    
    def _load_from_cache(self, region_name: str, resolution: int) -> Optional[ElevationData]:
        """Load elevation data from disk cache"""
        cache_file = self.cache_dir / f"{region_name}_{resolution}.pkl"
        
        if cache_file.exists():
            try:
                print(f"📂 Loading cached elevation data for {region_name}...")
                with open(cache_file, 'rb') as f:
                    elevation_data = pickle.load(f)
                print(f"✅ Loaded {elevation_data.resolution}x{elevation_data.resolution} elevation grid from cache")
                return elevation_data
            except Exception as e:
                self.ui.print_warning(f"Failed to load cache: {e}")
                return None
        
        return None
    
    def _save_to_cache(self, elevation_data: ElevationData) -> None:
        """Save elevation data to disk cache"""
        cache_file = self.cache_dir / f"{elevation_data.region_name}_{elevation_data.resolution}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(elevation_data, f)
            print(f"💾 Cached elevation data to: {cache_file}")
        except Exception as e:
            self.ui.print_warning(f"Failed to save cache: {e}")
    
    def _download_elevation_data(self, bounds: RegionBounds, resolution: int) -> Optional[ElevationData]:
        """Download elevation data from Open Elevation API with optimized batching"""
        try:
            # Create coordinate grid
            lats = np.linspace(bounds.lat_min, bounds.lat_max, resolution)
            lons = np.linspace(bounds.lon_min, bounds.lon_max, resolution)
            
            # Create all coordinate pairs
            locations = []
            for lat in lats:
                for lon in lons:
                    locations.append((lat, lon))
            
            print(f"📡 Downloading elevation for {len(locations):,} points...")
            
            # Download in optimized batches
            elevations_flat = self._download_elevation_batch(locations)
            
            if len(elevations_flat) != len(locations):
                self.ui.print_error("Incomplete elevation data received")
                return None
            
            # Reshape to 2D array
            elevations = np.array(elevations_flat).reshape((resolution, resolution))
            
            # Create ElevationData object
            from datetime import datetime
            elevation_data = ElevationData(
                region_name=bounds.name,
                lons=lons,
                lats=lats,
                elevations=elevations,
                resolution=resolution,
                bounds=bounds,
                download_date=datetime.now().isoformat()
            )
            
            print(f"✅ Downloaded {resolution}x{resolution} elevation grid")
            print(f"🏔️  Elevation range: {elevations.min():.0f}m to {elevations.max():.0f}m")
            
            return elevation_data
            
        except Exception as e:
            self.ui.print_error(f"Elevation download failed: {e}")
            return None
    
    def _download_elevation_batch(self, locations: List[Tuple[float, float]], 
                                 max_batch_size: int = 50) -> List[float]:
        """Download elevation data in optimized batches"""
        elevations = []
        total_batches = len(locations) // max_batch_size + (1 if len(locations) % max_batch_size > 0 else 0)
        
        for i, batch_start in enumerate(range(0, len(locations), max_batch_size)):
            batch = locations[batch_start:batch_start + max_batch_size]
            
            # Show progress
            print(f"   📊 Batch {i+1}/{total_batches} ({len(batch)} points)...")
            
            # Create location string for API
            location_string = "|".join([f"{lat},{lon}" for lat, lon in batch])
            
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    url = f"https://api.open-elevation.com/api/v1/lookup?locations={location_string}"
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'results' in data and len(data['results']) == len(batch):
                            batch_elevations = [result['elevation'] for result in data['results']]
                            elevations.extend(batch_elevations)
                            break
                        else:
                            self.ui.print_warning("Incomplete batch data, using defaults")
                            elevations.extend([1000] * len(batch))  # Alpine default
                            break
                    else:
                        raise Exception(f"API returned status {response.status_code}")
                        
                except Exception as e:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"      ⚠️ Retry {retry_count}/{max_retries} after error: {e}")
                        time.sleep(2 ** retry_count)  # Exponential backoff
                    else:
                        self.ui.print_warning(f"Batch failed after {max_retries} retries, using defaults")
                        elevations.extend([1000] * len(batch))  # Alpine default
            
            # Rate limiting between batches
            if i < total_batches - 1:  # Don't wait after the last batch
                time.sleep(1)  # 1 second between batches
        
        return elevations
    
    def create_custom_region(self, name: str, lat_min: float, lat_max: float, 
                           lon_min: float, lon_max: float, description: str) -> RegionBounds:
        """
        Create a custom region definition
        
        Args:
            name: Region identifier
            lat_min, lat_max: Latitude bounds
            lon_min, lon_max: Longitude bounds
            description: Human-readable description
            
        Returns:
            RegionBounds object
        """
        custom_region = RegionBounds(
            name=name,
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            description=description
        )
        
        # Add to predefined regions for this session
        self.PREDEFINED_REGIONS[name] = custom_region
        
        return custom_region
    
    def get_region_info(self, elevation_data: ElevationData) -> Dict:
        """Get summary information about elevation data"""
        return {
            'region_name': elevation_data.region_name,
            'resolution': f"{elevation_data.resolution}x{elevation_data.resolution}",
            'elevation_range': f"{elevation_data.elevations.min():.0f}m - {elevation_data.elevations.max():.0f}m",
            'area_km2': self._calculate_area_km2(elevation_data.bounds),
            'download_date': elevation_data.download_date[:10],  # Just the date part
            'bounds': {
                'lat_range': f"{elevation_data.bounds.lat_min:.3f} to {elevation_data.bounds.lat_max:.3f}",
                'lon_range': f"{elevation_data.bounds.lon_min:.3f} to {elevation_data.bounds.lon_max:.3f}"
            }
        }
    
    def _calculate_area_km2(self, bounds: RegionBounds) -> float:
        """Rough calculation of area in km²"""
        # Rough conversion: 1 degree lat ≈ 111 km, 1 degree lon ≈ 111 * cos(lat) km
        lat_km = (bounds.lat_max - bounds.lat_min) * 111
        avg_lat = (bounds.lat_min + bounds.lat_max) / 2
        lon_km = (bounds.lon_max - bounds.lon_min) * 111 * np.cos(np.radians(avg_lat))
        return lat_km * lon_km

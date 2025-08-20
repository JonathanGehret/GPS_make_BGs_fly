"""
3D System Demo Script

Quick test of the 3D visualization system with sample data.
Tests elevation data download and 3D rendering capabilities.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.elevation_data_manager import ElevationDataManager
from core.animation_3d_engine import Animation3DEngine
from utils.user_interface_3d import UserInterface3D
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def create_sample_gps_data():
    """Create sample GPS data for testing in Austrian Alps region"""
    
    # Use Salzburg area coordinates (Saalfelden to Bischofshofen region)
    # This should match the 'salzburg_south' region bounds:
    # lat_min=47.45, lat_max=47.60, lon_min=12.85, lon_max=13.20
    
    base_lat = 47.52  # Center of Saalfelden/Bischofshofen area
    base_lon = 13.00  # Center longitude
    
    # Create sample flight paths for 2 vultures
    sample_data = []
    
    start_time = datetime.now() - timedelta(hours=3)
    
    # Vulture 1: Circular flight pattern around Saalfelden area
    for i in range(50):
        time_offset = i * 3  # 3 minutes between points
        angle = (i * 7.2) % 360  # Full circle every 50 points
        radius = 0.03  # About 3 km radius within region bounds
        
        lat = base_lat + radius * np.cos(np.radians(angle))
        lon = base_lon + radius * np.sin(np.radians(angle))
        altitude = 1200 + 200 * np.sin(np.radians(angle * 2))  # Varying altitude
        
        sample_data.append({
            'Timestamp [UTC]': start_time + timedelta(minutes=time_offset),
            'Latitude': lat,
            'Longitude': lon,
            'Height': altitude,
            'vulture_id': 'Sample Vulture 1'
        })
    
    # Vulture 2: Linear flight with turns (Saalfelden to Bischofshofen direction)
    for i in range(40):
        time_offset = i * 4  # 4 minutes between points
        
        if i < 15:
            # Flying southwest towards Bischofshofen
            lat = base_lat - (i * 0.002)  # Moving south
            lon = base_lon - 0.05 + (i * 0.002)  # Moving slightly west
        elif i < 30:
            # Flying east towards Tennengebirge
            lat = base_lat - 0.03
            lon = base_lon - 0.02 + ((i - 15) * 0.004)
        else:
            # Flying back north
            lat = base_lat - 0.03 + ((i - 30) * 0.003)
            lon = base_lon + 0.05
        
        altitude = 1300 + 150 * np.sin(i * 0.3)  # Gentle altitude changes
        
        sample_data.append({
            'Timestamp [UTC]': start_time + timedelta(minutes=time_offset),
            'Latitude': lat,
            'Longitude': lon,
            'Height': altitude,
            'vulture_id': 'Sample Vulture 2'
        })
    
    return pd.DataFrame(sample_data)


def main():
    """Demo the 3D system with sample data"""
    
    ui = UserInterface3D()
    
    try:
        ui.show_3d_welcome()
        
        # Initialize components
        print("🔧 Initializing 3D system components...")
        elevation_manager = ElevationDataManager()
        animation_engine = Animation3DEngine(elevation_manager)
        ui.set_elevation_manager(elevation_manager)
        
        # Create sample data
        print("📊 Creating sample GPS data...")
        sample_data = create_sample_gps_data()
        print(f"   ✅ Generated {len(sample_data)} GPS points for 2 sample vultures")
        
        # Get terrain settings (with defaults for demo)
        print("\n🗺️ Using demo terrain settings...")
        region = "saalfelden_bischofshofen"  # 30x30km region you requested
        resolution = 50  # Lower resolution for speed
        
        print(f"   🏔️ Region: {region} (30x30km square: Saalfelden to Bischofshofen)")
        print(f"   📐 Resolution: {resolution}")
        
        # Setup terrain
        ui.show_3d_progress("terrain_check")
        terrain_success = animation_engine.setup_terrain(
            region_name=region,
            resolution=resolution,
            force_download=False
        )
        
        if not terrain_success:
            ui.print_error("Failed to setup terrain data")
            return False
        
        # Load GPS data
        ui.show_3d_progress("gps_process")
        animation_engine.load_processed_data(sample_data)
        
        # Create full animation with time controls
        ui.show_3d_progress("render_3d", "Creating animated 3D view with time controls")
        output_path = animation_engine.create_3d_visualization('full')
        
        if output_path:
            # Show completion info
            info = animation_engine.get_3d_info()
            ui.show_3d_completion_info(info, output_path)
            
            ui.print_success("🎉 3D Demo Complete!")
            print("\n📂 Open the file to view your 3D visualization:")
            print(f"   {output_path}")
            
            return True
        else:
            ui.print_error("Demo failed to create 3D visualization")
            return False
    
    except KeyboardInterrupt:
        ui.print_warning("\n⚠️ Demo interrupted by user")
        return False
    except Exception as e:
        ui.print_error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🏔️ 3D VISUALIZATION DEMO")
    print("=" * 50)
    print("This demo will:")
    print("  • Create sample GPS flight data")
    print("  • Download real terrain data (if needed)")
    print("  • Generate a 3D visualization")
    print("  • Show the complete 3D system in action")
    print()
    
    input("Press Enter to start the demo...")
    print()
    
    success = main()
    sys.exit(0 if success else 1)

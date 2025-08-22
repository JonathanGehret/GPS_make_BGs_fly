"""
3D Animation - Main Script

Entry point for 3D GPS visualization with real terrain data.
Uses modular architecture with downloadable elevation models.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import DataLoader, ensure_output_directories
from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.elevation_data_manager import ElevationDataManager
from core.animation_3d_engine import Animation3DEngine
import pandas as pd


def main():
    """Main 3D animation workflow"""
    ui = UserInterface()
    
    try:
        # Initialize system
        ui.print_header("🏔️ 3D GPS VISUALIZATION WITH REAL TERRAIN", 80)
        ensure_output_directories()
        
        # Load GPS data
        ui.print_section("📁 LOADING GPS DATA")
        data_loader = DataLoader()
        dataframes = data_loader.load_all_csv_files()
        
        if not dataframes:
            ui.print_error("No GPS data found!")
            return False
        
        print(f"Loaded {len(dataframes)} GPS data files")
        
        # Initialize components
        elevation_manager = ElevationDataManager()
        animation_engine = Animation3DEngine(elevation_manager)
        
        # Show available regions and get user choice
        ui.print_section("🗺️ TERRAIN REGION SELECTION")
        elevation_manager.list_available_regions()
        
        # Get region selection from user
        region_choice = ui.get_user_input(
            "Select region (berchtesgaden_full recommended)", 
            "berchtesgaden_full", 
            str
        )
        
        # Get terrain resolution
        resolution_choice = ui.get_user_input(
            "Terrain resolution (higher = more detail, slower download)", 
            "100", 
            int
        )
        
        if resolution_choice < 20 or resolution_choice > 200:
            ui.print_warning("Resolution should be between 20-200, using 100")
            resolution_choice = 100
        
        # Setup terrain data
        terrain_success = animation_engine.setup_terrain(
            region_name=region_choice,
            resolution=resolution_choice,
            force_download=False
        )
        
        if not terrain_success:
            ui.print_error("Failed to setup terrain data")
            return False
        
        # Get performance optimization for GPS data
        ui.print_section("⚡ GPS DATA OPTIMIZATION")
        optimizer = PerformanceOptimizer()
        
        time_step = ui.get_user_input(
            "Time step for GPS filtering (seconds, larger = fewer points)", 
            "120", 
            int
        )
        
        # Process GPS data
        ui.print_section("🔄 PROCESSING GPS DATA")
        processed_dataframes = []
        
        for i, df in enumerate(dataframes):
            print(f"   📊 Processing file {i+1}/{len(dataframes)}...")
            
            # Apply time step filtering
            filtered_df = optimizer.filter_by_time_step(df, time_step)
            
            if len(filtered_df) > 0:
                # Add vulture ID if not present
                if 'vulture_id' not in filtered_df.columns:
                    filtered_df = filtered_df.copy()
                    filtered_df['vulture_id'] = f'Vulture {i+1:02d}'
                
                processed_dataframes.append(filtered_df)
                print(f"      ✅ {len(filtered_df):,} points retained")
            else:
                print("      ⚠️ No data after filtering")
        
        if not processed_dataframes:
            ui.print_error("No data remaining after filtering!")
            return False
        
        # Combine processed data
        combined_data = pd.concat(processed_dataframes, ignore_index=True)
        print(f"📊 Total GPS points for 3D visualization: {len(combined_data):,}")
        
        # Load data into animation engine
        animation_engine.load_processed_data(combined_data)
        
        # Get animation type choice
        ui.print_section("🎬 3D VISUALIZATION OPTIONS")
        print("Animation types:")
        print("  1. Full animation (with time slider and play controls)")
        print("  2. Static 3D paths (all paths shown at once)")
        
        anim_choice = ui.get_user_input(
            "Select animation type (1 or 2)", 
            "1", 
            int
        )
        
        animation_type = 'full' if anim_choice == 1 else 'static'
        
        # Create 3D visualization
        output_path = animation_engine.create_3d_visualization(animation_type)
        
        if output_path:
            # Display completion information
            ui.print_section("✅ 3D VISUALIZATION COMPLETE")
            
            # Show detailed information
            info = animation_engine.get_3d_info()
            print("📊 3D Visualization Details:")
            print(f"   🏔️ Terrain: {info.get('terrain_region', 'N/A')}")
            print(f"   📐 Terrain resolution: {info.get('terrain_resolution', 'N/A')}")
            print(f"   🗻 Terrain elevation: {info.get('terrain_elevation_range', 'N/A')}")
            print(f"   📏 Terrain area: {info.get('terrain_area_km2', 0):.1f} km²")
            print(f"   📱 GPS points: {info.get('total_points', 0):,}")
            print(f"   🦅 Vultures: {info.get('unique_vultures', 0)}")
            print(f"   ⏱️ Time span: {info.get('time_span_hours', 0):.1f} hours")
            print(f"   🎬 Animation type: {animation_type}")
            print(f"   💾 Output: {output_path}")
            
            ui.print_success("🏔️ 3D terrain visualization ready!")
            
            # Usage tips
            print("\n📋 3D Visualization Tips:")
            print("   • Drag to rotate the 3D view")
            print("   • Scroll to zoom in/out")
            print("   • Click and drag terrain for details")
            print("   • Use animation controls to play through time")
            print("   • Hover over flight paths for vulture info")
            
            return True
        else:
            ui.print_error("3D visualization creation failed")
            return False
    
    except KeyboardInterrupt:
        ui.print_warning("\n⚠️ Operation interrupted by user")
        return False
    except Exception as e:
        ui.print_error(f"3D animation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

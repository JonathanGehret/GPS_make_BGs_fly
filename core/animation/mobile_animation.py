"""
Mobile Animation - Main Script

Streamlined entry point for mobile-optimized GPS animation using modular architecture.
This script has been refactored from the original 513-line version to use
dedicated modules for better maintainability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gps_utils import DataLoader, ensure_output_directories
from utils.mobile_interface import MobileInterface
from utils.performance_optimizer import PerformanceOptimizer
from core.mobile_animation_engine import MobileAnimationEngine
import pandas as pd
import os


def main():
    """Main mobile animation workflow"""
    mobile_ui = MobileInterface()
    
    try:
        # Initialize components
        mobile_ui.display_mobile_welcome()
        
        # Ensure output directories exist
        ensure_output_directories()
        
        # Load GPS data
        mobile_ui.ui.print_section("📁 LOADING DATA")
        data_loader = DataLoader()
        dataframes = data_loader.load_all_csv_files()
        
        if not dataframes:
            mobile_ui.ui.print_error("No GPS data found!")
            return False
        
        print(f"Loaded {len(dataframes)} GPS data files")
        
        # Get mobile performance optimization
        selected_time_step = mobile_ui.display_mobile_performance_options(dataframes)
        if selected_time_step is None:
            mobile_ui.ui.print_warning("Operation cancelled")
            return False
        
        # Process data with selected optimization
        mobile_ui.ui.print_section("⚡ PROCESSING DATA")
        optimizer = PerformanceOptimizer()
        processed_dataframes = []
        
        for i, df in enumerate(dataframes):
            print(f"   📱 Processing file {i+1}/{len(dataframes)}...")
            
            # Apply time step filtering for mobile optimization
            filtered_df = optimizer.filter_by_time_step(df, selected_time_step)
            
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
            mobile_ui.ui.print_error("No data remaining after mobile optimization!")
            return False
        
        # Combine processed data
        combined_data = pd.concat(processed_dataframes, ignore_index=True)
        total_points = len(combined_data)
        
        print(f"📱 Total mobile-optimized points: {total_points:,}")
        
        # Initialize mobile animation engine
        mobile_ui.ui.print_section("🎬 MOBILE ANIMATION SETUP")
        
        # Get mobile configuration from user
        mobile_height = mobile_ui.get_mobile_input(
            "Visualization height (pixels)", "500", int
        )
        mobile_zoom = mobile_ui.get_mobile_input(
            "Default zoom level", "13", int
        )
        mobile_marker_size = mobile_ui.get_mobile_input(
            "Marker size (larger for easier touch)", "12", int
        )
        
        # Create animation engine with mobile settings
        # Ask for performance and playback preferences (mobile CLI inputs)
        perf_ans = mobile_ui.get_mobile_input("Enable mobile performance mode (head-only, faster) [y/N]", "N", str)
        playback_speed = mobile_ui.get_mobile_input("Playback speed multiplier (e.g. 1.0 for normal)", "1.0", float)

        # Set environment variables so the engine reads consistent configuration
        os.environ['PERFORMANCE_MODE'] = '1' if (str(perf_ans).lower().strip() in ('y', 'yes', '1', 'true')) else '0'
        os.environ['PLAYBACK_SPEED'] = str(playback_speed)

        animation_engine = MobileAnimationEngine(
            mobile_height=mobile_height,
            mobile_zoom=mobile_zoom,
            mobile_marker_size=mobile_marker_size
        )
        
        # Load processed data
        animation_engine.load_processed_data(combined_data)
        
        # Create mobile visualization
        output_path = animation_engine.create_mobile_visualization()
        
        if output_path:
            # Display completion information
            mobile_ui.display_mobile_completion(output_path)
            
            # Show animation info
            info = animation_engine.get_animation_info()
            print("\n📊 Animation Details:")
            print(f"   📱 Total GPS points: {info['total_points']:,}")
            print(f"   🦅 Vultures tracked: {info['unique_vultures']}")
            print(f"   🎬 Animation frames: {info['animation_frames']:,}")
            print(f"   ⏱️ Time span: {info['time_span_hours']:.1f} hours")
            print(f"   📏 Marker size: {info['marker_size']}px (touch-friendly)")
            print(f"   📐 Height: {info['mobile_height']}px (mobile-optimized)")
            
            mobile_ui.ui.print_success("✅ Mobile animation completed successfully!")
            return True
        else:
            mobile_ui.ui.print_error("Mobile visualization creation failed")
            return False
        
    except KeyboardInterrupt:
        mobile_ui.ui.print_warning("\n⚠️ Operation interrupted by user")
        return False
    except Exception as e:
        mobile_ui.ui.print_error(f"Mobile animation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Live Map Animation - Main Script

Simplified entry point for GPS live map visualization with trail effects.
"""

import sys
import os
import pandas as pd
import plotly.express as px
from typing import Optional, List
from pathlib import Path
from utils.user_interface import UserInterface
from utils.performance_optimizer import PerformanceOptimizer
from utils.html_injection import inject_fullscreen
from utils.animation_builders import (
    build_color_map,
    create_base_figure,
    apply_standard_layout,
    apply_controls_and_slider,
    attach_frames,
)
from core.trail_system import TrailSystem
from gps_utils import (
    get_numbered_output_path, ensure_output_directories, logger,
    DataLoader, VisualizationHelper
)

# Add the scripts directory to the Python path
scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, scripts_dir)


class LiveMapAnimator:
    """
    Simplified Live Map Animator using modular architecture
    """
    
    def __init__(self):
        self.ui = UserInterface()
        
        # Use custom data directory from GUI if available
        custom_data_dir = os.environ.get('GPS_DATA_DIR')
        if custom_data_dir and os.path.exists(custom_data_dir):
            self.data_loader = DataLoader(custom_data_dir)
            self.ui.print_success(f"Using GUI data directory: {custom_data_dir}")
        else:
            self.data_loader = DataLoader()
        
        self.optimizer = PerformanceOptimizer()
        self.viz_helper = VisualizationHelper()
        self.trail_system = TrailSystem(self.ui)
        
        # Configuration
        self.selected_time_step: Optional[int] = None
        self.dataframes: List[pd.DataFrame] = []
        self.combined_data: Optional[pd.DataFrame] = None
        self.base_animation_speed = 600  # ms per frame at 1x speed for 2D maps
        self.playback_speed = 1.0  # Default playback speed multiplier
        
        # Read playback speed from environment if available (from GUI)
        playback_speed_env = os.environ.get('PLAYBACK_SPEED')
        if playback_speed_env:
            try:
                self.playback_speed = float(playback_speed_env)
                self.playback_speed = max(0.1, min(10.0, self.playback_speed))  # Clamp between 0.1x and 10x
                print(f"🎬 Using GUI playback speed: {self.playback_speed:.1f}x")
            except Exception:
                print(f"⚠️ Invalid playback speed from GUI: {playback_speed_env}, using default 1.0x")
    
    def set_playback_speed(self, speed_multiplier: float) -> None:
        """
        Set the playback speed multiplier
        
        Args:
            speed_multiplier: Speed multiplier (1.0 = normal, 2.0 = 2x faster, 0.5 = 2x slower)
        """
        self.playback_speed = max(0.1, min(10.0, speed_multiplier))  # Clamp between 0.1x and 10x
        print(f"🎬 2D Animation playback speed set to {self.playback_speed:.1f}x")
    
    def get_frame_duration(self) -> int:
        """
        Get the current frame duration based on playback speed
        
        Returns:
            Frame duration in milliseconds
        """
        return max(50, int(self.base_animation_speed / self.playback_speed))
    
    def _parse_time_step_from_gui(self, time_step_str: str) -> int:
        """Parse time step from GUI format to seconds"""
        time_step_str = time_step_str.lower().strip()
        
        # Handle different GUI formats
        if time_step_str.endswith('seconds') or time_step_str.endswith('second'):
            return int(time_step_str.split()[0])
        elif time_step_str.endswith('minutes') or time_step_str.endswith('minute'):
            return int(time_step_str.split()[0]) * 60
        elif time_step_str.endswith('hours') or time_step_str.endswith('hour'):
            return int(time_step_str.split()[0]) * 3600
        elif time_step_str.endswith('s'):
            return int(time_step_str[:-1])
        elif time_step_str.endswith('m'):
            return int(time_step_str[:-1]) * 60
        elif time_step_str.endswith('h'):
            return int(time_step_str[:-1]) * 3600
        else:
            # Default to seconds if no unit specified
            return int(time_step_str)
    
    def run(self) -> bool:
        """Main execution workflow"""
        try:
            self.ui.print_header("🦅 BEARDED VULTURE GPS VISUALIZATION", 80)
            print("Live Map Animation with Performance Optimization")
            print()
            print("Features:")
            print("  ✅ Interactive real-time map visualization")
            print("  ✅ Configurable trail length system")
            print("  ✅ Professional-grade data processing")
            print("  ✅ Responsive design for all screen sizes")
            print()
            
            # Data analysis
            if not self.analyze_data():
                return False
            
            # Performance configuration
            if not self.configure_performance():
                return False
            
            # Trail configuration
            if not self.configure_trail_system():
                return False
            
            # Data processing
            if not self.process_data():
                return False
            
            # Create visualization
            if not self.create_visualization():
                return False
            
            # Show completion summary
            self.show_completion_summary()
            return True
            
        except KeyboardInterrupt:
            self.ui.print_info("\nOperation cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            logger.exception("Unexpected error in main workflow")
            return False
    
    def analyze_data(self) -> bool:
        """Analyze available GPS data"""
        self.ui.print_section("📊 DATA ANALYSIS")
        
        try:
            csv_files = self.data_loader.find_csv_files()
            if not csv_files:
                self.ui.print_error("No CSV files found in data directory!")
                self.ui.print_info("Please add GPS data files to the 'data/' folder")
                return False
            
            total_points = 0
            print(f"Found {len(csv_files)} GPS data file(s):")
            
            for i, csv_file in enumerate(csv_files, 1):
                try:
                    df = self.data_loader.load_single_csv(csv_file)
                    if df is not None:
                        points = len(df)
                        total_points += points
                        filename = Path(csv_file).name
                        print(f"    {i}. {filename:<25} ({points:4d} GPS points)")
                        self.dataframes.append(df)
                except Exception as e:
                    filename = Path(csv_file).name
                    self.ui.print_warning(f"Could not analyze {filename}: {e}")
            
            if not self.dataframes:
                self.ui.print_error("No valid GPS data found!")
                return False
            
            print(f"\n📈 Total GPS points available: {total_points}")
            return True
            
        except Exception as e:
            self.ui.print_error(f"Failed to analyze data: {e}")
            return False
    
    def configure_performance(self) -> bool:
        """Configure performance optimization"""
        # Check if running from GUI (environment variable set)
        time_step_env = os.environ.get('TIME_STEP')
        if time_step_env:
            try:
                # Convert from GUI format (e.g., "5 minutes") to seconds
                self.selected_time_step = self._parse_time_step_from_gui(time_step_env)
                self.ui.print_success(f"Using GUI time step: {time_step_env} ({self.selected_time_step}s)")
                return True
            except Exception:
                self.ui.print_warning(f"Invalid time step from GUI: {time_step_env}, falling back to manual selection")
        
        # For testing: use default 1 minute time step
        self.ui.print_info("Using default 1 minute time step for testing")
        self.selected_time_step = 60  # 1 minute
        return True

    def configure_trail_system(self) -> bool:
        """Configure trail length system"""
        try:
            trail_length = self.trail_system.select_trail_length()
            if trail_length is False:  # User cancelled
                return False
            
            self.trail_system.trail_length_minutes = trail_length
            return True
            
        except Exception as e:
            self.ui.print_error(f"Failed to configure trail system: {e}")
            return False
    
    def process_data(self) -> bool:
        """Process and filter data"""
        self.ui.print_section("🔄 DATA PROCESSING")
        print(f"Applying {self.selected_time_step/60:.1f} minute time step filter...")
        print()
        
        try:
            processed_dataframes = []
            
            for i, df in enumerate(self.dataframes):
                filename = df['source_file'].iloc[0] if 'source_file' in df.columns else f"File {i+1}"
                print(f"   📁 Processing {filename}...")
                
                original_count = len(df)
                filtered_df = self.optimizer.filter_by_time_step(df, self.selected_time_step)
                filtered_count = len(filtered_df)
                
                if filtered_count == 0:
                    self.ui.print_warning(f"No data points remain after filtering {filename}")
                    continue
                
                reduction = ((original_count - filtered_count) / original_count * 100) if original_count > 0 else 0
                print(f"   ✅ Filtered: {original_count} → {filtered_count} points ({reduction:.1f}% reduction)")
                
                # Add color assignment
                filtered_df = filtered_df.copy()
                filtered_df['color'] = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
                processed_dataframes.append(filtered_df)
            
            if not processed_dataframes:
                self.ui.print_error("No data remained after processing!")
                return False
            
            # Combine all data
            self.combined_data = pd.concat(processed_dataframes, ignore_index=True)
            total_points = len(self.combined_data)
            rating = self.optimizer.get_performance_rating(total_points)
            
            print(f"\n✅ Total processed data points: {total_points}")
            print(f"⚡ Expected performance: {rating}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Failed to process data: {e}")
            return False
    
    def create_visualization(self, base_name: str = 'live_map_animation') -> bool:
        """Create the live map visualization"""
        if self.combined_data is None or len(self.combined_data) == 0:
            return False
        
        self.ui.print_section("🎬 VISUALIZATION CREATION")
        print("Creating interactive live map animation...")
        
        try:
            # Prepare timestamp data
            df = self.combined_data.copy()
            df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
            df['timestamp_display'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
            df = df.sort_values('Timestamp [UTC]')
            
            # Get unique vultures and assign colors
            vulture_ids = df['vulture_id'].unique()
            color_map = build_color_map(vulture_ids)
            
            # Calculate optimal center and zoom using helper (with ~10% padding)
            map_cfg = self.viz_helper.calculate_map_bounds(df, padding_percent=0.1)
            center_lat = map_cfg['center']['lat']
            center_lon = map_cfg['center']['lon']
            zoom_level = map_cfg['zoom']
            
            # For logs, also compute raw ranges without padding
            lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
            lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
            lat_range_raw = lat_max - lat_min
            lon_range_raw = lon_max - lon_min
            max_range = max(lat_range_raw, lon_range_raw)
            
            print(f"📍 Map center: Lat {center_lat:.4f}, Lon {center_lon:.4f}")
            print(f"🔍 Optimal zoom level: {zoom_level} (data range: {max_range:.4f}°)")
            print(f"📏 Bounds: Lat [{lat_min:.4f}, {lat_max:.4f}], Lon [{lon_min:.4f}, {lon_max:.4f}]")
            
            # Create figure with empty traces
            fig = create_base_figure(vulture_ids, color_map)
            
            # Create frames using trail system
            unique_times = sorted(df['timestamp_str'].unique())
            attach_frames(
                fig,
                trail_system=self.trail_system,
                df=df,
                vulture_ids=vulture_ids,
                color_map=color_map,
                unique_times=unique_times,
                enable_prominent_time_display=False,
            )
            
            # Configure layout with FIXED center, zoom, and dimensions to prevent jumping
            apply_standard_layout(fig, center_lat=center_lat, center_lon=center_lon, zoom_level=zoom_level)
            apply_controls_and_slider(
                fig,
                unique_times=unique_times,
                frame_duration_ms=self.get_frame_duration(),
                center_lat=center_lat,
                center_lon=center_lon,
                zoom_level=zoom_level,
                include_speed_controls=True,
            )
            
            # Save visualization with fullscreen support
            filename = self.trail_system.get_output_filename(base_name=base_name, bird_names=list(vulture_ids))
            output_path = get_numbered_output_path(filename)
            
            # Configure fullscreen and other useful modebar buttons
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': [
                    'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
                ],
                'modeBarButtonsToRemove': ['sendDataToCloud'],
                'responsive': False,  # Disable responsive behavior for consistent layout
                'scrollZoom': True,   # Allow scroll to zoom
                'doubleClick': 'reset',  # Double-click to reset view
                'showTips': True,    # Show tooltips on modebar buttons
            }
            
            # Save HTML and inject fullscreen assets
            html_string = fig.to_html(config=config)
            html_string = inject_fullscreen(html_string)
            
            # Write the modified HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_string)
            
            self.ui.print_success("✨ Interactive live map animation created with custom fullscreen support!")
            print(f"📁 Saved: {output_path}")
            print("🎯 Fullscreen: Click the '⛶ Fullscreen' button in the controls to view entire interface fullscreen")
            print("📱 Features: All controls, slider, and map included in fullscreen mode")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Error creating visualization: {str(e)}")
            return False
    
    def show_completion_summary(self):
        """Show completion summary"""
        self.ui.print_section("🎉 COMPLETION SUMMARY")
        print("Your optimized GPS visualization is ready!")
        print()
        print("🎯 Features:")
        print("   • Fullscreen mode: Click ⛶ button in the top-right corner")
        print("   • Interactive controls: Pan, zoom, select, and reset view")
        print("   • Smooth animation: No jumping or layout shifts")
        print("   • Professional quality: Fixed layout and stable positioning")
        print()
        print("💡 Performance Tips:")
        print("   • Use larger time steps (10m+) for older computers")
        print("   • Use smaller time steps (1-2m) for detailed analysis")
        print("   • The visualization will load much faster now!")
        print()
        print("� Controls:")
        print("   • ▶ Play/Pause: Control animation playback")
        print("   • ⛶ Fullscreen: Immersive viewing experience")
        print("   • 🖱️ Hover: Detailed information for each point")
        print("   • 🔍 Zoom/Pan: Navigate the map interactively")


def main():
    """Main entry point"""
    try:
        ensure_output_directories()
        animator = LiveMapAnimator()
        success = animator.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()

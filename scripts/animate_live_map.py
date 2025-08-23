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
            except Exception as e:
                self.ui.print_warning(f"Invalid time step from GUI: {time_step_env}, falling back to manual selection")
        
        self.ui.print_section("⚡ PERFORMANCE CONFIGURATION")
        print("Choose time step resolution for optimal performance:")
        print("(Larger time steps = faster loading, fewer details)")
        print()
        
        try:
            # Show options with data point estimates
            for key, option in self.optimizer.TIME_STEP_OPTIONS.items():
                original, filtered = self.optimizer.estimate_data_points(
                    self.dataframes, option["seconds"]
                )
                rating = self.optimizer.get_performance_rating(filtered)
                reduction = ((original - filtered) / original * 100) if original > 0 else 0
                
                print(f"{key:>3s} ) {option['label']:<15} {rating}")
                print(f"      {option['description']:<20} → {filtered:4d} points ({reduction:4.1f}% reduction)")
            
            print()
            
            # Get user choice
            while True:
                choice = input("Enter your choice (1s, 2m, 5m, etc.) or 'q' to quit: ").strip().lower()
                
                if choice == 'q':
                    self.ui.print_info("Operation cancelled by user")
                    return False
                
                if choice in self.optimizer.TIME_STEP_OPTIONS:
                    selected = self.optimizer.TIME_STEP_OPTIONS[choice]
                    original, filtered = self.optimizer.estimate_data_points(
                        self.dataframes, selected["seconds"]
                    )
                    
                    self.ui.print_success(f"Selected: {selected['label']}")
                    print(f"📊 Estimated data points: {filtered} (reduced from {original})")
                    
                    self.selected_time_step = selected["seconds"]
                    return True
                
                self.ui.print_error("Invalid choice. Please enter a valid option (e.g., '1m', '5m', '10m')")
                
        except Exception as e:
            self.ui.print_error(f"Failed to configure performance: {e}")
            return False
    
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
            colors = px.colors.qualitative.Set1[:len(vulture_ids)]
            color_map = dict(zip(vulture_ids, colors))
            
            # Create figure with empty traces
            import plotly.graph_objects as go
            fig = go.Figure()
            
            for vulture_id in vulture_ids:
                fig.add_trace(
                    go.Scattermap(
                        lat=[], lon=[], mode='lines+markers', name=vulture_id,
                        line=dict(color=color_map[vulture_id], width=3),
                        marker=dict(color=color_map[vulture_id], size=8),
                        showlegend=True  # Ensure all birds always show in legend
                    )
                )
            
            # Create frames using trail system
            unique_times = sorted(df['timestamp_str'].unique())
            frames = self.trail_system.create_frames_with_trail(df, vulture_ids, color_map, unique_times)
            fig.frames = frames
            
            # Configure layout
            fig.update_layout(
                map=dict(
                    style="open-street-map",
                    center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
                    zoom=12
                ),
                height=600,
                title="🦅 Bearded Vulture GPS Flight Paths - Live Map Visualization",
                showlegend=True,
                updatemenus=[dict(
                    type="buttons", direction="left",
                    buttons=[
                        dict(label="▶", method="animate", 
                             args=[None, {"frame": {"duration": 600, "redraw": True}, 
                                         "transition": {"duration": 300}, "fromcurrent": True}]),
                        dict(label="⏸", method="animate", 
                             args=[[None], {"frame": {"duration": 0, "redraw": False}, 
                                           "mode": "immediate", "transition": {"duration": 0}}])
                    ]
                )],
                sliders=[dict(
                    active=0, currentvalue={"prefix": "Time: "},
                    steps=[dict(label=time_str, method="animate",
                               args=[[time_str], dict(mode="immediate", transition=dict(duration=300))])
                          for time_str in unique_times]
                )]
            )
            
            # Save visualization
            filename = self.trail_system.get_output_filename(base_name=base_name, bird_names=list(vulture_ids))
            output_path = get_numbered_output_path(filename)
            fig.write_html(output_path)
            
            self.ui.print_success("✨ Interactive live map animation created!")
            print(f"📁 Saved: {output_path}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Error creating visualization: {str(e)}")
            return False
    
    def show_completion_summary(self):
        """Show completion summary"""
        self.ui.print_section("🎉 COMPLETION SUMMARY")
        print("Your optimized GPS visualization is ready!")
        print()
        print("💡 Performance Tips:")
        print("   • Use larger time steps (10m+) for older computers")
        print("   • Use smaller time steps (1-2m) for detailed analysis")
        print("   • The visualization will load much faster now!")
        print()
        print("🎯 Next Steps:")
        print("   • Open the HTML file in your web browser")
        print("   • Use the play controls to animate the flight paths")
        print("   • Hover over points for detailed information")
        print("   • Try the mobile version for touch devices")


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

#!/usr/bin/env python3
"""
Optimized Live Map Animation for Bearded Vulture GPS Visualization

This script provides a high-performance, user-friendly interface for visualizing
GPS flight paths with real-time map tiles and configurable time-step filtering.

Features:
- Interactive configuration interface
- Performance optimization through time-step filtering  
- Real-time data point estimation
- Comprehensive error handling and validation
- Beautiful, responsive visualizations
- Professional code structure following best practices

Author: GPS Visualization Team
Version: 2.0
"""

import sys
import os
from typing import List, Optional

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gps_utils import (
    DataLoader, PerformanceOptimizer, VisualizationHelper, UserInterface,
    get_output_path, ensure_output_directories, logger,
    DataLoadError
)
import pandas as pd
import plotly.express as px


class LiveMapAnimator:
    """
    Main class for creating optimized live map animations
    
    This class handles the complete workflow from data loading through
    visualization creation, with emphasis on performance and user experience.
    """
    
    def __init__(self):
        self.ui = UserInterface()
        self.data_loader = DataLoader()
        self.optimizer = PerformanceOptimizer()
        self.viz_helper = VisualizationHelper()
        
        # Configuration
        self.selected_time_step: Optional[int] = None
        self.dataframes: List[pd.DataFrame] = []
        self.combined_data: Optional[pd.DataFrame] = None
    
    def display_welcome_screen(self) -> None:
        """Display welcome screen and project information"""
        self.ui.print_header("🦅 BEARDED VULTURE GPS VISUALIZATION", 80)
        print("Live Map Animation with Performance Optimization")
        print()
        print("Features:")
        print("  ✅ Interactive real-time map visualization")
        print("  ✅ Configurable performance optimization")
        print("  ✅ Professional-grade data processing")
        print("  ✅ Responsive design for all screen sizes")
        print()
    
    def analyze_available_data(self) -> bool:
        """
        Analyze available CSV files and display summary
        
        Returns:
            True if data files are found, False otherwise
        """
        self.ui.print_section("📊 DATA ANALYSIS")
        
        csv_files = self.data_loader.find_csv_files()
        
        if not csv_files:
            self.ui.print_error("No CSV files found in data directory!")
            self.ui.print_info("Please add GPS data files to the 'data/' folder")
            return False
        
        print(f"Found {len(csv_files)} GPS data file(s):")
        
        total_records = 0
        for i, file_path in enumerate(csv_files, 1):
            filename = os.path.basename(file_path)
            try:
                # Quick count without full loading
                df = pd.read_csv(file_path, sep=';')
                valid_records = len(df[df['display'] == 1]) if 'display' in df.columns else len(df)
                total_records += valid_records
                print(f"   {i:2d}. {filename:<25} ({valid_records:4d} GPS points)")
            except Exception as e:
                self.ui.print_warning(f"Could not analyze {filename}: {e}")
        
        print(f"\n📈 Total GPS points available: {total_records:,}")
        
        if total_records == 0:
            self.ui.print_error("No valid GPS data found!")
            return False
        
        return True
    
    def display_performance_options(self) -> Optional[int]:
        """
        Display performance configuration options and get user selection
        
        Returns:
            Selected time step in seconds, or None if user cancels
        """
        self.ui.print_section("⚡ PERFORMANCE CONFIGURATION")
        print("Choose time step resolution for optimal performance:")
        print("(Larger time steps = faster loading, fewer details)")
        print()
        
        options = self.optimizer.TIME_STEP_OPTIONS
        
        # Load data for estimation
        try:
            self.dataframes = self.data_loader.load_all_csv_files()
            if not self.dataframes:
                raise DataLoadError("No valid data files could be loaded")
        except Exception as e:
            self.ui.print_error(f"Failed to load data for analysis: {e}")
            return None
        
        # Display options with performance estimates
        print("TIME STEP OPTIONS:")
        print("-" * 70)
        
        for key, option in options.items():
            original_points, filtered_points = self.optimizer.estimate_data_points(
                self.dataframes, option["seconds"]
            )
            
            if original_points == 0:
                continue
                
            reduction_percent = (original_points - filtered_points) / original_points * 100
            performance_rating = self.optimizer.get_performance_rating(filtered_points)
            
            print(f"{key:4s}) {option['label']:25s} {performance_rating}")
            print(f"      {option['description']:25s} → {filtered_points:4d} points "
                  f"({reduction_percent:5.1f}% reduction)")
            print()
        
        # Get user selection
        return self._get_user_time_step_choice(options)
    
    def _get_user_time_step_choice(self, options: dict) -> Optional[int]:
        """Get and validate user's time step choice"""
        while True:
            choice = input("\nEnter your choice (1s, 2m, 5m, etc.) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                self.ui.print_info("Operation cancelled by user")
                return None
            
            if choice in options:
                selected = options[choice]
                original_points, filtered_points = self.optimizer.estimate_data_points(
                    self.dataframes, selected["seconds"]
                )
                
                self.ui.print_success(f"Selected: {selected['label']}")
                print(f"📊 Estimated data points: {filtered_points:,} (reduced from {original_points:,})")
                
                # Warning for high data counts
                if filtered_points > 1000:
                    self.ui.print_warning("High data point count may still cause slower performance")
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return selected["seconds"]
            
            self.ui.print_error("Invalid choice. Please enter a valid option (e.g., '1m', '5m', '10m')")
    
    def process_data(self) -> bool:
        """
        Process and filter data according to selected time step
        
        Returns:
            True if processing succeeds, False otherwise
        """
        if not self.dataframes or self.selected_time_step is None:
            return False
        
        self.ui.print_section("🔄 DATA PROCESSING")
        print(f"Applying {self.selected_time_step/60:.1f} minute time step filter...")
        print()
        
        processed_dataframes = []
        
        for i, df in enumerate(self.dataframes):
            filename = df['source_file'].iloc[0] if 'source_file' in df.columns else f"File {i+1}"
            print(f"   📁 Processing {filename}...")
            
            try:
                original_count = len(df)
                filtered_df = self.optimizer.filter_by_time_step(df, self.selected_time_step)
                filtered_count = len(filtered_df)
                
                if filtered_count == 0:
                    self.ui.print_warning(f"No data points remain after filtering {filename}")
                    continue
                
                # Add color assignment
                filtered_df = filtered_df.copy()
                filtered_df['color'] = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
                
                processed_dataframes.append(filtered_df)
                
                reduction_percent = (original_count - filtered_count) / original_count * 100
                print(f"   ✅ Filtered: {original_count:,} → {filtered_count:,} points "
                      f"({reduction_percent:.1f}% reduction)")
                
            except Exception as e:
                self.ui.print_error(f"Failed to process {filename}: {e}")
                continue
        
        if not processed_dataframes:
            self.ui.print_error("No data remained after processing!")
            return False
        
        # Combine all processed data
        try:
            self.combined_data = pd.concat(processed_dataframes, ignore_index=True)
            total_points = len(self.combined_data)
            
            print(f"\n✅ Total processed data points: {total_points:,}")
            
            performance_rating = self.optimizer.get_performance_rating(total_points)
            print(f"⚡ Expected performance: {performance_rating}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Failed to combine processed data: {e}")
            return False
    
    def create_visualization(self) -> bool:
        """
        Create the interactive live map visualization
        
        Returns:
            True if visualization creation succeeds, False otherwise
        """
        if self.combined_data is None or len(self.combined_data) == 0:
            return False
        
        self.ui.print_section("🎬 VISUALIZATION CREATION")
        print("Creating interactive live map animation...")
        
        try:
            # Prepare timestamp data for animation
            df = self.combined_data.copy()
            df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
            df['timestamp_display'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
            
            # Create animated line map with flight paths
            fig = px.line_mapbox(
                df,
                lat="Latitude",
                lon="Longitude",
                color="vulture_id",
                animation_frame="timestamp_str",
                hover_name="vulture_id",
                hover_data={
                    "timestamp_display": ":Time",
                    "Latitude": ":.6f",
                    "Longitude": ":.6f",
                    "Height": ":Altitude (m)",
                    "vulture_id": False,
                    "timestamp_str": False
                },
                labels={
                    "timestamp_display": "Time",
                    "Latitude": "Latitude",
                    "Longitude": "Longitude",
                    "Height": "Altitude (m)",
                    "vulture_id": "Vulture"
                },
                mapbox_style="open-street-map",
                height=600,
                title="🦅 Bearded Vulture GPS Flight Paths - Live Map Visualization"
            )
            
            # Update traces to show both lines and markers
            fig.update_traces(
                mode='lines+markers',  # Show both lines and markers
                line=dict(width=3),
                marker=dict(size=8, opacity=0.9)
            )
            
            # Apply layout optimizations
            layout_config = self.viz_helper.setup_mapbox_layout(df, height=600, zoom=12)
            
            fig.update_layout(
                **layout_config,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.02,
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1
                ),
                margin=dict(l=0, r=120, t=50, b=0),
                font=dict(size=12),
                title=dict(
                    font=dict(size=16),
                    x=0.5,
                    xanchor='center'
                )
            )
            
            # Optimize animation performance
            if hasattr(fig, 'layout') and hasattr(fig.layout, 'updatemenus'):
                fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 600
                fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 300
            
            # Save the visualization
            output_path = get_output_path('flight_paths_live_map_optimized.html')
            
            print("💾 Saving visualization...")
            fig.write_html(output_path)
            
            self.ui.print_success("Visualization created successfully!")
            print(f"📁 Saved to: {output_path}")
            print(f"⚡ Data points: {len(df):,}")
            print(f"🕒 Time resolution: {self.selected_time_step/60:.1f} minutes")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Failed to create visualization: {e}")
            logger.exception("Visualization creation failed")
            return False
    
    def display_completion_summary(self) -> None:
        """Display completion summary and usage tips"""
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
        print()
    
    def run(self) -> bool:
        """
        Main execution method
        
        Returns:
            True if the complete workflow succeeds, False otherwise
        """
        try:
            # Welcome and data analysis
            self.display_welcome_screen()
            
            if not self.analyze_available_data():
                return False
            
            # Performance configuration
            self.selected_time_step = self.display_performance_options()
            if self.selected_time_step is None:
                return False
            
            # Data processing
            if not self.process_data():
                return False
            
            # Visualization creation
            if not self.create_visualization():
                return False
            
            # Completion
            self.display_completion_summary()
            return True
            
        except KeyboardInterrupt:
            self.ui.print_info("\nOperation cancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            logger.exception("Unexpected error in main workflow")
            return False


def main():
    """Main entry point for the live map animator"""
    try:
        # Ensure output directories exist
        ensure_output_directories()
        
        # Create and run the animator
        animator = LiveMapAnimator()
        success = animator.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mobile-Optimized Live Map Animation for Bearded Vulture GPS Visualization

This script creates touch-friendly, mobile-optimized GPS flight path visualizations
with performance optimization and responsive design specifically for mobile devices.

Features:
- Mobile-first responsive design
- Touch-friendly controls and larger markers
- Compact interface optimized for small screens
- Performance optimization for mobile browsers
- Professional code structure with comprehensive error handling

Author: GPS Visualization Team  
Version: 2.0 Mobile
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
import plotly.graph_objects as go


class MobileLiveMapAnimator:
    """
    Mobile-optimized class for creating GPS flight path animations
    
    Specifically designed for mobile devices with:
    - Touch-friendly interface
    - Compact visual design
    - Optimized performance for mobile browsers
    - Larger interactive elements
    """
    
    def __init__(self):
        self.ui = UserInterface()
        self.data_loader = DataLoader()
        self.optimizer = PerformanceOptimizer()
        self.viz_helper = VisualizationHelper()
        
        # Mobile-specific configuration
        self.mobile_height = 500
        self.mobile_zoom = 13
        self.mobile_marker_size = 12
        
        # Workflow state
        self.selected_time_step: Optional[int] = None
        self.dataframes: List[pd.DataFrame] = []
        self.combined_data: Optional[pd.DataFrame] = None
    
    def display_mobile_welcome(self) -> None:
        """Display mobile-optimized welcome screen"""
        self.ui.print_header("📱 VULTURE GPS - MOBILE OPTIMIZER", 60)
        print("Mobile-Optimized Flight Path Visualization")
        print()
        print("Mobile Features:")
        print("  📱 Touch-friendly controls")
        print("  🔍 Larger markers for easy selection")
        print("  ⚡ Optimized for mobile performance")
        print("  📊 Compact interface design")
        print()
    
    def display_mobile_performance_options(self) -> Optional[int]:
        """
        Display mobile-optimized performance configuration
        
        Returns:
            Selected time step in seconds, or None if cancelled
        """
        self.ui.print_section("⚡ MOBILE PERFORMANCE SETUP")
        
        # Load data for estimation
        try:
            self.dataframes = self.data_loader.load_all_csv_files()
            if not self.dataframes:
                raise DataLoadError("No valid data files could be loaded")
        except Exception as e:
            self.ui.print_error(f"Data loading failed: {e}")
            return None
        
        # Check data availability
        csv_files = self.data_loader.find_csv_files()
        print(f"📊 Found {len(csv_files)} data file(s)")
        print()
        
        # Mobile-optimized options display
        options = self.optimizer.TIME_STEP_OPTIONS
        
        print("MOBILE PERFORMANCE OPTIONS:")
        print("-" * 40)
        
        for key, option in options.items():
            original_points, filtered_points = self.optimizer.estimate_data_points(
                self.dataframes, option["seconds"]
            )
            
            if original_points == 0:
                continue
            
            # Mobile-friendly performance indicators
            performance_emoji = self._get_mobile_performance_emoji(filtered_points)
            speed_description = self._get_mobile_speed_description(filtered_points)
            
            print(f"{key:3s}) {option['label']:12s} {performance_emoji}")
            print(f"     ~{filtered_points:3d} points - {speed_description}")
            print()
        
        return self._get_mobile_user_choice(options)
    
    def _get_mobile_performance_emoji(self, point_count: int) -> str:
        """Get mobile-specific performance emoji"""
        if point_count < 50:
            return "🔥 Ultra Fast"
        elif point_count < 100:
            return "🚀 Very Fast"
        elif point_count < 300:
            return "⚡ Fast"
        else:
            return "🐌 Slower"
    
    def _get_mobile_speed_description(self, point_count: int) -> str:
        """Get mobile-friendly speed description"""
        if point_count < 50:
            return "Instant loading"
        elif point_count < 100:
            return "Quick loading"
        elif point_count < 300:
            return "Good performance"
        elif point_count < 500:
            return "May be slow on older phones"
        else:
            return "Recommended for WiFi only"
    
    def _get_mobile_user_choice(self, options: dict) -> Optional[int]:
        """Get and validate user choice with mobile considerations"""
        while True:
            choice = input("Choose option (1m, 5m, etc.) or 'q': ").strip().lower()
            
            if choice == 'q':
                self.ui.print_info("Cancelled")
                return None
            
            if choice in options:
                selected = options[choice]
                original_points, filtered_points = self.optimizer.estimate_data_points(
                    self.dataframes, selected["seconds"]
                )
                
                self.ui.print_success(f"Selected: {selected['label']}")
                print(f"📊 Data points: {filtered_points:,}")
                
                # Mobile-specific warnings
                if filtered_points > 500:
                    self.ui.print_warning("May be slow on mobile devices!")
                    confirm = input("Continue? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return selected["seconds"]
            
            self.ui.print_error("Invalid choice. Try again.")
    
    def process_mobile_data(self) -> bool:
        """
        Process data with mobile-specific optimizations
        
        Returns:
            True if processing succeeds, False otherwise
        """
        if not self.dataframes or self.selected_time_step is None:
            return False
        
        self.ui.print_section("🔄 MOBILE DATA PROCESSING")
        print("Optimizing data for mobile devices...")
        print()
        
        processed_dataframes = []
        
        for i, df in enumerate(self.dataframes):
            filename = df['source_file'].iloc[0] if 'source_file' in df.columns else f"File {i+1}"
            print(f"   📁 {filename}...")
            
            try:
                original_count = len(df)
                filtered_df = self.optimizer.filter_by_time_step(df, self.selected_time_step)
                filtered_count = len(filtered_df)
                
                if filtered_count == 0:
                    self.ui.print_warning(f"No data points remain in {filename}")
                    continue
                
                # Mobile-optimized color assignment
                filtered_df = filtered_df.copy()
                filtered_df['color'] = px.colors.qualitative.Set1[i % len(px.colors.qualitative.Set1)]
                
                processed_dataframes.append(filtered_df)
                print(f"   ✅ {original_count} → {filtered_count} points")
                
            except Exception as e:
                self.ui.print_error(f"Processing failed for {filename}: {e}")
                continue
        
        if not processed_dataframes:
            self.ui.print_error("No data remained after processing!")
            return False
        
        # Combine processed data
        try:
            self.combined_data = pd.concat(processed_dataframes, ignore_index=True)
            total_points = len(self.combined_data)
            
            print(f"\n✅ Total points: {total_points:,}")
            
            performance_rating = self._get_mobile_performance_emoji(total_points)
            print(f"📱 Mobile performance: {performance_rating}")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Data combination failed: {e}")
            return False
    
    def create_mobile_visualization(self) -> bool:
        """
        Create mobile-optimized interactive visualization
        
        Returns:
            True if visualization creation succeeds, False otherwise
        """
        if self.combined_data is None or len(self.combined_data) == 0:
            return False
        
        self.ui.print_section("📱 MOBILE VISUALIZATION")
        print("Creating mobile-optimized animation...")
        
        try:
            # Prepare mobile-friendly timestamp formatting
            df = self.combined_data.copy()
            df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
            df['timestamp_mobile'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
            
            # Sort for proper animation
            df = df.sort_values('Timestamp [UTC]')
            
            # Use the working manual trace approach for mobile
            fig = go.Figure()
            
            # Get unique vultures and assign colors
            vulture_ids = df['vulture_id'].unique()
            colors = px.colors.qualitative.Set1[:len(vulture_ids)]
            color_map = dict(zip(vulture_ids, colors))
            
            # Add initial empty traces for each vulture using MapLibre-compatible Scattermap
            for vulture_id in vulture_ids:
                fig.add_trace(
                    go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                        lat=[],
                        lon=[],
                        mode='lines+markers',
                        name=vulture_id,
                        line=dict(color=color_map[vulture_id], width=4),  # Thicker for mobile
                        marker=dict(color=color_map[vulture_id], size=self.mobile_marker_size),
                        hovertemplate=(
                            f"<b>{vulture_id}</b><br>"
                            "Time: %{customdata[0]}<br>"
                            "Lat: %{lat:.4f}°<br>"
                            "Lon: %{lon:.4f}°<br>"
                            "Alt: %{customdata[1]}m"
                            "<extra></extra>"
                        )
                    )
                )
            
            # Create animation frames
            frames = []
            unique_times = df['timestamp_str'].unique()
            
            for time_str in unique_times:
                frame_data = []
                
                for vulture_id in vulture_ids:
                    # Get cumulative data up to this time for each vulture
                    vulture_data = df[df['vulture_id'] == vulture_id]
                    cumulative_data = vulture_data[vulture_data['timestamp_str'] <= time_str]
                    
                    if len(cumulative_data) > 0:
                        # Prepare custom data for hover
                        customdata = []
                        for _, row in cumulative_data.iterrows():
                            customdata.append([row['timestamp_mobile'], row['Height']])
                        
                        frame_data.append(
                            go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                                lat=cumulative_data['Latitude'].tolist(),
                                lon=cumulative_data['Longitude'].tolist(),
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=4),
                                marker=dict(color=color_map[vulture_id], size=self.mobile_marker_size),
                                customdata=customdata,
                                hovertemplate=(
                                    f"<b>{vulture_id}</b><br>"
                                    "Time: %{customdata[0]}<br>"
                                    "Lat: %{lat:.4f}°<br>"
                                    "Lon: %{lon:.4f}°<br>"
                                    "Alt: %{customdata[1]}m"
                                    "<extra></extra>"
                                )
                            )
                        )
                    else:
                        # Empty trace for vultures with no data at this time
                        frame_data.append(
                            go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                                lat=[],
                                lon=[],
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=4),
                                marker=dict(color=color_map[vulture_id], size=self.mobile_marker_size)
                            )
                        )
                
                frames.append(go.Frame(data=frame_data, name=time_str))
            
            fig.frames = frames
            
            # Mobile-optimized MapLibre layout (successor to deprecated Mapbox)
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",  # MapLibre-compatible OpenStreetMap style
                    center=dict(
                        lat=df['Latitude'].mean(),
                        lon=df['Longitude'].mean()
                    ),
                    zoom=self.mobile_zoom  # Higher zoom for mobile detail
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",  # Horizontal legend for mobile
                    yanchor="top",
                    y=-0.1,
                    xanchor="center",
                    x=0.5,
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="rgba(0,0,0,0.2)",
                    borderwidth=1,
                    font=dict(size=10)
                ),
                margin=dict(l=10, r=10, t=40, b=60),
                font=dict(size=11),
                title=dict(
                    font=dict(size=14),
                    x=0.5,
                    xanchor='center'
                )
            )
            
            # Mobile-friendly control buttons and slider configuration
            fig.update_layout(
                updatemenus=[dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(label="▶", method="animate", args=[None, {
                            "frame": {"duration": 1000, "redraw": True},
                            "transition": {"duration": 400},
                            "fromcurrent": True
                        }]),
                        dict(label="⏸", method="animate", args=[[None], {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }])
                    ]),
                    pad={"r": 10, "t": 70},
                    showactive=False,
                    x=0.1,
                    xanchor="right",
                    y=0.02,
                    yanchor="top"
                )],
                sliders=[dict(
                    active=0,
                    yanchor="top",
                    xanchor="left",
                    currentvalue=dict(
                        font=dict(size=12),
                        prefix="Time: ",
                        visible=True,
                        xanchor="right"
                    ),
                    transition=dict(duration=400, easing="cubic-in-out"),
                    pad=dict(b=10, t=50),
                    len=0.9,
                    x=0.05,
                    y=0,
                    steps=[dict(
                        args=[[frame.name], {"frame": {"duration": 1000, "redraw": True},
                                           "mode": "immediate", "transition": {"duration": 400}}],
                        label=pd.to_datetime(frame.name).strftime('%d.%m %H:%M'),
                        method="animate"
                    ) for frame in frames]
                )]
            )
            
            # Save mobile visualization
            output_path = get_output_path('flight_paths_mobile_professional.html')
            
            print("💾 Saving mobile visualization...")
            fig.write_html(output_path)
            
            self.ui.print_success("Mobile visualization created!")
            print(f"📱 Saved to: {output_path}")
            print(f"⚡ Data points: {len(df):,}")
            print(f"🕒 Time step: {self.selected_time_step/60:.1f} minutes")
            
            return True
            
        except Exception as e:
            self.ui.print_error(f"Mobile visualization creation failed: {e}")
            logger.exception("Mobile visualization creation failed")
            return False
    
    def display_mobile_completion(self) -> None:
        """Display mobile-specific completion summary"""
        self.ui.print_section("📱 MOBILE SUCCESS!")
        
        print("Your mobile-optimized visualization is ready!")
        print()
        print("📱 Mobile Features:")
        print("   ✅ Touch-friendly controls")
        print("   ✅ Larger markers for easy touch")
        print("   ✅ Optimized for small screens")
        print("   ✅ Fast loading performance")
        print()
        print("💡 Mobile Tips:")
        print("   • Best viewed in landscape mode")
        print("   • Use pinch-to-zoom for detail")
        print("   • Tap markers for information")
        print("   • Works offline once loaded")
        print()
    
    def run(self) -> bool:
        """
        Main mobile execution workflow
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Mobile welcome
            self.display_mobile_welcome()
            
            # Performance configuration
            self.selected_time_step = self.display_mobile_performance_options()
            if self.selected_time_step is None:
                return False
            
            # Data processing
            if not self.process_mobile_data():
                return False
            
            # Visualization creation
            if not self.create_mobile_visualization():
                return False
            
            # Completion
            self.display_mobile_completion()
            return True
            
        except KeyboardInterrupt:
            self.ui.print_info("\nCancelled by user")
            return False
        except Exception as e:
            self.ui.print_error(f"Unexpected error: {e}")
            logger.exception("Unexpected error in mobile workflow")
            return False


def main():
    """Main entry point for mobile live map animator"""
    try:
        # Ensure output directories exist
        ensure_output_directories()
        
        # Create and run mobile animator
        animator = MobileLiveMapAnimator()
        success = animator.run()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        logger.exception("Critical error in mobile main")
        sys.exit(1)


if __name__ == "__main__":
    main()

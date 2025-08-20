#!/usr/bin/env python3
"""
Optimized Live Map Animation for Bearded Vulture GPS Visualization

This script provides a high-performance, user-friendly interface for visualizing
GPS flight paths with real-time map tiles and configurable time-step filtering.

Features:
- Interac            # Add initial empty traces for each vulture using MapLibre-compati                        # Empty trace for vultures with no data at this time
                        frame_data.append(
                            go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                                lat=[],
                                lon=[],
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=3),
                                marker=dict(color=color_map[vulture_id], size=6)
                            )
                        )map
            for vulture_id in vulture_ids:
                fig.add_trace(
                    go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                        lat=[],
                        lon=[],
                        mode='lines+markers',
                        name=vulture_id,
                        line=dict(color=color_map[vulture_id], width=3),
                        marker=dict(color=color_map[vulture_id], size=6),
                        hovertemplate=(
                            f"<b>{vulture_id}</b><br>"
                            "Time: %{customdata[0]}<br>"
                            "Lat: %{lat:.6f}°<br>"
                            "Lon: %{lon:.6f}°<br>"
                            "Alt: %{customdata[1]}m"
                            "<extra></extra>"
                        )
                    )
                )nterface
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
    get_output_path, get_numbered_output_path, ensure_output_directories, logger,
    DataLoadError, format_height_display
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
            
            # Create frame index for animation
            df = df.sort_values('Timestamp [UTC]')
            df['frame_index'] = range(len(df))
            
            # Use the working approach with go.Figure and manual traces
            import plotly.graph_objects as go
            
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
                        line=dict(color=color_map[vulture_id], width=3),
                        marker=dict(color=color_map[vulture_id], size=8),
                        hovertemplate=(
                            f"<b>{vulture_id}</b><br>"
                            "Time: %{customdata[0]}<br>"
                            "Lat: %{lat:.6f}°<br>"
                            "Lon: %{lon:.6f}°<br>"
                            "Alt: %{customdata[1]}m"
                            "<extra></extra>"
                        )
                    )
                )
            
            # Create animation frames (simplified approach)
            frames = []
            unique_times = sorted(df['timestamp_str'].unique())
            
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
                            height_display = format_height_display(row['Height'])
                            customdata.append([row['timestamp_display'], height_display])
                        
                        frame_data.append(
                            go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                                lat=cumulative_data['Latitude'].tolist(),
                                lon=cumulative_data['Longitude'].tolist(),
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=3),
                                marker=dict(color=color_map[vulture_id], size=6),
                                customdata=customdata,
                                hovertemplate=(
                                    f"<b>{vulture_id}</b><br>"
                                    "Time: %{customdata[0]}<br>"
                                    "Lat: %{lat:.6f}°<br>"
                                    "Lon: %{lon:.6f}°<br>"
                                    "Alt: %{customdata[1]}"
                                    "<extra></extra>"
                                )
                            )
                        )
                    else:
                        # Empty trace for vultures with no data at this time (MapLibre compatible)
                        frame_data.append(
                            go.Scattermap(  # Updated from Scattermapbox for MapLibre compatibility
                                lat=[],
                                lon=[],
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=3),
                                marker=dict(color=color_map[vulture_id], size=8)
                            )
                        )
                
                frames.append(go.Frame(data=frame_data, name=time_str))
            
            fig.frames = frames
            
            # Apply layout optimizations
            # Configure MapLibre map layout (OpenStreetMap with MapLibre GL JS)
            fig.update_layout(
                map=dict(
                    style="open-street-map",  # MapLibre-compatible style
                    center=dict(
                        lat=df['Latitude'].mean(),
                        lon=df['Longitude'].mean()
                    ),
                    zoom=12
                ),
                height=600,
                title="🦅 Bearded Vulture GPS Flight Paths - Live Map Visualization",
                showlegend=True,
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
                updatemenus=[dict(
                    type="buttons",
                    direction="left",
                    buttons=list([
                        dict(
                            label="▶",
                            method="animate",
                            args=[None, {"frame": {"duration": 600, "redraw": True},
                                        "transition": {"duration": 300},
                                        "fromcurrent": True}]
                        ),
                        dict(
                            label="⏸",
                            method="animate",
                            args=[[None], {"frame": {"duration": 0, "redraw": False},
                                          "mode": "immediate",
                                          "transition": {"duration": 0}}]
                        )
                    ]),
                    pad={"r": 10, "t": 87},
                    showactive=False,
                    x=0.011,
                    xanchor="left",
                    y=0,
                    yanchor="top"
                )],
                sliders=[
                    # Start Time Slider (left) - Controls how far back to show data
                    dict(
                        active=0,
                        yanchor="top",
                        xanchor="left",
                        currentvalue=dict(
                            font=dict(size=14),
                            prefix="Hide before: ",
                            visible=True,
                            xanchor="right"
                        ),
                        transition=dict(duration=200, easing="cubic-in-out"),
                        pad=dict(b=10, t=50),
                        len=0.35,  # Shorter slider
                        x=0.05,   # Positioned to the left
                        y=0,
                        steps=[dict(
                            args=[i],  # Just pass the index
                            label=frame.name.split(' ')[0] + ' ' + frame.name.split(' ')[1],  # Short format
                            method="skip",  # Use skip method for custom handling
                            value=str(i)
                        ) for i, frame in enumerate(frames)]
                    ),
                    # Main Time Slider (right) - Controls current time
                    dict(
                        active=len(frames) - 1,  # Start at last frame
                        yanchor="top",
                        xanchor="left",
                        currentvalue=dict(
                            font=dict(size=16),
                            prefix="Current time: ",
                            visible=True,
                            xanchor="right"
                        ),
                        transition=dict(duration=300, easing="cubic-in-out"),
                        pad=dict(b=10, t=50),
                        len=0.5,   # Main slider
                        x=0.45,    # Positioned to the right
                        y=0,
                        steps=[dict(
                            args=[[frame.name], {"frame": {"duration": 300, "redraw": True},
                                                "mode": "immediate", "transition": {"duration": 300}}],
                            label=frame.name.split(' ')[0] + ' ' + frame.name.split(' ')[1],  # Short format
                            method="animate"
                        ) for frame in frames]
                    )
                ]
            )
            
            # Apply comprehensive MapLibre layout configuration with smart bounds
            map_bounds = self.viz_helper.calculate_map_bounds(df, padding_percent=0.15)
            fig.update_layout(
                # MapLibre configuration with auto-fitted bounds
                map=dict(
                    style="open-street-map",  # MapLibre-compatible OpenStreetMap style
                    center=map_bounds['center'],
                    zoom=map_bounds['zoom']
                ),
                height=600,
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
            
            # Save the visualization with consecutive numbering
            output_path = get_numbered_output_path('flight_paths_live_map_professional')
            
            print("💾 Saving visualization...")
            
            # Write the HTML with custom JavaScript for dual slider interaction
            html_string = fig.to_html(include_plotlyjs=True)
            
            # Add custom JavaScript for time window functionality
            unique_times = sorted(df['timestamp_str'].unique())
            time_window_js = f"""
            <script>
            // Time window control variables
            let startTimeIndex = 0;
            let currentTimeIndex = {len(unique_times) - 1};
            let timeFrames = {[t for t in unique_times]};
            let plotlyDiv = document.querySelector('.plotly-graph-div');
            let allFrameData = {{}};  // Store all frame data for filtering
            
            // Store original frame data when the page loads
            document.addEventListener('DOMContentLoaded', function() {{
                setTimeout(function() {{
                    if (plotlyDiv && plotlyDiv._fullLayout && plotlyDiv._fullLayout._frames) {{
                        // Store all original frame data
                        plotlyDiv._fullLayout._frames.forEach(function(frame, index) {{
                            allFrameData[frame.name] = frame.data;
                        }});
                        
                        // Set up slider event listeners
                        setupSliderListeners();
                    }}
                }}, 1000);
            }});
            
            // Function to create filtered frame data based on time window
            function createFilteredFrame(endTimeIndex, startTimeIndex) {{
                if (!plotlyDiv || !plotlyDiv._fullData) return null;
                
                // Get the current frame data
                let currentFrameData = plotlyDiv._fullData;
                
                // Get the time values for filtering
                let timeSteps = [];
                if (plotlyDiv._fullLayout && plotlyDiv._fullLayout.sliders && plotlyDiv._fullLayout.sliders[1]) {{
                    timeSteps = plotlyDiv._fullLayout.sliders[1].steps.map(step => step.label);
                }}
                
                if (timeSteps.length === 0) return currentFrameData;
                
                // Get start and end time strings for filtering
                let startTimeStr = timeSteps[startTimeIndex] || timeSteps[0];
                let endTimeStr = timeSteps[endTimeIndex] || timeSteps[timeSteps.length - 1];
                
                console.log('Time filtering:', {{
                    startTimeIndex: startTimeIndex,
                    endTimeIndex: endTimeIndex,
                    startTime: startTimeStr,
                    endTime: endTimeStr
                }});
                
                // Parse times for comparison
                let startTime = parseTimeString(startTimeStr);
                let endTime = parseTimeString(endTimeStr);
                
                // Filter each trace based on actual timestamps
                let filteredData = currentFrameData.map(function(trace) {{
                    if (!trace.lat || !trace.lon || !trace.customdata || trace.lat.length === 0) {{
                        return trace; // Return empty trace as-is
                    }}
                    
                    let filteredIndices = [];
                    
                    // Check each data point's timestamp
                    trace.customdata.forEach(function(customPoint, pointIndex) {{
                        if (customPoint && customPoint[0]) {{
                            // customPoint[0] contains the timestamp display (e.g., "15.06 08:02")
                            let pointTime = parseTimeString(customPoint[0]);
                            
                            // Include point if it's within the time window
                            if (pointTime >= startTime && pointTime <= endTime) {{
                                filteredIndices.push(pointIndex);
                            }}
                        }}
                    }});
                    
                    console.log('Filtered trace:', {{
                        originalPoints: trace.lat.length,
                        filteredPoints: filteredIndices.length,
                        traceName: trace.name
                    }});
                    
                    // Create filtered trace
                    let filteredTrace = {{
                        ...trace,
                        lat: filteredIndices.map(i => trace.lat[i]),
                        lon: filteredIndices.map(i => trace.lon[i]),
                        customdata: filteredIndices.map(i => trace.customdata[i])
                    }};
                    
                    return filteredTrace;
                }});
                
                return filteredData;
            }}
            
            // Helper function to parse time strings into comparable values
            function parseTimeString(timeStr) {{
                // Handle different time formats
                // Expected formats: "15.06.2024 08:02:00" or "15.06 08:02"
                let parts = timeStr.trim().split(' ');
                if (parts.length < 2) return 0;
                
                let datePart = parts[0]; // "15.06.2024" or "15.06"
                let timePart = parts[1]; // "08:02:00" or "08:02"
                
                // Parse date
                let dateComponents = datePart.split('.');
                let day = parseInt(dateComponents[0]) || 1;
                let month = parseInt(dateComponents[1]) || 1;
                let year = parseInt(dateComponents[2]) || 2024;
                
                // Parse time
                let timeComponents = timePart.split(':');
                let hours = parseInt(timeComponents[0]) || 0;
                let minutes = parseInt(timeComponents[1]) || 0;
                let seconds = parseInt(timeComponents[2]) || 0;
                
                // Create a timestamp for comparison
                let date = new Date(year, month - 1, day, hours, minutes, seconds);
                return date.getTime();
            }}
            
            // Function to update visualization based on time window
            function updateTimeWindow() {{
                if (!plotlyDiv) return;
                
                console.log('Updating time window:', {{
                    startTimeIndex: startTimeIndex,
                    currentTimeIndex: currentTimeIndex
                }});
                
                // First, navigate to the correct time frame using Plotly's animation
                if (plotlyDiv._fullLayout && plotlyDiv._fullLayout.sliders && plotlyDiv._fullLayout.sliders[1]) {{
                    let mainSlider = plotlyDiv._fullLayout.sliders[1];
                    if (mainSlider.steps && mainSlider.steps[currentTimeIndex]) {{
                        // Navigate to the current time frame first
                        Plotly.animate(plotlyDiv, [mainSlider.steps[currentTimeIndex].name], {{
                            frame: {{ duration: 0, redraw: true }},
                            transition: {{ duration: 0 }}
                        }}).then(function() {{
                            // After navigation, apply the time window filter
                            let filteredData = createFilteredFrame(currentTimeIndex, startTimeIndex);
                            if (filteredData) {{
                                Plotly.react(plotlyDiv, filteredData, plotlyDiv.layout);
                            }}
                        }});
                    }}
                }} else {{
                    // Fallback: just apply filtering
                    let filteredData = createFilteredFrame(currentTimeIndex, startTimeIndex);
                    if (filteredData) {{
                        Plotly.react(plotlyDiv, filteredData, plotlyDiv.layout);
                    }}
                }}
            }}
            
            // Set up slider event listeners
            function setupSliderListeners() {{
                console.log('Setting up slider listeners...');
                
                // Strategy 1: Look for Plotly slider containers
                let sliderContainers = document.querySelectorAll('.slider-container, .rangeslider-container, [class*="slider"]');
                console.log('Found slider containers:', sliderContainers.length);
                
                // Strategy 2: Look for input range elements directly
                let rangeInputs = document.querySelectorAll('input[type="range"]');
                console.log('Found range inputs:', rangeInputs.length);
                
                // Strategy 3: Look within Plotly's layout structure
                let plotlySliders = document.querySelectorAll('.plotly .slider-group, .plotly [class*="slider"]');
                console.log('Found plotly sliders:', plotlySliders.length);
                
                // Try to find slider inputs
                let allSliderInputs = Array.from(rangeInputs);
                
                if (allSliderInputs.length >= 2) {{
                    console.log('Setting up event listeners for', allSliderInputs.length, 'sliders');
                    
                    // Start time slider (left) - index 0
                    let startSlider = allSliderInputs[0];
                    if (startSlider) {{
                        console.log('Setting up start slider');
                        startSlider.addEventListener('input', function(e) {{
                            console.log('Start slider changed to:', e.target.value);
                            startTimeIndex = parseInt(e.target.value) || 0;
                            updateTimeWindow();
                        }});
                    }}
                    
                    // Main time slider (right) - index 1
                    let mainSlider = allSliderInputs[1];
                    if (mainSlider) {{
                        console.log('Setting up main slider');
                        mainSlider.addEventListener('input', function(e) {{
                            console.log('Main slider changed to:', e.target.value);
                            currentTimeIndex = parseInt(e.target.value) || timeFrames.length - 1;
                            updateTimeWindow();
                        }});
                    }}
                }} else {{
                    console.log('Not enough slider inputs found, retrying in 1 second...');
                    setTimeout(setupSliderListeners, 1000);
                }}
            }}
            </script>
            """
            
            # Insert the custom JavaScript before the closing body tag
            html_string = html_string.replace('</body>', time_window_js + '</body>')
            
            # Write the modified HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_string)
            
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

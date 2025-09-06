"""
Trail System Module

Handles trail length configuration and animation frame creation with trail effects.
"""

import os
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, List
from utils.user_interface import UserInterface
from core.gps_utils import format_height_display


class TrailSystem:
    """Manages trail length configuration and frame creation for animations"""
    
    TRAIL_OPTIONS = {
        "all": {"minutes": None, "label": "Show complete flight path (no trail limit)"},
        "30m": {"minutes": 30, "label": "30 minutes trail"},
        "1h": {"minutes": 60, "label": "1 hour trail"},
        "2h": {"minutes": 120, "label": "2 hours trail"},
        "4h": {"minutes": 240, "label": "4 hours trail"},
        "6h": {"minutes": 360, "label": "6 hours trail"},
        "12h": {"minutes": 720, "label": "12 hours trail"},
        "1d": {"minutes": 1440, "label": "1 day trail"},
    }
    
    def __init__(self, ui: UserInterface):
        self.ui = ui
        self.trail_length_minutes: Optional[int] = None
    
    def select_trail_length(self) -> Optional[int]:
        """Let user choose trail length for animation"""
        # Check if running from GUI (environment variable set)
        trail_length_env = os.environ.get('TRAIL_LENGTH_HOURS')
        if trail_length_env:
            try:
                trail_hours = float(trail_length_env)
                trail_minutes = int(trail_hours * 60)
                self.ui.print_success(f"Using GUI trail length: {trail_hours} hours ({trail_minutes} minutes)")
                return trail_minutes
            except Exception:
                self.ui.print_warning(f"Invalid trail length from GUI: {trail_length_env}, falling back to manual selection")
        
        # For testing: use default 2 hours trail length
        self.ui.print_info("Using default 2 hours trail length for testing")
        return 120  # 2 hours in minutes
    
    def _get_user_trail_length_choice(self) -> Optional[int]:
        """Get and validate user's trail length choice"""
        while True:
            choice = input("\nEnter your choice (30m, 1h, 2h, all, etc.) or 'q' to quit: ").strip().lower()
            
            if choice == 'q':
                self.ui.print_info("Operation cancelled by user")
                return False
            
            if choice in self.TRAIL_OPTIONS:
                selected = self.TRAIL_OPTIONS[choice]
                self.ui.print_success(f"Selected: {selected['label']}")
                
                if selected["minutes"] is None:
                    print("📊 Will show complete flight path without trail limitation")
                else:
                    print(f"📊 Will show moving trail of {selected['minutes']} minutes")
                    
                return selected["minutes"]
            
            self.ui.print_error("Invalid choice. Please enter a valid option (e.g., '30m', '1h', 'all')")
    
    def create_frames_with_trail(self, df: pd.DataFrame, vulture_ids: List[str], 
                                color_map: Dict[str, str], unique_times: List[str], 
                                enable_prominent_time_display: bool = True,
                                strategy: str = "markers_fade",
                                enable_precipitation_overlay: bool = False) -> List[go.Frame]:
        """Create animation frames with trail length support and visual effects.

        strategy:
            - "markers_fade": original behavior (lines+markers with fading trail)
            - "line_head": performance mode (single line trail + one head marker)
        """
        frames = []
        
        for time_str in unique_times:
            frame_data = []
            # Parse current frame time as timezone-aware UTC to match dataframes
            current_time = pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S', utc=True)
            
            for vulture_id in vulture_ids:
                vulture_data = df[df['vulture_id'] == vulture_id]
                
                if self.trail_length_minutes is None:
                    # Show complete flight path (no trail limit)
                    trail_data = vulture_data[vulture_data['timestamp_str'] <= time_str]
                else:
                    # Apply trail length filter using tz-aware timestamps
                    trail_start = current_time - pd.Timedelta(minutes=self.trail_length_minutes)
                    # Ensure the 'Timestamp [UTC]' column is tz-aware; if not, try to localize to UTC
                    ts_series = vulture_data['Timestamp [UTC]']
                    try:
                        if ts_series.dt.tz is None:
                            # Localize naive timestamps to UTC (assume they are UTC)
                            ts_series = ts_series.dt.tz_localize('UTC')
                    except Exception:
                        # If .dt accessor fails, fall back to original series
                        pass
                    mask_time = (ts_series >= trail_start)
                    mask_until_frame = (vulture_data['timestamp_str'] <= time_str)
                    trail_data = vulture_data[mask_time & mask_until_frame]
                
                if len(trail_data) > 0:
                    # Sort by timestamp to ensure correct order
                    trail_data = trail_data.sort_values('Timestamp [UTC]')

                    if strategy == "line_head":
                        # Performance: draw the trail once as a line (no per-point styling) and the current head as a single marker
                        # Trail line
                        frame_data.append(
                            go.Scattermap(
                                lat=trail_data['Latitude'].tolist(),
                                lon=trail_data['Longitude'].tolist(),
                                mode='lines',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=3),
                                hoverinfo='skip',
                                showlegend=True,
                            )
                        )
                        # Head marker (latest point only)
                        head = trail_data.iloc[-1]
                        height_display = format_height_display(head['Height'])
                        
                        # Precipitation-based coloring
                        if enable_precipitation_overlay and 'precipitation_mm' in head:
                            precip_value = head['precipitation_mm'] if pd.notna(head['precipitation_mm']) else 0
                            # Color scale: blue for rain, original color for no rain
                            if precip_value > 0:
                                marker_color = self._get_precipitation_color(precip_value)
                                marker_size = 15  # Slightly larger for visibility
                            else:
                                marker_color = color_map[vulture_id]
                                marker_size = 12
                        else:
                            marker_color = color_map[vulture_id]
                            marker_size = 12
                        
                        precip_info = ""
                        if enable_precipitation_overlay and 'precipitation_mm' in head and pd.notna(head['precipitation_mm']) and head['precipitation_mm'] > 0:
                            precip_info = f"<br>🌧️ Rain: {head['precipitation_mm']:.1f} mm/h"
                        
                        frame_data.append(
                            go.Scattermap(
                                lat=[head['Latitude']],
                                lon=[head['Longitude']],
                                mode='markers',
                                name=f"{vulture_id} (current)",
                                marker=dict(color=marker_color, size=marker_size),
                                customdata=[[head['timestamp_display'], height_display, head.get('precipitation_mm', 0)]],
                                hovertemplate=(
                                    f"<b>{vulture_id}</b><br>"
                                    "Time: %{customdata[0]}<br>"
                                    "Lat: %{lat:.6f}°<br>"
                                    "Lon: %{lon:.6f}°<br>"
                                    "Alt: %{customdata[1]}"
                                    f"{precip_info}"
                                    "<extra></extra>"
                                ),
                                showlegend=False,
                            )
                        )
                    else:
                        # Original: fading markers along the trail with precipitation coloring
                        trail_points = len(trail_data)
                        marker_sizes = []
                        marker_opacities = []
                        marker_colors = []
                        customdata = []
                        
                        for i, (_, row) in enumerate(trail_data.iterrows()):
                            height_display = format_height_display(row['Height'])
                            customdata.append([row['timestamp_display'], height_display, row.get('precipitation_mm', 0)])
                            age_factor = i / max(1, trail_points - 1) if trail_points > 1 else 1.0
                            
                            # Precipitation-based coloring
                            if enable_precipitation_overlay and 'precipitation_mm' in row:
                                precip_value = row['precipitation_mm'] if pd.notna(row['precipitation_mm']) else 0
                                if precip_value > 0:
                                    marker_colors.append(self._get_precipitation_color(precip_value))
                                else:
                                    marker_colors.append(color_map[vulture_id])
                            else:
                                marker_colors.append(color_map[vulture_id])
                            
                            if i == trail_points - 1:
                                marker_sizes.append(12)
                                marker_opacities.append(1.0)
                            else:
                                fade_size = 3 + (3 * age_factor)
                                marker_sizes.append(fade_size)
                                fade_opacity = 0.3 + (0.5 * age_factor)
                                marker_opacities.append(fade_opacity)

                        frame_data.append(
                            go.Scattermap(
                                lat=trail_data['Latitude'].tolist(),
                                lon=trail_data['Longitude'].tolist(),
                                mode='lines+markers',
                                name=vulture_id,
                                line=dict(color=color_map[vulture_id], width=3),
                                marker=dict(color=marker_colors, size=marker_sizes, opacity=marker_opacities),
                                customdata=customdata,
                                hovertemplate=(
                                    f"<b>{vulture_id}</b><br>"
                                    "Time: %{customdata[0]}<br>"
                                    "Lat: %{lat:.6f}°<br>"
                                    "Lon: %{lon:.6f}°<br>"
                                    "Alt: %{customdata[1]}<br>"
                                    "🌧️ Rain: %{customdata[2]:.1f} mm/h"
                                    "<extra></extra>"
                                ),
                            )
                        )
                else:
                    # Empty trace for vultures with no data in the trail window
                    frame_data.append(
                        go.Scattermap(
                            lat=[],
                            lon=[],
                            mode='lines+markers',
                            name=vulture_id,
                            line=dict(color=color_map[vulture_id], width=3),
                            marker=dict(color=color_map[vulture_id], size=6)
                        )
                    )
            
            # Create frame with data and layout updates for prominent time display
            frame_layout = {}
            if enable_prominent_time_display:
                frame_layout = {
                    'annotations': [
                        dict(
                            text=f"<b>📅 Current Time:</b><br><span style='font-size: 20px; color: #2E86AB; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);'>{time_str}</span>",
                            x=0.98,
                            y=0.98,
                            xref='paper',
                            yref='paper',
                            xanchor='right',
                            yanchor='top',
                            showarrow=False,
                            bgcolor='rgba(255, 255, 255, 0.95)',
                            bordercolor='rgba(46, 134, 171, 0.8)',
                            borderwidth=2,
                            borderpad=10,
                            font=dict(
                                size=16,
                                color='#333',
                                family='Arial, sans-serif'
                            )
                        )
                    ]
                }
            
            frames.append(go.Frame(data=frame_data, layout=frame_layout, name=time_str))
        
        return frames
    
    def _get_precipitation_color(self, precipitation_mm: float) -> str:
        """Get color based on precipitation intensity"""
        if precipitation_mm <= 0:
            return 'rgba(255, 255, 255, 0.7)'  # Transparent white for no rain
        elif precipitation_mm < 0.5:
            return 'rgba(173, 216, 230, 0.8)'  # Light blue for light rain
        elif precipitation_mm < 2.0:
            return 'rgba(70, 130, 180, 0.9)'   # Medium blue for moderate rain
        elif precipitation_mm < 5.0:
            return 'rgba(25, 25, 112, 0.95)'   # Dark blue for heavy rain
        else:
            return 'rgba(0, 0, 139, 1.0)'      # Very dark blue for very heavy rain
    
    def get_output_filename(self, base_name: str = 'live_map_animation', bird_names: list = None) -> str:
        """Generate appropriate filename based on trail configuration and bird names"""
        filename = base_name
        
        # Add bird names to filename if provided
        if bird_names and len(bird_names) > 0:
            # Sort bird names for consistent ordering
            sorted_birds = sorted(bird_names)
            if len(sorted_birds) <= 3:
                # Include all bird names if 3 or fewer
                birds_str = "_".join(sorted_birds)
            else:
                # Include first 3 birds + count if more
                birds_str = "_".join(sorted_birds[:3]) + f"_and_{len(sorted_birds)-3}_more"
            filename = f'{base_name}_{birds_str}'
        
        # Add trail configuration
        if self.trail_length_minutes is not None:
            return f'{filename}_trail_{self.trail_length_minutes}m'
        else:
            return f'{filename}_full_path'

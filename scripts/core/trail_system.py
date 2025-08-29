"""
Trail System Module

Handles trail length configuration and animation frame creation with trail effects.
"""

import os
import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, List
from utils.user_interface import UserInterface
from gps_utils import format_height_display


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
                                color_map: Dict[str, str], unique_times: List[str]) -> List[go.Frame]:
        """Create animation frames with trail length support"""
        frames = []
        
        for time_str in unique_times:
            frame_data = []
            current_time = pd.to_datetime(time_str, format='%d.%m.%Y %H:%M:%S')
            
            for vulture_id in vulture_ids:
                vulture_data = df[df['vulture_id'] == vulture_id]
                
                if self.trail_length_minutes is None:
                    # Show complete flight path (no trail limit)
                    trail_data = vulture_data[vulture_data['timestamp_str'] <= time_str]
                else:
                    # Apply trail length filter
                    trail_start = current_time - pd.Timedelta(minutes=self.trail_length_minutes)
                    trail_data = vulture_data[
                        (vulture_data['Timestamp [UTC]'] >= trail_start) & 
                        (vulture_data['timestamp_str'] <= time_str)
                    ]
                
                if len(trail_data) > 0:
                    # Prepare custom data for hover
                    customdata = []
                    for _, row in trail_data.iterrows():
                        height_display = format_height_display(row['Height'])
                        customdata.append([row['timestamp_display'], height_display])
                    
                    frame_data.append(
                        go.Scattermap(
                            lat=trail_data['Latitude'].tolist(),
                            lon=trail_data['Longitude'].tolist(),
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
            
            frames.append(go.Frame(data=frame_data, name=time_str))
        
        return frames
    
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

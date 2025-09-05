"""
Mobile Animation Engine

Core mobile-optimized visualization and animation system for GPS flight paths.
Provides touch-friendly interfaces and performance-optimized rendering.
"""

import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, Any
from gps_utils import VisualizationHelper, format_height_display, get_numbered_output_path
from utils.enhanced_timeline_labels import create_enhanced_slider_config
from utils.animation_state_manager import create_reliable_animation_controls
from utils.user_interface import UserInterface
from utils.offline_tiles import ensure_offline_style_for_bounds
from utils.html_injection import inject_fullscreen


class MobileAnimationEngine:
    """Core mobile animation engine for GPS visualizations"""
    
    def __init__(self, mobile_height: int = 500, mobile_zoom: int = 13, mobile_marker_size: int = 12):
        """
        Initialize mobile animation engine
        
        Args:
            mobile_height: Height of mobile visualization in pixels
            mobile_zoom: Default zoom level for mobile maps
            mobile_marker_size: Size of markers for touch interaction
        """
        self.ui = UserInterface()
        self.viz_helper = VisualizationHelper()
        
        # Mobile-specific configuration
        self.mobile_height = mobile_height
        self.mobile_zoom = mobile_zoom
        self.mobile_marker_size = mobile_marker_size
        
        # Animation data
        self.combined_data: Optional[pd.DataFrame] = None
    
    def load_processed_data(self, combined_data: pd.DataFrame) -> None:
        """
        Load processed GPS data for animation
        
        Args:
            combined_data: Combined and filtered GPS dataframe
        """
        self.combined_data = combined_data.copy()
        print(f"📱 Loaded {len(self.combined_data):,} GPS points for mobile animation")
    
    def create_mobile_visualization(self) -> Optional[str]:
        """
        Create mobile-optimized interactive visualization
        
        Returns:
            Path to generated visualization file, or None if failed
        """
        if self.combined_data is None or len(self.combined_data) == 0:
            self.ui.print_error("No data available for visualization")
            return None
        
        self.ui.print_section("📱 MOBILE VISUALIZATION")
        print("Creating mobile-optimized animation...")
        
        try:
            # Prepare mobile-friendly data
            df = self._prepare_mobile_data()
            
            # Create mobile-optimized figure
            fig = self._create_mobile_figure(df)

            # Add animation frames
            self._add_mobile_frames(fig, df)

            # Apply mobile layout (may receive offline style)
            offline_map_style = None
            # If offline map requested, try to prepare an offline style dict
            OFFLINE_MAP = os.environ.get('OFFLINE_MAP', '0') == '1'
            OFFLINE_MAP_DOWNLOAD = os.environ.get('OFFLINE_MAP_DOWNLOAD', '1') == '1'
            TILES_DIR = os.environ.get('TILES_DIR') or os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'tiles_cache')
            try:
                if OFFLINE_MAP:
                    lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
                    lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
                    offline_map_style = ensure_offline_style_for_bounds(
                        lat_min=float(lat_min),
                        lat_max=float(lat_max),
                        lon_min=float(lon_min),
                        lon_max=float(lon_max),
                        zoom_level=self.mobile_zoom,
                        tiles_dir=TILES_DIR,
                        download=OFFLINE_MAP_DOWNLOAD,
                        zoom_pad=1,
                        tile_url_template=os.environ.get('TILE_SERVER_URL', 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
                        tiles_href='./tiles_cache' if os.path.isabs(TILES_DIR) else TILES_DIR,
                    )
                    print(f"🗺️ Using offline tiles from: {TILES_DIR}")
            except Exception as te:
                self.ui.print_warning(f"Offline map setup failed, using online tiles: {te}")

            self._apply_mobile_layout(fig, df, offline_map_style)
            
            # Save visualization
            vulture_ids = df['vulture_id'].unique()
            # Generate filename with bird names
            if len(vulture_ids) <= 3:
                birds_filename = "_".join(sorted(vulture_ids))
            else:
                birds_filename = f"{'_'.join(sorted(vulture_ids)[:3])}_and_{len(vulture_ids)-3}_more"

            output_path = get_numbered_output_path(f'mobile_live_map_{birds_filename}')
            # (offline tiles prepared earlier and applied to layout if requested)
            # Export HTML, inject fullscreen helper and write to disk
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToAdd': [
                    'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
                ],
                'modeBarButtonsToRemove': ['sendDataToCloud'],
                'responsive': False,
                'scrollZoom': True,
                'doubleClick': 'reset',
                'showTips': True,
            }

            html_string = fig.to_html(config=config)
            try:
                html_string = inject_fullscreen(html_string)
            except Exception:
                pass

            # Write out the HTML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_string)

            # If offline tiles were used and tiles dir is absolute, copy tiles next to HTML for portability
            try:
                if OFFLINE_MAP and os.path.isabs(TILES_DIR):
                    import shutil
                    html_dir = os.path.dirname(output_path)
                    dst_tiles = os.path.join(html_dir, 'tiles_cache')
                    if not os.path.exists(dst_tiles):
                        shutil.copytree(TILES_DIR, dst_tiles, dirs_exist_ok=True)
            except Exception as ce:
                self.ui.print_warning(f"Could not copy offline tiles next to HTML: {ce}")

            print(f"📱 Mobile visualization saved: {output_path}")
            return output_path
            
        except Exception as e:
            self.ui.print_error(f"Mobile visualization creation failed: {e}")
            return None
    
    def _prepare_mobile_data(self) -> pd.DataFrame:
        """Prepare data with mobile-friendly formatting"""
        df = self.combined_data.copy()
        
        # Create mobile-friendly timestamp formats
        df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%d.%m.%Y %H:%M:%S')
        df['timestamp_mobile'] = df['Timestamp [UTC]'].dt.strftime('%d.%m %H:%M')
        
        # Sort for proper animation
        df = df.sort_values('Timestamp [UTC]')
        
        return df
    
    def _create_mobile_figure(self, df: pd.DataFrame) -> go.Figure:
        """Create mobile-optimized figure with initial traces"""
        fig = go.Figure()
        
        # Get unique vultures and assign colors
        vulture_ids = df['vulture_id'].unique()
        colors = px.colors.qualitative.Set1[:len(vulture_ids)]
        color_map = dict(zip(vulture_ids, colors))
        
        # Add initial empty traces for each vulture using MapLibre-compatible Scattermap
        for vulture_id in vulture_ids:
            fig.add_trace(
                go.Scattermap(  # MapLibre compatible
                    lat=[],
                    lon=[],
                    mode='lines+markers',
                    name=vulture_id,
                    line=dict(color=color_map[vulture_id], width=4),  # Thicker for mobile
                    marker=dict(color=color_map[vulture_id], size=self.mobile_marker_size),
                    showlegend=True,  # Ensure all birds always show in legend
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
        
        return fig
    
    def _add_mobile_frames(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add animation frames optimized for mobile devices"""
        vulture_ids = df['vulture_id'].unique()
        colors = px.colors.qualitative.Set1[:len(vulture_ids)]
        color_map = dict(zip(vulture_ids, colors))
        
        frames = []
        unique_times = df['timestamp_str'].unique()
        
        print(f"   📊 Creating {len(unique_times)} animation frames...")
        
        for time_str in unique_times:
            frame_data = []
            
            for vulture_id in vulture_ids:
                # Get cumulative data up to this time for each vulture
                vulture_data = df[df['vulture_id'] == vulture_id]
                cumulative_data = vulture_data[vulture_data['timestamp_str'] <= time_str].sort_values('Timestamp [UTC]')
                
                if len(cumulative_data) > 0:
                    # Calculate visual effects for fading trail
                    trail_points = len(cumulative_data)
                    marker_sizes = []
                    marker_opacities = []
                    
                    # Prepare custom data for hover and calculate fading effects
                    customdata = []
                    for i, (_, row) in enumerate(cumulative_data.iterrows()):
                        height_display = format_height_display(row['Height'])
                        customdata.append([row['timestamp_mobile'], height_display])
                        
                        # Calculate age factor (0 = oldest, 1 = newest)
                        age_factor = i / max(1, trail_points - 1) if trail_points > 1 else 1.0
                        
                        # Create fading effect for markers (mobile-optimized sizes)
                        if i == trail_points - 1:  # Current position (newest point)
                            marker_sizes.append(self.mobile_marker_size + 4)  # Even larger for mobile touch
                            marker_opacities.append(1.0)  # Full opacity for current position
                        else:
                            # Fade trail markers based on age (mobile-friendly sizes)
                            base_size = max(6, self.mobile_marker_size - 4)
                            fade_size = base_size + (4 * age_factor)
                            marker_sizes.append(fade_size)
                            # Fade opacity (min 0.4, max 0.8 for trail)
                            fade_opacity = 0.4 + (0.4 * age_factor)
                            marker_opacities.append(fade_opacity)
                    
                    frame_data.append(
                        go.Scattermap(  # MapLibre compatible
                            lat=cumulative_data['Latitude'].tolist(),
                            lon=cumulative_data['Longitude'].tolist(),
                            mode='lines+markers',
                            name=vulture_id,
                            line=dict(color=color_map[vulture_id], width=4),
                            marker=dict(
                                color=color_map[vulture_id], 
                                size=marker_sizes,
                                opacity=marker_opacities
                            ),
                            customdata=customdata,
                            hovertemplate=(
                                f"<b>{vulture_id}</b><br>"
                                "Time: %{customdata[0]}<br>"
                                "Lat: %{lat:.4f}°<br>"
                                "Lon: %{lon:.4f}°<br>"
                                "Alt: %{customdata[1]}"
                                "<extra></extra>"
                            )
                        )
                    )
                else:
                    # Empty trace for vultures with no data at this time
                    frame_data.append(
                        go.Scattermap(  # MapLibre compatible
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
        print(f"   ✅ Added {len(frames)} mobile-optimized frames")
    
    def _apply_mobile_layout(self, fig: go.Figure, df: pd.DataFrame, offline_map_style: Optional[dict] = None) -> None:
        """Apply mobile-optimized layout settings"""
        # Calculate smart bounds with extra padding for mobile
        map_bounds = self.viz_helper.calculate_map_bounds(df, padding_percent=0.2)

        # Determine map style: prefer offline_map_style if provided
        map_style_value = offline_map_style if offline_map_style is not None else "open-street-map"

        fig.update_layout(
            # Mobile-optimized MapLibre layout
            map=dict(
                style=map_style_value,  # MapLibre-compatible style or online string
                center=dict(
                    lat=map_bounds['center']['lat'], 
                    lon=map_bounds['center']['lon']
                ),
                zoom=self.mobile_zoom,
                bearing=0,
                pitch=0
            ),
            
            # Mobile-specific dimensions and styling
            height=self.mobile_height,
            width=None,  # Let it be responsive
            margin=dict(l=0, r=0, t=40, b=0),  # Minimal margins for mobile
            
            # Mobile-friendly title
            title=dict(
                text="📱 Mobile GPS Flight Animation",
                font=dict(size=16),  # Smaller title for mobile
                x=0.5,
                xanchor='center'
            ),
            
            # Mobile-optimized legend
            legend=dict(
                orientation="h",  # Horizontal legend for mobile
                x=0.5,
                xanchor='center',
                y=-0.05,
                yanchor='top',
                font=dict(size=10)  # Smaller legend text
            ),
            
            # Mobile-friendly reliable animation controls
            **create_reliable_animation_controls(
                frame_duration=800,  # Mobile-optimized slower pace
                include_speed_controls=False  # Simplified for mobile
            ),
            
            # Mobile-optimized enhanced slider
            sliders=[create_enhanced_slider_config(
                [frame.name for frame in fig.frames], 
                position_y=0.02, 
                position_x=0.1, 
                length=0.8,
                enable_prominent_display=True
            )]
        )
        
        print("   ✅ Applied mobile-optimized layout")
    
    def get_animation_info(self) -> Dict[str, Any]:
        """
        Get information about the current animation setup
        
        Returns:
            Dictionary with animation metrics
        """
        if self.combined_data is None:
            return {}
        
        df = self.combined_data
        unique_times = df['Timestamp [UTC]'].unique()
        
        return {
            'total_points': len(df),
            'unique_vultures': len(df['vulture_id'].unique()),
            'animation_frames': len(unique_times),
            'time_span_hours': (df['Timestamp [UTC]'].max() - df['Timestamp [UTC]'].min()).total_seconds() / 3600,
            'mobile_optimized': True,
            'marker_size': self.mobile_marker_size,
            'mobile_height': self.mobile_height
        }

"""
3D Animation Engine

Core 3D visualization system for GPS flight paths with real terrain data.
Provides high-quality 3D animations with downloadable elevation models.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Optional, Dict, Any
from gps_utils import VisualizationHelper, format_height_display, get_numbered_output_path
from utils.user_interface import UserInterface
from core.elevation_data_manager import ElevationDataManager, ElevationData


class Animation3DEngine:
    """Core 3D animation engine for GPS visualizations with real terrain"""
    
    def __init__(self, elevation_manager: ElevationDataManager = None):
        """
        Initialize 3D animation engine
        
        Args:
            elevation_manager: Optional elevation data manager instance
        """
        self.ui = UserInterface()
        self.viz_helper = VisualizationHelper()
        
        # Elevation data management
        self.elevation_manager = elevation_manager or ElevationDataManager()
        self.current_elevation_data: Optional[ElevationData] = None
        
        # Animation data
        self.combined_data: Optional[pd.DataFrame] = None
        
        # 3D visualization settings
        self.terrain_opacity = 0.7
        self.terrain_colorscale = 'earth'
        self.animation_speed = 800  # ms per frame
        self.trail_mode = 'lines+markers'
        self.marker_size = 8
        self.line_width = 3
    
    def load_processed_data(self, combined_data: pd.DataFrame) -> None:
        """
        Load processed GPS data for 3D animation
        
        Args:
            combined_data: Combined and filtered GPS dataframe
        """
        self.combined_data = combined_data.copy()
        print(f"🎬 Loaded {len(self.combined_data):,} GPS points for 3D animation")
    
    def setup_terrain(self, region_name: str = 'berchtesgaden_full', 
                     resolution: int = 100, force_download: bool = False) -> bool:
        """
        Set up terrain data for the 3D visualization
        
        Args:
            region_name: Name of predefined region
            resolution: Terrain grid resolution
            force_download: Force re-download of elevation data
            
        Returns:
            True if terrain setup successful, False otherwise
        """
        self.ui.print_section("🏔️ TERRAIN SETUP")
        
        # Show available regions if user wants to see options
        print("Available regions:")
        self.elevation_manager.list_available_regions()
        
        # Load elevation data
        elevation_data = self.elevation_manager.get_elevation_data(
            region_name, resolution, force_download
        )
        
        if elevation_data:
            self.current_elevation_data = elevation_data
            
            # Display terrain info
            info = self.elevation_manager.get_region_info(elevation_data)
            print(f"✅ Terrain ready: {info['region_name']}")
            print(f"   📊 Resolution: {info['resolution']}")
            print(f"   🏔️  Elevation: {info['elevation_range']}")
            print(f"   📐 Area: {info['area_km2']:.1f} km²")
            
            return True
        else:
            self.ui.print_error("Failed to load terrain data")
            return False
    
    def create_3d_visualization(self, animation_type: str = 'full') -> Optional[str]:
        """
        Create 3D visualization with real terrain
        
        Args:
            animation_type: 'full' for full animation, 'static' for single frame
            
        Returns:
            Path to generated visualization file, or None if failed
        """
        if self.combined_data is None or len(self.combined_data) == 0:
            self.ui.print_error("No GPS data available for visualization")
            return None
        
        if self.current_elevation_data is None:
            self.ui.print_error("No terrain data loaded. Call setup_terrain() first.")
            return None
        
        self.ui.print_section("🎬 CREATING 3D VISUALIZATION")
        print(f"Animation type: {animation_type}")
        
        try:
            # Prepare 3D data
            df = self._prepare_3d_data()
            
            # Validate data is within terrain bounds
            if not self._validate_data_bounds(df):
                self.ui.print_warning("GPS data extends beyond terrain bounds")
                print("Consider using a larger terrain region or different data")
            
            # Create 3D figure
            fig = self._create_3d_figure(df, animation_type)
            
            # Add terrain surface
            self._add_terrain_surface(fig)
            
            # Add GPS flight paths
            if animation_type == 'full':
                self._add_3d_animation_frames(fig, df)
            else:
                self._add_static_3d_paths(fig, df)
            
            # Apply 3D layout
            self._apply_3d_layout(fig, df, animation_type)
            
            # Save visualization
            vulture_ids = df['vulture_id'].unique()
            # Generate filename with bird names
            if len(vulture_ids) <= 3:
                birds_filename = "_".join(sorted(vulture_ids))
            else:
                birds_filename = f"{'_'.join(sorted(vulture_ids)[:3])}_and_{len(vulture_ids)-3}_more"
            
            base_filename = '3d_flight_animation' if animation_type == 'full' else '3d_flight_paths'
            filename = f'{base_filename}_{birds_filename}'
            output_path = get_numbered_output_path(filename)
            fig.write_html(output_path)
            
            self.ui.print_success(f"🏔️ 3D visualization saved: {output_path}")
            return output_path
            
        except Exception as e:
            self.ui.print_error(f"3D visualization creation failed: {e}")
            return None
    
    def _prepare_3d_data(self) -> pd.DataFrame:
        """Prepare data for 3D visualization"""
        df = self.combined_data.copy()
        
        # Ensure required columns exist
        required_columns = ['Timestamp [UTC]', 'Latitude', 'Longitude', 'Height', 'vulture_id']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Create formatted timestamps for display
        df['timestamp_str'] = df['Timestamp [UTC]'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['timestamp_short'] = df['Timestamp [UTC]'].dt.strftime('%H:%M')
        
        # Sort by timestamp for proper animation
        df = df.sort_values('Timestamp [UTC]')
        
        # Ensure height is numeric and handle missing values
        df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
        df['Height'] = df['Height'].fillna(df['Height'].median())
        
        return df
    
    def _validate_data_bounds(self, df: pd.DataFrame) -> bool:
        """Check if GPS data fits within terrain bounds"""
        terrain = self.current_elevation_data
        
        lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
        lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
        
        within_bounds = (
            lat_min >= terrain.bounds.lat_min and lat_max <= terrain.bounds.lat_max and
            lon_min >= terrain.bounds.lon_min and lon_max <= terrain.bounds.lon_max
        )
        
        if not within_bounds:
            print(f"   ⚠️ Data bounds: lat {lat_min:.3f}-{lat_max:.3f}, lon {lon_min:.3f}-{lon_max:.3f}")
            print(f"   🏔️ Terrain bounds: lat {terrain.bounds.lat_min:.3f}-{terrain.bounds.lat_max:.3f}, "
                  f"lon {terrain.bounds.lon_min:.3f}-{terrain.bounds.lon_max:.3f}")
        
        return within_bounds
    
    def _create_3d_figure(self, df: pd.DataFrame, animation_type: str) -> go.Figure:
        """Create base 3D figure"""
        fig = go.Figure()
        
        # Set up initial empty traces for each vulture
        vulture_ids = df['vulture_id'].unique()
        colors = px.colors.qualitative.Set1[:len(vulture_ids)]
        
        for i, vulture_id in enumerate(vulture_ids):
            fig.add_trace(
                go.Scatter3d(
                    x=[], y=[], z=[],
                    mode=self.trail_mode,
                    name=vulture_id,
                    line=dict(color=colors[i], width=self.line_width),
                    marker=dict(color=colors[i], size=self.marker_size),
                    showlegend=True,  # Ensure all birds always show in legend
                    hovertemplate=(
                        f"<b>{vulture_id}</b><br>"
                        "Time: %{customdata[0]}<br>"
                        "Lat: %{y:.4f}°<br>"
                        "Lon: %{x:.4f}°<br>"
                        "Alt: %{customdata[1]}m"
                        "<extra></extra>"
                    )
                )
            )
        
        return fig
    
    def _add_terrain_surface(self, fig: go.Figure) -> None:
        """Add terrain surface to the 3D plot"""
        terrain = self.current_elevation_data
        
        print("   🏔️ Adding terrain surface...")
        
        # Create meshgrid for terrain
        X, Y = np.meshgrid(terrain.lons, terrain.lats)
        
        # Add terrain surface
        fig.add_trace(
            go.Surface(
                x=X,
                y=Y,
                z=terrain.elevations,
                colorscale=self.terrain_colorscale,
                opacity=self.terrain_opacity,
                showscale=False,
                name=f'Terrain ({terrain.region_name})',
                hovertemplate=(
                    "Terrain<br>"
                    "Lat: %{y:.4f}°<br>"
                    "Lon: %{x:.4f}°<br>"
                    "Elevation: %{z:.0f}m"
                    "<extra></extra>"
                ),
                lighting=dict(
                    ambient=0.3,
                    diffuse=0.8,
                    specular=0.2,
                    roughness=0.5
                ),
                contours=dict(
                    z=dict(show=True, start=terrain.elevations.min(), 
                          end=terrain.elevations.max(), size=200,
                          color="white", width=1)
                )
            )
        )
        
        print(f"   ✅ Terrain surface added ({terrain.resolution}x{terrain.resolution} grid)")
    
    def _add_3d_animation_frames(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add animation frames for 3D visualization"""
        vulture_ids = df['vulture_id'].unique()
        colors = px.colors.qualitative.Set1[:len(vulture_ids)]
        color_map = dict(zip(vulture_ids, colors))
        
        # Get unique timestamps for frames
        unique_times = df['timestamp_str'].unique()
        
        print(f"   🎬 Creating {len(unique_times)} animation frames...")
        
        frames = []
        for time_str in unique_times:
            frame_data = []
            
            # Re-add terrain surface for each frame
            terrain = self.current_elevation_data
            X, Y = np.meshgrid(terrain.lons, terrain.lats)
            frame_data.append(
                go.Surface(
                    x=X, y=Y, z=terrain.elevations,
                    colorscale=self.terrain_colorscale,
                    opacity=self.terrain_opacity,
                    showscale=False,
                    name=f'Terrain ({terrain.region_name})'
                )
            )
            
            # Add cumulative flight paths for each vulture
            for vulture_id in vulture_ids:
                vulture_data = df[df['vulture_id'] == vulture_id]
                cumulative_data = vulture_data[vulture_data['timestamp_str'] <= time_str]
                
                if len(cumulative_data) > 0:
                    # Prepare custom data for hover
                    customdata = []
                    for _, row in cumulative_data.iterrows():
                        height_display = format_height_display(row['Height'])
                        customdata.append([row['timestamp_short'], height_display])
                    
                    frame_data.append(
                        go.Scatter3d(
                            x=cumulative_data['Longitude'].tolist(),
                            y=cumulative_data['Latitude'].tolist(),
                            z=cumulative_data['Height'].tolist(),
                            mode=self.trail_mode,
                            name=vulture_id,
                            line=dict(color=color_map[vulture_id], width=self.line_width),
                            marker=dict(color=color_map[vulture_id], size=self.marker_size),
                            customdata=customdata,
                            hovertemplate=(
                                f"<b>{vulture_id}</b><br>"
                                "Time: %{customdata[0]}<br>"
                                "Lat: %{y:.4f}°<br>"
                                "Lon: %{x:.4f}°<br>"
                                "Alt: %{customdata[1]}"
                                "<extra></extra>"
                            )
                        )
                    )
                else:
                    # Empty trace for vultures with no data at this time
                    frame_data.append(
                        go.Scatter3d(
                            x=[], y=[], z=[],
                            mode=self.trail_mode,
                            name=vulture_id,
                            line=dict(color=color_map[vulture_id], width=self.line_width),
                            marker=dict(color=color_map[vulture_id], size=self.marker_size)
                        )
                    )
            
            frames.append(go.Frame(data=frame_data, name=time_str))
        
        fig.frames = frames
        print(f"   ✅ Added {len(frames)} 3D animation frames")
    
    def _add_static_3d_paths(self, fig: go.Figure, df: pd.DataFrame) -> None:
        """Add static 3D flight paths (no animation)"""
        vulture_ids = df['vulture_id'].unique()
        
        print(f"   🛤️ Adding static 3D paths for {len(vulture_ids)} vultures...")
        
        for i, vulture_id in enumerate(vulture_ids):
            vulture_data = df[df['vulture_id'] == vulture_id].sort_values('Timestamp [UTC]')
            
            if len(vulture_data) > 0:
                # Prepare custom data for hover
                customdata = []
                for _, row in vulture_data.iterrows():
                    height_display = format_height_display(row['Height'])
                    customdata.append([row['timestamp_short'], height_display])
                
                # Update the existing trace
                fig.data[i].update(
                    x=vulture_data['Longitude'].tolist(),
                    y=vulture_data['Latitude'].tolist(),
                    z=vulture_data['Height'].tolist(),
                    customdata=customdata
                )
        
        print(f"   ✅ Added static paths for {len(vulture_ids)} vultures")
    
    def _apply_3d_layout(self, fig: go.Figure, df: pd.DataFrame, animation_type: str) -> None:
        """Apply 3D layout settings"""
        terrain = self.current_elevation_data
        
        # Calculate scene bounds
        alt_max = max(df['Height'].max(), terrain.elevations.max()) * 1.2
        
        # Set up 3D scene
        scene_dict = dict(
            xaxis=dict(
                title='Longitude (°)',
                range=[terrain.bounds.lon_min, terrain.bounds.lon_max],
                showgrid=True,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Latitude (°)',
                range=[terrain.bounds.lat_min, terrain.bounds.lat_max],
                showgrid=True,
                gridcolor='lightgray'
            ),
            zaxis=dict(
                title='Elevation (m)',
                range=[terrain.elevations.min() * 0.9, alt_max],
                showgrid=True,
                gridcolor='lightgray'
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode='manual',
            aspectratio=dict(
                x=1,
                y=(terrain.bounds.lat_max - terrain.bounds.lat_min) / 
                  (terrain.bounds.lon_max - terrain.bounds.lon_min),
                z=0.3  # Compressed z-axis for better visualization
            )
        )
        
        layout_updates = dict(
            title=dict(
                text=f"🏔️ 3D GPS Flight Paths - {terrain.bounds.description}",
                font=dict(size=18),
                x=0.5,
                xanchor='center'
            ),
            scene=scene_dict,
            height=800,
            margin=dict(l=0, r=0, t=60, b=0),
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='gray',
                borderwidth=1
            )
        )
        
        # Add animation controls if this is an animated visualization
        if animation_type == 'full' and hasattr(fig, 'frames') and fig.frames:
            layout_updates.update({
                'updatemenus': [{
                    'buttons': [
                        {
                            'args': [None, {
                                'frame': {'duration': self.animation_speed, 'redraw': True},
                                'transition': {'duration': 300}
                            }],
                            'label': '▶️ Play',
                            'method': 'animate'
                        },
                        {
                            'args': [[None], {
                                'frame': {'duration': 0, 'redraw': True},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }],
                            'label': '⏸️ Pause',
                            'method': 'animate'
                        }
                    ],
                    'direction': 'left',
                    'pad': {'r': 10, 't': 85},
                    'type': 'buttons',
                    'x': 0.1,
                    'y': 0.02,
                    'xanchor': 'right',
                    'yanchor': 'bottom'
                }],
                'sliders': [{
                    'steps': [
                        {
                            'args': [[frame.name], {
                                'frame': {'duration': 0, 'redraw': True},
                                'mode': 'immediate',
                                'transition': {'duration': 0}
                            }],
                            'label': frame.name.split(' ')[1] if ' ' in frame.name else frame.name[:10],
                            'method': 'animate'
                        } for frame in fig.frames
                    ],
                    'active': 0,
                    'len': 0.8,
                    'x': 0.1,
                    'y': 0.02,
                    'xanchor': 'left',
                    'yanchor': 'bottom',
                    'transition': {'duration': 300},
                    'currentvalue': {
                        'font': {'size': 12},
                        'prefix': '🕒 ',
                        'visible': True,
                        'xanchor': 'center'
                    }
                }]
            })
        
        fig.update_layout(**layout_updates)
        print("   ✅ Applied 3D layout with terrain camera positioning")
    
    def get_3d_info(self) -> Dict[str, Any]:
        """Get information about the current 3D setup"""
        info = {
            'has_data': self.combined_data is not None,
            'has_terrain': self.current_elevation_data is not None,
            'animation_speed_ms': self.animation_speed,
            'terrain_opacity': self.terrain_opacity
        }
        
        if self.combined_data is not None:
            df = self.combined_data
            info.update({
                'total_points': len(df),
                'unique_vultures': len(df['vulture_id'].unique()),
                'time_span_hours': (df['Timestamp [UTC]'].max() - df['Timestamp [UTC]'].min()).total_seconds() / 3600,
                'altitude_range_m': f"{df['Height'].min():.0f} - {df['Height'].max():.0f}"
            })
        
        if self.current_elevation_data is not None:
            terrain_info = self.elevation_manager.get_region_info(self.current_elevation_data)
            info.update({
                'terrain_region': terrain_info['region_name'],
                'terrain_resolution': terrain_info['resolution'],
                'terrain_elevation_range': terrain_info['elevation_range'],
                'terrain_area_km2': terrain_info['area_km2']
            })
        
        return info

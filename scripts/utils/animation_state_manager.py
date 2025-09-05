"""
Animation State Management System
Handles reliable animation state for Plotly visualizations

This module provides robust animation control that handles common issues:
- Play button not working after slider interaction
- Animation state conflicts between manual slider and play controls
- Memory management for smooth performance
- Frame synchronization and timing
"""

from typing import Dict, Any, Optional, List


class AnimationStateManager:
    """Manages reliable animation state for Plotly visualizations"""
    
    def __init__(self, frame_duration: int = 500):
        """
        Initialize animation state manager
        
        Args:
            frame_duration: Default frame duration in milliseconds
        """
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.total_frames = 0
        self.is_playing = False
        
    def create_robust_play_button(self, frame_duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a robust play button configuration that handles state conflicts
        
        Args:
            frame_duration: Frame duration in milliseconds (uses default if None)
            
        Returns:
            Play button configuration dict
        """
        duration = frame_duration or self.frame_duration
        
        return {
            "label": "▶️ Play",
            "method": "animate",
            "args": [None, {
                "frame": {
                    "duration": duration,
                    "redraw": True  # Force redraw for reliability
                },
                "transition": {
                    "duration": min(100, duration // 3),  # Faster transitions
                    "easing": "linear"
                },
                "fromcurrent": True,  # Continue from current position
                "mode": "immediate"   # Start immediately, don't wait
            }],
            "execute": True  # Ensure execution regardless of state
        }
    
    def create_robust_pause_button(self) -> Dict[str, Any]:
        """
        Create a robust pause button configuration
        
        Returns:
            Pause button configuration dict
        """
        return {
            "label": "⏸️ Pause",
            "method": "animate",
            "args": [[None], {
                "frame": {"duration": 0, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 0}
            }],
            "execute": True
        }
    
    def create_robust_restart_button(self, frame_duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a robust restart button that resets animation state
        
        Args:
            frame_duration: Frame duration in milliseconds (uses default if None)
            
        Returns:
            Restart button configuration dict
        """
        duration = frame_duration or self.frame_duration
        
        return {
            "label": "⏮️ Restart",
            "method": "animate",
            "args": [None, {
                "frame": {
                    "duration": duration,
                    "redraw": True
                },
                "transition": {
                    "duration": 100,
                    "easing": "linear"
                },
                "fromcurrent": False,  # Start from beginning
                "mode": "immediate"
            }],
            "execute": True
        }
    
    def create_recenter_button(self, center_lat: float, center_lon: float, zoom_level: int) -> Dict[str, Any]:
        """
        Create a recenter button that resets the map view to original bounds
        
        Args:
            center_lat: Original center latitude
            center_lon: Original center longitude  
            zoom_level: Original zoom level
            
        Returns:
            Recenter button configuration dict
        """
        return {
            "label": "🎯 Recenter",
            "method": "relayout",
            "args": [{
                "map.center.lat": center_lat,
                "map.center.lon": center_lon,
                "map.zoom": zoom_level
            }],
            "execute": True
        }
    
    def create_fullscreen_button(self) -> Dict[str, Any]:
        """
        Create a fullscreen button that makes the entire page fullscreen
        
        Returns:
            Fullscreen button configuration dict
        """
        return {
            "label": "⛶ Fullscreen",
            "method": "restyle",  # We'll use custom JavaScript for this
            "args": [{}],  # Empty args, functionality handled by custom JS
            "execute": True
        }

    def create_radar_toggle_button(self) -> Dict[str, Any]:
        """Create a button to toggle radar overlay visibility via injected JS."""
        return {
            "label": "☔ Radar",
            "method": "restyle",  # Handled by custom JS injection
            "args": [{}],
            "execute": True,
        }
    
    def create_speed_control_buttons(self, speeds: List[float] = None) -> List[Dict[str, Any]]:
        """
        Create speed control buttons for dynamic playback speed
        
        Args:
            speeds: List of speed multipliers (default: [1.0, 2.0, 3.0, 5.0, 10.0])
            
        Returns:
            List of speed control button configurations
        """
        if speeds is None:
            speeds = [1.0, 2.0, 3.0, 5.0, 10.0]
        
        speed_buttons = []
        for speed in speeds:
            duration = max(50, int(self.frame_duration / speed))  # Minimum 50ms
            label = f"{speed:g}x"  # Format without unnecessary .0 decimals
            
            speed_buttons.append({
                "label": label,
                "method": "animate",  # Back to animate method
                "args": [None, {
                    "frame": {
                        "duration": duration,
                        "redraw": True
                    },
                    "transition": {
                        "duration": min(100, duration // 3),
                        "easing": "linear"
                    },
                    "fromcurrent": True,
                    "mode": "immediate"  # Changed to immediate for consistency
                }],
                "execute": True
            })
        
        return speed_buttons
    
    def create_speed_control_slider(self, min_speed: float = 1.0, max_speed: float = 10.0, 
                                   step: float = 0.5, position_y: float = 0.25) -> Dict[str, Any]:
        """
        Create a speed control slider for continuous speed adjustment
        
        Args:
            min_speed: Minimum speed multiplier
            max_speed: Maximum speed multiplier  
            step: Step size for speed increments
            position_y: Y position of the slider (0-1)
            
        Returns:
            Speed slider configuration dict
        """
        # Create speed steps from min to max
        speeds = []
        current = min_speed
        while current <= max_speed:
            speeds.append(current)
            current += step
            
        # Ensure max_speed is included
        if speeds[-1] != max_speed:
            speeds.append(max_speed)
        
        speed_steps = []
        for speed in speeds:
            duration = max(50, int(self.frame_duration / speed))
            label = f"{speed:g}x"  # Format without unnecessary decimals
            
            speed_steps.append({
                'args': [None, {
                    "frame": {
                        "duration": duration,
                        "redraw": True
                    },
                    "transition": {
                        "duration": min(100, duration // 3),
                        "easing": "linear"
                    },
                    "fromcurrent": True,
                    "mode": "immediate"
                }],
                'label': label,
                'method': 'animate',
                'execute': True
            })
        
        return {
            'active': 0,  # Default to first speed (1x)
            'currentvalue': {
                'prefix': '⚡ Speed: ',
                'suffix': '',
                'font': {'size': 12, 'color': '#2c3e50'},
                'visible': True,
                'xanchor': 'left',
                'offset': 10
            },
            'x': 0.75,  # Right side position
            'y': position_y,
            'len': 0.2,  # Compact slider
            'steps': speed_steps,
            'transition': {'duration': 100},
            'tickcolor': 'rgba(0,0,0,0.4)',
            'bordercolor': 'rgba(0,0,0,0.4)', 
            'borderwidth': 1,
            'bgcolor': 'rgba(255,255,255,0.9)',
            'pad': {'t': 10, 'b': 10},
            'visible': True
        }
    
    def create_enhanced_updatemenus(self, 
                                   include_speed_controls: bool = True,
                                   frame_duration: Optional[int] = None,
                                   center_lat: Optional[float] = None,
                                   center_lon: Optional[float] = None,
                                   zoom_level: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Create enhanced animation control menus with improved reliability
        
        Args:
            include_speed_controls: Whether to include speed control buttons
            frame_duration: Frame duration in milliseconds
            center_lat: Map center latitude for recenter button
            center_lon: Map center longitude for recenter button
            zoom_level: Map zoom level for recenter button
            
        Returns:
            List of updatemenu configurations
        """
        duration = frame_duration or self.frame_duration
        
        # Main playback controls (centered, bottom position)
        main_controls = {
            "type": "buttons",
            "direction": "left",
            "x": 0.5,
            "y": 0.05,  # Moved up slightly from slider
            "xanchor": "center",
            "yanchor": "bottom",
            "showactive": True,
            "bgcolor": "rgba(255,255,255,0.95)",
            "bordercolor": "rgba(0,0,0,0.3)",
            "borderwidth": 2,
            "font": {"size": 14, "color": "#333"},
            "buttons": [
                self.create_robust_play_button(duration),
                self.create_robust_pause_button(),
                self.create_robust_restart_button(duration),
                self.create_fullscreen_button(),
                self.create_radar_toggle_button()
            ] + ([self.create_recenter_button(center_lat, center_lon, zoom_level)] 
                 if all(x is not None for x in [center_lat, center_lon, zoom_level]) else []),
            # Fixed positioning to prevent movement
            "pad": {"t": 8, "b": 8, "l": 12, "r": 12}
        }
        
        updatemenus = [main_controls]
        
        # Speed controls (well separated above main controls)
        if include_speed_controls:
            speed_controls = {
                "type": "buttons",
                "direction": "left",
                "x": 0.5,
                "y": 0.18,  # Much higher to avoid overlap
                "xanchor": "center",
                "yanchor": "bottom",
                "showactive": True,
                "bgcolor": "rgba(240,240,240,0.9)",
                "bordercolor": "rgba(0,0,0,0.2)",
                "borderwidth": 1,
                "font": {"size": 11, "color": "#666"},
                "buttons": self.create_speed_control_buttons(),
                # Compact padding to keep buttons tight
                "pad": {"t": 4, "b": 4, "l": 8, "r": 8}
            }
            updatemenus.append(speed_controls)
        
        return updatemenus
    
    def create_robust_slider_step(self, frame_index: int, 
                                 frame_name: str, 
                                 label: str) -> Dict[str, Any]:
        """
        Create a robust slider step that maintains animation state
        
        Args:
            frame_index: Index of the frame
            frame_name: Name of the frame
            label: Display label for the step
            
        Returns:
            Slider step configuration dict
        """
        return {
            "args": [[frame_name], {
                "frame": {"duration": 0, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 0}
            }],
            "label": label,
            "method": "animate",
            "execute": True,  # Ensure execution
            "value": frame_index  # Track frame position
        }
    
    def get_animation_config(self, frame_duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive animation configuration for Plotly figures
        
        Args:
            frame_duration: Frame duration in milliseconds
            
        Returns:
            Complete animation configuration dict
        """
        duration = frame_duration or self.frame_duration
        
        return {
            "frame": {
                "duration": duration,
                "redraw": True
            },
            "transition": {
                "duration": min(200, duration // 2),
                "easing": "linear"
            },
            "fromcurrent": True,
            "mode": "afterall"
        }


def create_memory_optimized_frames(vulture_data: Dict, 
                                  frame_names: List[str],
                                  max_frames_in_memory: int = 50) -> List[Dict[str, Any]]:
    """
    Create memory-optimized animation frames to prevent performance issues
    
    Args:
        vulture_data: Dictionary of vulture position data
        frame_names: List of frame names/timestamps
        max_frames_in_memory: Maximum frames to keep in memory simultaneously
        
    Returns:
        List of optimized frame configurations
    """
    # Implementation would depend on specific data structure
    # This is a placeholder for memory optimization logic
    optimized_frames = []
    
    for i, frame_name in enumerate(frame_names):
        # Only keep essential data for each frame
        frame_data = {
            "name": frame_name,
            "data": [],  # Minimal data structure
            "layout": {}  # Minimal layout updates
        }
        optimized_frames.append(frame_data)
    
    return optimized_frames


# Factory function for easy integration
def create_reliable_animation_controls(frame_duration: int = 500,
                                     include_speed_controls: bool = True,
                                     center_lat: Optional[float] = None,
                                     center_lon: Optional[float] = None,
                                     zoom_level: Optional[int] = None) -> Dict[str, Any]:
    """
    Factory function to create reliable animation controls
    
    Args:
        frame_duration: Default frame duration in milliseconds
        include_speed_controls: Whether to include speed control buttons
        center_lat: Map center latitude for recenter button
        center_lon: Map center longitude for recenter button
        zoom_level: Map zoom level for recenter button
        
    Returns:
        Dictionary containing updatemenus configuration
    """
    manager = AnimationStateManager(frame_duration)
    return {
        "updatemenus": manager.create_enhanced_updatemenus(
            include_speed_controls=include_speed_controls,
            frame_duration=frame_duration,
            center_lat=center_lat,
            center_lon=center_lon,
            zoom_level=zoom_level
        )
    }

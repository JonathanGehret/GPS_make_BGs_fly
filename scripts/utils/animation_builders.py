"""
Animation builder utilities to keep main scripts lean and reusable.

Functions:
- build_color_map: consistent color assignment for vultures
- create_base_figure: initializes a Plotly figure with empty traces
- apply_standard_layout: sets map, size, margins, title, legend
- apply_controls_and_slider: wires updatemenus and slider
- attach_frames: applies TrailSystem frames to the figure
"""

from __future__ import annotations

from typing import Dict, Sequence

import plotly.express as px
import plotly.graph_objects as go

from .enhanced_timeline_labels import create_enhanced_slider_config
from .animation_state_manager import create_reliable_animation_controls


def build_color_map(vulture_ids: Sequence[str]) -> Dict[str, str]:
    """Return a color map for the given vulture IDs using a qualitative palette."""
    colors = px.colors.qualitative.Set1[: len(vulture_ids)]
    return dict(zip(vulture_ids, colors))


def create_base_figure(vulture_ids: Sequence[str], color_map: Dict[str, str], *, strategy: str = "markers_fade") -> go.Figure:
    """Create a base figure with empty traces matching the animation strategy.

    strategy:
      - "markers_fade": one trace per vulture (lines+markers)
      - "line_head": two traces per vulture (line trail + current head marker)
    """
    fig = go.Figure()
    for vulture_id in vulture_ids:
        if strategy == "line_head":
            # Trail line trace
            fig.add_trace(
                go.Scattermap(
                    lat=[],
                    lon=[],
                    mode="lines",
                    name=vulture_id,
                    line=dict(color=color_map[vulture_id], width=3),
                    hoverinfo="skip",
                    showlegend=True,
                )
            )
            # Head marker trace
            fig.add_trace(
                go.Scattermap(
                    lat=[],
                    lon=[],
                    mode="markers",
                    name=f"{vulture_id} (current)",
                    marker=dict(color=color_map[vulture_id], size=12),
                    showlegend=False,
                )
            )
        else:
            fig.add_trace(
                go.Scattermap(
                    lat=[],
                    lon=[],
                    mode="lines+markers",
                    name=vulture_id,
                    line=dict(color=color_map[vulture_id], width=3),
                    marker=dict(color=color_map[vulture_id], size=8),
                    showlegend=True,
                )
            )
    return fig


def apply_standard_layout(
    fig: go.Figure,
    *,
    center_lat: float,
    center_lon: float,
    zoom_level: int,
) -> None:
    """Apply standard map layout (fixed center/zoom, size, margins, title, legend)."""
    fig.update_layout(
        map=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=zoom_level),
        width=1200,
        height=800,
        autosize=True,
        margin=dict(l=40, r=40, t=100, b=140),
        title=dict(
            text="🦅 Bearded Vulture GPS Flight Paths - Live Map Visualization",
            x=0.5,
            xanchor="center",
        ),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
        ),
    )


def apply_controls_and_slider(
    fig: go.Figure,
    *,
    unique_times: Sequence[str],
    frame_duration_ms: int,
    center_lat: float,
    center_lon: float,
    zoom_level: int,
    include_speed_controls: bool = True,
) -> None:
    """Wire updatemenus (play/pause/restart/fullscreen/recenter) and the timeline slider."""
    fig.update_layout(
        **create_reliable_animation_controls(
            frame_duration=frame_duration_ms,
            include_speed_controls=include_speed_controls,
            center_lat=center_lat,
            center_lon=center_lon,
            zoom_level=zoom_level,
        ),
        sliders=[
            create_enhanced_slider_config(
                list(unique_times),
                position_y=0.02,
                position_x=0.05,
                length=0.9,
                enable_prominent_display=True,
            )
        ],
    )


def attach_frames(
    fig: go.Figure,
    *,
    trail_system,
    df,
    vulture_ids: Sequence[str],
    color_map: Dict[str, str],
    unique_times: Sequence[str],
    enable_prominent_time_display: bool = False,
    strategy: str = "markers_fade",
) -> None:
    """Use the TrailSystem to generate and attach frames to the figure."""
    frames = trail_system.create_frames_with_trail(
        df,
        list(vulture_ids),
        color_map,
        list(unique_times),
        enable_prominent_time_display=enable_prominent_time_display,
        strategy=strategy,
    )
    fig.frames = frames

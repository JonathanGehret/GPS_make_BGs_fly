from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Tuple, List

import plotly.graph_objects as go
import plotly.io as pio


def _collect_latlon_bounds_from_state(states: Iterable[dict]) -> Tuple[float, float, float, float]:
    """Collect overall lat/lon bounds from a sequence of composed trace states (dicts)."""
    lat_min = float("inf")
    lat_max = float("-inf")
    lon_min = float("inf")
    lon_max = float("-inf")
    any_points = False
    for traces in states:
        for t in traces:
            lats = t.get("lat")
            lons = t.get("lon")
            if not lats or not lons:
                continue
            any_points = True
            lat_min = min(lat_min, float(min(lats)))
            lat_max = max(lat_max, float(max(lats)))
            lon_min = min(lon_min, float(min(lons)))
            lon_max = max(lon_max, float(max(lons)))
    if not any_points:
        return 45.0, 48.0, 6.0, 13.0
    return lat_min, lat_max, lon_min, lon_max


def _compose_frame_state(fig: go.Figure, frame: go.Frame | None) -> List[dict]:
    """Compose full trace state for a frame by overlaying frame data on base fig.data.

    This respects frame.traces mapping when present, otherwise applies sequentially.
    Returns a list of plain trace dicts.
    """
    base: List[dict] = [t.to_plotly_json() for t in fig.data]
    if frame is None or not frame.data:
        return base

    # Determine indices to update
    if getattr(frame, "traces", None):
        indices = list(frame.traces)
    else:
        indices = list(range(len(frame.data)))

    for idx, upd in zip(indices, frame.data):
        upd_dict = upd.to_plotly_json()
        # Ensure base is large enough
        while idx >= len(base):
            base.append({})
        base[idx].update(upd_dict)

    return base


def _convert_trace_to_geo_from_dict(t: dict) -> go.Scattergeo | None:
    """Convert a MapLibre-like trace dict to Scattergeo for static export."""
    lat = t.get("lat")
    lon = t.get("lon")
    if lat is None or lon is None:
        return None
    mode = t.get("mode", "lines+markers")
    name = t.get("name")
    marker = t.get("marker")
    line = t.get("line")
    customdata = t.get("customdata")
    hovertemplate = t.get("hovertemplate")
    hoverinfo = t.get("hoverinfo")
    showlegend = t.get("showlegend", True)

    g = go.Scattergeo(
        lat=lat,
        lon=lon,
        mode=mode,
        name=name,
        showlegend=showlegend,
    )
    if marker is not None:
        g.marker = marker
    if line is not None:
        g.line = line
    if customdata is not None:
        g.customdata = customdata
    if hovertemplate is not None:
        g.hovertemplate = hovertemplate
    if hoverinfo is not None:
        g.hoverinfo = hoverinfo
    return g


def _geo_layout_for_bounds(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> dict:
    """Build a geo layout with padded bounds and neutral styling (no web tiles needed)."""
    # Add ~5% padding to each axis
    lat_pad = max(0.01, (lat_max - lat_min) * 0.05)
    lon_pad = max(0.01, (lon_max - lon_min) * 0.05)
    return dict(
        geo=dict(
            projection_type="equirectangular",
            lataxis=dict(range=[lat_min - lat_pad, lat_max + lat_pad], showgrid=True, gridcolor="#eeeeee"),
            lonaxis=dict(range=[lon_min - lon_pad, lon_max + lon_pad], showgrid=True, gridcolor="#eeeeee"),
            showland=True,
            landcolor="#f8f8f8",
            showocean=True,
            oceancolor="#eaf6ff",
            showcountries=True,
            countrycolor="#bbbbbb",
        ),
        margin=dict(l=40, r=40, t=60, b=60),
        showlegend=True,
    )


def export_animation_video(
    fig: go.Figure,
    out_path: str,
    fps: int = 30,
    width: int = 1280,
    height: int = 720,
    quality_crf: int = 20,
) -> str:
    """
    Renders every animation frame to PNG and encodes an MP4 using ffmpeg.
    Requires:
      - pip install -U kaleido
      - ffmpeg available on PATH
    """
    out = Path(out_path).with_suffix(".mp4")
    tmpdir = Path(tempfile.mkdtemp(prefix="frames_"))
    try:
        frames: List[go.Frame] = list(fig.frames or [])

        # Compose full per-frame states (base fig.data + frame overrides)
        composed_states: List[List[dict]] = []
        if not frames:
            composed_states.append(_compose_frame_state(fig, None))
        else:
            for fr in frames:
                composed_states.append(_compose_frame_state(fig, fr))

        # Compute bounds from composed states and prepare a base geo layout
        lat_min, lat_max, lon_min, lon_max = _collect_latlon_bounds_from_state(composed_states)
        base_geo_layout = _geo_layout_for_bounds(lat_min, lat_max, lon_min, lon_max)

        # Render each composed state as a Scattergeo figure
        for i, state in enumerate(composed_states):
            geo_traces = []
            for t in state:
                g = _convert_trace_to_geo_from_dict(t)
                if g is not None:
                    geo_traces.append(g)

            tmp_fig = go.Figure(geo_traces)
            tmp_fig.update_layout(base_geo_layout)
            # keep title if present on original figure
            if fig.layout and getattr(fig.layout, "title", None):
                tmp_fig.update_layout(title=dict(text=fig.layout.title.text, x=0.5, xanchor="center"))

            tmp_fig.update_layout(width=width, height=height)
            pio.write_image(
                tmp_fig,
                tmpdir / f"{i:05d}.png",
                format="png",
                width=width,
                height=height,
                scale=1,
            )

        cmd = [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(tmpdir / "%05d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            str(quality_crf),
            str(out),
        ]
        subprocess.run(cmd, check=True)
        return str(out)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

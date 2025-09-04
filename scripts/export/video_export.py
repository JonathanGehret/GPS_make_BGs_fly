from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Tuple

import plotly.graph_objects as go
import plotly.io as pio


def _collect_latlon_bounds(frames: Iterable[go.Frame]) -> Tuple[float, float, float, float]:
    """Collect overall lat/lon bounds from all frames' traces.

    Returns (lat_min, lat_max, lon_min, lon_max). If no data, returns a sane default box.
    """
    lat_min = float("inf")
    lat_max = float("-inf")
    lon_min = float("inf")
    lon_max = float("-inf")
    any_points = False
    for fr in frames or []:
        for tr in fr.data or []:
            # Traces may be Scattermap (MapLibre) or already Scattergeo; both expose lat/lon sequences
            lats = getattr(tr, "lat", None)
            lons = getattr(tr, "lon", None)
            if lats is None or lons is None:
                continue
            if len(lats) == 0:
                continue
            any_points = True
            try:
                lat_min = min(lat_min, min(lats))
                lat_max = max(lat_max, max(lats))
                lon_min = min(lon_min, min(lons))
                lon_max = max(lon_max, max(lons))
            except TypeError:
                # Some Plotly arrays could be numpy arrays; min/max will still work, but be safe
                lat_min = min(lat_min, float(min(list(lats))))
                lat_max = max(lat_max, float(max(list(lats))))
                lon_min = min(lon_min, float(min(list(lons))))
                lon_max = max(lon_max, float(max(list(lons))))

    if not any_points:
        # Default to Alps-ish box to avoid errors
        return 45.0, 48.0, 6.0, 13.0
    return lat_min, lat_max, lon_min, lon_max


def _convert_trace_to_geo(tr: go.BaseTraceType) -> go.Scattergeo:
    """Convert a MapLibre Scattermap-like trace to a tile-free Scattergeo trace for static export."""
    # Preserve core styling and metadata
    mode = getattr(tr, "mode", "lines+markers")
    name = getattr(tr, "name", None)
    marker = getattr(tr, "marker", None)
    line = getattr(tr, "line", None)
    customdata = getattr(tr, "customdata", None)
    hovertemplate = getattr(tr, "hovertemplate", None)
    showlegend = getattr(tr, "showlegend", True)
    hoverinfo = getattr(tr, "hoverinfo", None)

    return go.Scattergeo(
        lat=getattr(tr, "lat", []),
        lon=getattr(tr, "lon", []),
        mode=mode,
        name=name,
        marker=marker,
        line=line,
        customdata=customdata,
        hovertemplate=hovertemplate,
        hoverinfo=hoverinfo,
        showlegend=showlegend,
    )


def _geo_layout_for_bounds(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> dict:
    """Build a geo layout with padded bounds and neutral styling (no web tiles needed)."""
    # Add ~5% padding to each axis
    lat_pad = max(0.01, (lat_max - lat_min) * 0.05)
    lon_pad = max(0.01, (lon_max - lon_min) * 0.05)
    return dict(
        geo=dict(
            projection_type="equirectangular",
            showland=True,
            landcolor="rgb(240,240,240)",
            showcountries=True,
            countrycolor="rgb(200,200,200)",
            showsubunits=True,
            subunitcolor="rgb(220,220,220)",
            lakecolor="rgb(230,230,255)",
            showlakes=True,
            lonaxis=dict(range=[lon_min - lon_pad, lon_max + lon_pad]),
            lataxis=dict(range=[lat_min - lat_pad, lat_max + lat_pad]),
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        showlegend=True,
    )


def export_animation_video(
    fig: go.Figure,
    out_path: str,
    fps: int = 30,
    width: int = 1280,
    height: int = 720,
    quality: int = 20,
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
        frames = fig.frames or []

        # Build a tile-free "geo" layout and convert traces for static export, to avoid MapLibre/tiles.
        lat_min, lat_max, lon_min, lon_max = _collect_latlon_bounds(frames)
        base_geo_layout = _geo_layout_for_bounds(lat_min, lat_max, lon_min, lon_max)

        if not frames:
            # Render a single empty frame with legend only
            tmp_fig = go.Figure()
            tmp_fig.update_layout(base_geo_layout)
            tmp_fig.update_layout(width=width, height=height)
            pio.write_image(tmp_fig, tmpdir / "00000.png", format="png", width=width, height=height, scale=1)
        else:
            for i, fr in enumerate(frames):
                # Convert each frame's traces to Scattergeo
                geo_traces = []
                for tr in fr.data or []:
                    try:
                        geo_traces.append(_convert_trace_to_geo(tr))
                    except Exception:
                        # Best-effort: skip unsupported trace types
                        continue

                tmp_fig = go.Figure(data=geo_traces)
                # Merge any per-frame layout (like annotations) while keeping the geo base
                tmp_fig.update_layout(base_geo_layout)
                if fr.layout:
                    tmp_fig.update_layout(fr.layout)

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
            str(quality),
            str(out),
        ]
        subprocess.run(cmd, check=True)
        return str(out)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

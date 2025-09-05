from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd
import plotly.graph_objects as go

from .precip_providers import BBox, _times_to_hours_utc, select_precip_provider


def build_precip_dataset(unique_times: List[datetime], bbox: BBox, provider_name: str, cache_dir=None):
    hours = _times_to_hours_utc(unique_times)
    provider = select_precip_provider(provider_name, bbox, cache_dir=cache_dir)
    data_by_hour = provider.fetch(hours, bbox)
    return data_by_hour, hours


def add_precip_trace(fig: go.Figure, zmax: float = 10.0) -> int:
    # Represent precipitation as sized/colored scatter points for compatibility
    trace = go.Scattermap(
        lat=[], lon=[], mode="markers",
        marker=dict(size=10, color=[], colorscale="Blues", cmin=0, cmax=zmax, opacity=0.6, colorbar=dict(title="mm/h")),
        visible=False,
        hovertemplate="Precip: %{marker.color:.2f} mm/h<extra></extra>",
        name="Precipitation",
        showlegend=True,
    )
    fig.add_trace(trace)
    return len(fig.data) - 1


def _to_hour_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def update_precip_for_hour(fig: go.Figure, trace_index: int, hour: datetime, data_by_hour: Dict[datetime, pd.DataFrame]):
    df = data_by_hour.get(_to_hour_utc(hour))
    if df is None or len(df) == 0:
        lat = []
        lon = []
        z = []
    else:
        lat = df["lat"].to_list()
        lon = df["lon"].to_list()
        z = df["precip_mm"].to_list()
    fig.data[trace_index].lat = lat
    fig.data[trace_index].lon = lon
    # Scatter uses marker.color instead of z
    fig.data[trace_index].marker.color = z


def apply_precip_to_frames(fig: go.Figure, trace_index: int, unique_times: List[datetime], data_by_hour: Dict[datetime, pd.DataFrame]):
    for fr in fig.frames:
        try:
            ftime = pd.to_datetime(fr.name, utc=True).to_pydatetime()
        except Exception:
            continue
        hour = _to_hour_utc(ftime)
        df = data_by_hour.get(hour)
        if df is None or len(df) == 0:
            lat = []
            lon = []
            z = []
        else:
            lat = df["lat"].to_list()
            lon = df["lon"].to_list()
            z = df["precip_mm"].to_list()

        # Append/update a frame entry for our precip trace index
        if getattr(fr, "traces", None):
            fr.data += (go.Scattermap(lat=lat, lon=lon, mode="markers", marker=dict(size=10, color=z, colorscale="Blues", cmin=0, cmax=10.0, opacity=0.6), visible=None, hoverinfo="skip"),)
            fr.traces += (trace_index,)
        else:
            needed = trace_index - len(fr.data) + 1
            if needed > 0:
                fr.data += tuple(go.Scattermap() for _ in range(needed))
            tmp = list(fr.data)
            tmp[trace_index] = go.Scattermap(lat=lat, lon=lon, mode="markers", marker=dict(size=10, color=z, colorscale="Blues", cmin=0, cmax=10.0, opacity=0.6), visible=None, hoverinfo="skip")
            fr.data = tuple(tmp)

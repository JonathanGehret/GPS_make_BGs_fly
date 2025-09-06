"""Native Plotly precipitation heatmap integration (no JS overlay).

This module fetches hourly precipitation over a coarse lat/lon grid
and adds a Plotly Heatmap trace plus frame updates so precipitation
animates in lock‑step with existing vulture flight frames.

Environment variables (optional):
  PRECIP_GRID_STEP   - grid step in degrees (default 0.25, clamp 0.05..1.0)
  PRECIP_ZMAX        - max precipitation (mm/h) for color scaling (default 8)
  PRECIP_OPACITY     - heatmap opacity (default 0.55)
  PRECIP_PROVIDER    - currently only 'open-meteo'
  PRECIP_MODE        - if set to 'heatmap' use this native approach

Caching: responses stored under .cache/precip_grid/. Safe to delete.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np  # already project dependency
import requests     # already project dependency


CACHE_DIR = ".cache/precip_grid"
os.makedirs(CACHE_DIR, exist_ok=True)


@dataclass
class PrecipHeatmapConfig:
    enable: bool = True
    grid_step_deg: float = 0.25
    zmax: float = 8.0
    opacity: float = 0.55
    provider: str = "open-meteo"
    timeout: float = 15.0


def _hash_key(parts: Sequence[str]) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def _hour_range(start: datetime, end: datetime) -> List[datetime]:
    start_utc = start.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    end_utc = end.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    out: List[datetime] = []
    cur = start_utc
    while cur <= end_utc:
        out.append(cur)
        cur += timedelta(hours=1)
    return out


def _cache_path(name: str) -> str:
    return os.path.join(CACHE_DIR, f"{name}.json")


def _fetch_point_open_meteo(lat: float, lon: float, start: datetime, end: datetime, timeout: float) -> Dict[str, float]:
    """Return mapping iso_hour -> precip_mm for one grid point."""
    start_date = start.date().isoformat()
    end_date = end.date().isoformat()
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat:.4f}&longitude={lon:.4f}"
        f"&start_date={start_date}&end_date={end_date}"
        "&hourly=precipitation&timezone=UTC"
    )
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    js = r.json()
    times = js.get("hourly", {}).get("time", [])
    vals = js.get("hourly", {}).get("precipitation", [])
    out: Dict[str, float] = {}
    for t, v in zip(times, vals):
        # Normalize to YYYY-MM-DDTHH:00:00Z
        if len(t) == 13:  # YYYY-MM-DDTHH
            t = t + ":00:00Z"
        elif len(t) == 16:  # YYYY-MM-DDTHH:MM
            t = t + ":00Z"
        elif t.endswith(":00") and not t.endswith(":00Z"):
            t = t + "Z"
        out[t] = float(v) if v is not None else 0.0
    return out


def fetch_precip_grid(
    bbox: Tuple[float, float, float, float],
    start: datetime,
    end: datetime,
    cfg: PrecipHeatmapConfig,
) -> Optional[Dict]:
    """Fetch / cache precipitation grid for hours in [start,end].

    Returns JSON‑serializable payload or None if disabled/failed.
    """
    if not cfg.enable:
        return None

    lat_min, lat_max, lon_min, lon_max = bbox
    if lat_min > lat_max:
        lat_min, lat_max = lat_max, lat_min
    if lon_min > lon_max:
        lon_min, lon_max = lon_max, lon_min

    step = max(0.05, min(1.0, float(cfg.grid_step_deg)))
    lats = np.arange(lat_min, lat_max + 1e-9, step)
    lons = np.arange(lon_min, lon_max + 1e-9, step)
    hours = _hour_range(start, end)
    hour_keys = [h.strftime("%Y-%m-%dT%H:00:00Z") for h in hours]

    cache_key = _hash_key([
        f"{lat_min:.3f}", f"{lat_max:.3f}", f"{lon_min:.3f}", f"{lon_max:.3f}",
        f"{step:.3f}", hour_keys[0], hour_keys[-1], str(len(lats)), str(len(lons)), f"z{cfg.zmax}", cfg.provider
    ])
    cache_file = _cache_path(cache_key)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            if payload.get("version") == 1:
                return payload
        except Exception:
            pass

    grids = {hk: np.zeros((len(lats), len(lons)), dtype=float) for hk in hour_keys}
    start_time = time.time()

    total_calls = len(lats) * len(lons)
    call_n = 0
    for i, la in enumerate(lats):
        for j, lo in enumerate(lons):
            call_n += 1
            try:
                mapping = _fetch_point_open_meteo(la, lo, hours[0], hours[-1], cfg.timeout)
            except Exception:
                mapping = {}
            for hk in hour_keys:
                grids[hk][i, j] = float(mapping.get(hk, 0.0))
            # Gentle rate limiting
            time.sleep(0.04)

    duration = round(time.time() - start_time, 2)
    serial_grids = {hk: grids[hk].tolist() for hk in hour_keys}
    payload = {
        "version": 1,
        "provider": cfg.provider,
        "lat": lats.tolist(),
        "lon": lons.tolist(),
        "hours": hour_keys,
        "grids": serial_grids,
        "zmax": float(cfg.zmax),
        "opacity": float(cfg.opacity),
        "meta": {
            "grid_step_deg": step,
            "calls": total_calls,
            "seconds": duration,
        },
    }
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f)
    except Exception:
        pass
    return payload


def build_precip_heatmap_traces(fig, precip_payload: Dict, zmax: float, opacity: float, frame_time_parser) -> int:
    """Insert heatmap trace + update frames.

    frame_time_parser: callable(frame_name:str)->datetime | None
    Returns index of the added trace.
    """
    import plotly.graph_objects as go

    if not precip_payload:
        return -1

    lat = precip_payload["lat"]
    lon = precip_payload["lon"]
    hours = precip_payload["hours"]
    grids = precip_payload["grids"]
    hour_to_z = {hk: np.array(grids[hk]) for hk in hours}
    first_hour = hours[0]

    heatmap = go.Heatmap(
        z=hour_to_z[first_hour],
        x=lon,
        y=lat,
        zmin=0,
        zmax=zmax,
        opacity=opacity,
        coloraxis=None,
        colorscale=[
            [0.0, "rgba(0,0,0,0)"],
            [0.05, "#d6f2ff"],
            [0.15, "#a4ddff"],
            [0.30, "#68c2ff"],
            [0.50, "#2495ff"],
            [0.70, "#0a55d0"],
            [0.85, "#6120a0"],
            [1.0, "#ff00ff"],
        ],
        name="Precipitation",
        showscale=True,
        hovertemplate="Precip: %{z:.2f} mm/h<extra></extra>",
        visible=True,
    )
    fig.add_trace(heatmap)
    idx = len(fig.data) - 1

    def hour_key(dt_obj: datetime) -> str:
        return dt_obj.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:00:00Z")

    for fr in fig.frames:
        dt_obj = frame_time_parser(fr.name) if frame_time_parser else None
        hk = hour_key(dt_obj) if dt_obj else first_hour
        z = hour_to_z.get(hk, hour_to_z[first_hour])
        # Ensure frame.data length covers new trace index
        if len(fr.data) < len(fig.data):
            fr.data = fr.data + tuple([{}] * (len(fig.data) - len(fr.data)))
        fr_list = list(fr.data)
        fr_list[idx] = {"z": z}
        fr.data = tuple(fr_list)

    # Add ON/OFF buttons (append to first updatemenu or create new)
    btn_on = dict(label="Precip ON", method="update", args=[{"visible": [True if i == idx else (d.visible if hasattr(d, 'visible') else True) for i, d in enumerate(fig.data)]}])
    btn_off = dict(label="Precip OFF", method="update", args=[{"visible": [False if i == idx else True for i in range(len(fig.data))]}])
    if fig.layout.updatemenus:
        fig.layout.updatemenus[0].buttons = tuple(list(fig.layout.updatemenus[0].buttons) + [btn_on, btn_off])
    else:
        fig.update_layout(updatemenus=[dict(type="buttons", direction="right", x=0.0, y=-0.08, buttons=[btn_on, btn_off])])
    return idx


__all__ = [
    "PrecipHeatmapConfig",
    "fetch_precip_grid",
    "build_precip_heatmap_traces",
]

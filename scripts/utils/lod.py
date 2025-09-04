"""
Level-of-Detail (LOD) utilities for interactive performance with large GPS datasets.

Provides temporal downsampling and geometric simplification (RDP) with a hard cap.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class LODConfig:
    max_points_per_track: int = 20_000
    target_points_per_min: int = 600
    rdp_epsilon_meters: float = 5.0
    use_rdp: bool = True


def _rdp_2d(x: np.ndarray, y: np.ndarray, eps_m: float) -> np.ndarray:
    """Simple iterative RDP for 2D lines. Returns boolean mask of kept vertices."""
    n = len(x)
    if n < 3:
        return np.ones(n, dtype=bool)
    keep = np.zeros(n, dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]

    # Rough conversion: 1 deg ~ 111_000 m for small extents (lat)
    scale = 1.0 / 111_000.0
    eps = eps_m * scale

    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        x0, y0, x1, y1 = x[i], y[i], x[j], y[j]
        dx, dy = x1 - x0, y1 - y0
        denom = dx * dx + dy * dy
        max_d = -1.0
        idx = -1
        for k in range(i + 1, j):
            if denom == 0.0:
                d = float(np.hypot(x[k] - x0, y[k] - y0))
            else:
                t = ((x[k] - x0) * dx + (y[k] - y0) * dy) / denom
                t = 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)
                px = x0 + t * dx
                py = y0 + t * dy
                d = float(np.hypot(x[k] - px, y[k] - py))
            if d > max_d:
                max_d, idx = d, k
        if max_d > eps:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return keep


def time_downsample(df: pd.DataFrame, ts_col: str, per_minute: int) -> pd.DataFrame:
    if per_minute <= 0 or len(df) < 2:
        return df
    df = df.sort_values(ts_col)
    seconds = df[ts_col].astype("int64") // 10**9
    total_seconds = int(seconds.iloc[-1] - seconds.iloc[0]) if len(seconds) else 0
    if total_seconds <= 0:
        return df
    target_total = (total_seconds / 60.0) * per_minute
    if target_total <= 0 or target_total >= len(df):
        return df
    stride = max(1, int(np.floor(len(df) / target_total)))
    return df.iloc[::stride].copy()


def apply_lod(
    df: pd.DataFrame,
    ts_col: str,
    lat_col: str,
    lon_col: str,
    cfg: LODConfig,
) -> pd.DataFrame:
    """Apply temporal decimation, geometric simplification, and a hard cap."""
    tmp = time_downsample(df, ts_col, cfg.target_points_per_min)
    if cfg.use_rdp and len(tmp) > 3:
        x = tmp[lon_col].to_numpy()
        y = tmp[lat_col].to_numpy()
        keep = _rdp_2d(x, y, cfg.rdp_epsilon_meters)
        tmp = tmp.loc[keep]
    if len(tmp) > cfg.max_points_per_track:
        step = max(1, len(tmp) // cfg.max_points_per_track)
        tmp = tmp.iloc[::step]
    return tmp.reset_index(drop=True)

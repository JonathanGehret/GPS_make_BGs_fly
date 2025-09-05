"""
Offline tiles support for MapLibre-style Plotly maps.

Features:
- Compute XYZ tiles covering lat/lon bounds for a zoom range
- Download tiles to a local cache directory (z/x/y.png)
- Build a minimal MapLibre style dict referencing local raster tiles

Notes:
- Default tile server is OpenStreetMap (https://tile.openstreetmap.org/{z}/{x}/{y}.png).
  Please respect OSM Tile Usage Policy; limit area/zoom and cache responsibly.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Tuple

import requests


def _latlon_to_tile_xy(lat: float, lon: float, z: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat)
    n = 2 ** z
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def _tile_bounds_for_area(lat_min: float, lat_max: float, lon_min: float, lon_max: float, z: int) -> Tuple[int, int, int, int]:
    x_min, y_max = _latlon_to_tile_xy(lat_min, lon_min, z)
    x_max, y_min = _latlon_to_tile_xy(lat_max, lon_max, z)
    # normalize ordering
    x0, x1 = sorted((x_min, x_max))
    y0, y1 = sorted((y_min, y_max))
    return x0, x1, y0, y1


def download_tiles(
    *,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    minzoom: int,
    maxzoom: int,
    out_dir: str | Path,
    tile_url_template: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    timeout: float = 10.0,
) -> int:
    """Download XYZ raster tiles for the given bounds and zoom range.

    Returns number of tiles written (skips existing files).
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    written = 0
    session = requests.Session()
    headers = {"User-Agent": "GPS_make_BGs_fly/offline-tiles (https://github.com/JonathanGehret)"}
    for z in range(minzoom, maxzoom + 1):
        x0, x1, y0, y1 = _tile_bounds_for_area(lat_min, lat_max, lon_min, lon_max, z)
        # clamp a bit to avoid runaway ranges
        max_span = 256  # safety cap
        if (x1 - x0 + 1) * (y1 - y0 + 1) > max_span * max_span:
            x1 = min(x1, x0 + max_span - 1)
            y1 = min(y1, y0 + max_span - 1)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                url = tile_url_template.format(z=z, x=x, y=y)
                tile_path = out_path / str(z) / str(x) / f"{y}.png"
                if tile_path.exists():
                    continue
                tile_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    r = session.get(url, headers=headers, timeout=timeout)
                    if r.status_code == 200 and r.content:
                        tile_path.write_bytes(r.content)
                        written += 1
                except Exception:
                    # skip failures silently; map will have gaps
                    pass
    return written


def build_local_raster_style(
    *,
    tiles_root: str | Path,
    minzoom: int,
    maxzoom: int,
    tile_size: int = 256,
    tiles_href: str | None = None,
) -> dict:
    """Return a simple MapLibre style dict pointing to local XYZ raster tiles.

    tiles_href: optional href to tiles root suitable for HTML (e.g., './offline_tiles').
    If not provided, falls back to POSIX path of tiles_root.
    """
    root = Path(tiles_root)
    # Prefer an href suitable for the HTML to load (relative path recommended)
    href = tiles_href if tiles_href is not None else root.as_posix()
    tiles_url = href.rstrip("/") + "/{z}/{x}/{y}.png"
    return {
        "version": 8,
        "sources": {
            "offline-raster": {
                "type": "raster",
                "tiles": [tiles_url],
                "tileSize": tile_size,
                "minzoom": minzoom,
                "maxzoom": maxzoom,
            }
        },
        "layers": [
            {
                "id": "offline-raster-layer",
                "type": "raster",
                "source": "offline-raster",
            }
        ],
    }


def ensure_offline_style_for_bounds(
    *,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    zoom_level: int,
    tiles_dir: str | Path,
    download: bool = True,
    zoom_pad: int = 1,
    tile_url_template: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    tiles_href: str | None = None,
) -> dict:
    """Ensure local tiles exist for bounds and return a style dict referencing them.

    Downloads tiles for zoom_level +/- zoom_pad when download=True.
    """
    minz = max(0, zoom_level - zoom_pad)
    maxz = min(19, zoom_level + zoom_pad)
    tiles_root = Path(tiles_dir)
    if download:
        download_tiles(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            minzoom=minz,
            maxzoom=maxz,
            out_dir=tiles_root,
            tile_url_template=tile_url_template,
        )
    return build_local_raster_style(tiles_root=tiles_root, minzoom=minz, maxzoom=maxz, tiles_href=tiles_href)

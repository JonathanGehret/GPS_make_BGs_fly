from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import numpy as np
import requests


@dataclass
class BBox:
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


def _to_hour_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def _times_to_hours_utc(times: Iterable[datetime]) -> List[datetime]:
    return sorted({_to_hour_utc(pd.Timestamp(t).to_pydatetime()) for t in times})


def _bbox_in_germany(b: BBox) -> bool:
    # Coarse check for Germany bbox
    return (47.0 <= b.lat_min <= 55.5 or 47.0 <= b.lat_max <= 55.5) and (5.0 <= b.lon_min <= 16.5 or 5.0 <= b.lon_max <= 16.5)


class PrecipProvider:
    name = "base"

    def fetch(self, hours_utc: List[datetime], bbox: BBox) -> Dict[datetime, pd.DataFrame]:
        raise NotImplementedError


class OpenMeteoGridProvider(PrecipProvider):
    """Query Open-Meteo ERA5 hourly precipitation over a coarse grid covering bbox."""

    name = "open-meteo"

    def __init__(self, grid_size: int = 5, timeout: int = 20, cache_dir: Optional[Path] = None):
        self.grid_size = max(2, min(10, grid_size))
        self.timeout = timeout
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, lat: float, lon: float, start_date: str, end_date: str) -> Path:
        raw = f"{lat:.4f}_{lon:.4f}_{start_date}_{end_date}"
        h = hashlib.sha1(raw.encode()).hexdigest()[:16]
        return self.cache_dir / f"openmeteo_{h}.json" if self.cache_dir else Path("/dev/null")

    def _parse_response(self, lat: float, lon: float, data: dict) -> pd.DataFrame:
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        prcp = hourly.get("precipitation", [])
        if not times or not prcp:
            return pd.DataFrame(columns=["time", "lat", "lon", "precip_mm"])
        df = pd.DataFrame({"time": pd.to_datetime(times, utc=True), "precip_mm": prcp})
        df["lat"] = lat
        df["lon"] = lon
        return df[["time", "lat", "lon", "precip_mm"]]

    def _fetch_point(self, lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
        cache_path = self._cache_key(lat, lon, start_date, end_date)
        if self.cache_dir and cache_path.exists():
            with cache_path.open("r") as f:
                return self._parse_response(lat, lon, json.load(f))

        url = "https://archive-api.open-meteo.com/v1/era5"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "precipitation",
            "timezone": "UTC",
        }
        r = requests.get(url, params=params, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        if self.cache_dir:
            with cache_path.open("w") as f:
                json.dump(data, f)
        return self._parse_response(lat, lon, data)

    def fetch(self, hours_utc: List[datetime], bbox: BBox) -> Dict[datetime, pd.DataFrame]:
        if not hours_utc:
            return {}
        start = hours_utc[0].strftime("%Y-%m-%d")
        end = hours_utc[-1].strftime("%Y-%m-%d")
        lats = list(np.linspace(bbox.lat_min, bbox.lat_max, self.grid_size))
        lons = list(np.linspace(bbox.lon_min, bbox.lon_max, self.grid_size))
        frames: List[pd.DataFrame] = []
        for la in lats:
            for lo in lons:
                try:
                    frames.append(self._fetch_point(la, lo, start, end))
                except Exception:
                    pass
        if not frames:
            return {}
        big = pd.concat(frames, ignore_index=True)
        big["hour"] = big["time"].dt.floor("h")
        result: Dict[datetime, pd.DataFrame] = {}
        for h in hours_utc:
            dfh = big[big["hour"] == pd.Timestamp(h)]
            result[h] = dfh[["lat", "lon", "precip_mm"]].reset_index(drop=True)
        return result


class DWDStationsProvider(PrecipProvider):
    """Use wetterdienst DWD hourly station precipitation (Germany-only)."""

    name = "dwd-stations"

    def __init__(self, fallback: Optional[PrecipProvider] = None):
        self._fallback = fallback or OpenMeteoGridProvider(grid_size=5)
        try:
            from wetterdienst.provider.dwd.observation import (
                DwdObservationRequest, DwdObservationResolution,
                DwdObservationParameter as Param,
            )
            from wetterdienst import Settings
            self._WD_OK = True
            self.DwdObservationRequest = DwdObservationRequest
            self.DwdObservationResolution = DwdObservationResolution
            self.Param = Param
            self.Settings = Settings
        except Exception:
            self._WD_OK = False

    def fetch(self, hours_utc: List[datetime], bbox: BBox) -> Dict[datetime, pd.DataFrame]:
        if not hours_utc:
            return {}
        if not self._WD_OK or not _bbox_in_germany(bbox):
            return self._fallback.fetch(hours_utc, bbox)
        start = hours_utc[0]
        end = hours_utc[-1]
        settings = self.Settings(ts_shape="long")
        req = self.DwdObservationRequest(
            parameter=[self.Param.HOURLY.PRECIPITATION_HEIGHT],
            resolution=self.DwdObservationResolution.HOURLY,
            start_date=start,
            end_date=end,
            settings=settings,
        )
        stations = req.filter_by_sql(
            f"latitude BETWEEN {bbox.lat_min} AND {bbox.lat_max} AND longitude BETWEEN {bbox.lon_min} AND {bbox.lon_max}"
        )
        df = stations.values.all().df
        if df is None or len(df) == 0:
            return self._fallback.fetch(hours_utc, bbox)
        df = df.rename(columns={"date": "time", "value": "precip_mm"})
        df["time"] = pd.to_datetime(df["time"], utc=True)
        df["hour"] = df["time"].dt.floor("h")
        out: Dict[datetime, pd.DataFrame] = {}
        for h in hours_utc:
            sel = df[df["hour"] == pd.Timestamp(h)]
            if len(sel) == 0:
                out[h] = pd.DataFrame(columns=["lat", "lon", "precip_mm"])
            else:
                out[h] = sel[["latitude", "longitude", "precip_mm"]].rename(columns={"latitude": "lat", "longitude": "lon"}).reset_index(drop=True)
        return out


def select_precip_provider(preferred: str, bbox: BBox, cache_dir: Optional[Path] = None) -> PrecipProvider:
    preferred = (preferred or "").lower()
    if preferred in ("dwd", "wetterdienst", "dwd-stations"):
        return DWDStationsProvider()
    return OpenMeteoGridProvider(grid_size=5, cache_dir=cache_dir)

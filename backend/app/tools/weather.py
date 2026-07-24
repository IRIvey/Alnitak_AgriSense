"""Live weather tool (Tier-0 #2) — Open-Meteo (free, keyless).

This is the one external service that MUST return real values. Two calls:
  1. Geocode the location name -> lat/lon.
  2. Fetch forecast (daily rainfall + temperature) for those coords.

The returned dict is what the agent uses (and what shows in the trace), so keep
it compact and honest — raw values only, no invented numbers.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


async def _geocode(location: str) -> tuple[float, float, str]:
    """Resolve a place name to (lat, lon, resolved_name)."""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            settings.open_meteo_geocode_url,
            params={"name": location, "count": 1, "language": "en"},
        )
        r.raise_for_status()
        data = r.json()
    results = data.get("results") or []
    if not results:
        raise ValueError(f"Could not geocode location: {location!r}")
    top = results[0]
    name = ", ".join(
        p for p in [top.get("name"), top.get("admin1"), top.get("country")] if p
    )
    return float(top["latitude"]), float(top["longitude"]), name


async def get_weather(
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
    days: int = 7,
) -> dict[str, Any]:
    """Return real current + N-day forecast for a location.

    Shape:
        {
          "location": "Rangpur, Bangladesh",
          "latitude": ..., "longitude": ...,
          "daily": [{"date","t_max","t_min","rain_mm","precip_prob"}...],
          "summary": {"total_rain_mm","avg_t_max","rain_days","source": "open-meteo"}
        }
    """
    if latitude is None or longitude is None:
        latitude, longitude, location = await _geocode(location)

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(
            settings.open_meteo_forecast_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "daily": ",".join(
                    [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "precipitation_probability_max",
                    ]
                ),
                "forecast_days": min(max(days, 1), 16),
                "timezone": "auto",
            },
        )
        r.raise_for_status()
        d = r.json().get("daily", {})

    dates = d.get("time", [])
    daily = [
        {
            "date": dates[i],
            "t_max": d.get("temperature_2m_max", [None] * len(dates))[i],
            "t_min": d.get("temperature_2m_min", [None] * len(dates))[i],
            "rain_mm": d.get("precipitation_sum", [None] * len(dates))[i],
            "precip_prob": d.get("precipitation_probability_max", [None] * len(dates))[i],
        }
        for i in range(len(dates))
    ]
    rain_vals = [x["rain_mm"] for x in daily if x["rain_mm"] is not None]
    tmax_vals = [x["t_max"] for x in daily if x["t_max"] is not None]
    summary = {
        "total_rain_mm": round(sum(rain_vals), 1),
        "avg_t_max": round(sum(tmax_vals) / len(tmax_vals), 1) if tmax_vals else None,
        "rain_days": sum(1 for v in rain_vals if v and v > 1.0),
        "source": "open-meteo",
    }
    return {
        "location": location,
        "latitude": latitude,
        "longitude": longitude,
        "daily": daily,
        "summary": summary,
    }

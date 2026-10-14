"""Weather Provider for SlopeSentinel.

Fetches real-time and forecast precipitation data for Gangtok from Open-Meteo API.
Provides robust in-memory TTL caching, timeout handling, and deterministic fallback
guarantees so that an API failure or offline demo environment never crashes the system.

DATA INTEGRITY INVARIANT:
- Fallback responses are explicitly flagged with source_status='fallback' and is_fallback=True.
- Cached responses are explicitly flagged with source_status='cached'.
- Live responses are explicitly flagged with source_status='live'.
- Under NO circumstance is fallback data presented as live meteorological observation.
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import httpx

from ..config import settings
from ..models.schemas import WeatherData

logger = logging.getLogger("slopesentinel.weather")

# WMO Weather interpretation codes (WMO code -> text)
WMO_CODE_MAP: Dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail",
}


class WeatherCacheEntry:
    def __init__(self, data: WeatherData, expires_at: float):
        self.data = data
        self.expires_at = expires_at

    def is_valid(self) -> bool:
        return time.time() < self.expires_at


class WeatherProvider:
    """Manages weather data acquisition with caching, resilience, and strict provenance."""

    def __init__(self):
        self._cache: Optional[WeatherCacheEntry] = None

    def _get_fallback_weather(self, reason: str) -> WeatherData:
        """Returns deterministic, clearly-labelled offline fallback data."""
        now_iso = datetime.now(timezone.utc).isoformat()
        return WeatherData(
            source="Open-Meteo Fallback (Offline/Cached Baseline)",
            source_status="fallback",
            timestamp=now_iso,
            temperature_c=18.5,
            relative_humidity_pct=76.0,
            apparent_temperature_c=18.0,
            current_precipitation_mm=0.0,
            forecast_24h_precip_mm=4.2,
            wind_speed_kmh=8.5,
            weather_code=3,
            condition_text="Overcast (Simulated Fallback Context)",
            is_fallback=True,
            notes=f"Live weather lookup unavailable ({reason}). Active fallback model engaged.",
        )

    async def get_weather(self, force_refresh: bool = False) -> WeatherData:
        """Fetches weather data for Gangtok with caching and fallback protection."""
        now = time.time()

        # Check in-memory cache if not forcing refresh
        if not force_refresh and self._cache and self._cache.is_valid():
            cached = self._cache.data.model_copy()
            # If the original was live, mark it as cached to be strictly truthful
            if cached.source_status == "live":
                cached.source_status = "cached"
            return cached

        # Attempt live API call to Open-Meteo
        params = {
            "latitude": settings.site.latitude,
            "longitude": settings.site.longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m",
            "daily": "precipitation_sum",
            "timezone": "auto",
            "forecast_days": 2,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.weather.request_timeout_seconds) as client:
                response = await client.get(settings.weather.open_meteo_url, params=params)
                response.raise_for_status()
                payload = response.json()

            current = payload.get("current", {})
            daily = payload.get("daily", {})
            
            # Forecast 24h precipitation: take today's or next 24h sum
            precip_sum_list = daily.get("precipitation_sum", [0.0])
            forecast_24h = float(precip_sum_list[0]) if precip_sum_list else 0.0

            wmo_code = int(current.get("weather_code", 0))
            condition_desc = WMO_CODE_MAP.get(wmo_code, "Variable Weather")

            live_weather = WeatherData(
                source="Open-Meteo API",
                source_status="live",
                timestamp=current.get("time", datetime.now(timezone.utc).isoformat()),
                temperature_c=float(current.get("temperature_2m", 18.0)),
                relative_humidity_pct=float(current.get("relative_humidity_2m", 70.0)),
                apparent_temperature_c=float(current.get("apparent_temperature", 18.0)),
                current_precipitation_mm=float(current.get("precipitation", 0.0)),
                forecast_24h_precip_mm=forecast_24h,
                wind_speed_kmh=float(current.get("wind_speed_10m", 5.0)),
                weather_code=wmo_code,
                condition_text=condition_desc,
                is_fallback=False,
                notes="Live meteorological observation retrieved from Open-Meteo API.",
            )

            # Store in cache
            self._cache = WeatherCacheEntry(
                data=live_weather,
                expires_at=now + settings.weather.cache_ttl_seconds,
            )

            return live_weather

        except httpx.TimeoutException:
            logger.warning("Open-Meteo API timed out. Falling back to deterministic demo weather.")
            return self._get_fallback_weather("Network request timed out")
        except httpx.HTTPStatusError as e:
            logger.warning("Open-Meteo API HTTP error %s. Falling back.", e.response.status_code)
            return self._get_fallback_weather(f"HTTP {e.response.status_code}")
        except Exception as e:
            logger.warning("Open-Meteo API retrieval error: %s. Falling back.", str(e))
            return self._get_fallback_weather(f"Exception: {type(e).__name__}")


# Singleton instance
weather_provider = WeatherProvider()

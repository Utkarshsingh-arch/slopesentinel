"""Tests for WeatherProvider resilience, caching, and fallback behaviour."""

import pytest
import httpx
from backend.services.weather import WeatherProvider
from backend.models.schemas import WeatherData


@pytest.mark.asyncio
async def test_weather_fallback_properties():
    provider = WeatherProvider()
    fallback = provider._get_fallback_weather("Test reason")
    
    assert fallback.is_fallback is True
    assert fallback.source_status == "fallback"
    assert "Fallback" in fallback.source
    assert fallback.forecast_24h_precip_mm >= 0.0
    assert fallback.notes is not None


@pytest.mark.asyncio
async def test_weather_network_error_handles_gracefully(monkeypatch):
    provider = WeatherProvider()

    # Mock httpx.AsyncClient to raise a TimeoutException
    async def mock_get(*args, **kwargs):
        raise httpx.TimeoutException("Simulated network timeout")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    # Calling get_weather must NOT raise an unhandled exception
    weather = await provider.get_weather(force_refresh=True)

    assert weather is not None
    assert weather.is_fallback is True
    assert weather.source_status == "fallback"
    assert "timed out" in weather.notes.lower()


@pytest.mark.asyncio
async def test_weather_caching():
    provider = WeatherProvider()

    # Pre-populate cache with a mock live object
    mock_live = WeatherData(
        source="Open-Meteo API",
        source_status="live",
        timestamp="2026-10-15T00:00:00Z",
        temperature_c=19.2,
        relative_humidity_pct=68.0,
        apparent_temperature_c=19.0,
        current_precipitation_mm=0.0,
        forecast_24h_precip_mm=2.5,
        wind_speed_kmh=6.0,
        weather_code=1,
        condition_text="Mainly Clear",
        is_fallback=False,
    )
    from backend.services.weather import WeatherCacheEntry
    import time
    provider._cache = WeatherCacheEntry(data=mock_live, expires_at=time.time() + 300)

    # Fetch without refresh -> should return cached with source_status='cached'
    cached_res = await provider.get_weather(force_refresh=False)
    assert cached_res.source_status == "cached"
    assert cached_res.temperature_c == 19.2

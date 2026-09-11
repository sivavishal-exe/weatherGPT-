import pytest
import time
import asyncio
from app.services.weather.adapters.mock_provider import MockWeatherProviderAdapter
from app.services.weather.orchestrator import WeatherServiceOrchestrator
from app.core.redis_cache import cache


@pytest.mark.asyncio
async def test_mock_provider_successful_response():
    adapter = MockWeatherProviderAdapter(custom_temp=24.0)
    res = await adapter.get_current_weather(35.6762, 139.6503, "Tokyo")
    
    assert res.location.name == "Tokyo"
    assert res.weather_parameters.temperature == 24.0
    assert res.data_source == "Mock Weather Test Service"
    assert res.is_stale is False
    assert res.stale_age_seconds == 0.0


@pytest.mark.asyncio
async def test_mock_provider_timeout():
    adapter = MockWeatherProviderAdapter(should_timeout=True)
    with pytest.raises((TimeoutError, asyncio.TimeoutError)):
        await adapter.get_current_weather(35.6762, 139.6503)


@pytest.mark.asyncio
async def test_mock_provider_invalid_response_failure():
    adapter = MockWeatherProviderAdapter(should_fail=True)
    with pytest.raises(RuntimeError):
        await adapter.get_current_weather(35.6762, 139.6503)


@pytest.mark.asyncio
async def test_mock_provider_missing_fields_no_fabrication():
    adapter = MockWeatherProviderAdapter(missing_fields=True)
    res = await adapter.get_current_weather(35.6762, 139.6503)
    
    # Requirement: Never fabricate missing weather values
    assert res.weather_parameters.temperature is None
    assert res.weather_parameters.humidity is None
    assert res.weather_parameters.condition_text == "Unknown Data"


@pytest.mark.asyncio
async def test_orchestrator_provider_failover():
    # Primary provider fails, Secondary succeeds
    primary_failing = MockWeatherProviderAdapter(should_fail=True)
    secondary_working = MockWeatherProviderAdapter(custom_temp=18.0)
    
    orchestrator = WeatherServiceOrchestrator(providers=[primary_failing, secondary_working])
    res = await orchestrator.get_current_weather(40.7128, -74.0060, "New York", max_retries=1)
    
    assert res.location.name == "New York"
    assert res.weather_parameters.temperature == 18.0
    assert res.is_stale is False


@pytest.mark.asyncio
async def test_orchestrator_stale_cache_detection():
    # Setup pre-populated cache entry
    lat, lon = 51.5074, -0.1278
    cache_key = f"norm_weather:{round(lat, 2)}:{round(lon, 2)}"
    
    past_timestamp = time.time() - 120.0  # 120 seconds ago
    cache_payload = {
        "location": {"name": "London", "latitude": lat, "longitude": lon},
        "observation_time": "2026-09-10T12:00:00Z",
        "last_updated_time": "2026-09-10T12:00:00Z",
        "fetched_at_timestamp": past_timestamp,
        "weather_parameters": {
            "temperature": 19.0,
            "apparent_temperature": 19.0,
            "humidity": 65.0,
            "pressure": 1015.0,
            "wind_speed": 10.0,
            "wind_direction": 90,
            "condition_text": "Cloudy"
        },
        "data_source": "Open-Meteo Meteorological Service",
        "is_stale": False,
        "stale_age_seconds": 0.0
    }
    await cache.set_json(cache_key, cache_payload, ttl=600)
    
    # All live providers fail
    failing_provider = MockWeatherProviderAdapter(should_fail=True)
    orchestrator = WeatherServiceOrchestrator(providers=[failing_provider])
    
    res = await orchestrator.get_current_weather(lat, lon, "London", max_retries=1)
    
    # Requirement: Never silently present old data as real-time information
    assert res.is_stale is True
    assert res.stale_age_seconds >= 100.0
    assert "STALE CACHE" in res.data_source
    assert res.stale_warning is not None
    assert "Real-time provider unavailable" in res.stale_warning


@pytest.mark.asyncio
async def test_orchestrator_get_temperature_and_wind():
    working = MockWeatherProviderAdapter(custom_temp=21.0)
    orchestrator = WeatherServiceOrchestrator(providers=[working])
    
    t_res = await orchestrator.get_temperature(35.6762, 139.6503)
    w_res = await orchestrator.get_wind(35.6762, 139.6503)
    r_res = await orchestrator.get_rainfall(35.6762, 139.6503)
    
    assert t_res["temperature_celsius"] == 21.0
    assert w_res["wind_speed_kmh"] == 15.0
    assert r_res["rainfall_mm"] == 0.0

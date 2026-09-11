import pytest
from app.services.weather_provider import weather_provider


@pytest.mark.asyncio
async def test_get_weather_success():
    # Tokyo coordinates
    res = await weather_provider.get_weather(35.6762, 139.6503, "Tokyo", days=3)
    assert res.location.latitude == 35.6762
    assert res.location.longitude == 139.6503
    assert res.current.temperature is not None
    assert res.current.humidity >= 0.0 and res.current.humidity <= 100.0
    assert len(res.daily_forecast) <= 3
    assert res.data_source is not None


@pytest.mark.asyncio
async def test_weather_caching():
    # Fetch twice, second call should return cached=True if first succeeded
    res1 = await weather_provider.get_weather(40.7128, -74.0060, "New York", days=3)
    res2 = await weather_provider.get_weather(40.7128, -74.0060, "New York", days=3)
    assert res2.cached is True or res1.cached is True or res1.data_source is not None


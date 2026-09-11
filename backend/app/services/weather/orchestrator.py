import time
import asyncio
import httpx
from typing import Optional, List, Dict, Any

from app.config import settings
from app.core.logging import logger
from app.core.redis_cache import cache
from app.services.weather.base import BaseWeatherProvider, NormalizedWeatherResponse
from app.services.weather.adapters.open_meteo import OpenMeteoProviderAdapter
from app.services.weather.adapters.mock_provider import MockWeatherProviderAdapter


class WeatherServiceOrchestrator:
    """
    Provider-Independent Weather Data Orchestrator.
    Manages multi-provider failover, retry logic, TTL caching, and explicit stale data tracking.
    """

    def __init__(self, providers: Optional[List[BaseWeatherProvider]] = None):
        self.providers: List[BaseWeatherProvider] = providers or [
            OpenMeteoProviderAdapter(),
            MockWeatherProviderAdapter()
        ]

    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        max_retries: int = 2
    ) -> NormalizedWeatherResponse:
        
        cache_key = f"norm_weather:{round(latitude, 2)}:{round(longitude, 2)}"
        
        # 1. Try Providers in sequence
        for provider in self.providers:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.info(f"Fetching weather from '{provider.provider_name}' (Attempt {attempt}/{max_retries})")
                    result = await provider.get_current_weather(latitude, longitude, location_name)
                    
                    # Store in cache with fetch timestamp
                    cache_payload = result.model_dump()
                    cache_payload["fetched_at_timestamp"] = time.time()
                    await cache.set_json(cache_key, cache_payload, ttl=settings.CACHE_TTL_SECONDS)
                    return result
                
                except (httpx.HTTPError, TimeoutError, asyncio.TimeoutError, RuntimeError, ValueError) as e:
                    logger.warning(f"Provider '{provider.provider_name}' attempt {attempt} failed: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(0.2 * attempt)
        
        # 2. If ALL live providers fail, check cache for stale fallback
        logger.warning(f"All weather providers failed for ({latitude}, {longitude}). Checking stale cache.")
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            fetched_at = cached_data.get("fetched_at_timestamp", time.time() - 300)
            stale_age = round(time.time() - fetched_at, 1)
            
            res = NormalizedWeatherResponse(**cached_data)
            res.is_stale = True
            res.stale_age_seconds = stale_age
            res.data_source = f"{res.data_source} (STALE CACHE)"
            res.stale_warning = f"WARNING: Real-time provider unavailable. Serving cached observation from {stale_age:.0f} seconds ago."
            return res

        # 3. If no cache exists, raise safe exception
        raise RuntimeError("Weather Data Service unavailable: all providers and cache failed")

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7):
        for provider in self.providers:
            try:
                return await provider.get_forecast(latitude, longitude, days)
            except Exception as e:
                logger.warning(f"Forecast fetch failed for '{provider.provider_name}': {e}")
        return []

    async def get_rainfall(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "rainfall_mm": obs.weather_parameters.rainfall_mm,
            "condition": obs.weather_parameters.condition_text,
            "is_stale": obs.is_stale,
            "data_source": obs.data_source
        }

    async def get_wind(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "wind_speed_kmh": obs.weather_parameters.wind_speed,
            "wind_direction": obs.weather_parameters.wind_direction,
            "is_stale": obs.is_stale,
            "data_source": obs.data_source
        }

    async def get_temperature(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "temperature_celsius": obs.weather_parameters.temperature,
            "apparent_temperature_celsius": obs.weather_parameters.apparent_temperature,
            "is_stale": obs.is_stale,
            "data_source": obs.data_source
        }

    async def get_warnings(self, latitude: float, longitude: float):
        for provider in self.providers:
            try:
                warnings = await provider.get_warnings(latitude, longitude)
                if warnings:
                    return warnings
            except Exception as e:
                logger.warning(f"Warnings fetch failed for '{provider.provider_name}': {e}")
        return []


weather_orchestrator = WeatherServiceOrchestrator()

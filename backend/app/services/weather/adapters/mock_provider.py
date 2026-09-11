import time
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.schemas.weather import DailyForecast, SevereWeatherAlert
from app.services.weather.base import (
    BaseWeatherProvider, NormalizedWeatherResponse, LocationDTO, WeatherParams
)


class MockWeatherProviderAdapter(BaseWeatherProvider):
    """
    Deterministic Mock Weather Provider Adapter for Unit Testing & Offline Isolation.
    """

    def __init__(
        self,
        should_timeout: bool = False,
        should_fail: bool = False,
        missing_fields: bool = False,
        custom_temp: Optional[float] = None
    ):
        self.should_timeout = should_timeout
        self.should_fail = should_fail
        self.missing_fields = missing_fields
        self.custom_temp = custom_temp

    @property
    def provider_name(self) -> str:
        return "Mock Weather Test Service"

    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherResponse:
        if self.should_timeout:
            await asyncio.sleep(2.0)
            raise TimeoutError("Mock Provider connection timed out")

        if self.should_fail:
            raise RuntimeError("Mock Provider external API service failure (503 Service Unavailable)")

        now_iso = datetime.now(timezone.utc).isoformat()

        if self.missing_fields:
            return NormalizedWeatherResponse(
                location=LocationDTO(name=location_name or "Test Location", latitude=latitude, longitude=longitude),
                observation_time=now_iso,
                last_updated_time=now_iso,
                fetched_at_timestamp=time.time(),
                weather_parameters=WeatherParams(
                    temperature=None,  # Missing field
                    apparent_temperature=None,
                    humidity=None,
                    pressure=None,
                    wind_speed=None,
                    condition_text="Unknown Data"
                ),
                data_source=self.provider_name
            )

        temp_val = self.custom_temp if self.custom_temp is not None else 22.5

        return NormalizedWeatherResponse(
            location=LocationDTO(name=location_name or "Test Location", latitude=latitude, longitude=longitude, country="MockLand"),
            observation_time=now_iso,
            last_updated_time=now_iso,
            fetched_at_timestamp=time.time(),
            weather_parameters=WeatherParams(
                temperature=temp_val,
                apparent_temperature=temp_val + 0.5,
                humidity=60.0,
                pressure=1012.5,
                wind_speed=15.0,
                wind_direction=180,
                rainfall_mm=0.0,
                condition_text="Sunny Clear Sky",
                uv_index=5.0
            ),
            data_source=self.provider_name
        )

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[DailyForecast]:
        if self.should_fail:
            raise RuntimeError("Mock Forecast Service Failed")

        return [
            DailyForecast(
                date=f"2026-09-{10+i:02d}",
                temp_min=15.0 + i,
                temp_max=25.0 + i,
                precipitation_probability=10.0,
                precipitation_sum_mm=0.0,
                condition_text="Clear"
            )
            for i in range(min(days, 7))
        ]

    async def get_rainfall(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {"rainfall_mm": obs.weather_parameters.rainfall_mm, "data_source": self.provider_name}

    async def get_wind(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {"wind_speed": obs.weather_parameters.wind_speed, "data_source": self.provider_name}

    async def get_temperature(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {"temperature": obs.weather_parameters.temperature, "data_source": self.provider_name}

    async def get_warnings(self, latitude: float, longitude: float) -> List[SevereWeatherAlert]:
        return []

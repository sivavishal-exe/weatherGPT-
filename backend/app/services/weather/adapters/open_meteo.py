import time
import httpx
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from app.config import settings
from app.core.logging import logger
from app.core.security import sanitize_weather_data, sanitize_input_text
from app.schemas.weather import DailyForecast, SevereWeatherAlert
from app.services.weather.base import (
    BaseWeatherProvider, NormalizedWeatherResponse, LocationDTO, WeatherParams
)

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow", 75: "Heavy snow",
    80: "Rain showers", 82: "Violent rain showers", 95: "Thunderstorm"
}


class OpenMeteoProviderAdapter(BaseWeatherProvider):
    """
    Open-Meteo Meteorological Data Provider Adapter.
    """

    @property
    def provider_name(self) -> str:
        return "Open-Meteo Meteorological Service"

    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherResponse:
        url = (
            f"{settings.OPEN_METEO_BASE_URL}/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,wind_speed_10m,wind_direction_10m,weather_code,precipitation"
            f"&timezone=auto"
        )

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            raw = resp.json()

        curr_raw = raw.get("current", {})
        if not curr_raw:
            raise ValueError("Malformed response from Open-Meteo: missing 'current' field")

        sanitized = sanitize_weather_data({
            "latitude": latitude,
            "longitude": longitude,
            "temperature": curr_raw.get("temperature_2m"),
            "humidity": curr_raw.get("relative_humidity_2m"),
            "pressure": curr_raw.get("surface_pressure"),
            "wind_speed": curr_raw.get("wind_speed_10m"),
        })

        now_iso = datetime.now(timezone.utc).isoformat()
        wmo_code = int(curr_raw.get("weather_code", 0))
        cond_str = WMO_CODES.get(wmo_code, "Partly Cloudy")
        precip = curr_raw.get("precipitation")
        precip_float = float(precip) if precip is not None else None

        loc_title = sanitize_input_text(location_name or f"Coordinates ({latitude:.2f}, {longitude:.2f})")

        return NormalizedWeatherResponse(
            location=LocationDTO(
                name=loc_title,
                latitude=latitude,
                longitude=longitude,
                country="Global",
                timezone=raw.get("timezone", "UTC")
            ),
            observation_time=now_iso,
            last_updated_time=now_iso,
            fetched_at_timestamp=time.time(),
            weather_parameters=WeatherParams(
                temperature=sanitized.get("temperature"),
                apparent_temperature=curr_raw.get("apparent_temperature"),
                humidity=sanitized.get("humidity"),
                pressure=sanitized.get("pressure"),
                wind_speed=sanitized.get("wind_speed"),
                wind_direction=int(curr_raw.get("wind_direction_10m", 0)),
                rainfall_mm=precip_float,
                condition_text=cond_str,
                uv_index=4.0
            ),
            data_source=self.provider_name,
            is_stale=False,
            stale_age_seconds=0.0
        )

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[DailyForecast]:
        url = (
            f"{settings.OPEN_METEO_BASE_URL}/forecast?"
            f"latitude={latitude}&longitude={longitude}"
            f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max"
            f"&forecast_days={days}&timezone=auto"
        )
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            raw = resp.json()

        daily_raw = raw.get("daily", {})
        dates = daily_raw.get("time", [])
        min_t = daily_raw.get("temperature_2m_min", [])
        max_t = daily_raw.get("temperature_2m_max", [])
        pop = daily_raw.get("precipitation_probability_max", [])
        p_sum = daily_raw.get("precipitation_sum", [])
        codes = daily_raw.get("weather_code", [])

        forecasts = []
        for i in range(min(len(dates), days)):
            forecasts.append(DailyForecast(
                date=dates[i],
                temp_min=float(min_t[i]) if i < len(min_t) and min_t[i] is not None else 15.0,
                temp_max=float(max_t[i]) if i < len(max_t) and max_t[i] is not None else 25.0,
                precipitation_probability=float(pop[i]) if i < len(pop) and pop[i] is not None else 0.0,
                precipitation_sum_mm=float(p_sum[i]) if i < len(p_sum) and p_sum[i] is not None else 0.0,
                condition_text=WMO_CODES.get(int(codes[i]) if i < len(codes) else 0, "Clear")
            ))
        return forecasts

    async def get_rainfall(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "rainfall_mm": obs.weather_parameters.rainfall_mm,
            "condition": obs.weather_parameters.condition_text,
            "data_source": self.provider_name
        }

    async def get_wind(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "wind_speed_kmh": obs.weather_parameters.wind_speed,
            "wind_direction": obs.weather_parameters.wind_direction,
            "data_source": self.provider_name
        }

    async def get_temperature(self, latitude: float, longitude: float) -> Dict[str, Any]:
        obs = await self.get_current_weather(latitude, longitude)
        return {
            "temperature_celsius": obs.weather_parameters.temperature,
            "apparent_temperature_celsius": obs.weather_parameters.apparent_temperature,
            "data_source": self.provider_name
        }

    async def get_warnings(self, latitude: float, longitude: float) -> List[SevereWeatherAlert]:
        return []

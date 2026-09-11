import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.weather import DailyForecast, SevereWeatherAlert


class LocationDTO(BaseModel):
    name: str = Field(..., description="Location or region name")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    country: Optional[str] = None
    timezone: Optional[str] = "UTC"


class WeatherParams(BaseModel):
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    apparent_temperature: Optional[float] = Field(None, description="Feels-like temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0.0, le=100.0, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Surface pressure in hPa")
    wind_speed: Optional[float] = Field(None, ge=0.0, description="Wind speed in km/h")
    wind_direction: Optional[int] = Field(None, ge=0, le=360)
    rainfall_mm: Optional[float] = Field(None, ge=0.0, description="Rainfall accumulation in mm")
    condition_text: str = Field("Unknown", description="Human readable weather condition")
    uv_index: Optional[float] = Field(None, ge=0.0)


class NormalizedWeatherResponse(BaseModel):
    location: LocationDTO
    observation_time: str = Field(..., description="ISO 8601 observation timestamp")
    last_updated_time: str = Field(..., description="ISO 8601 provider fetch/update timestamp")
    fetched_at_timestamp: float = Field(default_factory=time.time, description="Unix timestamp of fetch")
    weather_parameters: WeatherParams
    data_source: str = Field(..., description="Identified meteorological data provider source")
    is_stale: bool = Field(False, description="Flag explicitly indicating if data is cached/stale")
    stale_age_seconds: float = Field(0.0, description="Age of cached data in seconds")
    stale_warning: Optional[str] = Field(None, description="Warning message when serving stale fallback data")
    daily_forecast: List[DailyForecast] = Field(default_factory=list)
    official_alerts: List[SevereWeatherAlert] = Field(default_factory=list)


class BaseWeatherProvider(ABC):
    """
    Abstract Provider-Independent Weather Interface.
    Enforces unified weather method contracts across all meteorological provider adapters.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the meteorological data provider."""
        pass

    @abstractmethod
    async def get_current_weather(
        self, latitude: float, longitude: float, location_name: Optional[str] = None
    ) -> NormalizedWeatherResponse:
        """Fetch normalized current weather observation."""
        pass

    @abstractmethod
    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> List[DailyForecast]:
        """Fetch multi-day weather forecast."""
        pass

    @abstractmethod
    async def get_rainfall(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch detailed rainfall accumulation and precipitation probability."""
        pass

    @abstractmethod
    async def get_wind(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch wind speed, direction, and gust parameters."""
        pass

    @abstractmethod
    async def get_temperature(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch current, feels-like, and daily min/max temperature parameters."""
        pass

    @abstractmethod
    async def get_warnings(self, latitude: float, longitude: float) -> List[SevereWeatherAlert]:
        """Fetch active official severe weather warnings."""
        pass

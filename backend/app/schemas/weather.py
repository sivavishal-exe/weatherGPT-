from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.alerts import (
    WeatherHazardType,
    RiskContributingFactor,
    WeatherGPTCalculatedRisk,
    OfficialMeteorologicalWarning,
    AIGeneratedAdvisory,
    LocationRiskFactors,
    WeatherRiskInput,
    WeatherRiskEvaluationResponse,
    AdminAlertCreate,
    AdminAlertUpdate
)


class LocationInfo(BaseModel):
    name: str = Field(..., description="Location or city name")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    country: Optional[str] = None
    timezone: Optional[str] = "UTC"


class HourlyForecast(BaseModel):
    time: str = Field(..., description="ISO timestamp string")
    temperature_2m: float
    apparent_temperature: float
    relative_humidity_2m: float
    dew_point_2m: Optional[float] = 0.0
    precipitation_probability: float = 0.0
    precipitation: float = 0.0
    rain: float = 0.0
    showers: float = 0.0
    snowfall: float = 0.0
    weather_code: int = 0
    surface_pressure: float = 1013.25
    cloud_cover: float = 0.0
    wind_speed_10m: float = 0.0
    soil_moisture_0_to_1cm: Optional[float] = 0.0
    soil_temperature_0cm: Optional[float] = 0.0


class CurrentWeather(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    apparent_temperature: float = Field(..., description="Feels like temperature in Celsius")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity percentage")
    pressure: float = Field(1013.25, description="Surface pressure in hPa")
    wind_speed: float = Field(..., ge=0.0, description="Wind speed in km/h")
    wind_direction: int = Field(0, ge=0, le=360)
    weather_code: int = Field(0)
    condition_text: str = Field(..., description="Human readable condition (e.g., Clear, Rain)")
    uv_index: Optional[float] = 0.0
    is_day: Optional[int] = 1
    rain: Optional[float] = 0.0
    showers: Optional[float] = 0.0
    snowfall: Optional[float] = 0.0


class DailyForecast(BaseModel):
    date: str = Field(..., description="ISO Date string (YYYY-MM-DD)")
    temp_min: float
    temp_max: float
    apparent_temp_min: Optional[float] = None
    apparent_temp_max: Optional[float] = None
    precipitation_probability: float = Field(0.0, ge=0.0, le=100.0)
    precipitation_sum_mm: float = 0.0
    uv_index_max: Optional[float] = 0.0
    condition_text: str


class SevereWeatherAlert(BaseModel):
    id: str
    event: str = Field(..., description="Alert title e.g. High Wind Warning, Typhoon Alert")
    severity: str = Field(..., description="EXTREME, SEVERE, MODERATE, MINOR")
    headline: str
    description: str
    instruction: Optional[str] = None
    source: str = Field("Official Meteorological Agency", description="Trusted Meteorological Authority")
    issued_at: str
    is_official_warning: bool = Field(True, description="Always true for official warnings")


class HistoricalClimateData(BaseModel):
    location_name: str
    historical_avg_temp: float
    current_anomaly_celsius: float
    precipitation_trend: str
    climate_baseline_years: str = "1991-2020 Baseline"


class WeatherDataResponse(BaseModel):
    location: LocationInfo
    current: CurrentWeather
    daily_forecast: List[DailyForecast]
    hourly_forecast: List[HourlyForecast] = []
    official_alerts: List[SevereWeatherAlert] = []
    climate_summary: Optional[HistoricalClimateData] = None
    data_source: str = "Open-Meteo & NOAA NWS Verified Meteorological Data"
    cached: bool = False
    low_bandwidth_mode: bool = False

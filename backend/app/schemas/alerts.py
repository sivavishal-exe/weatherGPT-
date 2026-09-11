from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
import html
import re

SUSPICIOUS_SCRIPT_REGEX = re.compile(r'(<script|javascript:|eval\(|onload=|onerror=)', re.IGNORECASE)


class WeatherHazardType(str, Enum):
    HEAVY_RAINFALL = "heavy_rainfall"
    THUNDERSTORM = "thunderstorm"
    STRONG_WIND = "strong_wind"
    HEATWAVE = "heatwave"
    CYCLONE = "cyclone"
    FLOOD_RISK = "flood_related_risk"
    BLIZZARD_DEEP_FREEZE = "blizzard_deep_freeze"
    EXTREME_UV = "extreme_uv"
    OTHER_OFFICIAL_WARNING = "other_official_warning"


class RiskContributingFactor(BaseModel):
    factor_name: str = Field(..., description="Name of evaluated risk factor (rainfall, wind, temperature, forecast_uncertainty, official_warning, location_risk)")
    score_contribution: float = Field(..., ge=0.0, le=100.0, description="Numerical points added to total risk score")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relative weighting factor")
    raw_value: str = Field(..., description="Observed metric or condition string")
    description: str = Field(..., description="Transparent explanation of factor calculation")


class WeatherGPTCalculatedRisk(BaseModel):
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Explainable Weather Impact Score (0 to 100)")
    severity: str = Field(..., description="MINIMAL (0-19), MODERATE (20-44), HIGH (45-69), EXTREME (70-100)")
    contributing_factors: List[RiskContributingFactor]
    detected_hazards: List[WeatherHazardType]
    timestamp: str = Field(..., description="ISO 8601 timestamp of calculation")
    source: str = Field("WeatherGPT Risk Engine v1.0", description="Proprietary WeatherGPT model rating")
    is_official_warning: bool = Field(False, description="Strictly False for WeatherGPT calculated risk")


class OfficialMeteorologicalWarning(BaseModel):
    id: str
    event: str = Field(..., description="Official alert title e.g. High Wind Warning, Typhoon Alert")
    severity: str = Field(..., description="EXTREME, SEVERE, MODERATE, MINOR")
    headline: str
    description: str
    instruction: Optional[str] = None
    source: str = Field(..., description="Government/Official Meteorological Authority (e.g. NOAA, WMO, IMD)")
    issued_at: str
    is_official_warning: bool = Field(True, description="Strictly True for verified official warnings")


class AIGeneratedAdvisory(BaseModel):
    advisory_text: str = Field(..., description="AI safety guidance")
    recommended_actions: List[str] = Field(default_factory=list)
    confidence_level: str = Field("HIGH", description="AI advisory confidence: HIGH, MEDIUM, LOW")
    timestamp: str
    source: str = Field("WeatherGPT AI Advisory Service", description="AI generated safety guidance")
    is_official_warning: bool = Field(False, description="Strictly False for AI advisories")


class LocationRiskFactors(BaseModel):
    is_coastal: bool = Field(False, description="Location is in a coastal zone")
    is_flood_prone: bool = Field(False, description="Location is in a river basin or flood plain")
    is_urban_dense: bool = Field(False, description="Location is an urban heat island")
    elevation_meters: Optional[float] = Field(0.0, ge=-500.0, le=9000.0)
    soil_saturation_pct: Optional[float] = Field(0.0, ge=0.0, le=100.0)


class WeatherRiskInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    temperature: float = Field(20.0, ge=-100.0, le=70.0)
    apparent_temperature: Optional[float] = Field(None, ge=-100.0, le=70.0)
    humidity: float = Field(50.0, ge=0.0, le=100.0)
    pressure: float = Field(1013.25, ge=800.0, le=1100.0)
    wind_speed: float = Field(10.0, ge=0.0, le=400.0)
    wind_gust: Optional[float] = Field(None, ge=0.0, le=500.0)
    precipitation_mm_hr: float = Field(0.0, ge=0.0, le=500.0)
    weather_code: int = Field(0, ge=0, le=99)
    forecast_uncertainty: float = Field(0.0, ge=0.0, le=1.0, description="0.0 = low uncertainty, 1.0 = high uncertainty")
    location_factors: Optional[LocationRiskFactors] = None
    official_alerts: Optional[List[OfficialMeteorologicalWarning]] = []


class WeatherRiskEvaluationResponse(BaseModel):
    location_name: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    official_warnings: List[OfficialMeteorologicalWarning] = Field(default_factory=list)
    calculated_risk: WeatherGPTCalculatedRisk
    ai_advisory: AIGeneratedAdvisory
    disclaimer: str = Field(
        "WeatherGPT calculated risk scores and AI advisories are decision-support predictive analytics and MUST NOT be represented as official government meteorological warnings.",
        description="Strict non-official attribution disclaimer"
    )


class AdminAlertCreate(BaseModel):
    event: str = Field(..., min_length=2, max_length=200)
    severity: str = Field(..., description="EXTREME, SEVERE, MODERATE, MINOR")
    headline: str = Field(..., min_length=2, max_length=500)
    description: str = Field(..., min_length=2, max_length=2000)
    instruction: Optional[str] = Field(None, max_length=1000)
    source: str = Field("Official Meteorological Agency", min_length=2, max_length=200)
    latitude_min: float = Field(-90.0, ge=-90.0, le=90.0)
    latitude_max: float = Field(90.0, ge=-90.0, le=90.0)
    longitude_min: float = Field(-180.0, ge=-180.0, le=180.0)
    longitude_max: float = Field(180.0, ge=-180.0, le=180.0)
    is_official_warning: bool = Field(True)

    @field_validator("event", "headline", "description", "instruction", "source")
    @classmethod
    def sanitize_text_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        clean = value.strip()
        if SUSPICIOUS_SCRIPT_REGEX.search(clean):
            clean = html.escape(clean)
        return clean


class AdminAlertUpdate(BaseModel):
    event: Optional[str] = Field(None, min_length=2, max_length=200)
    severity: Optional[str] = Field(None)
    headline: Optional[str] = Field(None, min_length=2, max_length=500)
    description: Optional[str] = Field(None, min_length=2, max_length=2000)
    instruction: Optional[str] = Field(None, max_length=1000)
    source: Optional[str] = Field(None, min_length=2, max_length=200)
    latitude_min: Optional[float] = Field(None, ge=-90.0, le=90.0)
    latitude_max: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude_min: Optional[float] = Field(None, ge=-180.0, le=180.0)
    longitude_max: Optional[float] = Field(None, ge=-180.0, le=180.0)
    is_official_warning: Optional[bool] = Field(None)

    @field_validator("event", "headline", "description", "instruction", "source")
    @classmethod
    def sanitize_text_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        clean = value.strip()
        if SUSPICIOUS_SCRIPT_REGEX.search(clean):
            clean = html.escape(clean)
        return clean

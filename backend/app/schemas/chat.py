from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.weather import SevereWeatherAlert


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User conversational weather query")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_name: Optional[str] = Field(None, max_length=200)
    language: str = Field("en", min_length=2, max_length=10, description="ISO language code (en, es, fr, hi, ja, etc.)")
    low_bandwidth: bool = Field(False, description="Optimization switch for low connectivity")


class GroundedFact(BaseModel):
    fact_type: str = Field(..., description="CURRENT_WEATHER, FORECAST, ALERT, CLIMATE")
    fact_text: str = Field(..., description="Verified statement directly from meteorology API")
    source: str = Field("Open-Meteo Meteorological Data Service")


class ChatResponse(BaseModel):
    query: str
    answer: str = Field(..., description="Conversational WeatherGPT response")
    grounded_facts: List[GroundedFact] = Field(default_factory=list, description="Verified facts ensuring zero hallucination")
    official_warnings: List[SevereWeatherAlert] = Field(default_factory=list, description="Official government warnings (MUST BE DISTINCT)")
    ai_recommendations: List[str] = Field(default_factory=list, description="AI safety advisories (clearly tagged)")
    language: str = "en"
    low_bandwidth_mode: bool = False

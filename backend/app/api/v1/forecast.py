from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException
from app.services.weather_provider import weather_provider
from app.schemas.weather import DailyForecast
from app.core.security import sanitize_input_text

router = APIRouter(prefix="/forecast", tags=["Weather Forecast"])


@APIRouter.get(router, "", response_model=List[DailyForecast])
async def get_multi_day_forecast(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    days: int = Query(7, ge=1, le=14),
    location_name: Optional[str] = Query(None)
):
    """
    Fetch multi-day weather forecast from verified meteorological providers.
    """
    sanitized_name = sanitize_input_text(location_name) if location_name else None
    weather = await weather_provider.get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=sanitized_name,
        days=days
    )
    return weather.daily_forecast

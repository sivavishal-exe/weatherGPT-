from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Request
from app.services.weather_provider import weather_provider
from app.services.bandwidth_service import bandwidth_service
from app.schemas.weather import WeatherDataResponse
from app.core.security import sanitize_input_text

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])


@APIRouter.get(router, "", response_model=WeatherDataResponse)
async def get_weather_forecast(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude degree (-90 to 90)"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude degree (-180 to 180)"),
    location_name: Optional[str] = Query(None, description="Optional city or region name"),
    days: int = Query(7, ge=1, le=14, description="Forecast days (1 to 14)"),
    low_bandwidth: bool = Query(False, description="Enable low bandwidth mode")
):
    """
    Fetch real-time weather, forecast, and official weather warnings from verified meteorological providers.
    Supports low-bandwidth payloads and Redis caching.
    """
    sanitized_name = sanitize_input_text(location_name) if location_name else None
    res = await weather_provider.get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=sanitized_name,
        days=days,
        low_bandwidth=low_bandwidth
    )
    return res


@APIRouter.get(router, "/compact")
async def get_compact_weather(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    location_name: Optional[str] = Query(None)
):
    """
    Ultra-low bandwidth endpoint returning minified JSON schema for extreme low connectivity.
    """
    sanitized_name = sanitize_input_text(location_name) if location_name else None
    res = await weather_provider.get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=sanitized_name,
        days=3,
        low_bandwidth=True
    )
    compact_dict = bandwidth_service.optimize_weather_payload(res)
    return compact_dict

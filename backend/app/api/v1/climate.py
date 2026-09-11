from typing import Optional
from fastapi import APIRouter, Query
from app.services.climate_service import climate_analytics
from app.schemas.weather import HistoricalClimateData
from app.core.security import sanitize_input_text

router = APIRouter(prefix="/climate", tags=["Climate Analytics"])


@APIRouter.get(router, "", response_model=HistoricalClimateData)
async def get_climate_analytics(
    location_name: str = Query(..., min_length=1, max_length=200),
    current_temp: float = Query(..., ge=-100.0, le=70.0),
    month: int = Query(9, ge=1, le=12)
):
    """
    Historical climate analytics & anomaly calculations against 30-year WMO baseline.
    """
    clean_name = sanitize_input_text(location_name)
    analysis = climate_analytics.analyze_anomaly(
        location_name=clean_name,
        current_temp=current_temp,
        month=month
    )
    return analysis

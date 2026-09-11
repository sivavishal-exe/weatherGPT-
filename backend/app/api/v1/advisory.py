from typing import List, Dict, Any
from fastapi import APIRouter, Query
from app.services.weather_provider import weather_provider
from app.services.alert_service import alert_engine

router = APIRouter(prefix="/advisory", tags=["Weather Safety Advisory"])


@APIRouter.get(router, "", response_model=Dict[str, Any])
async def get_weather_advisories(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    location_name: str = Query("Your Location")
):
    """
    Generates location-based weather safety advisories & risk evaluation.
    """
    weather = await weather_provider.get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        days=1
    )
    
    risk_assessment = alert_engine.calculate_risk_score(weather.current)
    
    advisories = []
    if risk_assessment["risk_level"] in ["EXTREME", "HIGH"]:
        advisories.append(f"HIGH RISK ADVISORY: {', '.join(risk_assessment['hazards'])}")
    else:
        advisories.append("Weather conditions are baseline normal. Standard outdoor activities permitted.")

    return {
        "location": weather.location.name,
        "risk_level": risk_assessment["risk_level"],
        "risk_score": risk_assessment["risk_score"],
        "hazards": risk_assessment["hazards"],
        "advisories": advisories,
        "official_alerts_count": len(weather.official_alerts)
    }

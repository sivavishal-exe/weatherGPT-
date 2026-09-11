import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import require_admin_user
from app.core.logging import logger
from app.services.weather_provider import weather_provider
from app.services.alert_service import alert_engine
from app.models.weather import SevereAlertRecord
from app.schemas.alerts import (
    OfficialMeteorologicalWarning,
    WeatherRiskInput,
    WeatherRiskEvaluationResponse,
    AdminAlertCreate,
    AdminAlertUpdate,
    LocationRiskFactors
)
from app.schemas.weather import SevereWeatherAlert

router = APIRouter(prefix="/alerts", tags=["Severe Weather Alerts & Risk Engine"])


@router.get("", response_model=List[OfficialMeteorologicalWarning])
async def get_active_alerts(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0)
):
    """
    Fetch official government & meteorological severe weather warnings for a location.
    All alerts returned are verified official warnings (e.g. NOAA, WMO, IMD).
    Never includes unverified AI predictions as official warnings.
    """
    raw_alerts = await weather_provider.fetch_official_alerts(latitude, longitude)
    official_warnings = []
    for alert in raw_alerts:
        if alert.is_official_warning:
            official_warnings.append(OfficialMeteorologicalWarning(
                id=alert.id,
                event=alert.event,
                severity=alert.severity,
                headline=alert.headline,
                description=alert.description,
                instruction=alert.instruction,
                source=alert.source,
                issued_at=alert.issued_at,
                is_official_warning=True
            ))
    return official_warnings


@router.get("/risk-assessment", response_model=WeatherRiskEvaluationResponse)
async def evaluate_location_risk(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    location_name: str = Query("Target Location"),
    is_coastal: bool = Query(False),
    is_flood_prone: bool = Query(False),
    forecast_uncertainty: float = Query(0.1, ge=0.0, le=1.0)
):
    """
    Transparent WeatherGPT Risk Evaluation & Advisory Engine.
    Calculates explainable Weather Impact Score (0–100) with contributing factors breakdown,
    and returns strictly separated Official Warnings, WeatherGPT Risk Score, and AI Advisories.
    """
    weather = await weather_provider.get_weather(
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        days=1
    )

    official_alerts_raw = weather.official_alerts or []
    official_warnings = [
        OfficialMeteorologicalWarning(
            id=a.id,
            event=a.event,
            severity=a.severity,
            headline=a.headline,
            description=a.description,
            instruction=a.instruction,
            source=a.source,
            issued_at=a.issued_at,
            is_official_warning=True
        ) for a in official_alerts_raw if a.is_official_warning
    ]

    loc_factors = LocationRiskFactors(
        is_coastal=is_coastal,
        is_flood_prone=is_flood_prone,
        is_urban_dense=False,
        elevation_meters=10.0 if not is_coastal else 2.0
    )

    risk_input = WeatherRiskInput(
        latitude=latitude,
        longitude=longitude,
        temperature=weather.current.temperature,
        apparent_temperature=weather.current.apparent_temperature,
        humidity=weather.current.humidity,
        pressure=weather.current.pressure,
        wind_speed=weather.current.wind_speed,
        precipitation_mm_hr=0.0,
        weather_code=weather.current.weather_code,
        forecast_uncertainty=forecast_uncertainty,
        location_factors=loc_factors,
        official_alerts=official_warnings
    )

    calculated_risk = alert_engine.evaluate_weather_risk(risk_input)
    ai_advisory = alert_engine.generate_ai_advisory(calculated_risk, official_warnings, weather.location.name)

    return WeatherRiskEvaluationResponse(
        location_name=weather.location.name,
        latitude=latitude,
        longitude=longitude,
        official_warnings=official_warnings,
        calculated_risk=calculated_risk,
        ai_advisory=ai_advisory
    )


@router.post("/evaluate", response_model=WeatherRiskEvaluationResponse)
async def evaluate_custom_weather_risk(risk_input: WeatherRiskInput):
    """
    Evaluates weather risk given a custom WeatherRiskInput payload.
    Supports boundary condition testing, custom forecasts, and location factors.
    """
    official_warnings = risk_input.official_alerts or []
    calculated_risk = alert_engine.evaluate_weather_risk(risk_input)
    ai_advisory = alert_engine.generate_ai_advisory(
        calculated_risk,
        official_warnings,
        f"Coords ({risk_input.latitude:.2f}, {risk_input.longitude:.2f})"
    )

    return WeatherRiskEvaluationResponse(
        location_name=f"Location ({risk_input.latitude:.2f}, {risk_input.longitude:.2f})",
        latitude=risk_input.latitude,
        longitude=risk_input.longitude,
        official_warnings=official_warnings,
        calculated_risk=calculated_risk,
        ai_advisory=ai_advisory
    )


# --- Administrative Alert Management Endpoints (Protected by Authorization) ---

@router.get("/admin/list", dependencies=[Depends(require_admin_user)])
async def list_admin_alerts(db: AsyncSession = Depends(get_db)):
    """List all administrative severe weather alerts. Requires Admin authentication."""
    stmt = select(SevereAlertRecord)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/admin", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
async def create_admin_alert(
    payload: AdminAlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create an administrative severe weather alert overlay.
    Protected by strict Authentication & Authorization requirements.
    Validates range checks and sanitizes text inputs against alert manipulation.
    """
    alert_id = f"admin-alert-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    record = SevereAlertRecord(
        id=alert_id,
        event=payload.event,
        severity=payload.severity.upper(),
        headline=payload.headline,
        description=payload.description,
        instruction=payload.instruction,
        source=payload.source,
        issued_at=now_str,
        is_official_warning=payload.is_official_warning,
        latitude_min=payload.latitude_min,
        latitude_max=payload.latitude_max,
        longitude_min=payload.longitude_min,
        longitude_max=payload.longitude_max
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    logger.info(f"Administrative severe weather alert created: {record.id} ({record.event})")
    return record


@router.put("/admin/{alert_id}", dependencies=[Depends(require_admin_user)])
async def update_admin_alert(
    alert_id: str,
    payload: AdminAlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing administrative severe weather alert overlay.
    Protected by strict Authentication & Authorization requirements.
    """
    stmt = select(SevereAlertRecord).where(SevereAlertRecord.id == alert_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID {alert_id} not found.")

    if payload.event is not None:
        record.event = payload.event
    if payload.severity is not None:
        record.severity = payload.severity.upper()
    if payload.headline is not None:
        record.headline = payload.headline
    if payload.description is not None:
        record.description = payload.description
    if payload.instruction is not None:
        record.instruction = payload.instruction
    if payload.source is not None:
        record.source = payload.source
    if payload.latitude_min is not None:
        record.latitude_min = payload.latitude_min
    if payload.latitude_max is not None:
        record.latitude_max = payload.latitude_max
    if payload.longitude_min is not None:
        record.longitude_min = payload.longitude_min
    if payload.longitude_max is not None:
        record.longitude_max = payload.longitude_max
    if payload.is_official_warning is not None:
        record.is_official_warning = payload.is_official_warning

    await db.commit()
    await db.refresh(record)
    logger.info(f"Administrative severe weather alert updated: {alert_id}")
    return record


@router.delete("/admin/{alert_id}", dependencies=[Depends(require_admin_user)])
async def delete_admin_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an administrative severe weather alert overlay.
    Protected by strict Authentication & Authorization requirements.
    """
    stmt = select(SevereAlertRecord).where(SevereAlertRecord.id == alert_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert with ID {alert_id} not found.")

    await db.delete(record)
    await db.commit()
    logger.info(f"Administrative severe weather alert deleted: {alert_id}")
    return {"status": "deleted", "id": alert_id}

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.schemas.alerts import (
    WeatherRiskInput,
    LocationRiskFactors,
    OfficialMeteorologicalWarning,
    WeatherHazardType
)
from app.services.alert_service import alert_engine


@pytest.mark.asyncio
async def test_hazard_1_heavy_rain_detection():
    """Verify Heavy Rain hazard detection & severe flood scoring."""
    risk_input = WeatherRiskInput(
        latitude=13.0827,
        longitude=80.2707,
        precipitation_mm_hr=35.0,  # Torrential rain
        temperature=28.0,
        humidity=90.0,
        pressure=1008.0,
        wind_speed=15.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.HEAVY_RAINFALL in result.detected_hazards
    assert WeatherHazardType.FLOOD_RISK in result.detected_hazards
    assert result.severity in ("HIGH", "EXTREME")
    assert result.risk_score >= 50.0


@pytest.mark.asyncio
async def test_hazard_2_thunderstorm_detection():
    """Verify Thunderstorm hazard detection."""
    risk_input = WeatherRiskInput(
        latitude=28.6139,
        longitude=77.2090,
        precipitation_mm_hr=12.0,
        temperature=30.0,
        humidity=85.0,
        pressure=1000.0,
        wind_speed=30.0,
        weather_code=95  # Thunderstorm
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.THUNDERSTORM in result.detected_hazards
    assert any(f.factor_name == "thunderstorm_convective" and f.score_contribution > 0 for f in result.contributing_factors)


@pytest.mark.asyncio
async def test_hazard_3_strong_wind_detection():
    """Verify Strong Wind hazard detection."""
    risk_input = WeatherRiskInput(
        latitude=19.0760,
        longitude=72.8777,
        temperature=28.0,
        wind_speed=85.0,  # Storm-force wind
        wind_gust=105.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.STRONG_WIND in result.detected_hazards
    assert result.severity in ("HIGH", "EXTREME")


@pytest.mark.asyncio
async def test_hazard_4_extreme_temperature_heatwave_and_deep_freeze():
    """Verify Extreme Temperature (Heatwave & Deep Freeze) hazard detection."""
    # Heatwave
    heat_input = WeatherRiskInput(
        latitude=25.2048,
        longitude=55.2708,
        temperature=45.0,  # Extreme heatwave
        apparent_temperature=52.0,
        humidity=70.0
    )
    heat_res = alert_engine.evaluate_weather_risk(heat_input)
    assert WeatherHazardType.HEATWAVE in heat_res.detected_hazards
    assert heat_res.severity in ("HIGH", "EXTREME")

    # Deep Freeze
    freeze_input = WeatherRiskInput(
        latitude=64.1466,
        longitude=-21.9426,
        temperature=-25.0,  # Extreme freeze
        wind_speed=40.0
    )
    freeze_res = alert_engine.evaluate_weather_risk(freeze_input)
    assert WeatherHazardType.BLIZZARD_DEEP_FREEZE in freeze_res.detected_hazards
    assert freeze_res.severity in ("HIGH", "EXTREME")


@pytest.mark.asyncio
async def test_hazard_5_flood_risk_with_location_factors():
    """Verify Flood Risk detection with low-elevation flood-prone location factors."""
    flood_input = WeatherRiskInput(
        latitude=11.0168,
        longitude=76.9558,
        precipitation_mm_hr=20.0,
        location_factors=LocationRiskFactors(
            is_coastal=True,
            is_flood_prone=True,
            soil_saturation_pct=88.0,
            elevation_meters=2.0
        )
    )
    flood_res = alert_engine.evaluate_weather_risk(flood_input)
    assert WeatherHazardType.FLOOD_RISK in flood_res.detected_hazards
    assert any(f.factor_name == "location_risk" for f in flood_res.contributing_factors)


@pytest.mark.asyncio
async def test_hazard_6_cyclone_detection():
    """Verify Cyclone hazard detection under severe low pressure and hurricane winds."""
    cyclone_input = WeatherRiskInput(
        latitude=20.5937,
        longitude=78.9629,
        temperature=27.0,
        pressure=975.0,  # Extreme low pressure
        wind_speed=95.0,
        wind_gust=130.0
    )
    cyclone_res = alert_engine.evaluate_weather_risk(cyclone_input)
    assert WeatherHazardType.CYCLONE in cyclone_res.detected_hazards
    assert WeatherHazardType.STRONG_WIND in cyclone_res.detected_hazards
    assert cyclone_res.severity == "EXTREME"


@pytest.mark.asyncio
async def test_hazard_7_official_weather_warnings_and_3_way_separation():
    """Verify Official Weather Warnings integration & strict 3-way separation."""
    official_warning = OfficialMeteorologicalWarning(
        id="official-imd-101",
        event="Severe Cyclone Alert",
        severity="EXTREME",
        headline="Category 4 Cyclone Approaching Coast",
        description="High winds and torrential rain expected. Evacuate low-lying areas.",
        source="India Meteorological Department (Official)",
        issued_at="2026-09-12T12:00:00Z",
        is_official_warning=True
    )
    risk_input = WeatherRiskInput(
        latitude=13.0827,
        longitude=80.2707,
        temperature=28.0,
        wind_speed=90.0,
        official_alerts=[official_warning]
    )
    
    calculated_risk = alert_engine.evaluate_weather_risk(risk_input)
    ai_advisory = alert_engine.generate_ai_advisory(calculated_risk, [official_warning], "Chennai")

    # 1. Official Warning Component
    assert official_warning.is_official_warning is True
    assert "IMD" in official_warning.source or "Official" in official_warning.source

    # 2. WeatherGPT Calculated Risk Component
    assert calculated_risk.is_official_warning is False
    assert calculated_risk.source == "WeatherGPT Risk Engine v1.0"

    # 3. AI Safety Advisory Component
    assert ai_advisory.is_official_warning is False
    assert ai_advisory.source == "WeatherGPT AI Advisory Service"


@pytest.mark.asyncio
async def test_duplicate_alert_prevention_and_deduplication():
    """Verify duplicate-alert prevention mechanism in fetch_official_alerts."""
    from app.services.weather_provider import weather_provider
    alerts = await weather_provider.fetch_official_alerts(13.0827, 80.2707)
    alert_ids = [a.id for a in alerts]
    assert len(alert_ids) == len(set(alert_ids))  # Zero duplicate IDs


@pytest.mark.asyncio
async def test_alert_risk_evaluation_api_endpoint():
    """Verify end-to-end GET /api/v1/alerts/risk-assessment endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/api/v1/alerts/risk-assessment?latitude=11.0168&longitude=76.9558&location_name=Coimbatore")
        assert resp.status_code == 200
        data = resp.json()
        assert data["location_name"] == "Coimbatore"
        assert "calculated_risk" in data
        assert "ai_advisory" in data
        assert "official_warnings" in data
        assert data["calculated_risk"]["is_official_warning"] is False
        assert data["ai_advisory"]["is_official_warning"] is False

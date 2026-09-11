import pytest
from httpx import AsyncClient
from app.schemas.alerts import (
    WeatherRiskInput,
    LocationRiskFactors,
    OfficialMeteorologicalWarning,
    WeatherHazardType,
    AdminAlertCreate,
    AdminAlertUpdate
)
from app.services.alert_service import alert_engine
from app.config import settings


# --- 1. Unit Tests for Hazard Types & Transparent Risk Scoring ---

def test_heavy_rainfall_hazard():
    risk_input = WeatherRiskInput(
        latitude=13.0827,
        longitude=80.2707,
        precipitation_mm_hr=45.0,  # Torrential rain
        temperature=28.0,
        humidity=90.0,
        pressure=1008.0,
        wind_speed=15.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.HEAVY_RAINFALL in result.detected_hazards
    assert WeatherHazardType.FLOOD_RISK in result.detected_hazards
    
    # Check explainable contributing factors
    rainfall_factor = next(f for f in result.contributing_factors if f.factor_name == "rainfall")
    assert rainfall_factor.score_contribution >= 30.0
    assert "Torrential rainfall" in rainfall_factor.description


def test_thunderstorm_hazard():
    risk_input = WeatherRiskInput(
        latitude=28.6139,
        longitude=77.2090,
        precipitation_mm_hr=10.0,
        temperature=30.0,
        humidity=80.0,
        pressure=1002.0,
        wind_speed=35.0,
        weather_code=95  # Thunderstorm
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.THUNDERSTORM in result.detected_hazards
    thunderstorm_factor = next(f for f in result.contributing_factors if f.factor_name == "thunderstorm_convective")
    assert thunderstorm_factor.score_contribution > 0
    assert "Thunderstorm" in thunderstorm_factor.description


def test_strong_wind_hazard():
    risk_input = WeatherRiskInput(
        latitude=51.5074,
        longitude=-0.1278,
        temperature=15.0,
        wind_speed=80.0,  # Severe gale
        wind_gust=100.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.STRONG_WIND in result.detected_hazards
    wind_factor = next(f for f in result.contributing_factors if f.factor_name == "wind")
    assert wind_factor.score_contribution >= 20.0


def test_heatwave_hazard():
    risk_input = WeatherRiskInput(
        latitude=25.2048,
        longitude=55.2708,
        temperature=44.0,  # Extreme heat
        apparent_temperature=49.0,
        humidity=75.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.HEATWAVE in result.detected_hazards
    assert result.severity in ("HIGH", "EXTREME") or result.risk_score >= 60.0
    temp_factor = next(f for f in result.contributing_factors if f.factor_name == "temperature")
    assert temp_factor.score_contribution >= 35.0


def test_cyclone_hazard():
    risk_input = WeatherRiskInput(
        latitude=20.5937,
        longitude=78.9629,
        temperature=27.0,
        pressure=980.0,  # Severe low pressure
        wind_speed=95.0,
        wind_gust=120.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.CYCLONE in result.detected_hazards
    assert WeatherHazardType.STRONG_WIND in result.detected_hazards
    assert result.severity == "EXTREME" or result.risk_score >= 70.0


def test_flood_related_risk():
    risk_input = WeatherRiskInput(
        latitude=19.0760,
        longitude=72.8777,
        precipitation_mm_hr=25.0,
        location_factors=LocationRiskFactors(
            is_coastal=True,
            is_flood_prone=True,
            soil_saturation_pct=85.0,
            elevation_meters=3.0
        )
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.FLOOD_RISK in result.detected_hazards
    loc_factor = next(f for f in result.contributing_factors if f.factor_name == "location_risk")
    assert loc_factor.score_contribution > 0


def test_blizzard_deep_freeze_hazard():
    risk_input = WeatherRiskInput(
        latitude=64.1466,
        longitude=-21.9426,
        temperature=-25.0,
        wind_speed=50.0
    )
    result = alert_engine.evaluate_weather_risk(risk_input)
    assert WeatherHazardType.BLIZZARD_DEEP_FREEZE in result.detected_hazards


def test_risk_score_clamping_boundary_conditions():
    # Test maximum extreme conditions to verify score never exceeds 100.0
    extreme_input = WeatherRiskInput(
        latitude=0.0,
        longitude=0.0,
        temperature=55.0,
        apparent_temperature=60.0,
        humidity=95.0,
        pressure=940.0,
        wind_speed=180.0,
        wind_gust=220.0,
        precipitation_mm_hr=100.0,
        weather_code=99,
        forecast_uncertainty=1.0,
        location_factors=LocationRiskFactors(is_coastal=True, is_flood_prone=True, soil_saturation_pct=95.0),
        official_alerts=[
            OfficialMeteorologicalWarning(
                id="w1", event="Super Typhoon Warning", severity="EXTREME", headline="Evacuate",
                description="Extreme typhoon", source="JMA", issued_at="Now", is_official_warning=True
            )
        ]
    )
    extreme_res = alert_engine.evaluate_weather_risk(extreme_input)
    assert extreme_res.risk_score == 100.0
    assert extreme_res.severity == "EXTREME"

    # Test baseline minimal conditions to verify score is clamped to >= 0.0
    baseline_input = WeatherRiskInput(
        latitude=0.0,
        longitude=0.0,
        temperature=22.0,
        humidity=50.0,
        pressure=1013.25,
        wind_speed=5.0,
        precipitation_mm_hr=0.0,
        weather_code=0,
        forecast_uncertainty=0.0
    )
    baseline_res = alert_engine.evaluate_weather_risk(baseline_input)
    assert 0.0 <= baseline_res.risk_score < 20.0
    assert baseline_res.severity == "MINIMAL"


# --- 2. Strict 3-Way Separation Tests ---

def test_three_way_separation_disclaimer():
    official_alert = OfficialMeteorologicalWarning(
        id="noaa-001",
        event="High Wind Warning",
        severity="SEVERE",
        headline="Damaging winds possible",
        description="Gale force winds expected overnight.",
        source="NOAA National Weather Service",
        issued_at="2026-09-10T12:00:00Z",
        is_official_warning=True
    )
    risk_input = WeatherRiskInput(
        latitude=40.7128,
        longitude=-74.0060,
        temperature=20.0,
        wind_speed=65.0,
        official_alerts=[official_alert]
    )

    calc_risk = alert_engine.evaluate_weather_risk(risk_input)
    ai_advisory = alert_engine.generate_ai_advisory(calc_risk, [official_alert], "New York")

    # 1. Official warning component check
    assert official_alert.is_official_warning is True
    assert "NOAA" in official_alert.source

    # 2. WeatherGPT Calculated risk component check
    assert calc_risk.is_official_warning is False
    assert calc_risk.source == "WeatherGPT Risk Engine v1.0"

    # 3. AI advisory component check
    assert ai_advisory.is_official_warning is False
    assert ai_advisory.source == "WeatherGPT AI Advisory Service"


# --- 3. API Integration & Security Tests ---

@pytest.mark.asyncio
async def test_risk_evaluation_endpoint(async_client: AsyncClient):
    resp = await async_client.get(
        "/api/v1/alerts/risk-assessment?latitude=35.6762&longitude=139.6503&location_name=Tokyo&is_coastal=true"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "calculated_risk" in data
    assert "ai_advisory" in data
    assert "disclaimer" in data
    assert data["calculated_risk"]["is_official_warning"] is False
    assert data["ai_advisory"]["is_official_warning"] is False


@pytest.mark.asyncio
async def test_admin_endpoints_authentication_required(async_client: AsyncClient):
    # Unauthenticated POST request -> 401 Unauthorized
    resp1 = await async_client.post(
        "/api/v1/alerts/admin",
        json={
            "event": "Custom Flood Warning",
            "severity": "EXTREME",
            "headline": "Flash Flood",
            "description": "Heavy rainfall alert",
            "source": "Emergency Agency"
        }
    )
    assert resp1.status_code == 401
    assert "Authentication required" in resp1.json()["error"]["message"]

    # Invalid admin token -> 403 Forbidden
    resp2 = await async_client.post(
        "/api/v1/alerts/admin",
        json={
            "event": "Custom Flood Warning",
            "severity": "EXTREME",
            "headline": "Flash Flood",
            "description": "Heavy rainfall alert",
            "source": "Emergency Agency"
        },
        headers={"X-Admin-API-Key": "wrong-admin-key"}
    )
    assert resp2.status_code == 403
    assert "Forbidden" in resp2.json()["error"]["message"]


@pytest.mark.asyncio
async def test_admin_alert_lifecycle_and_sanitization(async_client: AsyncClient):
    admin_headers = {"X-Admin-API-Key": settings.ADMIN_SECRET_KEY}

    # 1. Create alert with potential XSS script injection
    payload = {
        "event": "<script>alert('xss')</script>Typhoon Alert",
        "severity": "EXTREME",
        "headline": "Severe storm approaching coastal areas",
        "description": "High wind and storm surge threat",
        "source": "Regional Met Authority",
        "latitude_min": 10.0,
        "latitude_max": 20.0,
        "longitude_min": 70.0,
        "longitude_max": 80.0,
        "is_official_warning": True
    }
    create_resp = await async_client.post("/api/v1/alerts/admin", json=payload, headers=admin_headers)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    alert_id = created_data["id"]
    
    # Sanitization check: script tag should be html escaped
    assert "<script>" not in created_data["event"]
    assert "&lt;script&gt;" in created_data["event"] or "Typhoon Alert" in created_data["event"]

    # 2. Query public alerts at matching location (lat 15, lon 75)
    alerts_resp = await async_client.get("/api/v1/alerts?latitude=15.0&longitude=75.0")
    assert alerts_resp.status_code == 200
    alert_list = alerts_resp.json()
    assert any(a["id"] == alert_id for a in alert_list)

    # 3. Update administrative alert
    update_payload = {"headline": "Updated Typhoon Category 4 Headline"}
    update_resp = await async_client.put(f"/api/v1/alerts/admin/{alert_id}", json=update_payload, headers=admin_headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["headline"] == "Updated Typhoon Category 4 Headline"

    # 4. Delete administrative alert
    delete_resp = await async_client.delete(f"/api/v1/alerts/admin/{alert_id}", headers=admin_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_numerical_range_validation_rejection(async_client: AsyncClient):
    # Test invalid latitude (> 90.0) in POST evaluate
    invalid_payload = {
        "latitude": 150.0,
        "longitude": 0.0,
        "temperature": 25.0
    }
    resp = await async_client.post("/api/v1/alerts/evaluate", json=invalid_payload)
    assert resp.status_code == 422
    assert resp.json()["status"] == "error"

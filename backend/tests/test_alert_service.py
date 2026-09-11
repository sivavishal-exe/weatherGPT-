from app.schemas.weather import CurrentWeather, SevereWeatherAlert
from app.services.alert_service import alert_engine


def test_alert_risk_score_calculation():
    # Extreme weather test
    extreme_curr = CurrentWeather(
        temperature=42.0,
        apparent_temperature=45.0,
        humidity=92.0,
        pressure=1005.0,
        wind_speed=75.0,
        wind_direction=180,
        weather_code=95,
        condition_text="Heavy Thunderstorm",
        uv_index=9.5
    )
    result = alert_engine.calculate_risk_score(extreme_curr)
    assert result["risk_level"] == "EXTREME"
    assert result["risk_score"] >= 70
    assert len(result["hazards"]) >= 2


def test_alert_filter_official_warnings():
    alerts = [
        SevereWeatherAlert(
            id="a1", event="Typhoon Warning", severity="EXTREME", headline="Evacuate coastal areas",
            description="High winds", source="Japan Met Agency", issued_at="Today", is_official_warning=True
        )
    ]
    official = alert_engine.filter_official_warnings(alerts)
    assert len(official) == 1
    assert official[0].is_official_warning is True

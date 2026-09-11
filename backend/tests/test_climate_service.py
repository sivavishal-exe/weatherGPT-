from app.services.climate_service import climate_analytics


def test_climate_anomaly_analysis():
    res = climate_analytics.analyze_anomaly(location_name="Denver", current_temp=30.0, month=9)
    assert res.location_name == "Denver"
    assert res.current_anomaly_celsius > 0
    assert "baseline" in res.precipitation_trend.lower()

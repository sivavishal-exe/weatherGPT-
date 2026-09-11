from app.core.security import sanitize_input_text, sanitize_weather_data


def test_sanitize_input_text_script_stripping():
    malicious = "<script>alert('xss')</script>Tokyo Weather"
    clean = sanitize_input_text(malicious)
    assert "<script>" not in clean
    assert "Tokyo Weather" in clean


def test_sanitize_weather_data_range_enforcement():
    untrusted = {
        "latitude": 120.0,      # Out of bounds (> 90)
        "longitude": -200.0,    # Out of bounds (< -180)
        "temperature": 150.0,   # Out of bounds (> 70)
        "humidity": -10.0,      # Out of bounds (< 0)
        "pressure": 1013.25,
        "wind_speed": 400.0     # Out of bounds (> 300)
    }
    clean = sanitize_weather_data(untrusted)
    assert clean["latitude"] == 90.0
    assert clean["longitude"] == -180.0
    assert clean["temperature"] == 70.0
    assert clean["humidity"] == 0.0
    assert clean["wind_speed"] == 300.0

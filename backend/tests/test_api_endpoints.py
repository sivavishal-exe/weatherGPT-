import pytest


@pytest.mark.asyncio
async def test_health_endpoints(async_client):
    r1 = await async_client.get("/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "healthy"

    r2 = await async_client.get("/api/v1/health")
    assert r2.status_code == 200
    assert r2.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_weather_valid_request(async_client):
    resp = await async_client.get("/api/v1/weather?latitude=35.6762&longitude=139.6503&location_name=Tokyo")
    assert resp.status_code == 200
    data = resp.json()
    assert data["location"]["name"] == "Tokyo"
    assert "current" in data


@pytest.mark.asyncio
async def test_weather_invalid_latitude(async_client):
    # Invalid latitude > 90
    resp = await async_client.get("/api/v1/weather?latitude=150.0&longitude=0.0")
    assert resp.status_code == 422
    data = resp.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == 422


@pytest.mark.asyncio
async def test_weather_missing_parameters(async_client):
    # Missing longitude
    resp = await async_client.get("/api/v1/weather?latitude=35.0")
    assert resp.status_code == 422
    assert resp.json()["status"] == "error"


@pytest.mark.asyncio
async def test_forecast_endpoint(async_client):
    resp = await async_client.get("/api/v1/forecast?latitude=35.6762&longitude=139.6503&days=5")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) <= 5


@pytest.mark.asyncio
async def test_climate_endpoint(async_client):
    resp = await async_client.get("/api/v1/climate?location_name=Denver&current_temp=28.5&month=9")
    assert resp.status_code == 200
    data = resp.json()
    assert data["location_name"] == "Denver"


@pytest.mark.asyncio
async def test_location_search_endpoint(async_client):
    resp = await async_client.get("/api/v1/location/search?query=Tokyo")
    assert resp.status_code == 200
    assert len(resp.json()) > 0
    assert "Tokyo" in resp.json()[0]["name"]


@pytest.mark.asyncio
async def test_advisory_endpoint(async_client):
    resp = await async_client.get("/api/v1/advisory?latitude=35.6762&longitude=139.6503&location_name=Tokyo")
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_level" in data
    assert "advisories" in data


@pytest.mark.asyncio
async def test_chat_malformed_json(async_client):
    # Post non-JSON string
    resp = await async_client.post("/api/v1/chat", content="malformed-string", headers={"Content-Type": "application/json"})
    assert resp.status_code == 422
    assert resp.json()["status"] == "error"
    # Ensure no internal stack trace or file path leaked
    assert "Traceback" not in resp.text
    assert "File " not in resp.text

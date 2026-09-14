import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.core.database import AsyncSessionLocal, init_db
from app.models.weather import (
    UserRecord, LocationRecord, WeatherObservationRecord, ForecastRecord,
    SevereAlertRecord, SavedLocationRecord, ChatSessionRecord, ChatMessageRecord,
    ClimateHistoryRecord, AdvisoryRecord
)
from app.repositories import (
    user_repo, location_repo, weather_obs_repo, forecast_repo,
    alert_repo, saved_location_repo, chat_repo, climate_repo, advisory_repo
)

@pytest.mark.asyncio
async def test_full_database_connection_and_tables():
    """Verify database initialization, schema creation, and session connectivity."""
    await init_db()
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(LocationRecord))
        assert res is not None

@pytest.mark.asyncio
async def test_crud_user_records():
    """Test full CRUD operations for User records."""
    test_email = f"crud_user_{uuid.uuid4().hex[:6]}@weathergpt.ai"
    async with AsyncSessionLocal() as db:
        # 1. CREATE
        user = await user_repo.create_user(db, test_email, "SecurePassword123!", "CRUD Test User")
        assert user.id is not None
        assert user.email == test_email

        # 2. READ
        fetched = await user_repo.get_by_email(db, test_email)
        assert fetched is not None
        assert fetched.id == user.id

        # 3. UPDATE
        updated = await user_repo.update(db, user.id, {"full_name": "Updated CRUD Name"})
        assert updated is not None
        assert updated.full_name == "Updated CRUD Name"

        # 4. DELETE
        deleted = await user_repo.delete(db, user.id)
        assert deleted is True

        post_delete = await user_repo.get_by_id(db, user.id)
        assert post_delete is None

@pytest.mark.asyncio
async def test_user_duplicate_email_prevention():
    """Verify unique constraint on user email prevents duplicates without data corruption."""
    test_email = f"dup_user_{uuid.uuid4().hex[:6]}@weathergpt.ai"
    async with AsyncSessionLocal() as db:
        await user_repo.create_user(db, test_email, "Pass123!", "User 1")
        
        with pytest.raises(IntegrityError):
            async with AsyncSessionLocal() as db_sub:
                await user_repo.create_user(db_sub, test_email, "Pass456!", "User 2")

@pytest.mark.asyncio
async def test_crud_location_and_saved_locations():
    """Test CRUD operations for Location and SavedLocation entities with relationships."""
    test_email = f"loc_user_{uuid.uuid4().hex[:6]}@weathergpt.ai"
    async with AsyncSessionLocal() as db:
        user = await user_repo.create_user(db, test_email, "Pass123!")
        
        # CREATE Location
        loc = await location_repo.get_or_create(db, "Bengaluru", 12.9716, 77.5946, "India")
        assert loc.id is not None

        # READ Location
        read_loc = await location_repo.get_by_coords(db, 12.9716, 77.5946)
        assert read_loc is not None
        assert read_loc.id == loc.id

        # CREATE SavedLocation
        saved = await saved_location_repo.create(db, {
            "user_id": user.id,
            "location_id": loc.id,
            "custom_alias": "Home Base",
            "is_favorite": True
        })
        assert saved.id is not None

        # READ SavedLocation
        user_saved = await saved_location_repo.get_by_user(db, user.id)
        assert len(user_saved) == 1
        assert user_saved[0].custom_alias == "Home Base"

        # UPDATE SavedLocation
        updated_saved = await saved_location_repo.update(db, saved.id, {"custom_alias": "HQ Bengaluru"})
        assert updated_saved.custom_alias == "HQ Bengaluru"

        # DELETE SavedLocation
        assert await saved_location_repo.delete(db, saved.id) is True
        assert await user_repo.delete(db, user.id) is True

@pytest.mark.asyncio
async def test_crud_weather_observations_and_advisories():
    """Test CRUD operations for WeatherObservation and linked Advisory records."""
    async with AsyncSessionLocal() as db:
        loc = await location_repo.get_or_create(db, "Chennai", 13.0827, 80.2707, "India")

        # CREATE WeatherObservation
        obs = await weather_obs_repo.create(db, {
            "location_id": loc.id,
            "temperature": 34.2,
            "apparent_temperature": 38.0,
            "humidity": 82.0,
            "surface_pressure": 1008.5,
            "wind_speed": 18.0,
            "wind_direction": 90.0,
            "weather_code": 61,
            "condition_text": "Slight rain",
            "data_source": "Open-Meteo"
        })
        assert obs.id is not None

        # CREATE Advisory linked to Observation
        adv = await advisory_repo.create(db, {
            "observation_id": obs.id,
            "advisory_type": "umbrella",
            "advisory_text": "Carry an umbrella due to rain in Chennai",
            "risk_level": "MEDIUM"
        })
        assert adv.id is not None

        # READ WeatherObservation & Advisory
        latest_obs = await weather_obs_repo.get_latest_for_location(db, loc.id)
        assert latest_obs is not None
        assert latest_obs.temperature == 34.2

        fetched_adv = await advisory_repo.get_by_id(db, adv.id)
        assert fetched_adv is not None
        assert fetched_adv.risk_level == "MEDIUM"

        # UPDATE WeatherObservation
        updated_obs = await weather_obs_repo.update(db, obs.id, {"temperature": 35.0})
        assert updated_obs.temperature == 35.0

        # DELETE (Cascades advisory deletion)
        assert await weather_obs_repo.delete(db, obs.id) is True

@pytest.mark.asyncio
async def test_crud_forecasts_and_alerts():
    """Test CRUD operations for Forecast and SevereAlert entities."""
    async with AsyncSessionLocal() as db:
        loc = await location_repo.get_or_create(db, "Mumbai", 19.0760, 72.8777, "India")

        # CREATE Forecast
        forecast = await forecast_repo.create(db, {
            "location_id": loc.id,
            "forecast_date": "2026-09-13",
            "temp_max": 31.5,
            "temp_min": 26.0,
            "precipitation_sum": 12.4,
            "precipitation_probability": 80.0,
            "weather_code": 63,
            "condition_text": "Moderate rain",
            "data_source": "XGBoost_Forecaster"
        })
        assert forecast.id is not None

        # READ Forecast
        loc_forecasts = await forecast_repo.get_forecasts_for_location(db, loc.id)
        assert len(loc_forecasts) >= 1

        # CREATE SevereAlert
        alert_id = f"alert-mumbai-{uuid.uuid4().hex[:6]}"
        alert = await alert_repo.create(db, {
            "id": alert_id,
            "event": "Heavy Rainfall Warning",
            "severity": "HIGH",
            "headline": "Heavy rainfall expected over Mumbai coast",
            "description": "Precipitation exceeding 50mm expected.",
            "instruction": "Avoid low lying areas.",
            "source": "IMD (Official)",
            "issued_at": "2026-09-12T12:00:00Z",
            "is_official_warning": True,
            "latitude_min": 18.5,
            "latitude_max": 19.5,
            "longitude_min": 72.5,
            "longitude_max": 73.5
        })
        assert alert.id == alert_id

        # READ Active Alerts for area
        active = await alert_repo.get_active_alerts_for_area(db, 19.0760, 72.8777)
        assert len(active) >= 1

        # UPDATE & DELETE
        assert await forecast_repo.delete(db, forecast.id) is True
        assert await alert_repo.delete(db, alert_id) is True

@pytest.mark.asyncio
async def test_crud_chat_sessions_messages_and_climate():
    """Test CRUD operations for Chat Sessions, Chat Messages, and Climate History."""
    async with AsyncSessionLocal() as db:
        # CREATE Chat Session & Messages
        session = await chat_repo.create_chat_session(db, title="Mumbai Rain Safety Query")
        assert session.id is not None

        msg1 = await chat_repo.add_message(db, session.id, "user", "Will it rain in Mumbai tomorrow?", "Heavy rain expected", "forecast")
        assert msg1.id is not None

        # READ Session Messages
        fetched_session = await chat_repo.get_by_id(db, session.id)
        assert fetched_session is not None

        # CREATE Climate History
        climate = await climate_repo.create(db, {
            "location_name": "Mumbai",
            "month": 9,
            "baseline_avg_temp": 27.5,
            "baseline_precip_mm": 340.0,
            "baseline_period": "1991-2020 WMO Baseline",
            "anomaly_temp": 1.2
        })
        assert climate.id is not None

        # READ Climate
        fetched_climate = await climate_repo.get_climate_baseline(db, "Mumbai", 9)
        assert fetched_climate is not None

        # DELETE Session (Cascades messages)
        assert await chat_repo.delete(db, session.id) is True
        assert await climate_repo.delete(db, climate.id) is True

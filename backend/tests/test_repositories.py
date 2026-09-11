import pytest
import pytest_asyncio
from app.core.database import engine, Base, AsyncSessionLocal
from app.repositories import (
    user_repo, location_repo, weather_obs_repo, forecast_repo,
    alert_repo, saved_location_repo, chat_repo, climate_repo, advisory_repo
)


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_user_repository_crud():
    async with AsyncSessionLocal() as db:
        user = await user_repo.create_user(db, "testuser@weathergpt.ai", "SecretPass123!", "Test User")
        assert user.id is not None
        assert user.email == "testuser@weathergpt.ai"

        fetched = await user_repo.get_by_email(db, "testuser@weathergpt.ai")
        assert fetched is not None
        assert fetched.id == user.id

        auth_success = await user_repo.authenticate(db, "testuser@weathergpt.ai", "SecretPass123!")
        assert auth_success is not None

        auth_fail = await user_repo.authenticate(db, "testuser@weathergpt.ai", "WrongPass")
        assert auth_fail is None


@pytest.mark.asyncio
async def test_location_and_observation_repositories():
    async with AsyncSessionLocal() as db:
        loc = await location_repo.get_or_create(db, "Coimbatore", 11.0168, 76.9558, "India")
        assert loc.id is not None
        assert loc.name == "Coimbatore"

        obs = await weather_obs_repo.create(db, {
            "location_id": loc.id,
            "temperature": 28.5,
            "apparent_temperature": 30.0,
            "humidity": 75.0,
            "surface_pressure": 1012.0,
            "wind_speed": 12.0,
            "wind_direction": 180.0,
            "weather_code": 0,
            "condition_text": "Clear sky",
            "data_source": "Open-Meteo"
        })
        assert obs.id is not None

        latest = await weather_obs_repo.get_latest_for_location(db, loc.id)
        assert latest is not None
        assert latest.temperature == 28.5


@pytest.mark.asyncio
async def test_chat_repository_and_messages():
    async with AsyncSessionLocal() as db:
        user = await user_repo.create_user(db, "chatuser@weathergpt.ai", "Pass12345!")
        session = await chat_repo.create_chat_session(db, user_id=user.id, title="Rain Forecast")
        assert session.id is not None

        msg = await chat_repo.add_message(
            db, session.id, "user", "Will it rain in Coimbatore today?", "Carry an umbrella", "umbrella"
        )
        assert msg.id is not None
        assert msg.session_id == session.id


@pytest.mark.asyncio
async def test_saved_location_repository():
    async with AsyncSessionLocal() as db:
        user = await user_repo.create_user(db, "favuser@weathergpt.ai", "Pass12345!")
        loc = await location_repo.get_or_create(db, "Tokyo", 35.6762, 139.6503, "Japan")

        saved = await saved_location_repo.create(db, {
            "user_id": user.id,
            "location_id": loc.id,
            "custom_alias": "My Tokyo Trip",
            "is_favorite": True
        })
        assert saved.id is not None

        user_favs = await saved_location_repo.get_by_user(db, user.id)
        assert len(user_favs) == 1
        assert user_favs[0].custom_alias == "My Tokyo Trip"

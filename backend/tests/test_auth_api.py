import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_user_registration_and_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register User
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": "apiuser@weathergpt.ai",
            "password": "SecurePassword123!",
            "full_name": "API Tester"
        })
        assert reg_res.status_code == 201
        data = reg_res.json()
        assert data["email"] == "apiuser@weathergpt.ai"

        # 2. Login
        login_res = await client.post("/api/v1/auth/login", json={
            "email": "apiuser@weathergpt.ai",
            "password": "SecurePassword123!"
        })
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # 3. Get /me Profile
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "apiuser@weathergpt.ai"


@pytest.mark.asyncio
async def test_unauthorized_access_rejection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/api/v1/auth/me")
        assert res.status_code == 401

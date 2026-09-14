import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_chat_api_endpoint_all_questions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        questions = [
            "What's the weather now?",
            "Will it rain tomorrow?",
            "Will it rain tomorrow evening in Coimbatore?",
            "I need to travel tomorrow at 7 AM. What weather should I expect?",
            "Is there any severe weather warning?",
            "What should I do during heavy rainfall?",
            "Show me the 5-day forecast."
        ]

        for q in questions:
            resp = await client.post("/api/v1/chat", json={
                "query": q,
                "location_name": "Coimbatore, India",
                "latitude": 11.0168,
                "longitude": 76.9558
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["query"] == q
            assert len(data["answer"]) > 0
            assert "grounded_facts" in data
            assert "ai_recommendations" in data

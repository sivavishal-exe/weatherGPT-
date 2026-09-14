import pytest
from app.schemas.chat import ChatRequest
from app.services.llm_service import llm_service
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_question_1_whats_the_weather_now():
    """Query 1: What's the weather now?"""
    req = ChatRequest(query="What's the weather now?", location_name="Coimbatore, India")
    res = await llm_service.process_chat(req)
    
    assert res.query == req.query
    assert "Weather Intelligence" in res.answer
    assert "Coimbatore" in res.answer or "Current Weather" in res.answer
    assert len(res.grounded_facts) > 0
    assert any(fact.fact_type == "CURRENT_WEATHER" for fact in res.grounded_facts)
    assert len(res.ai_recommendations) > 0


@pytest.mark.asyncio
async def test_question_2_will_it_rain_tomorrow():
    """Query 2: Will it rain tomorrow?"""
    req = ChatRequest(query="Will it rain tomorrow?")
    res = await llm_service.process_chat(req)
    
    assert "Rainfall Status" in res.answer
    assert "% chance" in res.answer or "Rain" in res.answer
    assert len(res.grounded_facts) > 0
    assert any(fact.fact_type == "FORECAST_METRICS" for fact in res.grounded_facts)


@pytest.mark.asyncio
async def test_question_3_will_it_rain_tomorrow_evening_in_coimbatore():
    """Query 3: Will it rain tomorrow evening in Coimbatore?"""
    req = ChatRequest(query="Will it rain tomorrow evening in Coimbatore?")
    res = await llm_service.process_chat(req)
    
    assert "Coimbatore" in res.answer
    assert "Rainfall Status" in res.answer
    assert "Evening" in res.answer
    assert len(res.grounded_facts) > 0


@pytest.mark.asyncio
async def test_question_4_travel_tomorrow_7am():
    """Query 4: I need to travel tomorrow at 7 AM. What weather should I expect?"""
    req = ChatRequest(query="I need to travel tomorrow at 7 AM. What weather should I expect?")
    res = await llm_service.process_chat(req)
    
    assert "Travel Forecast" in res.answer
    assert "Morning" in res.answer or "7 AM" in res.answer
    assert len(res.ai_recommendations) > 0
    assert any("travel" in rec.lower() for rec in res.ai_recommendations)


@pytest.mark.asyncio
async def test_question_5_severe_weather_warning():
    """Query 5: Is there any severe weather warning?"""
    req = ChatRequest(query="Is there any severe weather warning?")
    res = await llm_service.process_chat(req)
    
    assert "Severe" in res.answer or "Warning" in res.answer or "Status" in res.answer
    assert len(res.ai_recommendations) > 0


@pytest.mark.asyncio
async def test_question_6_heavy_rainfall_advisory():
    """Query 6: What should I do during heavy rainfall?"""
    req = ChatRequest(query="What should I do during heavy rainfall?")
    res = await llm_service.process_chat(req)
    
    assert "Safety Advisory" in res.answer or "Guidelines" in res.answer
    assert "Indoors" in res.answer or "Flood" in res.answer
    assert any("heavy rainfall safety" in rec.lower() for rec in res.ai_recommendations)


@pytest.mark.asyncio
async def test_question_7_5_day_forecast():
    """Query 7: Show me the 5-day forecast."""
    req = ChatRequest(query="Show me the 5-day forecast.")
    res = await llm_service.process_chat(req)
    
    assert "5-Day Forecast" in res.answer
    assert len(res.grounded_facts) > 0


@pytest.mark.asyncio
async def test_critical_rule_weather_service_failure_communication():
    """CRITICAL RULE: Weather service failure must be clearly communicated without invented data."""
    req = ChatRequest(query="What's the weather now?")
    with patch("app.services.llm_service.weather_provider.get_weather", side_effect=Exception("API connection timeout")):
        res = await llm_service.process_chat(req)
        assert "unavailable" in res.answer.lower()
        assert len(res.grounded_facts) == 0  # No invented facts when service fails!

import pytest
from app.schemas.chat import ChatRequest
from app.services.llm_service import llm_service


@pytest.mark.asyncio
async def test_grounded_llm_chat():
    req = ChatRequest(query="What is the weather in London today?", location_name="London")
    res = await llm_service.process_chat(req)
    
    assert res.query == req.query
    assert "London" in res.answer or "Weather Intelligence" in res.answer
    assert len(res.grounded_facts) > 0
    assert res.grounded_facts[0].source is not None
    # Check strict requirement: AI recommendations are present and distinct
    assert len(res.ai_recommendations) > 0
    assert any("AI Advisory:" in rec for rec in res.ai_recommendations)

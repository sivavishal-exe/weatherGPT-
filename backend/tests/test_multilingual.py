import pytest
from app.schemas.chat import ChatRequest
from app.services.llm_service import llm_service
from unittest.mock import patch


LANGUAGES = [
    ("en", "English", "Weather Intelligence"),
    ("hi", "Hindi", "मौसम बुद्धिमत्ता"),
    ("ta", "Tamil", "வானிலை நுண்ணறிவு"),
    ("ja", "Japanese", "気象インテリジェンス"),
    ("es", "Spanish", "Inteligencia Meteorológica"),
    ("fr", "French", "Intelligence Météorologique"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code,lang_name,expected_keyword", LANGUAGES)
async def test_multilingual_chat_responses(lang_code, lang_name, expected_keyword):
    """Verify AI responses for all 6 supported languages."""
    req = ChatRequest(query="What's the weather now?", location_name="Coimbatore", language=lang_code)
    res = await llm_service.process_chat(req)

    assert res.language == lang_code
    assert expected_keyword in res.answer
    assert len(res.ai_recommendations) > 0
    assert len(res.grounded_facts) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code,lang_name,expected_keyword", LANGUAGES)
async def test_multilingual_rain_and_umbrella_advice(lang_code, lang_name, expected_keyword):
    """Verify rain & umbrella advisory responses across languages."""
    req = ChatRequest(query="Will it rain tomorrow?", location_name="Coimbatore", language=lang_code)
    res = await llm_service.process_chat(req)

    assert res.language == lang_code
    assert expected_keyword in res.answer
    assert len(res.ai_recommendations) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code,lang_name,expected_keyword", LANGUAGES)
async def test_multilingual_heavy_rain_safety_advisory(lang_code, lang_name, expected_keyword):
    """Verify heavy rainfall safety protocol across all languages."""
    req = ChatRequest(query="What should I do during heavy rainfall?", language=lang_code)
    res = await llm_service.process_chat(req)

    assert res.language == lang_code
    assert expected_keyword in res.answer


@pytest.mark.asyncio
@pytest.mark.parametrize("lang_code,lang_name,expected_keyword", LANGUAGES)
async def test_multilingual_outage_error_communication(lang_code, lang_name, expected_keyword):
    """Verify network outage error message is returned in the requested language."""
    req = ChatRequest(query="What's the weather now?", language=lang_code)
    with patch("app.services.llm_service.weather_provider.get_weather", side_effect=Exception("Outage")):
        res = await llm_service.process_chat(req)
        assert res.language == lang_code
        assert len(res.answer) > 0
        assert len(res.grounded_facts) == 0  # Zero hallucinated facts

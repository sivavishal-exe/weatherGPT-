from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.core.security import sanitize_input_text

router = APIRouter(prefix="/chat", tags=["Conversational WeatherGPT"])


@APIRouter.post(router, "", response_model=ChatResponse)
async def chat_weather_gpt(request: ChatRequest):
    """
    Conversational AI Weather Intelligence.
    Guaranteed zero hallucination of weather data: all facts are fetched directly from trusted weather services.
    Official warnings and AI advisories are explicitly separated.
    """
    request.query = sanitize_input_text(request.query)
    if request.location_name:
        request.location_name = sanitize_input_text(request.location_name)

    response = await llm_service.process_chat(request)
    return response

from typing import Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from app.services.voice_service import voice_service

router = APIRouter(prefix="/voice", tags=["Voice & Multilingual Interaction"])


class VoiceQueryPayload(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio payload")
    audio_format: str = Field("wav", description="Audio format e.g. wav, mp3, m4a")
    language: str = Field("en", description="Target ISO language code")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    low_bandwidth: bool = False


@APIRouter.post(router, "")
async def process_voice(payload: VoiceQueryPayload):
    """
    Processes audio voice queries: performs Speech-to-Text, executes grounded WeatherGPT chat,
    and returns synthesized audio payload options.
    """
    res = await voice_service.process_voice_query(
        audio_base64=payload.audio_base64,
        audio_format=payload.audio_format,
        language=payload.language,
        latitude=payload.latitude,
        longitude=payload.longitude,
        low_bandwidth=payload.low_bandwidth
    )
    return res

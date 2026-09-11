from fastapi import APIRouter
from app.api.v1 import weather, forecast, chat, alerts, climate, location, advisory, voice, auth

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(weather.router)
api_router.include_router(forecast.router)
api_router.include_router(chat.router)
api_router.include_router(alerts.router)
api_router.include_router(climate.router)
api_router.include_router(location.router)
api_router.include_router(advisory.router)
api_router.include_router(voice.router)

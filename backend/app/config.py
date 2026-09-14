from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings loaded from environment variables.
    Never hardcode secrets, tokens, or API keys in source files.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "WeatherGPT Intelligence Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Security Secrets
    SECRET_KEY: str = "dev-secret-key-change-in-production-weathergpt-2026"
    ADMIN_SECRET_KEY: str = "admin-secret-key-weathergpt-2026"
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    # Persistent Storage (SQLite for dev/test fallback, PostgreSQL/PostGIS for prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./weathergpt.db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Caching (Redis URL, fallback to memory cache if unavailable)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 600  # 10 minutes cache for weather facts
    
    # Weather Provider APIs (Open-Meteo doesn't require API key; OpenWeather optional)
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    NOAA_ALERTS_BASE_URL: str = "https://api.weather.gov"
    OPENWEATHER_API_KEY: Optional[str] = None
    VISUAL_CROSSING_API_KEY: Optional[str] = None
    
    # Conversational Intelligence / LLM
    LLM_PROVIDER: str = "grounded-weathergpt"  # 'grounded-weathergpt', 'openai', or 'gemini'
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    
    # Rate Limiting & Low Bandwidth Config
    RATE_LIMIT_PER_MINUTE: int = 60
    DEFAULT_FORECAST_DAYS: int = 7
    LOW_BANDWIDTH_FORECAST_DAYS: int = 3


settings = Settings()

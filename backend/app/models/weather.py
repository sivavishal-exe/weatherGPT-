import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class UserRecord(Base):
    """Registered application user entity."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    saved_locations = relationship("SavedLocationRecord", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSessionRecord", back_populates="user", cascade="all, delete-orphan")


class LocationRecord(Base):
    """Geographic location entity with coordinates and PostGIS / metadata fallback."""
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(250), nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    country = Column(String(100), nullable=True, default="Unknown")
    state = Column(String(100), nullable=True)
    timezone = Column(String(100), default="UTC", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    observations = relationship("WeatherObservationRecord", back_populates="location", cascade="all, delete-orphan")
    forecasts = relationship("ForecastRecord", back_populates="location", cascade="all, delete-orphan")
    saved_by = relationship("SavedLocationRecord", back_populates="location", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_location_lat_lon", "latitude", "longitude"),
    )


class WeatherObservationRecord(Base):
    """Historical & current meteorological observations."""
    __tablename__ = "weather_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    apparent_temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    surface_pressure = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Float, nullable=False)
    weather_code = Column(Integer, nullable=False)
    condition_text = Column(String(250), nullable=False)
    data_source = Column(String(100), default="Open-Meteo", nullable=False)
    observed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    location = relationship("LocationRecord", back_populates="observations")
    advisories = relationship("AdvisoryRecord", back_populates="observation", cascade="all, delete-orphan")


class ForecastRecord(Base):
    """Daily meteorological forecasts & XGBoost forecaster results."""
    __tablename__ = "forecast_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_date = Column(String(20), nullable=False, index=True)
    temp_max = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    precipitation_sum = Column(Float, default=0.0, nullable=False)
    precipitation_probability = Column(Float, default=0.0, nullable=False)
    weather_code = Column(Integer, nullable=False)
    condition_text = Column(String(250), nullable=False)
    data_source = Column(String(100), default="XGBoost_Forecaster", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    location = relationship("LocationRecord", back_populates="forecasts")

    __table_args__ = (
        Index("idx_forecast_loc_date", "location_id", "forecast_date"),
    )


class SevereAlertRecord(Base):
    """Official weather warnings and severe weather alerts."""
    __tablename__ = "severe_alerts"

    id = Column(String(250), primary_key=True, index=True)
    event = Column(String(250), nullable=False)
    severity = Column(String(50), nullable=False, index=True)
    headline = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    instruction = Column(Text, nullable=True)
    source = Column(String(250), nullable=False)
    issued_at = Column(String(100), nullable=False)
    expires_at = Column(String(100), nullable=True)
    is_official_warning = Column(Boolean, default=True, nullable=False)
    latitude_min = Column(Float, default=-90.0, nullable=False)
    latitude_max = Column(Float, default=90.0, nullable=False)
    longitude_min = Column(Float, default=-180.0, nullable=False)
    longitude_max = Column(Float, default=180.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


AlertRecord = SevereAlertRecord


class SavedLocationRecord(Base):
    """User saved/favorite locations."""
    __tablename__ = "saved_locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    custom_alias = Column(String(250), nullable=True)
    is_favorite = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    user = relationship("UserRecord", back_populates="saved_locations")
    location = relationship("LocationRecord", back_populates="saved_by")


class ChatSessionRecord(Base):
    """Conversational AI chat session container."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(250), default="Weather Query", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("UserRecord", back_populates="chat_sessions")
    messages = relationship("ChatMessageRecord", back_populates="session", cascade="all, delete-orphan")


class ChatMessageRecord(Base):
    """Individual messages inside a chat session."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(50), nullable=False)  # 'user' or 'assistant'
    query = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    intent = Column(String(100), default="current", nullable=False)
    grounded_facts_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    session = relationship("ChatSessionRecord", back_populates="messages")


class ModelMetadataRecord(Base):
    """Metadata registry for fine-tuned WeatherGPT LLM and XGBoost forecaster models."""
    __tablename__ = "model_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    model_name = Column(String(250), nullable=False, index=True)
    model_type = Column(String(100), nullable=False)  # 'LLM_QLoRA' or 'Time_Series_XGBoost'
    model_version = Column(String(50), nullable=False)
    adapter_path = Column(String(500), nullable=True)
    hyperparameters_json = Column(Text, nullable=True)
    performance_metrics_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class WeatherCacheRecord(Base):
    """Redis / PostgreSQL fallback cache table."""
    __tablename__ = "weather_cache"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cache_key = Column(String(250), unique=True, index=True, nullable=False)
    payload_json = Column(Text, nullable=False)
    created_at = Column(Float, default=lambda: datetime.now(timezone.utc).timestamp())
    expires_at = Column(Float, nullable=False)


class ClimateHistoryRecord(Base):
    """30-year climate baseline statistics."""
    __tablename__ = "climate_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(250), nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    baseline_avg_temp = Column(Float, nullable=False)
    baseline_precip_mm = Column(Float, nullable=False)
    baseline_period = Column(String(100), default="1991-2020 WMO Baseline", nullable=False)
    anomaly_temp = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


ClimateDataRecord = ClimateHistoryRecord


class AdvisoryRecord(Base):
    """AI Safety & localized advisories."""
    __tablename__ = "advisories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    observation_id = Column(String(36), ForeignKey("weather_observations.id", ondelete="CASCADE"), nullable=True, index=True)
    advisory_type = Column(String(100), nullable=False, index=True)  # umbrella, travel, thermal, severe
    advisory_text = Column(Text, nullable=False)
    risk_level = Column(String(50), default="LOW", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    observation = relationship("WeatherObservationRecord", back_populates="advisories")

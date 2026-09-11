from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from app.repositories.base import BaseRepository
from app.models.weather import (
    UserRecord,
    LocationRecord,
    WeatherObservationRecord,
    ForecastRecord,
    SevereAlertRecord,
    SavedLocationRecord,
    ChatSessionRecord,
    ChatMessageRecord,
    ClimateHistoryRecord,
    AdvisoryRecord
)
from app.core.security import hash_password, verify_password, sanitize_input_text


class UserRepository(BaseRepository[UserRecord]):
    def __init__(self):
        super().__init__(UserRecord)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[UserRecord]:
        clean_email = sanitize_input_text(email).lower()
        result = await db.execute(select(UserRecord).where(UserRecord.email == clean_email))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, email: str, password: str, full_name: Optional[str] = None) -> UserRecord:
        clean_email = sanitize_input_text(email).lower()
        hashed_pwd = hash_password(password)
        user_data = {
            "email": clean_email,
            "hashed_password": hashed_pwd,
            "full_name": sanitize_input_text(full_name) if full_name else None,
            "is_active": True,
            "is_superuser": False
        }
        return await self.create(db, user_data)

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> Optional[UserRecord]:
        user = await self.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


class LocationRepository(BaseRepository[LocationRecord]):
    def __init__(self):
        super().__init__(LocationRecord)

    async def get_by_coords(self, db: AsyncSession, lat: float, lon: float, tolerance: float = 0.05) -> Optional[LocationRecord]:
        result = await db.execute(
            select(LocationRecord).where(
                and_(
                    LocationRecord.latitude >= lat - tolerance,
                    LocationRecord.latitude <= lat + tolerance,
                    LocationRecord.longitude >= lon - tolerance,
                    LocationRecord.longitude <= lon + tolerance
                )
            )
        )
        return result.scalars().first()

    async def get_or_create(self, db: AsyncSession, name: str, lat: float, lon: float, country: str = "Unknown") -> LocationRecord:
        existing = await self.get_by_coords(db, lat, lon)
        if existing:
            return existing
        loc_data = {
            "name": sanitize_input_text(name),
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "country": sanitize_input_text(country),
            "timezone": "UTC"
        }
        return await self.create(db, loc_data)


class WeatherObservationRepository(BaseRepository[WeatherObservationRecord]):
    def __init__(self):
        super().__init__(WeatherObservationRecord)

    async def get_latest_for_location(self, db: AsyncSession, location_id: int) -> Optional[WeatherObservationRecord]:
        result = await db.execute(
            select(WeatherObservationRecord)
            .where(WeatherObservationRecord.location_id == location_id)
            .order_by(WeatherObservationRecord.observed_at.desc())
            .limit(1)
        )
        return result.scalars().first()


class ForecastRepository(BaseRepository[ForecastRecord]):
    def __init__(self):
        super().__init__(ForecastRecord)

    async def get_forecasts_for_location(self, db: AsyncSession, location_id: int) -> List[ForecastRecord]:
        result = await db.execute(
            select(ForecastRecord)
            .where(ForecastRecord.location_id == location_id)
            .order_by(ForecastRecord.forecast_date.asc())
        )
        return list(result.scalars().all())


class AlertRepository(BaseRepository[SevereAlertRecord]):
    def __init__(self):
        super().__init__(SevereAlertRecord)

    async def get_active_alerts_for_area(
        self, db: AsyncSession, lat: float, lon: float
    ) -> List[SevereAlertRecord]:
        result = await db.execute(
            select(SevereAlertRecord).where(
                and_(
                    SevereAlertRecord.latitude_min <= lat,
                    SevereAlertRecord.latitude_max >= lat,
                    SevereAlertRecord.longitude_min <= lon,
                    SevereAlertRecord.longitude_max >= lon
                )
            )
        )
        return list(result.scalars().all())


class SavedLocationRepository(BaseRepository[SavedLocationRecord]):
    def __init__(self):
        super().__init__(SavedLocationRecord)

    async def get_by_user(self, db: AsyncSession, user_id: str) -> List[SavedLocationRecord]:
        result = await db.execute(
            select(SavedLocationRecord).where(SavedLocationRecord.user_id == user_id)
        )
        return list(result.scalars().all())


class ChatRepository(BaseRepository[ChatSessionRecord]):
    def __init__(self):
        super().__init__(ChatSessionRecord)

    async def create_chat_session(self, db: AsyncSession, user_id: Optional[str] = None, title: str = "Weather Query") -> ChatSessionRecord:
        data = {
            "user_id": user_id,
            "title": sanitize_input_text(title)
        }
        return await self.create(db, data)

    async def add_message(
        self, db: AsyncSession, session_id: str, sender: str, query: str, response_text: str, intent: str = "current"
    ) -> ChatMessageRecord:
        msg = ChatMessageRecord(
            session_id=session_id,
            sender=sender,
            query=sanitize_input_text(query),
            response_text=response_text,
            intent=intent
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg


class ClimateRepository(BaseRepository[ClimateHistoryRecord]):
    def __init__(self):
        super().__init__(ClimateHistoryRecord)

    async def get_climate_baseline(self, db: AsyncSession, location_name: str, month: int) -> Optional[ClimateHistoryRecord]:
        clean_loc = sanitize_input_text(location_name).lower()
        result = await db.execute(
            select(ClimateHistoryRecord).where(
                and_(
                    ClimateHistoryRecord.location_name.ilike(f"%{clean_loc}%"),
                    ClimateHistoryRecord.month == month
                )
            )
        )
        return result.scalars().first()


class AdvisoryRepository(BaseRepository[AdvisoryRecord]):
    def __init__(self):
        super().__init__(AdvisoryRecord)


# Singleton Instances
user_repo = UserRepository()
location_repo = LocationRepository()
weather_obs_repo = WeatherObservationRepository()
forecast_repo = ForecastRepository()
alert_repo = AlertRepository()
saved_location_repo = SavedLocationRepository()
chat_repo = ChatRepository()
climate_repo = ClimateRepository()
advisory_repo = AdvisoryRepository()

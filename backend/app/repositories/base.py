from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.core.database import Base
from app.core.logging import logger

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic Base Repository enforcing parameterized ORM queries, safe transactions, and error handling."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id_val: Any) -> Optional[ModelType]:
        try:
            result = await db.execute(select(self.model).where(self.model.id == id_val))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Error fetching {self.model.__tablename__} by id {id_val}: {e}")
            raise e

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            result = await db.execute(select(self.model).offset(skip).limit(limit))
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error fetching all {self.model.__tablename__}: {e}")
            raise e

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating {self.model.__tablename__}: {e}")
            raise e

    async def update(self, db: AsyncSession, db_obj_or_id: Any, obj_in: dict) -> Optional[ModelType]:
        try:
            if isinstance(db_obj_or_id, (str, int)):
                db_obj = await self.get_by_id(db, db_obj_or_id)
            else:
                db_obj = db_obj_or_id

            if not db_obj:
                return None

            for field, value in obj_in.items():
                if hasattr(db_obj, field) and value is not None:
                    setattr(db_obj, field, value)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating {self.model.__tablename__}: {e}")
            raise e

    async def delete(self, db: AsyncSession, id_val: Any) -> bool:
        try:
            db_obj = await self.get_by_id(db, id_val)
            if db_obj:
                await db.delete(db_obj)
                await db.commit()
                return True
            return False
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting {self.model.__tablename__} id {id_val}: {e}")
            raise e

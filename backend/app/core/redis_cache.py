import json
import time
from typing import Any, Optional
from app.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class InMemoryCache:
    """In-memory TTL cache fallback when Redis is not running or unavailable."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            val, expiry = self._store[key]
            if expiry == 0 or time.time() < expiry:
                return val
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 600):
        expiry = time.time() + ttl if ttl > 0 else 0
        self._store[key] = (value, expiry)

    def delete(self, key: str):
        self._store.pop(key, None)

    def clear(self):
        self._store.clear()


class CacheManager:
    """Unified cache interface with Redis backend and In-Memory fallback."""

    def __init__(self):
        self._memory_cache = InMemoryCache()
        self._redis_client: Optional[Any] = None
        self._use_redis = False

    async def connect(self):
        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1.0
                )
                await self._redis_client.ping()
                self._use_redis = True
                logger.info("Successfully connected to Redis server.")
            except Exception as e:
                logger.warning(f"Redis connection failed ({e}). Falling back to In-Memory cache.")
                self._use_redis = False
        else:
            logger.info("Using In-Memory cache engine.")

    async def get_json(self, key: str) -> Optional[dict]:
        try:
            if self._use_redis and self._redis_client:
                data = await self._redis_client.get(key)
                return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get failed: {e}. Checking memory fallback.")

        raw = self._memory_cache.get(key)
        if raw and isinstance(raw, str):
            try:
                return json.loads(raw)
            except Exception:
                return None
        return raw if isinstance(raw, dict) else None

    async def set_json(self, key: str, value: dict, ttl: int = 600):
        raw = json.dumps(value)
        self._memory_cache.set(key, raw, ttl=ttl)
        if self._use_redis and self._redis_client:
            try:
                await self._redis_client.set(key, raw, ex=ttl)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

    async def delete(self, key: str):
        self._memory_cache.delete(key)
        if self._use_redis and self._redis_client:
            try:
                await self._redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

    async def close(self):
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception:
                pass


cache = CacheManager()

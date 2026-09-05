from __future__ import annotations

from typing import Any, TypeVar

from app.cache.redis import get_redis
from app.cache.serialization import deserialize_json, serialize_json
from app.core.config import settings
from app.core.logging import logger

T = TypeVar("T")


class CacheService:
    """
    Centralized caching abstraction providing:
    - Safe JSON serialization/deserialization.
    - Non-blocking SCAN-based pattern invalidation.
    - Graceful degradation on Redis connection failure or timeouts.
    - Configurable TTLs per domain.
    """

    @staticmethod
    async def get(key: str) -> str | None:
        """Fetch raw string value from Redis cache."""
        if not settings.CACHE_ENABLED:
            return None
        try:
            client = await get_redis()
            if client is None:
                return None
            return await client.get(key)
        except Exception as e:
            logger.warning("Cache GET failed for key '%s': %s", key, e)
            return None

    @staticmethod
    async def set(key: str, value: str, ttl: int | None = None) -> bool:
        """Store raw string value in Redis with optional TTL."""
        if not settings.CACHE_ENABLED:
            return False
        try:
            client = await get_redis()
            if client is None:
                return False
            if ttl is not None and ttl > 0:
                await client.set(key, value, ex=ttl)
            else:
                await client.set(key, value)
            return True
        except Exception as e:
            logger.warning("Cache SET failed for key '%s': %s", key, e)
            return False

    @classmethod
    async def get_json(cls, key: str, target_cls: type[T] | None = None) -> Any:
        """Fetch and deserialize JSON payload from Redis."""
        raw = await cls.get(key)
        if raw is None:
            return None
        try:
            return deserialize_json(raw, target_cls=target_cls)
        except Exception as e:
            logger.warning("Cache deserialization failed for key '%s': %s", key, e)
            return None

    @classmethod
    async def set_json(cls, key: str, value: Any, ttl: int | None = None) -> bool:
        """Serialize data to JSON and store in Redis."""
        try:
            payload = serialize_json(value)
            return await cls.set(key, payload, ttl=ttl)
        except Exception as e:
            logger.warning("Cache serialization failed for key '%s': %s", key, e)
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a single key from Redis."""
        try:
            client = await get_redis()
            if client is None:
                return False
            result = await client.delete(key)
            return bool(result > 0)
        except Exception as e:
            logger.warning("Cache DELETE failed for key '%s': %s", key, e)
            return False

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """
        Delete all keys matching a glob pattern using SCAN iteration.
        Prevents blocking the Redis main event loop on large keyspaces.
        """
        if not settings.CACHE_ENABLED:
            return 0
        deleted_count = 0
        try:
            client = await get_redis()
            if client is None:
                return 0

            # Iterative non-blocking SCAN
            keys_batch: list[str] = []
            async for k in client.scan_iter(match=pattern, count=100):
                keys_batch.append(k)
                if len(keys_batch) >= 100:
                    deleted = await client.unlink(*keys_batch)
                    deleted_count += deleted
                    keys_batch = []

            if keys_batch:
                deleted = await client.unlink(*keys_batch)
                deleted_count += deleted

            if deleted_count > 0:
                logger.info(
                    "Invalidated %d cache keys matching pattern '%s'", deleted_count, pattern
                )
        except Exception as e:
            logger.warning("Cache DELETE_PATTERN failed for pattern '%s': %s", pattern, e)
        return deleted_count

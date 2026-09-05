import asyncio
import time
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    """
    Get or initialize the shared async Redis client instance.
    Returns None if Redis cannot be reached, ensuring graceful degradation.
    """
    global redis_client
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if redis_client is not None:
        try:
            pool = getattr(redis_client, "connection_pool", None)
            if pool and getattr(pool, "_loop", None) is not None and pool._loop != current_loop:
                redis_client = None
        except Exception:
            redis_client = None

    if redis_client is None:
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
        except Exception as e:
            logger.warning("Failed to initialize Redis client: %s", e)
            return None
    return redis_client


async def close_redis_connection() -> None:
    """Close Redis connection pools on shutdown."""
    global redis_client
    if redis_client is not None:
        logger.info("Closing Redis connection pool...")
        try:
            await redis_client.aclose()
        except Exception as e:
            logger.warning("Error closing Redis connection: %s", e)
        finally:
            redis_client = None
        logger.info("Redis connection closed.")


async def check_redis_health() -> dict[str, Any]:
    """
    Verify Redis connectivity via PING.
    Distinguishes between healthy, degraded, and unavailable.
    """
    client: aioredis.Redis | None = None
    try:
        client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
        start_time = time.perf_counter()
        pong = await client.ping()
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if pong:
            return {
                "status": "healthy",
                "cache": "redis",
                "latency_ms": round(latency_ms, 2),
            }
        else:
            return {
                "status": "degraded",
                "cache": "redis",
                "error": "Redis did not respond with PONG",
            }
    except Exception as e:
        logger.warning("Redis health check failed (graceful degradation): %s", str(e))
        return {
            "status": "unavailable",
            "cache": "redis",
            "error": "Redis connection unreachable",
        }
    finally:
        if client is not None:
            try:
                await client.aclose()
            except Exception:
                pass

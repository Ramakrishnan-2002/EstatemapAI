import pytest
import redis.asyncio as aioredis


@pytest.mark.asyncio
async def test_redis_ping(redis_conn: aioredis.Redis):
    """Verify Redis server is reachable and responds to PING."""
    pong = await redis_conn.ping()
    assert pong is True


@pytest.mark.asyncio
async def test_redis_set_get_and_expiration(redis_conn: aioredis.Redis):
    """Verify standard caching operations: set, get, ttl, and delete."""
    test_key = "test:estatemap:healthcheck"
    test_val = "ok_value"

    await redis_conn.set(test_key, test_val, ex=10)
    retrieved = await redis_conn.get(test_key)
    assert retrieved == test_val

    ttl = await redis_conn.ttl(test_key)
    assert 0 < ttl <= 10

    await redis_conn.delete(test_key)
    assert await redis_conn.get(test_key) is None

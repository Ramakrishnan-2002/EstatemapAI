import datetime

import pytest

from app.cache.cache_service import CacheService
from app.cache.serialization import deserialize_json, serialize_json


@pytest.mark.asyncio
async def test_cache_service_set_get_json(redis_conn):
    """Test basic JSON serialization, cache write, and cache read."""
    payload = {"city": "Bangalore", "score": 94.5, "tags": ["metro", "park"]}
    key = "estatemap:test:v1:sample"

    # Set
    success = await CacheService.set_json(key, payload, ttl=60)
    assert success is True

    # Get
    cached = await CacheService.get_json(key)
    assert cached == payload


@pytest.mark.asyncio
async def test_cache_service_delete(redis_conn):
    """Test specific key deletion."""
    key = "estatemap:test:v1:delete_me"
    await CacheService.set_json(key, {"value": 123}, ttl=60)
    assert await CacheService.get_json(key) is not None

    deleted = await CacheService.delete(key)
    assert deleted is True
    assert await CacheService.get_json(key) is None


@pytest.mark.asyncio
async def test_cache_service_delete_pattern(redis_conn):
    """Test non-blocking pattern deletion using SCAN."""
    # Write multiple keys under different domains
    await CacheService.set_json("estatemap:map:v1:bounds:1", {"data": 1}, ttl=60)
    await CacheService.set_json("estatemap:map:v1:bounds:2", {"data": 2}, ttl=60)
    await CacheService.set_json("estatemap:ranking:v1:hash1", {"data": 3}, ttl=60)
    await CacheService.set_json("estatemap:route:v1:r1", {"data": 4}, ttl=60)

    # Invalidate only map and ranking
    del_count = await CacheService.delete_pattern("estatemap:map:v1:*")
    assert del_count == 2
    assert await CacheService.get_json("estatemap:map:v1:bounds:1") is None
    assert await CacheService.get_json("estatemap:map:v1:bounds:2") is None
    assert await CacheService.get_json("estatemap:ranking:v1:hash1") is not None
    assert await CacheService.get_json("estatemap:route:v1:r1") is not None


def test_safe_json_serialization():
    """Test safe JSON serializer with datetimes and primitives."""
    now = datetime.datetime.now(datetime.UTC)
    raw = {"time": now, "items": [1, 2, 3]}
    serialized = serialize_json(raw)
    deserialized = deserialize_json(serialized)

    assert deserialized["items"] == [1, 2, 3]
    assert isinstance(deserialized["time"], str)

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.cache.cache_service import CacheService


@pytest.mark.asyncio
async def test_cache_service_graceful_degradation_on_redis_failure():
    """CacheService must return default/None on Redis failure without throwing."""
    with patch("app.cache.cache_service.get_redis", return_value=None):
        # Read returns None safely
        val = await CacheService.get_json("estatemap:any:key")
        assert val is None

        # Write returns False safely
        success = await CacheService.set_json("estatemap:any:key", {"a": 1})
        assert success is False

        # Pattern delete returns 0 safely
        del_count = await CacheService.delete_pattern("estatemap:*")
        assert del_count == 0


@pytest.mark.asyncio
async def test_search_and_commute_degradation_when_redis_unavailable(async_client: AsyncClient):
    """Endpoints must continue serving responses (fail-open) when Redis is down."""
    with patch("app.cache.redis.get_redis", return_value=None):
        res = await async_client.get(
            "/api/v1/commute/route",
            params={
                "origin_lat": 12.9716,
                "origin_lng": 77.5946,
                "dest_lat": 12.9352,
                "dest_lng": 77.6245,
                "mode": "driving",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "distance_km" in data
        assert "duration_minutes" in data


@pytest.mark.asyncio
async def test_rate_limiter_fail_closed_behavior(async_client: AsyncClient):
    """When fail_open=False (e.g. auth), Redis unavailability must raise 429 safely."""
    with patch("app.core.rate_limit.get_redis", return_value=None):
        res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "Password123!"},
        )
        # With fail_open=False on auth, rate limiter rejects if Redis is down
        assert res.status_code == 429
        assert res.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"

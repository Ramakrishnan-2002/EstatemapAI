import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_rate_limiter_under_limit_allowed(async_client: AsyncClient):
    """Requests under limit must return 200 OK."""
    # Commute direct route endpoint has limit of settings.RATE_LIMIT_COMMUTE_REQUESTS
    for _ in range(5):
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


@pytest.mark.asyncio
async def test_rate_limiter_breach_returns_429(async_client: AsyncClient):
    """Exceeding request limit must return HTTP 429 with Retry-After header."""
    # Direct route limit is settings.RATE_LIMIT_COMMUTE_REQUESTS (default 30)
    # Perform requests until breach
    limit = settings.RATE_LIMIT_COMMUTE_REQUESTS
    got_429 = False

    for _ in range(limit + 5):
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
        if res.status_code == 429:
            got_429 = True
            assert "Retry-After" in res.headers
            assert int(res.headers["Retry-After"]) > 0
            body = res.json()
            assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
            assert "details" in body["error"]
            break

    assert got_429 is True


@pytest.mark.asyncio
async def test_rate_limiter_identity_isolation(async_client: AsyncClient):
    """Different client IPs must have independent rate limit buckets."""
    # Client A consumes requests
    for _ in range(3):
        res = await async_client.get(
            "/api/v1/commute/route",
            params={
                "origin_lat": 12.9716,
                "origin_lng": 77.5946,
                "dest_lat": 12.9352,
                "dest_lng": 77.6245,
            },
            headers={"X-Forwarded-For": "203.0.113.195"},
        )
        assert res.status_code == 200

    # Client B makes a request with clean limit
    res_b = await async_client.get(
        "/api/v1/commute/route",
        params={
            "origin_lat": 12.9716,
            "origin_lng": 77.5946,
            "dest_lat": 12.9352,
            "dest_lng": 77.6245,
        },
        headers={"X-Forwarded-For": "198.51.100.42"},
    )
    assert res_b.status_code == 200

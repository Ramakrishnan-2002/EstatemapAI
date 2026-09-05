from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.config import settings


async def seed_test_property(async_client: AsyncClient) -> int:
    """Helper to seed an active test property via API."""
    import uuid

    user_email = f"ai_owner_{uuid.uuid4().hex[:8]}@estatemap.ai"
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": user_email,
            "password": "Password123!",
            "full_name": "AI Test Owner",
        },
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "password": "Password123!"},
    )
    token = login_res.json()["access_token"]

    prop_res = await async_client.post(
        "/api/v1/properties",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Prestige Shantiniketan",
            "description": "Luxury 3 BHK high-rise apartment near ITPL",
            "price": 12000000.0,
            "bedrooms": 3,
            "bathrooms": 3.0,
            "area_sqft": 1800.0,
            "property_type": "apartment",
            "address": "ITPL Main Road",
            "locality": "Whitefield",
            "city": "Bengaluru",
            "pincode": "560066",
            "latitude": 12.9892,
            "longitude": 77.7289,
        },
    )
    return prop_res.json()["id"]


@pytest.mark.asyncio
async def test_ai_health_endpoint(async_client: AsyncClient):
    """Test AI health diagnostics endpoint."""
    res = await async_client.get("/api/v1/ai/health")
    assert res.status_code == 200
    data = res.json()
    assert "enabled" in data
    assert "provider" in data
    assert "reachable" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_ai_parse_search_endpoint(async_client: AsyncClient):
    """Test natural language search intent parsing endpoint."""
    # Use mock provider for predictable testing
    with patch("app.core.config.settings.AI_PROVIDER", "mock"):
        from app.ai.router import AIRouter

        AIRouter.reset()

        res = await async_client.post(
            "/api/v1/ai/parse-search",
            json={"query": "2 BHK under 70 lakh near Whitefield with hospital access"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        assert data["intent"]["bedrooms"] == 2
        assert data["intent"]["max_price"] == 7_000_000.0
        assert data["intent"]["locality"] == "Whitefield"
        assert "hospital" in data["intent"]["preferred_poi_categories"]
        assert data["latency_ms"] >= 0.0

        AIRouter.reset()


@pytest.mark.asyncio
async def test_ai_property_explain_endpoint_with_fallback(async_client: AsyncClient):
    """Test property explanation endpoint with deterministic fallback."""
    prop_id = await seed_test_property(async_client)

    # Use mock provider
    with patch("app.core.config.settings.AI_PROVIDER", "mock"):
        from app.ai.router import AIRouter

        AIRouter.reset()

        res = await async_client.post(
            f"/api/v1/ai/properties/{prop_id}/explain",
            json={
                "destination_lat": 12.9716,
                "destination_lng": 77.5946,
                "destination_name": "MG Road",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["property_id"] == prop_id
        assert len(data["explanation"]) > 10
        assert "factual_context" in data
        assert data["factual_context"]["property"]["locality"] == "Whitefield"

        AIRouter.reset()


@pytest.mark.asyncio
async def test_ai_rate_limiting_breach(async_client: AsyncClient):
    """Verify AI rate limiting triggers 429 when threshold is breached."""
    limit = settings.RATE_LIMIT_AI_REQUESTS
    got_429 = False

    with patch("app.core.config.settings.AI_PROVIDER", "mock"):
        from app.ai.router import AIRouter

        AIRouter.reset()

        for _ in range(limit + 5):
            res = await async_client.post(
                "/api/v1/ai/parse-search",
                json={"query": "2 BHK in Indiranagar"},
            )
            if res.status_code == 429:
                got_429 = True
                assert "Retry-After" in res.headers
                assert res.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
                break

        assert got_429 is True
        AIRouter.reset()

        import redis.asyncio as aioredis

        r_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            keys = await r_client.keys("estatemap:ratelimit:*")
            if keys:
                await r_client.delete(*keys)
        finally:
            await r_client.aclose()

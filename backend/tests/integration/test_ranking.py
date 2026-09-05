"""
Integration tests for Phase 9: Deterministic Property Ranking & Recommendations.

Verifies:
1. Hard database filtering is enforced strictly before ranking.
2. Dynamic weight adjustment alters ranking positions predictably.
3. Deterministic tie-breaking behavior (final_score DESC -> price ASC -> ID ASC).
4. Multi-run deterministic reproducibility.
5. Location intelligence & commute integration.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Truncate all tables before and after each ranking test."""
    await db_session.execute(
        text(
            "TRUNCATE TABLE pois, property_amenities, property_images, "
            "properties, amenities, users RESTART IDENTITY CASCADE;"
        )
    )
    await db_session.commit()
    yield
    await db_session.execute(
        text(
            "TRUNCATE TABLE pois, property_amenities, property_images, "
            "properties, amenities, users RESTART IDENTITY CASCADE;"
        )
    )
    await db_session.commit()


async def _register_and_login(
    async_client: AsyncClient, email: str = "rank_tester@estatemap.ai"
) -> str:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword123", "full_name": "Ranking Tester"},
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "securepassword123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _create_property(
    async_client: AsyncClient,
    token: str,
    title: str,
    price: float,
    bedrooms: int,
    area_sqft: float,
    locality: str,
    lat: float,
    lng: float,
) -> int:
    resp = await async_client.post(
        "/api/v1/properties",
        json={
            "title": title,
            "description": f"Listing in {locality}",
            "price": price,
            "property_type": "apartment",
            "bedrooms": bedrooms,
            "bathrooms": 2,
            "area_sqft": area_sqft,
            "address": f"Sample Road, {locality}",
            "city": "Bengaluru",
            "locality": locality,
            "latitude": lat,
            "longitude": lng,
            "status": "active",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_poi(
    async_client: AsyncClient,
    token: str,
    name: str,
    category: str,
    lat: float,
    lng: float,
) -> int:
    resp = await async_client.post(
        "/api/v1/pois",
        json={
            "name": name,
            "category": category,
            "latitude": lat,
            "longitude": lng,
            "city": "Bengaluru",
            "locality": "Central",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ─── 1. Hard Filtering Tests ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ranked_search_hard_filters_enforced(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    # Prop 1: 45 Lakhs, 2 BHK
    p1 = await _create_property(
        async_client, token, "Budget 2 BHK", 4500000, 2, 950, "Koramangala", 12.9352, 77.6245
    )
    # Prop 2: 95 Lakhs, 3 BHK
    p2 = await _create_property(
        async_client, token, "Luxury 3 BHK", 9500000, 3, 1600, "Indiranagar", 12.9784, 77.6408
    )

    # 1. Hard filter: max_price = 60 Lakhs
    r1 = await async_client.post(
        "/api/v1/search/ranked",
        json={
            "max_price": 6000000,
            "weights": {
                "price": 0.5,
                "bedrooms": 0.5,
                "area": 0.0,
                "location": 0.0,
                "commute": 0.0,
                "locality": 0.0,
            },
        },
    )
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["total_candidates"] == 1
    assert len(d1["items"]) == 1
    assert d1["items"][0]["property"]["id"] == p1

    # 2. Hard filter: bedrooms = 3
    r2 = await async_client.post(
        "/api/v1/search/ranked",
        json={
            "bedrooms": 3,
            "weights": {
                "price": 0.5,
                "bedrooms": 0.5,
                "area": 0.0,
                "location": 0.0,
                "commute": 0.0,
                "locality": 0.0,
            },
        },
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["total_candidates"] == 1
    assert d2["items"][0]["property"]["id"] == p2


# ─── 2. Weight Shifts Alter Ranking Predictably ───────────────────────────────


@pytest.mark.asyncio
async def test_ranked_search_weight_shifts(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    # Prop 1: Indiranagar - expensive (90L), but 3km from CBD
    p_close = await _create_property(
        async_client, token, "Close CBD Luxury", 9000000, 3, 1500, "Indiranagar", 12.9784, 77.6408
    )
    # Prop 2: Whitefield - cheap (40L), but 18km from CBD
    p_cheap = await _create_property(
        async_client, token, "Far CBD Affordable", 4000000, 3, 1500, "Whitefield", 12.9866, 77.7381
    )

    cbd_destination = {"name": "MG Road CBD", "latitude": 12.9756, "longitude": 77.6066}

    # Case A: Prioritize Price (price = 1.0, commute = 0.0)
    resp_price_dominant = await async_client.post(
        "/api/v1/search/ranked",
        json={
            "destination": cbd_destination,
            "weights": {
                "price": 1.0,
                "bedrooms": 0.0,
                "area": 0.0,
                "location": 0.0,
                "commute": 0.0,
                "locality": 0.0,
            },
        },
    )
    assert resp_price_dominant.status_code == 200
    items_a = resp_price_dominant.json()["items"]
    assert len(items_a) == 2
    assert items_a[0]["property"]["id"] == p_cheap
    assert items_a[0]["rank"] == 1
    assert items_a[1]["property"]["id"] == p_close
    assert items_a[1]["rank"] == 2

    # Case B: Prioritize Commute (commute = 1.0, price = 0.0)
    resp_commute_dominant = await async_client.post(
        "/api/v1/search/ranked",
        json={
            "destination": cbd_destination,
            "weights": {
                "price": 0.0,
                "bedrooms": 0.0,
                "area": 0.0,
                "location": 0.0,
                "commute": 1.0,
                "locality": 0.0,
            },
        },
    )
    assert resp_commute_dominant.status_code == 200
    items_b = resp_commute_dominant.json()["items"]
    assert len(items_b) == 2
    assert items_b[0]["property"]["id"] == p_close
    assert items_b[0]["rank"] == 1
    assert items_b[1]["property"]["id"] == p_cheap
    assert items_b[1]["rank"] == 2


# ─── 3. Deterministic Reproducibility & Explanations ──────────────────────────


@pytest.mark.asyncio
async def test_ranked_search_deterministic_reproducibility(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    await _create_property(
        async_client, token, "Prop 1", 5000000, 2, 1000, "Koramangala", 12.9352, 77.6245
    )
    await _create_property(
        async_client, token, "Prop 2", 6000000, 3, 1400, "Indiranagar", 12.9784, 77.6408
    )

    payload = {
        "target_price": 5500000,
        "preferred_bedrooms": 2,
        "weights": {
            "price": 0.4,
            "bedrooms": 0.3,
            "area": 0.3,
            "location": 0.0,
            "commute": 0.0,
            "locality": 0.0,
        },
    }

    # Execute 3 consecutive identical queries
    r1 = await async_client.post("/api/v1/search/ranked", json=payload)
    r2 = await async_client.post("/api/v1/search/ranked", json=payload)
    r3 = await async_client.post("/api/v1/search/ranked", json=payload)

    d1, d2, d3 = r1.json(), r2.json(), r3.json()
    assert d1 == d2 == d3

    # Validate explanation bullets
    top_item = d1["items"][0]
    assert len(top_item["explanations"]) >= 1
    assert top_item["score_breakdown"]["price"]["available"] is True
    assert top_item["score_breakdown"]["bedrooms"]["available"] is True


# ─── 4. Tie-Breaking Rule Verification ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_ranked_search_tie_breaking(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    # Two properties with equal scores but different prices
    p_lower_price = await _create_property(
        async_client, token, "Tie Prop A", 4500000, 2, 1000, "HSR", 12.9121, 77.6446
    )
    p_higher_price = await _create_property(
        async_client, token, "Tie Prop B", 5500000, 2, 1000, "HSR", 12.9122, 77.6447
    )

    # Bedrooms only ranking (both are 2 BHK -> bedroom score = 1.0)
    payload = {
        "preferred_bedrooms": 2,
        "weights": {
            "price": 0.0,
            "bedrooms": 1.0,
            "area": 0.0,
            "location": 0.0,
            "commute": 0.0,
            "locality": 0.0,
        },
    }

    resp = await async_client.post("/api/v1/search/ranked", json=payload)
    assert resp.status_code == 200
    items = resp.json()["items"]

    assert items[0]["final_score"] == items[1]["final_score"]
    # Tie broken by lower price first
    assert items[0]["property"]["id"] == p_lower_price
    assert items[1]["property"]["id"] == p_higher_price


# ─── 5. Recommendations Alias Endpoint ────────────────────────────────────────


@pytest.mark.asyncio
async def test_recommendations_ranked_endpoint(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    await _create_property(
        async_client, token, "Rec Prop", 5000000, 2, 1100, "BTM", 12.9165, 77.6101
    )

    resp = await async_client.post("/api/v1/recommendations/ranked", json={"limit": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_candidates"] == 1
    assert data["items"][0]["rank"] == 1

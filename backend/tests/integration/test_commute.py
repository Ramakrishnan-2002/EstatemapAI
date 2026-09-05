"""
Integration tests for Phase 8 Commute & Travel Intelligence endpoints.

Tests cover:
- GET /api/v1/properties/{id}/commute
- POST /api/v1/properties/{id}/commute/batch
- POST /api/v1/commute/compare
- GET /api/v1/commute/route
- Redis caching integration and fallback behavior
- GeoJSON LineString coordinate compliance [longitude, latitude]
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def cleanup_database(db_session: AsyncSession):
    """Optional database cleanup fixture."""
    yield


async def _register_and_login(async_client: AsyncClient, email: str | None = None) -> str:
    user_email = email or f"commute_{uuid.uuid4().hex[:8]}@estatemap.ai"
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": user_email, "password": "securepassword123", "full_name": "Commute Tester"},
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": user_email, "password": "securepassword123"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _create_property(
    async_client: AsyncClient,
    token: str,
    title: str,
    lat: float,
    lng: float,
) -> int:
    resp = await async_client.post(
        "/api/v1/properties",
        json={
            "title": title,
            "description": "Property for commute test",
            "price": 8500000,
            "property_type": "apartment",
            "bedrooms": 3,
            "bathrooms": 2,
            "area_sqft": 1450,
            "address": "100 Feet Road, Indiranagar",
            "city": "Bengaluru",
            "locality": "Indiranagar",
            "latitude": lat,
            "longitude": lng,
            "status": "active",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# ─── 1. Single Property Commute Tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_property_commute_success(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    # Indiranagar: 12.9784, 77.6408
    prop_id = await _create_property(async_client, token, "Indiranagar Flat", 12.9784, 77.6408)

    # Destination: Electronic City (12.8399, 77.6770)
    response = await async_client.get(
        f"/api/v1/properties/{prop_id}/commute",
        params={
            "destination_lat": 12.8399,
            "destination_lng": 77.6770,
            "destination_name": "Electronic City Infosys Campus",
            "mode": "driving",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["property_id"] == prop_id
    assert data["origin"]["latitude"] == 12.9784
    assert data["origin"]["longitude"] == 77.6408
    assert data["destination"]["name"] == "Electronic City Infosys Campus"
    assert data["destination"]["latitude"] == 12.8399
    assert data["destination"]["longitude"] == 77.6770
    assert data["mode"] == "driving"
    assert data["distance_meters"] > 0
    assert data["distance_km"] > 0
    assert data["duration_seconds"] > 0
    assert data["duration_minutes"] > 0
    assert data["provider"] == "mock"

    # GeoJSON LineString validation
    geometry = data["geometry"]
    assert geometry["type"] == "LineString"
    assert len(geometry["coordinates"]) >= 2
    # First coord is origin [lng, lat]
    assert geometry["coordinates"][0] == [77.6408, 12.9784]
    # Last coord is destination [lng, lat]
    assert geometry["coordinates"][-1] == [77.6770, 12.8399]


@pytest.mark.asyncio
async def test_get_property_commute_different_travel_modes(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    prop_id = await _create_property(async_client, token, "Koramangala Studio", 12.9352, 77.6245)

    # Commute to MG Road
    dest_lat, dest_lng = 12.9716, 77.5946

    # 1. Driving
    r_drive = await async_client.get(
        f"/api/v1/properties/{prop_id}/commute",
        params={"destination_lat": dest_lat, "destination_lng": dest_lng, "mode": "driving"},
    )
    assert r_drive.status_code == 200

    # 2. Cycling
    r_cycle = await async_client.get(
        f"/api/v1/properties/{prop_id}/commute",
        params={"destination_lat": dest_lat, "destination_lng": dest_lng, "mode": "cycling"},
    )
    assert r_cycle.status_code == 200

    # 3. Walking
    r_walk = await async_client.get(
        f"/api/v1/properties/{prop_id}/commute",
        params={"destination_lat": dest_lat, "destination_lng": dest_lng, "mode": "walking"},
    )
    assert r_walk.status_code == 200

    d_drive = r_drive.json()["duration_seconds"]
    d_cycle = r_cycle.json()["duration_seconds"]
    d_walk = r_walk.json()["duration_seconds"]

    assert d_drive < d_cycle < d_walk


@pytest.mark.asyncio
async def test_get_property_commute_not_found(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/properties/99999/commute",
        params={"destination_lat": 12.9716, "destination_lng": 77.5946},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_property_commute_invalid_coords(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    prop_id = await _create_property(async_client, token, "Test", 12.9352, 77.6245)

    response = await async_client.get(
        f"/api/v1/properties/{prop_id}/commute",
        params={"destination_lat": 95.0, "destination_lng": 77.5946},
    )
    assert response.status_code == 422


# ─── 2. Batch Commute Tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_property_batch_commute_success(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    prop_id = await _create_property(async_client, token, "HSR Layout Villa", 12.9121, 77.6446)

    payload = {
        "destinations": [
            {"name": "Electronic City", "latitude": 12.8399, "longitude": 77.6770},
            {"name": "Whitefield ITPL", "latitude": 12.9866, "longitude": 77.7381},
            {"name": "MG Road CBD", "latitude": 12.9716, "longitude": 77.5946},
        ],
        "mode": "driving",
    }

    response = await async_client.post(
        f"/api/v1/properties/{prop_id}/commute/batch",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["property_id"] == prop_id
    assert data["total_destinations"] == 3
    assert len(data["results"]) == 3
    for res in data["results"]:
        assert res["property_id"] == prop_id
        assert res["distance_km"] > 0
        assert res["duration_minutes"] > 0
        assert len(res["geometry"]["coordinates"]) >= 2


@pytest.mark.asyncio
async def test_get_property_batch_commute_limit_exceeded(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    prop_id = await _create_property(async_client, token, "Test", 12.9121, 77.6446)

    payload = {
        "destinations": [
            {"name": f"Dest {i}", "latitude": 12.9 + i * 0.01, "longitude": 77.6 + i * 0.01}
            for i in range(6)
        ],
        "mode": "driving",
    }
    response = await async_client.post(
        f"/api/v1/properties/{prop_id}/commute/batch",
        json=payload,
    )
    assert response.status_code == 422


# ─── 3. Multi-Property Commute Comparison Tests ───────────────────────────────


@pytest.mark.asyncio
async def test_compare_properties_commute_success(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    # Property 1: Indiranagar (closer to MG Road)
    p1 = await _create_property(async_client, token, "Indiranagar Home", 12.9784, 77.6408)
    # Property 2: Whitefield (farther from MG Road)
    p2 = await _create_property(async_client, token, "Whitefield Home", 12.9866, 77.7381)

    target_dest = {"name": "MG Road Metro", "latitude": 12.9756, "longitude": 77.6066}

    payload = {
        "property_ids": [p1, p2],
        "destination": target_dest,
        "mode": "driving",
    }

    response = await async_client.post("/api/v1/commute/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["destination"]["name"] == "MG Road Metro"
    assert len(data["comparisons"]) == 2
    # Indiranagar is closer and faster to MG Road than Whitefield
    assert data["fastest_property_id"] == p1
    assert data["shortest_property_id"] == p1


@pytest.mark.asyncio
async def test_compare_properties_missing_property(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    p1 = await _create_property(async_client, token, "Valid Prop", 12.9784, 77.6408)

    payload = {
        "property_ids": [p1, 999999],
        "destination": {"name": "Office", "latitude": 12.9716, "longitude": 77.5946},
    }
    response = await async_client.post("/api/v1/commute/compare", json=payload)
    assert response.status_code == 404


# ─── 4. Direct Point-to-Point Route Endpoint ──────────────────────────────────


@pytest.mark.asyncio
async def test_get_direct_route_endpoint(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/commute/route",
        params={
            "origin_lat": 12.9716,
            "origin_lng": 77.5946,
            "dest_lat": 12.8399,
            "dest_lng": 77.6770,
            "dest_name": "Direct Commute Path",
            "mode": "driving",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["property_id"] is None
    assert data["destination"]["name"] == "Direct Commute Path"
    assert data["distance_km"] > 0
    assert data["duration_minutes"] > 0
    assert data["geometry"]["type"] == "LineString"


# ─── 5. Caching Verification ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_commute_redis_caching(async_client: AsyncClient):
    token = await _register_and_login(async_client)
    prop_id = await _create_property(async_client, token, "Cache Test Prop", 12.9784, 77.6408)

    params = {
        "destination_lat": 12.9352,
        "destination_lng": 77.6245,
        "destination_name": "Cache Test Dest",
        "mode": "driving",
    }

    # First request: computes and caches
    r1 = await async_client.get(f"/api/v1/properties/{prop_id}/commute", params=params)
    assert r1.status_code == 200

    # Second request: served from cache (if Redis active)
    r2 = await async_client.get(f"/api/v1/properties/{prop_id}/commute", params=params)
    assert r2.status_code == 200
    d1 = r1.json()
    d2 = r2.json()

    assert d1["distance_meters"] == d2["distance_meters"]
    assert d1["duration_seconds"] == d2["duration_seconds"]

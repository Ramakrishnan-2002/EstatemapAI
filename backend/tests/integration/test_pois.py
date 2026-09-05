"""
Integration tests for Phase 7 POI endpoints.

Tests cover:
- GET /api/v1/pois/nearby
- POST /api/v1/pois (auth required)
- GET /api/v1/pois/{id}
- GET /api/v1/maps/pois (GeoJSON bbox)
- GET /api/v1/properties/{id}/nearby
- GET /api/v1/properties/{id}/location-intelligence

Spatial fixtures:
  All POIs use deterministic coordinates relative to
  Bengaluru center (12.9716, 77.5946) to verify
  PostGIS radius containment and exclusion.

  POI Layout from center:
    hospital_near  : 12.9716, 77.5946  → exactly at center (~0 km)
    hospital_far   : 12.9500, 77.5500  → ~7 km away
    school_near    : 12.9750, 77.6000  → ~0.5 km
    transit_near   : 12.9800, 77.6050  → ~1.1 km
    park_far       : 13.0300, 77.6500  → ~12 km away

  Test property: Bengaluru center (12.9716, 77.5946)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Truncate all tables before and after each POI test."""
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


async def _register_and_login(async_client: AsyncClient, email: str, password: str) -> str:
    """Register a user and return the bearer token."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


async def _create_property(async_client: AsyncClient, token: str, lat: float, lng: float) -> int:
    """Create a property at (lat, lng) and return its ID."""
    resp = await async_client.post(
        "/api/v1/properties",
        json={
            "title": "Test Property",
            "description": "For testing",
            "price": 5000000,
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "area_sqft": 900,
            "address": "Test Address",
            "city": "Bengaluru",
            "locality": "Central",
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
    city: str = "Bengaluru",
    locality: str | None = "Central",
) -> int:
    """Create a POI and return its ID."""
    resp = await async_client.post(
        "/api/v1/pois",
        json={
            "name": name,
            "category": category,
            "latitude": lat,
            "longitude": lng,
            "city": city,
            "locality": locality,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, f"POI creation failed: {resp.json()}"
    return resp.json()["id"]


# ─── POST /api/v1/pois ────────────────────────────────────────────────────────


class TestCreatePOI:
    async def test_create_poi_requires_auth(self, async_client: AsyncClient):
        resp = await async_client.post(
            "/api/v1/pois",
            json={
                "name": "Test Hospital",
                "category": "hospital",
                "latitude": 12.97,
                "longitude": 77.59,
                "city": "Bengaluru",
            },
        )
        assert resp.status_code == 401

    async def test_create_poi_with_auth(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "poi_creator@test.com", "Password123!")
        resp = await async_client.post(
            "/api/v1/pois",
            json={
                "name": "City Hospital",
                "category": "hospital",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "city": "Bengaluru",
                "locality": "Central",
                "is_active": True,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "City Hospital"
        assert data["category"] == "hospital"
        assert abs(data["latitude"] - 12.9716) < 0.001
        assert abs(data["longitude"] - 77.5946) < 0.001
        assert data["is_active"] is True

    async def test_create_poi_invalid_category(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "poi2@test.com", "Password123!")
        resp = await async_client.post(
            "/api/v1/pois",
            json={
                "name": "Test",
                "category": "invalid_category",
                "latitude": 12.97,
                "longitude": 77.59,
                "city": "Bengaluru",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    async def test_create_poi_invalid_coordinates(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "poi3@test.com", "Password123!")
        resp = await async_client.post(
            "/api/v1/pois",
            json={
                "name": "Test",
                "category": "hospital",
                "latitude": 200.0,  # invalid
                "longitude": 77.59,
                "city": "Bengaluru",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


# ─── GET /api/v1/pois/{id} ────────────────────────────────────────────────────


class TestGetPOI:
    async def test_get_poi_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/pois/99999")
        assert resp.status_code == 404

    async def test_get_poi_success(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "poi4@test.com", "Password123!")
        poi_id = await _create_poi(
            async_client, token, "Metro Station", "transit", 12.9756, 77.6086
        )
        resp = await async_client.get(f"/api/v1/pois/{poi_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Metro Station"
        assert resp.json()["category"] == "transit"


# ─── GET /api/v1/pois/nearby ──────────────────────────────────────────────────


class TestNearbyPOIs:
    async def test_poi_inside_radius_returned(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "nearby1@test.com", "Password123!")
        # Hospital at center
        await _create_poi(async_client, token, "Near Hospital", "hospital", 12.9716, 77.5946)

        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 1.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["poi"]["name"] == "Near Hospital"
        assert data["items"][0]["distance_km"] < 0.1  # essentially 0

    async def test_poi_outside_radius_excluded(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "nearby2@test.com", "Password123!")
        # Hospital ~7 km away from center
        await _create_poi(async_client, token, "Far Hospital", "hospital", 12.9500, 77.5500)

        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={
                "latitude": 12.9716,
                "longitude": 77.5946,
                "radius_km": 1.0,  # only 1 km
            },
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_category_filter(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "nearby3@test.com", "Password123!")
        await _create_poi(async_client, token, "Near Hospital", "hospital", 12.9716, 77.5946)
        await _create_poi(async_client, token, "Near School", "school", 12.9720, 77.5950)

        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={
                "latitude": 12.9716,
                "longitude": 77.5946,
                "radius_km": 2.0,
                "category": "hospital",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert all(item["poi"]["category"] == "hospital" for item in data["items"])
        assert data["category"] == "hospital"

    async def test_distance_increases_with_separation(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "nearby4@test.com", "Password123!")
        # Near: center
        await _create_poi(async_client, token, "Near School", "school", 12.9716, 77.5946)
        # Far: ~5 km east
        await _create_poi(async_client, token, "Far School", "school", 12.9716, 77.6400)

        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 10.0},
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 2
        distances = [item["distance_km"] for item in items]
        # Sorted by distance ascending — first should be smaller
        assert distances[0] < distances[1]

    async def test_limit_respected(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "nearby5@test.com", "Password123!")
        for i in range(5):
            await _create_poi(
                async_client, token, f"Park {i}", "park", 12.9716 + i * 0.001, 77.5946
            )

        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={
                "latitude": 12.9716,
                "longitude": 77.5946,
                "radius_km": 5.0,
                "limit": 2,
            },
        )
        assert resp.status_code == 200
        assert len(resp.json()["items"]) <= 2

    async def test_invalid_latitude_rejected(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={"latitude": 200.0, "longitude": 77.5946, "radius_km": 1.0},
        )
        assert resp.status_code == 422

    async def test_invalid_radius_rejected(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={"latitude": 12.97, "longitude": 77.59, "radius_km": -1.0},
        )
        assert resp.status_code == 422

    async def test_radius_too_large_rejected(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/pois/nearby",
            params={"latitude": 12.97, "longitude": 77.59, "radius_km": 100.0},
        )
        # POI nearby max is 50 km
        assert resp.status_code == 422


# ─── GET /api/v1/maps/pois ────────────────────────────────────────────────────


class TestMapsPOIs:
    async def test_bbox_returns_pois_inside(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "maps1@test.com", "Password123!")
        # POI inside bbox
        await _create_poi(async_client, token, "Inside Park", "park", 12.9716, 77.5946)
        # POI outside bbox (far north)
        await _create_poi(async_client, token, "Outside Park", "park", 13.5000, 77.5946)

        resp = await async_client.get(
            "/api/v1/maps/pois",
            params={
                "north": 13.1,
                "south": 12.8,
                "east": 77.7,
                "west": 77.4,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        names = [f["properties"]["name"] for f in data["features"]]
        assert "Inside Park" in names
        assert "Outside Park" not in names

    async def test_geojson_coordinate_order(self, async_client: AsyncClient):
        """GeoJSON coordinates must be [longitude, latitude] per RFC 7946."""
        token = await _register_and_login(async_client, "maps2@test.com", "Password123!")
        await _create_poi(async_client, token, "Coord Test", "hospital", 12.9716, 77.5946)

        resp = await async_client.get(
            "/api/v1/maps/pois",
            params={"north": 13.1, "south": 12.8, "east": 77.7, "west": 77.4},
        )
        assert resp.status_code == 200
        feature = resp.json()["features"][0]
        coords = feature["geometry"]["coordinates"]
        assert feature["geometry"]["type"] == "Point"
        # [longitude, latitude]
        assert abs(coords[0] - 77.5946) < 0.001  # longitude
        assert abs(coords[1] - 12.9716) < 0.001  # latitude

    async def test_geojson_feature_structure(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "maps3@test.com", "Password123!")
        await _create_poi(async_client, token, "Metro", "transit", 12.9716, 77.5946)

        resp = await async_client.get(
            "/api/v1/maps/pois",
            params={"north": 13.1, "south": 12.8, "east": 77.7, "west": 77.4},
        )
        feature = resp.json()["features"][0]
        assert feature["type"] == "Feature"
        assert "id" in feature
        assert feature["geometry"]["type"] == "Point"
        props = feature["properties"]
        assert "name" in props
        assert "category" in props
        assert "city" in props
        assert "is_active" in props

    async def test_category_filter_in_bbox(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "maps4@test.com", "Password123!")
        await _create_poi(async_client, token, "Hospital A", "hospital", 12.9716, 77.5946)
        await _create_poi(async_client, token, "School A", "school", 12.9720, 77.5950)

        resp = await async_client.get(
            "/api/v1/maps/pois",
            params={
                "north": 13.1,
                "south": 12.8,
                "east": 77.7,
                "west": 77.4,
                "category": "hospital",
            },
        )
        data = resp.json()
        assert all(f["properties"]["category"] == "hospital" for f in data["features"])

    async def test_empty_bbox_returns_empty_collection(self, async_client: AsyncClient):
        resp = await async_client.get(
            "/api/v1/maps/pois",
            params={
                "north": 14.0,
                "south": 13.5,
                "east": 78.0,
                "west": 77.8,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 0
        assert resp.json()["features"] == []


# ─── GET /api/v1/properties/{id}/nearby ──────────────────────────────────────


class TestPropertyNearby:
    async def test_property_nearby_returns_pois(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "propnear1@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        await _create_poi(async_client, token, "Near Hospital", "hospital", 12.9716, 77.5946)
        await _create_poi(async_client, token, "Far School", "school", 13.5000, 78.0000)

        resp = await async_client.get(
            f"/api/v1/properties/{prop_id}/nearby",
            params={"radius_km": 5.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        names = [item["poi"]["name"] for item in data["items"]]
        assert "Near Hospital" in names
        assert "Far School" not in names

    async def test_property_nearby_category_filter(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "propnear2@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        await _create_poi(async_client, token, "Near Hospital", "hospital", 12.9716, 77.5946)
        await _create_poi(async_client, token, "Near School", "school", 12.9720, 77.5950)

        resp = await async_client.get(
            f"/api/v1/properties/{prop_id}/nearby",
            params={"category": "hospital", "radius_km": 5.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["poi"]["category"] == "hospital" for item in data["items"])
        assert data["category"] == "hospital"

    async def test_property_not_found_returns_404(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/properties/99999/nearby")
        assert resp.status_code == 404

    async def test_property_nearby_distance_is_computed(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "propnear3@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        # POI at same location → distance ≈ 0
        await _create_poi(async_client, token, "Co-located Park", "park", 12.9716, 77.5946)

        resp = await async_client.get(
            f"/api/v1/properties/{prop_id}/nearby",
            params={"category": "park", "radius_km": 1.0},
        )
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["distance_km"] < 0.01


# ─── GET /api/v1/properties/{id}/location-intelligence ───────────────────────


class TestLocationIntelligence:
    async def test_location_intelligence_structure(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "li1@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)

        # Create one POI per required category
        await _create_poi(async_client, token, "Hospital", "hospital", 12.9716, 77.5946)
        await _create_poi(async_client, token, "School", "school", 12.9750, 77.6000)
        await _create_poi(async_client, token, "Metro", "transit", 12.9700, 77.5900)
        await _create_poi(async_client, token, "Supermarket", "supermarket", 12.9730, 77.5960)
        await _create_poi(async_client, token, "Park", "park", 12.9710, 77.5940)

        resp = await async_client.get(
            f"/api/v1/properties/{prop_id}/location-intelligence",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["property_id"] == prop_id
        assert "radius_km" in data
        assert "categories" in data

        categories = data["categories"]
        # All categories should be present
        for cat in ["hospital", "school", "transit", "supermarket", "park"]:
            assert cat in categories, f"Category '{cat}' missing from response"
            cat_data = categories[cat]
            assert "nearest_distance_km" in cat_data
            assert "count_within_radius" in cat_data
            assert cat_data["count_within_radius"] >= 0

    async def test_location_intelligence_nearest_distance(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "li2@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        # Hospital at essentially the same location → distance ≈ 0
        await _create_poi(async_client, token, "Zero Hospital", "hospital", 12.9716, 77.5946)

        resp = await async_client.get(f"/api/v1/properties/{prop_id}/location-intelligence")
        assert resp.status_code == 200
        hospital_data = resp.json()["categories"]["hospital"]
        assert hospital_data["nearest_distance_km"] is not None
        assert hospital_data["nearest_distance_km"] < 0.01

    async def test_location_intelligence_no_pois_for_category(self, async_client: AsyncClient):
        """When no POIs exist for a category, nearest_distance_km must be None."""
        token = await _register_and_login(async_client, "li3@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        # Only create a hospital — no school, transit, etc.
        await _create_poi(async_client, token, "Only Hospital", "hospital", 12.9716, 77.5946)

        resp = await async_client.get(f"/api/v1/properties/{prop_id}/location-intelligence")
        assert resp.status_code == 200
        categories = resp.json()["categories"]
        # school should have no nearest POI
        assert categories["school"]["nearest_distance_km"] is None
        assert categories["school"]["count_within_radius"] == 0

    async def test_location_intelligence_deterministic(self, async_client: AsyncClient):
        """Calling location intelligence twice should return identical results."""
        token = await _register_and_login(async_client, "li4@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        await _create_poi(async_client, token, "Stable Hospital", "hospital", 12.9730, 77.5960)

        resp1 = await async_client.get(f"/api/v1/properties/{prop_id}/location-intelligence")
        resp2 = await async_client.get(f"/api/v1/properties/{prop_id}/location-intelligence")
        assert resp1.json()["categories"]["hospital"] == resp2.json()["categories"]["hospital"]

    async def test_location_intelligence_property_not_found(self, async_client: AsyncClient):
        resp = await async_client.get("/api/v1/properties/99999/location-intelligence")
        assert resp.status_code == 404

    async def test_location_intelligence_custom_radius(self, async_client: AsyncClient):
        token = await _register_and_login(async_client, "li5@test.com", "Password123!")
        prop_id = await _create_property(async_client, token, 12.9716, 77.5946)
        # Hospital ~4 km away
        await _create_poi(async_client, token, "Far Hospital", "hospital", 12.9716, 77.6300)

        # With radius 2 km: hospital should NOT be in count
        resp_small = await async_client.get(
            f"/api/v1/properties/{prop_id}/location-intelligence",
            params={"radius_km": 2.0},
        )
        # With radius 10 km: hospital SHOULD be in count
        resp_large = await async_client.get(
            f"/api/v1/properties/{prop_id}/location-intelligence",
            params={"radius_km": 10.0},
        )
        assert resp_small.json()["categories"]["hospital"]["count_within_radius"] == 0
        assert resp_large.json()["categories"]["hospital"]["count_within_radius"] >= 1

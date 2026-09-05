import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Clean tables before and after each spatial test."""
    await db_session.execute(
        text(
            "TRUNCATE TABLE property_amenities, property_images, properties, amenities, users RESTART IDENTITY CASCADE;"
        )
    )
    await db_session.commit()
    yield
    await db_session.execute(
        text(
            "TRUNCATE TABLE property_amenities, property_images, properties, amenities, users RESTART IDENTITY CASCADE;"
        )
    )
    await db_session.commit()


async def seed_spatial_properties(async_client: AsyncClient) -> dict[str, int]:
    """
    Seed properties with distinct, realistic geographic distances from Bangalore Center (12.9716, 77.5946).
    """
    # 1. Register and login owner
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "geo_owner@estatemap.ai",
            "password": "SecurePassword123!",
            "full_name": "Geo Owner",
        },
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "geo_owner@estatemap.ai", "password": "SecurePassword123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    properties_data = [
        # Center: MG Road (0.0 km)
        {
            "key": "center",
            "title": "Central MG Road Luxury Flat",
            "description": "Heart of Bengaluru",
            "price": 15000000,
            "property_type": "apartment",
            "bedrooms": 3,
            "bathrooms": 3,
            "area_sqft": 1800,
            "address": "MG Road",
            "city": "Bengaluru",
            "locality": "Central",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "status": "active",
        },
        # ~5 km East: Indiranagar
        {
            "key": "indiranagar",
            "title": "Indiranagar 100ft Road Penthouse",
            "description": "Boutique residential",
            "price": 22000000,
            "property_type": "apartment",
            "bedrooms": 3,
            "bathrooms": 3,
            "area_sqft": 2400,
            "address": "100ft Road",
            "city": "Bengaluru",
            "locality": "Indiranagar",
            "latitude": 12.9719,
            "longitude": 77.6412,
            "status": "active",
        },
        # ~17 km East: Whitefield
        {
            "key": "whitefield",
            "title": "Whitefield Tech Park Condo",
            "description": "IT corridor living",
            "price": 8500000,
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": 1250,
            "address": "ITPL Main Road",
            "city": "Bengaluru",
            "locality": "Whitefield",
            "latitude": 12.9698,
            "longitude": 77.7500,
            "status": "active",
        },
        # ~18 km South: Electronic City
        {
            "key": "electronic_city",
            "title": "Electronic City Gated Villa",
            "description": "Green residential community",
            "price": 6500000,
            "property_type": "villa",
            "bedrooms": 2,
            "bathrooms": 2,
            "area_sqft": 1100,
            "address": "Phase 1",
            "city": "Bengaluru",
            "locality": "Electronic City",
            "latitude": 12.8399,
            "longitude": 77.6770,
            "status": "active",
        },
        # ~130 km Away: Mysuru
        {
            "key": "mysuru",
            "title": "Mysuru Heritage Bungalow",
            "description": "Far outside Bengaluru",
            "price": 5000000,
            "property_type": "independent_house",
            "bedrooms": 4,
            "bathrooms": 4,
            "area_sqft": 3000,
            "address": "Gokulam",
            "city": "Mysuru",
            "locality": "Gokulam",
            "latitude": 12.2958,
            "longitude": 76.6394,
            "status": "active",
        },
    ]

    ids: dict[str, int] = {}
    for p in properties_data:
        key = p.pop("key")
        res = await async_client.post("/api/v1/properties", json=p, headers=headers)
        assert res.status_code == 201, res.text
        ids[key] = res.json()["id"]

    return ids


@pytest.mark.asyncio
async def test_search_radius_5km_center(async_client: AsyncClient):
    ids = await seed_spatial_properties(async_client)

    # 5 km radius around Bangalore Center (12.9716, 77.5946)
    res = await async_client.get(
        "/api/v1/search/radius",
        params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 6.0},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    returned_ids = [item["property"]["id"] for item in data["items"]]
    assert ids["center"] in returned_ids
    assert ids["indiranagar"] in returned_ids
    assert ids["whitefield"] not in returned_ids
    assert ids["mysuru"] not in returned_ids

    # Verify distances are returned and ordered ascending
    distances = [item["distance_km"] for item in data["items"]]
    assert distances[0] <= distances[1]
    assert distances[0] < 0.1  # Center is ~0 km
    assert 4.0 <= distances[1] <= 6.0  # Indiranagar is ~5 km


@pytest.mark.asyncio
async def test_search_radius_25km_and_composed_filters(async_client: AsyncClient):
    ids = await seed_spatial_properties(async_client)

    # 25 km radius should include center, indiranagar, whitefield, electronic_city
    res = await async_client.get(
        "/api/v1/search/radius",
        params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 25.0},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    returned_ids = [item["property"]["id"] for item in data["items"]]
    assert ids["mysuru"] not in returned_ids

    # Now apply price filter: min_price 1 Cr (10000000)
    res_filtered = await async_client.get(
        "/api/v1/search/radius",
        params={
            "latitude": 12.9716,
            "longitude": 77.5946,
            "radius_km": 25.0,
            "min_price": 10000000,
        },
    )
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.json()
    assert filtered_data["total"] == 2
    filtered_ids = [item["property"]["id"] for item in filtered_data["items"]]
    assert ids["center"] in filtered_ids
    assert ids["indiranagar"] in filtered_ids


@pytest.mark.asyncio
async def test_search_bbox_inside_and_outside(async_client: AsyncClient):
    ids = await seed_spatial_properties(async_client)

    # Bounding box enclosing Central Bengaluru & Indiranagar
    res = await async_client.get(
        "/api/v1/search/bbox",
        params={
            "min_lat": 12.95,
            "min_lng": 77.58,
            "max_lat": 12.99,
            "max_lng": 77.66,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    returned_ids = [p["id"] for p in data["items"]]
    assert ids["center"] in returned_ids
    assert ids["indiranagar"] in returned_ids
    assert ids["whitefield"] not in returned_ids


@pytest.mark.asyncio
async def test_maps_viewport_returns_valid_geojson(async_client: AsyncClient):
    await seed_spatial_properties(async_client)

    # Map viewport (north, south, east, west)
    res = await async_client.get(
        "/api/v1/maps/properties",
        params={
            "north": 13.00,
            "south": 12.95,
            "east": 77.66,
            "west": 77.58,
        },
    )
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert geojson["total"] == 2
    assert len(geojson["features"]) == 2

    # Verify GeoJSON RFC 7946 compliance: Point [longitude, latitude]
    for feat in geojson["features"]:
        assert feat["type"] == "Feature"
        assert feat["geometry"]["type"] == "Point"
        lng, lat = feat["geometry"]["coordinates"]
        assert 77.0 <= lng <= 78.0
        assert 12.0 <= lat <= 14.0
        assert "id" in feat["properties"]
        assert "title" in feat["properties"]
        assert "price" in feat["properties"]


@pytest.mark.asyncio
async def test_maps_radius_geojson(async_client: AsyncClient):
    await seed_spatial_properties(async_client)

    res = await async_client.get(
        "/api/v1/maps/radius",
        params={"latitude": 12.9716, "longitude": 77.5946, "radius_km": 10.0},
    )
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert geojson["total"] == 2
    for feat in geojson["features"]:
        assert "distance_km" in feat["properties"]
        assert feat["properties"]["distance_km"] >= 0.0


@pytest.mark.asyncio
async def test_search_polygon_postgis(async_client: AsyncClient):
    ids = await seed_spatial_properties(async_client)

    # Polygon around Central Bangalore & Indiranagar
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [77.58, 12.95],
                [77.66, 12.95],
                [77.66, 13.00],
                [77.58, 13.00],
                [77.58, 12.95],
            ]
        ],
    }

    res = await async_client.post(
        "/api/v1/search/polygon",
        json={"polygon": polygon},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    returned_ids = [p["id"] for p in data["items"]]
    assert ids["center"] in returned_ids
    assert ids["indiranagar"] in returned_ids
    assert ids["whitefield"] not in returned_ids


@pytest.mark.asyncio
async def test_maps_polygon_geojson(async_client: AsyncClient):
    await seed_spatial_properties(async_client)

    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [77.58, 12.95],
                [77.66, 12.95],
                [77.66, 13.00],
                [77.58, 13.00],
                [77.58, 12.95],
            ]
        ],
    }

    res = await async_client.post(
        "/api/v1/maps/polygon",
        json={"polygon": polygon},
    )
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert geojson["total"] == 2


@pytest.mark.asyncio
async def test_spatial_query_validation_errors(async_client: AsyncClient):
    # 1. Latitude > 90
    res_lat = await async_client.get(
        "/api/v1/search/radius",
        params={"latitude": 105.0, "longitude": 77.59, "radius_km": 10},
    )
    assert res_lat.status_code == 422
    assert "error" in res_lat.json()
    assert res_lat.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in res_lat.json()["error"]

    # 2. Radius <= 0
    res_radius = await async_client.get(
        "/api/v1/search/radius",
        params={"latitude": 12.97, "longitude": 77.59, "radius_km": 0},
    )
    assert res_radius.status_code == 422
    assert res_radius.json()["error"]["code"] == "VALIDATION_ERROR"

    # 3. Unclosed Polygon
    unclosed_poly = {
        "type": "Polygon",
        "coordinates": [
            [
                [77.58, 12.95],
                [77.66, 12.95],
                [77.66, 13.00],
                [77.58, 13.00],
            ]
        ],
    }
    res_poly = await async_client.post(
        "/api/v1/search/polygon",
        json={"polygon": unclosed_poly},
    )
    assert res_poly.status_code == 422
    assert res_poly.json()["error"]["code"] == "VALIDATION_ERROR"

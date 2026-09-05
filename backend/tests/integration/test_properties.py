import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.amenity import Amenity


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Truncate properties, amenities, and users tables before each integration test."""
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


async def create_test_user(
    async_client: AsyncClient,
    email: str = "owner@estatemap.ai",
    password: str = "OwnerPassword123!",
) -> str:
    """Helper to register and login a test user, returning access token."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Property Owner"},
    )
    res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return res.json()["access_token"]


async def seed_amenities(db_session: AsyncSession) -> list[Amenity]:
    """Helper to insert test amenities."""
    amenities = [
        Amenity(name="Swimming Pool", category="Leisure", icon="pool"),
        Amenity(name="Gymnasium", category="Fitness", icon="dumbbell"),
        Amenity(name="Power Backup", category="Utility", icon="zap"),
    ]
    db_session.add_all(amenities)
    await db_session.commit()
    for a in amenities:
        await db_session.refresh(a)
    return amenities


@pytest.mark.asyncio
async def test_create_property_success(async_client: AsyncClient, db_session: AsyncSession):
    token = await create_test_user(async_client)
    amenities = await seed_amenities(db_session)
    amenity_ids = [a.id for a in amenities[:2]]

    payload = {
        "title": "Modern 3BHK Apartment in Indiranagar",
        "description": "Spacious sun-lit apartment close to metro station.",
        "price": 14500000.0,
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 2.0,
        "area_sqft": 1650.0,
        "address": "100 Feet Road, Indiranagar",
        "city": "Bengaluru",
        "locality": "Indiranagar",
        "latitude": 12.9719,
        "longitude": 77.6412,
        "image_urls": [
            "https://cdn.estatemap.ai/img1.jpg",
            "https://cdn.estatemap.ai/img2.jpg",
        ],
        "amenity_ids": amenity_ids,
    }

    response = await async_client.post(
        "/api/v1/properties",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()

    assert data["id"] is not None
    assert data["title"] == payload["title"]
    assert data["price"] == payload["price"]
    assert data["latitude"] == pytest.approx(12.9719, rel=1e-4)
    assert data["longitude"] == pytest.approx(77.6412, rel=1e-4)
    assert len(data["images"]) == 2
    assert data["images"][0]["display_order"] == 0
    assert data["images"][1]["display_order"] == 1
    assert len(data["amenities"]) == 2


@pytest.mark.asyncio
async def test_create_property_unauthenticated(async_client: AsyncClient):
    payload = {
        "title": "Unauthorized Listing",
        "price": 5000000.0,
        "property_type": "plot",
        "area_sqft": 1200.0,
        "address": "Anywhere",
        "city": "Bengaluru",
        "locality": "HSR Layout",
        "latitude": 12.91,
        "longitude": 77.63,
    }
    response = await async_client.post("/api/v1/properties", json=payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_get_property_by_id(async_client: AsyncClient):
    token = await create_test_user(async_client)
    payload = {
        "title": "Cozy Studio in Koramangala",
        "price": 4500000.0,
        "property_type": "apartment",
        "bedrooms": 1,
        "bathrooms": 1.0,
        "area_sqft": 550.0,
        "address": "5th Block Koramangala",
        "city": "Bengaluru",
        "locality": "Koramangala",
        "latitude": 12.9352,
        "longitude": 77.6245,
    }
    create_res = await async_client.post(
        "/api/v1/properties",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    prop_id = create_res.json()["id"]

    # Public fetch
    get_res = await async_client.get(f"/api/v1/properties/{prop_id}")
    assert get_res.status_code == 200
    prop_data = get_res.json()
    assert prop_data["id"] == prop_id
    assert prop_data["title"] == payload["title"]
    assert prop_data["latitude"] == pytest.approx(12.9352, rel=1e-4)
    assert prop_data["longitude"] == pytest.approx(77.6245, rel=1e-4)


@pytest.mark.asyncio
async def test_get_property_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/properties/999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_property_by_owner(async_client: AsyncClient):
    token = await create_test_user(async_client)
    payload = {
        "title": "Original Title",
        "price": 10000000.0,
        "property_type": "villa",
        "area_sqft": 2000.0,
        "address": "Sarjapur Road",
        "city": "Bengaluru",
        "locality": "Sarjapur",
        "latitude": 12.92,
        "longitude": 77.68,
    }
    create_res = await async_client.post(
        "/api/v1/properties",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    prop_id = create_res.json()["id"]

    # Update title, price, and coordinates
    update_payload = {
        "title": "Updated Luxury Villa",
        "price": 12000000.0,
        "latitude": 12.925,
        "longitude": 77.685,
    }
    patch_res = await async_client.patch(
        f"/api/v1/properties/{prop_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert patch_res.status_code == 200
    updated_data = patch_res.json()
    assert updated_data["title"] == "Updated Luxury Villa"
    assert updated_data["price"] == 12000000.0
    assert updated_data["latitude"] == pytest.approx(12.925, rel=1e-4)
    assert updated_data["longitude"] == pytest.approx(77.685, rel=1e-4)


@pytest.mark.asyncio
async def test_update_and_delete_property_by_non_owner_forbidden(
    async_client: AsyncClient,
):
    token_owner = await create_test_user(async_client, email="owner1@estatemap.ai")
    token_stranger = await create_test_user(async_client, email="stranger@estatemap.ai")

    create_res = await async_client.post(
        "/api/v1/properties",
        json={
            "title": "Owner Property",
            "price": 8000000.0,
            "property_type": "apartment",
            "area_sqft": 1100.0,
            "address": "MG Road",
            "city": "Bengaluru",
            "locality": "Central",
            "latitude": 12.97,
            "longitude": 77.60,
        },
        headers={"Authorization": f"Bearer {token_owner}"},
    )
    prop_id = create_res.json()["id"]

    # Stranger tries to PATCH
    patch_res = await async_client.patch(
        f"/api/v1/properties/{prop_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {token_stranger}"},
    )
    assert patch_res.status_code == 403
    assert patch_res.json()["error"]["code"] == "FORBIDDEN"

    # Stranger tries to DELETE
    delete_res = await async_client.delete(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {token_stranger}"},
    )
    assert delete_res.status_code == 403
    assert delete_res.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_delete_property_by_owner_success(async_client: AsyncClient):
    token = await create_test_user(async_client)
    create_res = await async_client.post(
        "/api/v1/properties",
        json={
            "title": "To Be Deleted",
            "price": 3000000.0,
            "property_type": "plot",
            "area_sqft": 1000.0,
            "address": "Bannerghatta",
            "city": "Bengaluru",
            "locality": "Bannerghatta",
            "latitude": 12.85,
            "longitude": 77.58,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    prop_id = create_res.json()["id"]

    # Owner deletes
    delete_res = await async_client.delete(
        f"/api/v1/properties/{prop_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_res.status_code == 204

    # Verify not found afterwards
    get_res = await async_client.get(f"/api/v1/properties/{prop_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_list_properties_filtering_sorting_and_pagination(
    async_client: AsyncClient,
):
    token = await create_test_user(async_client)

    properties_to_create = [
        {
            "title": "Apt in Bengaluru Whitefield",
            "price": 5000000.0,
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 2.0,
            "area_sqft": 1000.0,
            "address": "Whitefield 1",
            "city": "Bengaluru",
            "locality": "Whitefield",
            "latitude": 12.96,
            "longitude": 77.74,
        },
        {
            "title": "Villa in Bengaluru Whitefield",
            "price": 15000000.0,
            "property_type": "villa",
            "bedrooms": 4,
            "bathrooms": 4.0,
            "area_sqft": 3000.0,
            "address": "Whitefield 2",
            "city": "Bengaluru",
            "locality": "Whitefield",
            "latitude": 12.97,
            "longitude": 77.75,
        },
        {
            "title": "Apartment in Mumbai Bandra",
            "price": 35000000.0,
            "property_type": "apartment",
            "bedrooms": 3,
            "bathrooms": 3.0,
            "area_sqft": 1500.0,
            "address": "Bandra West",
            "city": "Mumbai",
            "locality": "Bandra",
            "latitude": 19.05,
            "longitude": 72.82,
        },
    ]

    for p in properties_to_create:
        await async_client.post(
            "/api/v1/properties",
            json=p,
            headers={"Authorization": f"Bearer {token}"},
        )

    # 1. Filter by city=bengaluru (case-insensitive)
    res_city = await async_client.get("/api/v1/properties?city=Bengaluru")
    assert res_city.status_code == 200
    data_city = res_city.json()
    assert data_city["total"] == 2
    assert len(data_city["items"]) == 2

    # 2. Filter by price range (6,000,000 to 20,000,000)
    res_price = await async_client.get("/api/v1/properties?min_price=6000000&max_price=20000000")
    assert res_price.status_code == 200
    data_price = res_price.json()
    assert data_price["total"] == 1
    assert data_price["items"][0]["title"] == "Villa in Bengaluru Whitefield"

    # 3. Sort by price_desc
    res_sort = await async_client.get("/api/v1/properties?sort_by=price_desc")
    assert res_sort.status_code == 200
    data_sort = res_sort.json()
    assert data_sort["items"][0]["price"] == 35000000.0
    assert data_sort["items"][-1]["price"] == 5000000.0

    # 4. Pagination (page_size=2, page=1)
    res_page1 = await async_client.get("/api/v1/properties?page=1&page_size=2")
    assert res_page1.status_code == 200
    data_p1 = res_page1.json()
    assert data_p1["total"] == 3
    assert data_p1["total_pages"] == 2
    assert len(data_p1["items"]) == 2

    # Page 2
    res_page2 = await async_client.get("/api/v1/properties?page=2&page_size=2")
    assert res_page2.status_code == 200
    data_p2 = res_page2.json()
    assert len(data_p2["items"]) == 1

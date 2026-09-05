import pytest
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property
from app.models.user import User
from app.repositories.property_repository import PropertyRepository
from app.schemas.ai import PropertySearchIntent
from app.schemas.property import PropertyFilterParams


@pytest.fixture
async def sample_properties_for_equivalence(db_session: AsyncSession):
    # Create test user
    user = User(
        email="equivalence_test@estatemap.ai",
        hashed_password="dummy_password_hash",
        full_name="Equivalence Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    p1 = Property(
        owner_id=user.id,
        title="2 BHK in Indiranagar",
        price=7500000.0,
        property_type="apartment",
        bedrooms=2,
        bathrooms=2,
        area_sqft=1200.0,
        address="100 Feet Road",
        city="Bengaluru",
        locality="Indiranagar",
        location=from_shape(Point(77.6412, 12.9716), srid=4326),
        status="active",
    )
    p2 = Property(
        owner_id=user.id,
        title="3 BHK Villa in Whitefield",
        price=18000000.0,
        property_type="villa",
        bedrooms=3,
        bathrooms=3,
        area_sqft=2500.0,
        address="ITPL Main Road",
        city="Bengaluru",
        locality="Whitefield",
        location=from_shape(Point(77.7499, 12.9698), srid=4326),
        status="active",
    )
    p3 = Property(
        owner_id=user.id,
        title="1 BHK Studio in Koramangala",
        price=4500000.0,
        property_type="apartment",
        bedrooms=1,
        bathrooms=1,
        area_sqft=650.0,
        address="5th Block",
        city="Bengaluru",
        locality="Koramangala",
        location=from_shape(Point(77.6245, 12.9352), srid=4326),
        status="active",
    )
    db_session.add_all([p1, p2, p3])
    await db_session.commit()
    return p1, p2, p3


@pytest.mark.asyncio
async def test_ai_intent_vs_manual_filter_equivalence_combinations(
    db_session: AsyncSession, sample_properties_for_equivalence
):
    repo = PropertyRepository(db_session)

    test_cases = [
        # Case 1: bedrooms + max price + locality
        (
            PropertySearchIntent(
                raw_query="2 BHK in Indiranagar under 80 lakh",
                bedrooms=2,
                max_price=8000000.0,
                locality="Indiranagar",
            ),
            PropertyFilterParams(
                bedrooms=2,
                max_price=8000000.0,
                locality="Indiranagar",
            ),
        ),
        # Case 2: property type + locality
        (
            PropertySearchIntent(
                raw_query="Villa in Whitefield",
                property_type="villa",
                locality="Whitefield",
            ),
            PropertyFilterParams(
                property_type="villa",
                locality="Whitefield",
            ),
        ),
        # Case 3: bedrooms + price + property type + locality
        (
            PropertySearchIntent(
                raw_query="1 BHK apartment in Koramangala under 50 lakh",
                bedrooms=1,
                max_price=5000000.0,
                property_type="apartment",
                locality="Koramangala",
            ),
            PropertyFilterParams(
                bedrooms=1,
                max_price=5000000.0,
                property_type="apartment",
                locality="Koramangala",
            ),
        ),
    ]

    for ai_intent, manual_filters in test_cases:
        # Map AI intent into PropertyFilterParams
        ai_filters = PropertyFilterParams(
            bedrooms=ai_intent.bedrooms,
            min_price=ai_intent.min_price,
            max_price=ai_intent.max_price,
            property_type=ai_intent.property_type,
            locality=ai_intent.locality,
            city=ai_intent.city,
        )

        ai_results, ai_total, _ = await repo.list(ai_filters)
        manual_results, manual_total, _ = await repo.list(manual_filters)

        # Assert 100% parity
        assert ai_total == manual_total
        assert len(ai_results) == len(manual_results)
        assert [p.id for p in ai_results] == [p.id for p in manual_results]

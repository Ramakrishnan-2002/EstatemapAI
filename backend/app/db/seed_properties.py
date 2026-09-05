import asyncio

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import async_session_factory
from app.models.property import Property
from app.models.user import User

DEMO_PROPERTIES = [
    {
        "title": "Luxury 3 BHK Penthouse in Indiranagar",
        "description": "Premium penthouse with panoramic skyline views, modern modular kitchen, and private terrace.",
        "price": 18500000.0,
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 3,
        "area_sqft": 2400.0,
        "address": "12th Main Road, Indiranagar",
        "city": "Bengaluru",
        "locality": "Indiranagar",
        "latitude": 12.9716,
        "longitude": 77.6412,
        "status": "active",
    },
    {
        "title": "Modern 2 BHK Apartment in Koramangala",
        "description": "Bright and spacious apartment close to trendy cafes, parks, and major tech parks.",
        "price": 9500000.0,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1350.0,
        "address": "80 Feet Road, 4th Block Koramangala",
        "city": "Bengaluru",
        "locality": "Koramangala",
        "latitude": 12.9352,
        "longitude": 77.6245,
        "status": "active",
    },
    {
        "title": "Spacious 4 BHK Villa in Whitefield",
        "description": "Gated community villa with private garden, clubhouse amenities, and close to international schools.",
        "price": 27500000.0,
        "property_type": "villa",
        "bedrooms": 4,
        "bathrooms": 4,
        "area_sqft": 3600.0,
        "address": "ECC Road, Whitefield",
        "city": "Bengaluru",
        "locality": "Whitefield",
        "latitude": 12.9698,
        "longitude": 77.7499,
        "status": "active",
    },
    {
        "title": "Affordable 2 BHK Flat in HSR Layout",
        "description": "Cozy 2 bedroom flat in peaceful residential sector with excellent connectivity to Silk Board and ORR.",
        "price": 6800000.0,
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 2,
        "area_sqft": 1100.0,
        "address": "27th Main, Sector 1, HSR Layout",
        "city": "Bengaluru",
        "locality": "HSR Layout",
        "latitude": 12.9121,
        "longitude": 77.6446,
        "status": "active",
    },
]


async def seed_demo_properties():
    async with async_session_factory() as session:
        # Check or create demo user
        user_stmt = select(User).where(User.email == "demo@estatemap.ai")
        res = await session.execute(user_stmt)
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                email="demo@estatemap.ai",
                hashed_password=get_password_hash("estatemap_demo_123"),
                full_name="Demo User",
                is_active=True,
                is_superuser=False,
            )
            session.add(user)
            await session.flush()

        prop_stmt = select(Property)
        existing = (await session.execute(prop_stmt)).scalars().all()
        if not existing:
            for p_data in DEMO_PROPERTIES:
                p = Property(
                    owner_id=user.id,
                    title=p_data["title"],
                    description=p_data["description"],
                    price=p_data["price"],
                    property_type=p_data["property_type"],
                    bedrooms=p_data["bedrooms"],
                    bathrooms=p_data["bathrooms"],
                    area_sqft=p_data["area_sqft"],
                    address=p_data["address"],
                    city=p_data["city"],
                    locality=p_data["locality"],
                    location=from_shape(Point(p_data["longitude"], p_data["latitude"]), srid=4326),
                    status=p_data["status"],
                )
                session.add(p)
            await session.commit()
            print(f"Successfully seeded {len(DEMO_PROPERTIES)} demo properties.")
        else:
            print(f"Database already contains {len(existing)} properties.")


if __name__ == "__main__":
    asyncio.run(seed_demo_properties())

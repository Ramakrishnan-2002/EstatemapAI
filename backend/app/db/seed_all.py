import asyncio
import random
from decimal import Decimal
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select, insert, func

from app.core.security import get_password_hash
from app.db.session import async_session_factory
from app.models.amenity import Amenity, property_amenities
from app.models.poi import PointOfInterest
from app.models.poi_category import POICategory
from app.models.property import Property
from app.models.property_image import PropertyImage
from app.models.user import User

BENGALURU_PROPERTIES = [
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

CHENNAI_LOCALITIES = [
    {"locality": "Sholinganallur", "lat": 12.8988, "lng": 80.2281, "type": "IT Hub", "price_multiplier": 0.9},
    {"locality": "Thoraipakkam", "lat": 12.9416, "lng": 80.2362, "type": "IT Corridor", "price_multiplier": 1.0},
    {"locality": "Perungudi", "lat": 12.9654, "lng": 80.2461, "type": "IT Corridor", "price_multiplier": 1.1},
    {"locality": "Navalur", "lat": 12.8458, "lng": 80.2265, "type": "Suburban", "price_multiplier": 0.75},
    {"locality": "Siruseri", "lat": 12.8256, "lng": 80.2185, "type": "SIPCOT IT", "price_multiplier": 0.7},
    {"locality": "Karapakkam", "lat": 12.9142, "lng": 80.2274, "type": "IT Hub", "price_multiplier": 0.85},
    {"locality": "Velachery", "lat": 12.9815, "lng": 80.2180, "type": "Urban Hub", "price_multiplier": 1.25},
    {"locality": "Adyar", "lat": 13.0012, "lng": 80.2565, "type": "Premium South", "price_multiplier": 2.1},
    {"locality": "Besant Nagar", "lat": 13.0003, "lng": 80.2667, "type": "Coastal Luxury", "price_multiplier": 2.4},
    {"locality": "Thiruvanmiyur", "lat": 12.9830, "lng": 80.2594, "type": "Coastal", "price_multiplier": 1.8},
    {"locality": "East Coast Road (ECR)", "lat": 12.9490, "lng": 80.2550, "type": "Luxury Coast", "price_multiplier": 2.2},
    {"locality": "T. Nagar", "lat": 13.0418, "lng": 80.2341, "type": "Central Commercial", "price_multiplier": 1.9},
    {"locality": "Nungambakkam", "lat": 13.0569, "lng": 80.2425, "type": "Central Premium", "price_multiplier": 2.2},
    {"locality": "Alwarpet", "lat": 13.0336, "lng": 80.2514, "type": "Historic Luxury", "price_multiplier": 2.5},
    {"locality": "Mylapore", "lat": 13.0368, "lng": 80.2676, "type": "Cultural Hub", "price_multiplier": 1.8},
    {"locality": "Anna Nagar", "lat": 13.0850, "lng": 80.2101, "type": "Planned Metro Hub", "price_multiplier": 1.9},
    {"locality": "Porur", "lat": 13.0382, "lng": 80.1565, "type": "DLF Cybercity Hub", "price_multiplier": 0.95},
    {"locality": "Guindy", "lat": 13.0067, "lng": 80.2025, "type": "Industrial/Tech", "price_multiplier": 1.4},
    {"locality": "Medavakkam", "lat": 12.9171, "lng": 80.1923, "type": "Residential South", "price_multiplier": 0.8},
    {"locality": "Kilpauk", "lat": 13.0784, "lng": 80.2412, "type": "Central Residential", "price_multiplier": 1.7},
]

PROPERTY_TEMPLATES = [
    {"type": "apartment", "bhk": 1, "baths": 1, "area_base": 600, "price_base": 4200000, "title_fmt": "Compact 1 BHK Smart Apartment in {locality}"},
    {"type": "apartment", "bhk": 2, "baths": 2, "area_base": 1150, "price_base": 7800000, "title_fmt": "Modern 2 BHK Gated Community Flat in {locality}"},
    {"type": "apartment", "bhk": 2, "baths": 2, "area_base": 1250, "price_base": 8500000, "title_fmt": "Contemporary 2 BHK Apartment near Tech Park in {locality}"},
    {"type": "apartment", "bhk": 3, "baths": 3, "area_base": 1650, "price_base": 13500000, "title_fmt": "Spacious 3 BHK Luxury Flat in {locality}"},
    {"type": "apartment", "bhk": 3, "baths": 3, "area_base": 1850, "price_base": 16000000, "title_fmt": "Premium 3 BHK High-rise with Skyline Views in {locality}"},
    {"type": "villa", "bhk": 4, "baths": 4, "area_base": 3200, "price_base": 29000000, "title_fmt": "Exclusive 4 BHK Gated Community Villa in {locality}"},
    {"type": "penthouse", "bhk": 4, "baths": 4, "area_base": 3600, "price_base": 38000000, "title_fmt": "Ultra-Luxury 4 BHK Penthouse with Private Terrace in {locality}"},
    {"type": "apartment", "bhk": 2, "baths": 2, "area_base": 1050, "price_base": 6500000, "title_fmt": "Affordable 2 BHK Starter Home in {locality}"},
    {"type": "apartment", "bhk": 3, "baths": 2, "area_base": 1500, "price_base": 11500000, "title_fmt": "Elegant 3 BHK Family Apartment in {locality}"},
    {"type": "villa", "bhk": 3, "baths": 3, "area_base": 2400, "price_base": 22000000, "title_fmt": "Charming 3 BHK Independent Duplex Villa in {locality}"},
]

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80",
]

AMENITIES_LIST = [
    {"name": "24/7 Security", "category": "security", "icon": "shield"},
    {"name": "Power Backup", "category": "basic", "icon": "zap"},
    {"name": "Covered Car Parking", "category": "basic", "icon": "car"},
    {"name": "Elevator / Lift", "category": "basic", "icon": "arrow-up"},
    {"name": "Swimming Pool", "category": "leisure", "icon": "waves"},
    {"name": "Gymnasium & Fitness Center", "category": "fitness", "icon": "dumbbell"},
    {"name": "Clubhouse & Community Hall", "category": "leisure", "icon": "users"},
    {"name": "Children's Play Area", "category": "outdoor", "icon": "smile"},
    {"name": "Rainwater Harvesting", "category": "eco", "icon": "droplet"},
    {"name": "Sea View Balcony", "category": "premium", "icon": "eye"},
    {"name": "Metro Proximity", "category": "transit", "icon": "train"},
    {"name": "Landscaped Garden", "category": "outdoor", "icon": "trees"},
]

CHENNAI_POIS = [
    {"name": "Guindy Metro Station", "cat": POICategory.TRANSIT, "sub": "metro", "lat": 13.0076, "lng": 80.2032, "loc": "Guindy"},
    {"name": "Anna Nagar Tower Metro", "cat": POICategory.TRANSIT, "sub": "metro", "lat": 13.0845, "lng": 80.2130, "loc": "Anna Nagar"},
    {"name": "Tidel Park MRTS Station", "cat": POICategory.TRANSIT, "sub": "train", "lat": 12.9870, "lng": 80.2482, "loc": "Taramani"},
    {"name": "Velachery MRTS Station", "cat": POICategory.TRANSIT, "sub": "train", "lat": 12.9772, "lng": 80.2198, "loc": "Velachery"},
    {"name": "Thiruvanmiyur Bus Terminus", "cat": POICategory.TRANSIT, "sub": "bus", "lat": 12.9840, "lng": 80.2580, "loc": "Thiruvanmiyur"},
    {"name": "Chennai Airport Metro Station", "cat": POICategory.TRANSIT, "sub": "metro", "lat": 12.9798, "lng": 80.1650, "loc": "Meenambakkam"},
    {"name": "Apollo Hospitals Greams Road", "cat": POICategory.HOSPITAL, "sub": "multispeciality", "lat": 13.0601, "lng": 80.2520, "loc": "Thousand Lights"},
    {"name": "Fortis Malar Hospital Adyar", "cat": POICategory.HOSPITAL, "sub": "multispeciality", "lat": 13.0070, "lng": 80.2570, "loc": "Adyar"},
    {"name": "MIOT International Hospital", "cat": POICategory.HOSPITAL, "sub": "multispeciality", "lat": 13.0245, "lng": 80.1830, "loc": "Manapakkam"},
    {"name": "Gleneagles Global Health City", "cat": POICategory.HOSPITAL, "sub": "super_speciality", "lat": 12.8980, "lng": 80.1980, "loc": "Perumbakkam"},
    {"name": "Kauvery Hospital Alwarpet", "cat": POICategory.HOSPITAL, "sub": "hospital", "lat": 13.0350, "lng": 80.2530, "loc": "Alwarpet"},
    {"name": "SBOA School & Junior College", "cat": POICategory.SCHOOL, "sub": "cbse", "lat": 13.0880, "lng": 80.1990, "loc": "Anna Nagar West"},
    {"name": "Chettinad Vidyashram", "cat": POICategory.SCHOOL, "sub": "cbse", "lat": 13.0180, "lng": 80.2650, "loc": "R.A. Puram"},
    {"name": "DAV Boys Senior Secondary School", "cat": POICategory.SCHOOL, "sub": "cbse", "lat": 13.0530, "lng": 80.2570, "loc": "Gopalapuram"},
    {"name": "Bala Vidya Mandir", "cat": POICategory.SCHOOL, "sub": "cbse", "lat": 13.0030, "lng": 80.2520, "loc": "Adyar"},
    {"name": "The PSBB Millennium School", "cat": POICategory.SCHOOL, "sub": "cbse", "lat": 13.0110, "lng": 80.1480, "loc": "Gerugambakkam"},
    {"name": "Semmozhi Poonga Botanical Garden", "cat": POICategory.PARK, "sub": "botanical_garden", "lat": 13.0520, "lng": 80.2505, "loc": "Cathedral Road"},
    {"name": "Guindy National Park", "cat": POICategory.PARK, "sub": "national_park", "lat": 13.0040, "lng": 80.2220, "loc": "Guindy"},
    {"name": "Anna Nagar Tower Park", "cat": POICategory.PARK, "sub": "urban_park", "lat": 13.0860, "lng": 80.2140, "loc": "Anna Nagar"},
    {"name": "Besant Nagar Elliot's Beach", "cat": POICategory.PARK, "sub": "beach", "lat": 12.9995, "lng": 80.2680, "loc": "Besant Nagar"},
    {"name": "Adyar Eco Park (Tholkappiya Poonga)", "cat": POICategory.PARK, "sub": "eco_park", "lat": 13.0190, "lng": 80.2680, "loc": "R.A. Puram"},
    {"name": "Phoenix MarketCity Velachery", "cat": POICategory.SUPERMARKET, "sub": "mall", "lat": 12.9915, "lng": 80.2165, "loc": "Velachery"},
    {"name": "VR Chennai Mall", "cat": POICategory.SUPERMARKET, "sub": "mall", "lat": 13.0840, "lng": 80.1980, "loc": "Anna Nagar"},
    {"name": "Express Avenue Mall", "cat": POICategory.SUPERMARKET, "sub": "mall", "lat": 13.0585, "lng": 80.2640, "loc": "Royapettah"},
    {"name": "Nilgiris Supermarket Adyar", "cat": POICategory.SUPERMARKET, "sub": "grocery", "lat": 13.0035, "lng": 80.2540, "loc": "Adyar"},
    {"name": "TIDEL Park", "cat": POICategory.BANK, "sub": "tech_park", "lat": 12.9890, "lng": 80.2475, "loc": "Taramani"},
    {"name": "DLF Cybercity Chennai", "cat": POICategory.BANK, "sub": "tech_park", "lat": 13.0360, "lng": 80.1600, "loc": "Porur"},
    {"name": "Olympia Tech Park", "cat": POICategory.BANK, "sub": "tech_park", "lat": 13.0100, "lng": 80.2080, "loc": "Guindy"},
    {"name": "ELCOT SEZ Sholinganallur", "cat": POICategory.BANK, "sub": "tech_park", "lat": 12.8950, "lng": 80.2310, "loc": "Sholinganallur"},
]


async def seed_all():
    async with async_session_factory() as session:
        # 1. Get or create demo user
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

        # 2. Seed Amenities
        amenity_ids = []
        for am_data in AMENITIES_LIST:
            stmt = select(Amenity).where(Amenity.name == am_data["name"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                am = Amenity(name=am_data["name"], category=am_data["category"], icon=am_data["icon"])
                session.add(am)
                await session.flush()
                amenity_ids.append(am.id)
            else:
                amenity_ids.append(existing.id)

        # 3. Seed Chennai POIs
        for poi_data in CHENNAI_POIS:
            stmt = select(PointOfInterest).where(PointOfInterest.name == poi_data["name"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                pt = Point(poi_data["lng"], poi_data["lat"])
                poi = PointOfInterest(
                    name=poi_data["name"],
                    category=poi_data["cat"],
                    subcategory=poi_data.get("sub"),
                    location=from_shape(pt, srid=4326),
                    address=f"{poi_data['loc']}, Chennai",
                    city="Chennai",
                    locality=poi_data["loc"],
                    is_active=True,
                )
                session.add(poi)
        await session.flush()

        # 4. Seed Bengaluru properties if not existing
        for p_data in BENGALURU_PROPERTIES:
            stmt = select(Property).where(Property.title == p_data["title"])
            existing = (await session.execute(stmt)).scalar_one_or_none()
            if not existing:
                pt = Point(p_data["longitude"], p_data["latitude"])
                p = Property(
                    owner_id=user.id,
                    title=p_data["title"],
                    description=p_data["description"],
                    price=Decimal(str(p_data["price"])),
                    property_type=p_data["property_type"],
                    bedrooms=p_data["bedrooms"],
                    bathrooms=p_data["bathrooms"],
                    area_sqft=p_data["area_sqft"],
                    address=p_data["address"],
                    city=p_data["city"],
                    locality=p_data["locality"],
                    location=from_shape(pt, srid=4326),
                    status=p_data["status"],
                )
                session.add(p)
                await session.flush()
                # Attach images
                for order, img_url in enumerate(IMAGE_URLS[:2]):
                    p_img = PropertyImage(
                        property_id=p.id,
                        image_url=img_url,
                        display_order=order,
                    )
                    session.add(p_img)
                # Attach amenities
                for a_id in amenity_ids[:4]:
                    await session.execute(
                        insert(property_amenities).values(property_id=p.id, amenity_id=a_id)
                    )

        # 5. Seed 100 Chennai properties
        random.seed(42)
        chennai_count = (await session.execute(
            select(func.count()).select_from(Property).where(Property.city == "Chennai")
        )).scalar() or 0

        if chennai_count < 100:
            for i in range(100):
                loc_data = CHENNAI_LOCALITIES[i % len(CHENNAI_LOCALITIES)]
                tmpl = PROPERTY_TEMPLATES[i % len(PROPERTY_TEMPLATES)]
                locality_name = loc_data["locality"]

                lat_jitter = random.uniform(-0.0075, 0.0075)
                lng_jitter = random.uniform(-0.0075, 0.0075)
                prop_lat = round(loc_data["lat"] + lat_jitter, 6)
                prop_lng = round(loc_data["lng"] + lng_jitter, 6)

                base_price = tmpl["price_base"] * loc_data["price_multiplier"]
                variance = random.uniform(0.92, 1.12)
                calculated_price = round(base_price * variance, -4)

                area_var = random.uniform(0.95, 1.10)
                calculated_area = round(tmpl["area_base"] * area_var, 1)

                is_omr = locality_name in ["Sholinganallur", "Thoraipakkam", "Perungudi", "Navalur", "Siruseri", "Karapakkam"]
                omr_tag = ", OMR IT Corridor" if is_omr else ""
                
                title = tmpl["title_fmt"].format(locality=locality_name)
                desc = f"Well-ventilated {tmpl['bhk']} BHK {tmpl['type']} located in {locality_name}{omr_tag}, Chennai. Offers excellent connectivity to IT corridors, schools, and transit."

                pt = Point(prop_lng, prop_lat)
                prop = Property(
                    owner_id=user.id,
                    title=f"{title} #{i+1}",
                    description=desc,
                    price=Decimal(str(calculated_price)),
                    property_type=tmpl["type"],
                    bedrooms=tmpl["bhk"],
                    bathrooms=tmpl["baths"],
                    area_sqft=calculated_area,
                    address=f"Plot #{100+i}, Sector {(i%8)+1}, {locality_name}{omr_tag}",
                    city="Chennai",
                    locality=locality_name,
                    location=from_shape(pt, srid=4326),
                    status="active",
                )
                session.add(prop)
                await session.flush()

                chosen_amenity_ids = random.sample(amenity_ids, k=random.randint(4, 7))
                for a_id in chosen_amenity_ids:
                    await session.execute(
                        insert(property_amenities).values(property_id=prop.id, amenity_id=a_id)
                    )

                img_count = random.randint(1, 3)
                sampled_imgs = random.sample(IMAGE_URLS, k=img_count)
                for order, img_url in enumerate(sampled_imgs):
                    p_img = PropertyImage(
                        property_id=prop.id,
                        image_url=img_url,
                        display_order=order,
                    )
                    session.add(p_img)

        await session.commit()
        total_p = (await session.execute(select(func.count()).select_from(Property))).scalar()
        total_poi = (await session.execute(select(func.count()).select_from(PointOfInterest))).scalar()
        print(f"Seed complete! Database has {total_p} properties and {total_poi} POIs.")


if __name__ == "__main__":
    asyncio.run(seed_all())

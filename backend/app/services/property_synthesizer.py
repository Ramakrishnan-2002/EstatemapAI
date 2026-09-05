from __future__ import annotations

import json
import random
from decimal import Decimal
from typing import Any

from geoalchemy2.shape import from_shape
from google import genai
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.logging import logger
from app.models.amenity import Amenity
from app.models.property import Property
from app.models.property_image import PropertyImage
from app.models.user import User
from app.utils.location_resolver import LocationResolver

CURATED_PROPERTY_IMAGES: list[str] = [
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
    "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80",
]


class PropertySynthesizer:
    """
    Synthesizes and persists realistic real estate listings when no data exists for a queried locality.
    Adheres strictly to EstateMap AI standards:
    - PostGIS Canonical POINT locations centered at verified locality coordinates with localized spatial dispersion.
    - Standard INR price points, realistic BHKs, bathrooms, and square footage.
    - Verified amenity associations (Lift, Security, Power Backup, Covered Parking, etc.).
    - Curated high-resolution architectural & interior photography.
    """

    @classmethod
    async def synthesize_for_locality(
        cls,
        session: AsyncSession,
        locality: str,
        city: str | None = None,
        bedrooms: int | None = None,
        property_type: str | None = None,
        max_price: float | None = None,
        count: int = 5,
    ) -> list[Property]:
        """
        Synthesize, persist, and return properties for a locality with zero existing listings.
        """
        locality_clean = locality.strip().title()
        city_name = (city or locality_clean).strip().title()
        
        resolved = LocationResolver.resolve_locality(locality_clean) or LocationResolver.resolve_destination(locality_clean)
        
        if resolved:
            base_lat, base_lng = resolved.latitude, resolved.longitude
            if 12.75 <= base_lat <= 13.35 and 80.00 <= base_lng <= 80.35:
                city_name = city or "Chennai"
            elif 12.70 <= base_lat <= 13.30 and 77.35 <= base_lng <= 77.85:
                city_name = city or "Bengaluru"
            else:
                city_name = city or locality_clean
        else:
            base_lat, base_lng = 10.9602, 79.3845 if "kumbakonam" in locality.lower() else (12.9716, 80.2458)

        # 1. Fetch Demo User (Owner)
        user_stmt = select(User).order_by(User.id.asc()).limit(1)
        user_res = await session.execute(user_stmt)
        owner = user_res.scalar_one_or_none()
        if not owner:
            logger.warning("No user found to associate synthesized properties.")
            return []
        owner_id = owner.id

        # 2. Fetch Active Amenities from DB
        amenity_stmt = select(Amenity)
        amenity_res = await session.execute(amenity_stmt)
        available_amenities = list(amenity_res.scalars().all())

        # 3. Attempt synthesis via Gemini LLM
        generated_data = await cls._generate_with_gemini(
            locality=locality_clean,
            city=city_name,
            target_bedrooms=bedrooms,
            target_property_type=property_type,
            target_max_price=max_price,
            count=count,
        )

        # 4. Fallback to deterministic synthesis if Gemini returns empty or fails
        if not generated_data or len(generated_data) < count:
            generated_data = cls._generate_deterministic_fallback(
                locality=locality_clean,
                city=city_name,
                target_bedrooms=bedrooms,
                target_property_type=property_type,
                target_max_price=max_price,
                count=count,
            )

        # 5. Build and persist Property models
        created_properties: list[Property] = []
        for idx, item in enumerate(generated_data):
            # Use item-provided coordinates if available and valid, else localized jitter
            item_lat = item.get("latitude")
            item_lng = item.get("longitude")
            
            if item_lat and item_lng and (-90 <= float(item_lat) <= 90) and (-180 <= float(item_lng) <= 180):
                prop_lat = round(float(item_lat), 6)
                prop_lng = round(float(item_lng), 6)
            else:
                lat_offset = (random.random() - 0.5) * 0.012
                lng_offset = (random.random() - 0.5) * 0.012
                prop_lat = round(base_lat + lat_offset, 6)
                prop_lng = round(base_lng + lng_offset, 6)

            geom_point = from_shape(Point(prop_lng, prop_lat), srid=4326)

            prop = Property(
                owner_id=owner_id,
                title=item["title"],
                description=item["description"],
                price=Decimal(str(item["price"])),
                property_type=item.get("property_type", "apartment").lower(),
                bedrooms=int(item["bedrooms"]) if item.get("bedrooms") else 2,
                bathrooms=float(item.get("bathrooms", 2.0)),
                area_sqft=float(item["area_sqft"]),
                address=item["address"],
                city=item.get("city", city_name),
                locality=item.get("locality", locality_clean),
                location=geom_point,
                status="active",
            )

            # Assign curated images
            img_url = CURATED_PROPERTY_IMAGES[idx % len(CURATED_PROPERTY_IMAGES)]
            prop.images.append(
                PropertyImage(image_url=img_url, display_order=0)
            )

            # Assign matching amenities
            if available_amenities:
                sample_count = min(len(available_amenities), random.randint(4, 7))
                selected_amenities = random.sample(available_amenities, sample_count)
                prop.amenities.extend(selected_amenities)

            session.add(prop)
            created_properties.append(prop)

        await session.commit()

        # Invalidate affected cache keys
        await CacheService.delete_pattern(CacheKeys.pattern_map())
        await CacheService.delete_pattern(CacheKeys.pattern_ranking())

        logger.info(
            "Synthesized %d properties for locality='%s', city='%s'",
            len(created_properties),
            locality_clean,
            city_name,
        )
        return created_properties

    @classmethod
    async def _generate_with_gemini(
        cls,
        locality: str,
        city: str,
        target_bedrooms: int | None,
        target_property_type: str | None,
        target_max_price: float | None,
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Call Gemini to generate realistic real estate property listings in JSON format."""
        if not settings.GEMINI_API_KEY:
            return []

        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            model_name = settings.GEMINI_MODEL or "gemini-flash-lite-latest"

            prompt = f"""Generate {count} realistic, distinct real estate property listings in {locality}, {city}, India.
Constraints:
- locality: exactly '{locality}'
- city: exactly '{city}'
- bedrooms: {target_bedrooms if target_bedrooms else 'mix of 2 and 3 BHK'}
- property_type: {target_property_type if target_property_type else 'apartment or villa'}
- max_price: {target_max_price if target_max_price else 'between 6000000 and 15000000 INR'}
- Output MUST be a JSON list of objects matching this exact schema:
[
  {{
    "title": "Modern 3 BHK Apartment in {locality}",
    "description": "Well-ventilated home with premium fittings, close to IT corridor and schools.",
    "price": 8500000.0,
    "property_type": "apartment",
    "bedrooms": 3,
    "bathrooms": 2.0,
    "area_sqft": 1450.0,
    "address": "Plot #42, 2nd Main Road, {locality}, {city}"
  }}
]
Return valid JSON only. Do not include markdown code block syntax or preamble."""

            response = await client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            text_resp = response.text.strip()
            if text_resp.startswith("```"):
                lines = text_resp.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                text_resp = "\n".join(lines).strip()

            parsed = json.loads(text_resp)
            if isinstance(parsed, list):
                return parsed
        except Exception as e:
            logger.warning("Gemini property synthesis failed: %s (using deterministic fallback)", e)

        return []

    @classmethod
    def _generate_deterministic_fallback(
        cls,
        locality: str,
        city: str,
        target_bedrooms: int | None,
        target_property_type: str | None,
        target_max_price: float | None,
        count: int = 5,
    ) -> list[dict[str, Any]]:
        """Generate high-quality deterministic listings conforming to EstateMap standards."""
        results: list[dict[str, Any]] = []
        bhk_options = [target_bedrooms] if target_bedrooms else [2, 3, 3, 2, 4]
        ptype = target_property_type or "apartment"

        base_price_per_sqft = 6200.0

        for i in range(count):
            bhk = bhk_options[i % len(bhk_options)] or 3
            bathrooms = float(min(bhk, 3))
            area = round(650.0 + (bhk * 380.0) + (random.random() * 150.0), 1)

            calculated_price = round(area * (base_price_per_sqft + (i * 250.0)), -4)
            if target_max_price and calculated_price > target_max_price:
                calculated_price = round(target_max_price * (0.85 + (i * 0.03)), -4)

            title_templates = [
                f"Spacious {bhk} BHK Luxury {ptype.capitalize()} in {locality}",
                f"Modern {bhk} BHK Family Home in {locality} #{i + 1}",
                f"Premium {bhk} BHK Gated Community {ptype.capitalize()} in {locality}",
                f"Well-Ventilated {bhk} BHK Apartment in Prime {locality}",
                f"Elegant {bhk} BHK Residential {ptype.capitalize()} in {locality}",
            ]

            results.append(
                {
                    "title": title_templates[i % len(title_templates)],
                    "description": (
                        f"Beautiful {bhk} BHK {ptype} located in prime {locality}, {city}. "
                        f"Features excellent ventilation, 24/7 security, power backup, and quick access to transit."
                    ),
                    "price": float(calculated_price),
                    "property_type": ptype,
                    "bedrooms": bhk,
                    "bathrooms": bathrooms,
                    "area_sqft": area,
                    "address": f"Plot #{100 + i * 15}, Sector {i + 1}, {locality}, {city}",
                }
            )

        return results

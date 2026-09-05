"""
POI Demo Seed Data for EstateMap AI — Phase 7

IMPORTANT: This file contains DEMO DATA ONLY.
These POIs are fictional records with plausible Bengaluru-area coordinates.
They are NOT verified real-world listings.
Do NOT present these as real hospital, school, transit or other facility data.

Coordinates are deterministic — the same seed produces the same dataset.
They are geographically coherent with the property seed fixtures used in
Phase 6 spatial integration tests (centered around MG Road, Bengaluru).

Geographic anchor: Bengaluru city center
  Latitude:  12.9716
  Longitude: 77.5946

Usage:
  This module is designed to be called once during test fixture setup
  or initial development seeding via a management script. It does NOT
  run automatically on app startup.

Data source: Internally authored for demonstration purposes.
Future enhancement: Replace with real OpenStreetMap / government open-data import.
"""

from __future__ import annotations

# Deterministic demo POI records aligned with Bengaluru property fixtures
# Format: (name, category, subcategory, latitude, longitude, address, city, locality)

DEMO_POIS = [
    # ─── Hospitals ────────────────────────────────────────────────────
    (
        "Manipal Hospital Old Airport Road",
        "hospital",
        "private",
        12.9592,
        77.6456,
        "98, HAL Airport Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "St. John's Medical College Hospital",
        "hospital",
        "private",
        12.9375,
        77.6195,
        "Sarjapur Road",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "Bowring and Lady Curzon Hospital",
        "hospital",
        "government",
        12.9788,
        77.6132,
        "Shivajinagar",
        "Bengaluru",
        "Shivajinagar",
    ),
    (
        "M.S. Ramaiah Memorial Hospital",
        "hospital",
        "private",
        13.0212,
        77.5609,
        "MSR Nagar",
        "Bengaluru",
        "Mathikere",
    ),
    (
        "Cloudnine Hospital Whitefield",
        "hospital",
        "private",
        12.9794,
        77.7408,
        "ITPL Road",
        "Bengaluru",
        "Whitefield",
    ),
    # ─── Schools ──────────────────────────────────────────────────────
    (
        "National Public School Koramangala",
        "school",
        "cbse",
        12.9384,
        77.6262,
        "15, 7th Block",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "Bishop Cotton Boys School",
        "school",
        "icse",
        12.9783,
        77.5981,
        "St. Mark's Road",
        "Bengaluru",
        "Central",
    ),
    (
        "Delhi Public School Indiranagar",
        "school",
        "cbse",
        12.9763,
        77.6409,
        "CMH Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "Whitefield Global School",
        "school",
        "cbse",
        12.9762,
        77.7294,
        "Whitefield Main Road",
        "Bengaluru",
        "Whitefield",
    ),
    (
        "Presidency School Jayanagar",
        "school",
        "cbse",
        12.9315,
        77.5829,
        "4th Block Jayanagar",
        "Bengaluru",
        "Jayanagar",
    ),
    (
        "Kendriya Vidyalaya Sadashivanagar",
        "school",
        "cbse",
        13.0096,
        77.5802,
        "Palace Road",
        "Bengaluru",
        "Sadashivanagar",
    ),
    # ─── Transit ──────────────────────────────────────────────────────
    (
        "MG Road Metro Station",
        "transit",
        "metro",
        12.9756,
        77.6086,
        "MG Road",
        "Bengaluru",
        "Central",
    ),
    (
        "Indiranagar Metro Station",
        "transit",
        "metro",
        12.9784,
        77.6408,
        "100 Feet Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "Whitefield Metro Station",
        "transit",
        "metro",
        12.9697,
        77.7495,
        "Whitefield Main Road",
        "Bengaluru",
        "Whitefield",
    ),
    (
        "Koramangala Bus Terminus",
        "transit",
        "bus",
        12.9371,
        77.6109,
        "Koramangala Inner Ring Road",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "KSR Bengaluru City Railway Station",
        "transit",
        "railway",
        12.9773,
        77.5671,
        "Dr. Ambedkar Road",
        "Bengaluru",
        "Majestic",
    ),
    (
        "Majestic BMTC Bus Stand",
        "transit",
        "bus",
        12.9773,
        77.5720,
        "Gubbi Thotadappa Road",
        "Bengaluru",
        "Majestic",
    ),
    # ─── Supermarkets ─────────────────────────────────────────────────
    (
        "Big Bazaar Koramangala",
        "supermarket",
        None,
        12.9335,
        77.6135,
        "Oasis Mall, 4th Block",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "Lulu Mall Hypermarket Bengaluru",
        "supermarket",
        None,
        13.0094,
        77.5661,
        "Lulu Mall, Rajajinagar",
        "Bengaluru",
        "Rajajinagar",
    ),
    (
        "More Supermarket Indiranagar",
        "supermarket",
        None,
        12.9746,
        77.6388,
        "100 Feet Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "Ratnadeep Supermarket Jayanagar",
        "supermarket",
        None,
        12.9299,
        77.5837,
        "Jayanagar 4th Block",
        "Bengaluru",
        "Jayanagar",
    ),
    (
        "Spar Hypermarket Whitefield",
        "supermarket",
        None,
        12.9802,
        77.7320,
        "VR Bengaluru Mall, Whitefield",
        "Bengaluru",
        "Whitefield",
    ),
    # ─── Parks ────────────────────────────────────────────────────────
    (
        "Cubbon Park",
        "park",
        "heritage",
        12.9763,
        77.5929,
        "Kasturba Road",
        "Bengaluru",
        "Central",
    ),
    (
        "Lalbagh Botanical Garden",
        "park",
        "botanical",
        12.9496,
        77.5846,
        "Lalbagh Road",
        "Bengaluru",
        "Lalbagh",
    ),
    (
        "Indiranagar 100 Feet Park",
        "park",
        "neighbourhood",
        12.9768,
        77.6422,
        "100 Feet Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "Koramangala Water Tank Park",
        "park",
        "neighbourhood",
        12.9356,
        77.6228,
        "Koramangala 1st Block",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "Whitefield Heritage Park",
        "park",
        "neighbourhood",
        12.9692,
        77.7468,
        "Whitefield",
        "Bengaluru",
        "Whitefield",
    ),
    # ─── Pharmacies ───────────────────────────────────────────────────
    (
        "MedPlus Pharmacy Indiranagar",
        "pharmacy",
        None,
        12.9755,
        77.6397,
        "100 Feet Road",
        "Bengaluru",
        "Indiranagar",
    ),
    (
        "Apollo Pharmacy Koramangala",
        "pharmacy",
        None,
        12.9354,
        77.6148,
        "5th Block Koramangala",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "Netmeds Pharmacy Central",
        "pharmacy",
        None,
        12.9744,
        77.6084,
        "MG Road",
        "Bengaluru",
        "Central",
    ),
    # ─── Banks ────────────────────────────────────────────────────────
    (
        "HDFC Bank MG Road",
        "bank",
        "private",
        12.9745,
        77.6092,
        "MG Road",
        "Bengaluru",
        "Central",
    ),
    (
        "SBI Koramangala Branch",
        "bank",
        "public",
        12.9352,
        77.6175,
        "6th Block Koramangala",
        "Bengaluru",
        "Koramangala",
    ),
    (
        "ICICI Bank Indiranagar",
        "bank",
        "private",
        12.9760,
        77.6392,
        "100 Feet Road",
        "Bengaluru",
        "Indiranagar",
    ),
]


async def seed_demo_pois() -> int:
    """
    Seed deterministic demo POIs into the database if not already present.
    Returns the count of seeded POIs.
    """
    from sqlalchemy import func, select

    from app.db.session import async_session_factory
    from app.models.poi import PointOfInterest
    from app.utils.geo import point_from_coords

    count = 0
    async with async_session_factory() as session:
        # Check if POIs already exist
        stmt = select(func.count(PointOfInterest.id))
        result = await session.execute(stmt)
        existing_count = result.scalar_one()

        if existing_count > 0:
            return existing_count

        for item in DEMO_POIS:
            name, category, subcategory, lat, lng, address, city, locality = item
            poi = PointOfInterest(
                name=name,
                category=category,
                subcategory=subcategory,
                location=point_from_coords(lat, lng),
                address=address,
                city=city,
                locality=locality,
                is_active=True,
            )
            session.add(poi)
            count += 1

        await session.commit()
    return count


if __name__ == "__main__":
    import asyncio

    seeded = asyncio.run(seed_demo_pois())
    print(f"Successfully seeded {seeded} demo POIs.")

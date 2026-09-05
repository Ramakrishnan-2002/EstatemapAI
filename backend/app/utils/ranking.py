from __future__ import annotations

import math

from app.models.poi_category import POICategory
from app.models.property import Property
from app.schemas.geo import CategoryIntelligence
from app.schemas.ranking import FactorScoreDetail


def clamp(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a floating point value to the inclusive [min_val, max_val] range."""
    if math.isnan(val) or math.isinf(val):
        return min_val
    return max(min_val, min(val, max_val))


def calculate_price_score(
    price: float,
    min_price: float | None = None,
    max_price: float | None = None,
    target_price: float | None = None,
    pool_min_price: float = 0.0,
    pool_max_price: float = 0.0,
) -> tuple[float, str]:
    """
    Calculate price affordability score in range [0.0, 1.0].
    Higher score indicates better affordability / budget alignment.
    """
    if target_price is not None and target_price > 0:
        if price <= target_price:
            # Under budget: reward up to 1.0
            savings_fraction = (target_price - price) / target_price
            score = 0.90 + 0.10 * min(1.0, savings_fraction)
            desc = f"Within target budget (₹{price:,.0f} vs ₹{target_price:,.0f})"
        else:
            # Over budget: penalty proportional to excess
            excess_fraction = (price - target_price) / target_price
            score = max(0.0, 0.90 - 1.5 * excess_fraction)
            desc = f"₹{price:,.0f} (above target budget ₹{target_price:,.0f})"
        return clamp(round(score, 4)), desc

    if max_price is not None and max_price > 0:
        base_min = min_price or 0.0
        range_span = max(1.0, max_price - base_min)
        fraction = (price - base_min) / range_span
        score = 1.0 - fraction
        desc = f"₹{price:,.0f} within requested ₹{base_min:,.0f} - ₹{max_price:,.0f} range"
        return clamp(round(score, 4)), desc

    if pool_max_price > pool_min_price:
        fraction = (price - pool_min_price) / (pool_max_price - pool_min_price)
        score = 1.0 - fraction
        desc = f"₹{price:,.0f} (pool range ₹{pool_min_price:,.0f} - ₹{pool_max_price:,.0f})"
        return clamp(round(score, 4)), desc

    return 1.0, f"Listing price ₹{price:,.0f}"


def calculate_bedroom_score(
    bedrooms: int | None,
    preferred_bedrooms: int | None = None,
) -> tuple[float, str]:
    """
    Calculate bedroom requirement score in range [0.0, 1.0].
    """
    if preferred_bedrooms is None:
        return 1.0, f"{bedrooms or 0} BHK"

    if bedrooms is None:
        return 0.5, "Bedroom count unspecified"

    if bedrooms == preferred_bedrooms:
        return 1.0, f"Exact bedroom match ({bedrooms} BHK)"

    diff = abs(bedrooms - preferred_bedrooms)
    if diff == 1:
        return 0.60, f"{bedrooms} BHK (preferred {preferred_bedrooms} BHK)"
    elif diff == 2:
        return 0.30, f"{bedrooms} BHK (preferred {preferred_bedrooms} BHK)"
    else:
        return 0.10, f"{bedrooms} BHK (preferred {preferred_bedrooms} BHK)"


def calculate_area_score(
    area_sqft: float,
    min_area_sqft: float | None = None,
    pool_min_area: float = 0.0,
    pool_max_area: float = 0.0,
) -> tuple[float, str]:
    """
    Calculate space/area score in range [0.0, 1.0].
    """
    if min_area_sqft is not None and min_area_sqft > 0:
        if area_sqft >= min_area_sqft:
            excess = area_sqft - min_area_sqft
            score = 0.85 + 0.15 * min(1.0, excess / min_area_sqft)
            desc = f"{area_sqft:,.0f} sq ft (exceeds preferred {min_area_sqft:,.0f} sq ft)"
        else:
            fraction = area_sqft / min_area_sqft
            score = 0.85 * fraction
            desc = f"{area_sqft:,.0f} sq ft (below preferred {min_area_sqft:,.0f} sq ft)"
        return clamp(round(score, 4)), desc

    if pool_max_area > pool_min_area:
        fraction = (area_sqft - pool_min_area) / (pool_max_area - pool_min_area)
        score = fraction
        desc = f"{area_sqft:,.0f} sq ft living area"
        return clamp(round(score, 4)), desc

    return 1.0, f"{area_sqft:,.0f} sq ft"


def calculate_locality_score(
    property_locality: str,
    preferred_locality: str | None = None,
) -> tuple[float, str]:
    """
    Calculate neighborhood / locality match score.
    """
    if not preferred_locality or not preferred_locality.strip():
        return 1.0, f"Located in {property_locality}"

    pref = preferred_locality.strip().lower()
    loc = property_locality.strip().lower()

    if pref in loc or loc in pref:
        return 1.0, f"Located in preferred locality ({property_locality})"

    return 0.30, f"Located in {property_locality} (preferred {preferred_locality})"


def calculate_location_score(
    categories_intel: dict[POICategory, CategoryIntelligence] | None,
    preferred_categories: list[POICategory] | None = None,
) -> tuple[float, bool, str]:
    """
    Calculate location intelligence score based on PostGIS POI proximity facts.
    """
    if not categories_intel:
        return 0.5, False, "Location intelligence data unavailable"

    targets = preferred_categories if preferred_categories else list(POICategory)
    if not targets:
        return 1.0, True, "All amenity categories acceptable"

    scores: list[float] = []
    highlights: list[str] = []

    for cat in targets:
        intel = categories_intel.get(cat)
        if intel is None or intel.nearest_distance_km is None:
            # Category has no nearby POI in radius
            scores.append(0.20)
            continue

        d = intel.nearest_distance_km
        if d <= 1.0:
            s = 1.0
        elif d <= 3.0:
            s = 1.0 - 0.35 * ((d - 1.0) / 2.0)
        elif d <= 5.0:
            s = 0.65 - 0.40 * ((d - 3.0) / 2.0)
        else:
            s = max(0.05, 0.25 - 0.20 * min(1.0, (d - 5.0) / 10.0))

        scores.append(s)
        if s >= 0.70:
            highlights.append(f"{cat.value.capitalize()} within {d:.1f}km")

    avg_score = sum(scores) / len(scores) if scores else 0.5
    desc = (
        ", ".join(highlights[:2])
        if highlights
        else f"Nearest amenity index ({avg_score * 100:.0f}%)"
    )
    return clamp(round(avg_score, 4)), True, desc


def calculate_commute_score(
    duration_minutes: float | None,
    destination_name: str | None = None,
) -> tuple[float, bool, str]:
    """
    Calculate commute convenience score in range [0.0, 1.0].
    Shorter duration -> higher score.
    """
    if duration_minutes is None:
        return 0.5, False, "Commute destination not specified"

    if duration_minutes <= 15.0:
        score = 1.0
    elif duration_minutes <= 30.0:
        score = 1.0 - 0.25 * ((duration_minutes - 15.0) / 15.0)
    elif duration_minutes <= 60.0:
        score = 0.75 - 0.50 * ((duration_minutes - 30.0) / 30.0)
    else:
        score = max(0.05, 0.25 - 0.20 * min(1.0, (duration_minutes - 60.0) / 60.0))

    dest_label = destination_name or "destination"
    desc = f"{duration_minutes:.1f} min travel time to {dest_label}"
    return clamp(round(score, 4)), True, desc


def generate_deterministic_explanations(
    breakdown: dict[str, FactorScoreDetail],
    property_obj: Property,
) -> list[str]:
    """
    Produce factual, rule-based explanation bullets without AI.
    Selects top factual strengths based on factor performance.
    """
    bullets: list[str] = []

    # 1. Price check
    price_info = breakdown.get("price")
    if price_info and price_info.score >= 0.85:
        bullets.append("Strong affordability within requested budget range")
    elif price_info and price_info.score >= 0.70:
        bullets.append("Competitive market price for this configuration")

    # 2. Bedrooms check
    bed_info = breakdown.get("bedrooms")
    if bed_info and bed_info.score == 1.0 and property_obj.bedrooms:
        bullets.append(f"Exact {property_obj.bedrooms} BHK configuration match")

    # 3. Commute check
    commute_info = breakdown.get("commute")
    if commute_info and commute_info.available and commute_info.score >= 0.75:
        bullets.append(f"Convenient commute ({commute_info.description})")

    # 4. Location check
    loc_info = breakdown.get("location")
    if loc_info and loc_info.available and loc_info.score >= 0.70:
        bullets.append(f"High location intelligence: {loc_info.description}")

    # 5. Locality match
    locality_info = breakdown.get("locality")
    if locality_info and locality_info.score == 1.0:
        bullets.append(f"Direct match for preferred {property_obj.locality} neighborhood")

    # 6. Area match
    area_info = breakdown.get("area")
    if area_info and area_info.score >= 0.80:
        bullets.append(f"Spacious layout ({property_obj.area_sqft:,.0f} sq ft)")

    if not bullets:
        bullets.append(
            f"Verified {property_obj.property_type.replace('_', ' ')} listing in {property_obj.city}"
        )

    return bullets[:4]

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from geoalchemy2.elements import WKTElement

from app.core.exceptions import EntityNotFoundException
from app.models.property import Property
from app.schemas.comparison import PropertyComparisonRequest
from app.schemas.geo import CategoryIntelligence, LocationIntelligenceResponse
from app.services.commute_service import CommuteResponse
from app.services.comparison_service import ComparisonService, format_inr_amount
from app.services.routing.models import TravelMode


def make_dummy_property(
    prop_id: int,
    title: str,
    price: float,
    area_sqft: float,
    bedrooms: int,
    locality: str,
    lat: float = 12.9716,
    lng: float = 77.5946,
) -> Property:
    p = Property()
    p.id = prop_id
    p.title = title
    p.description = f"Description for {title}"
    p.price = price
    p.area_sqft = area_sqft
    p.bedrooms = bedrooms
    p.bathrooms = 2.0
    p.property_type = "apartment"
    p.address = f"Street in {locality}"
    p.locality = locality
    p.city = "Bengaluru"
    p.status = "active"
    p.location = WKTElement(f"POINT({lng} {lat})", srid=4326)
    p.images = []
    return p


def test_format_inr_amount():
    assert (
        format_inr_amount(6_800_000.0) == "₹68.00 L"
        or format_inr_amount(6_800_000.0) == "₹68 L"
        or "68" in format_inr_amount(6_800_000.0)
    )
    assert "1.85" in format_inr_amount(18_500_000.0)
    assert format_inr_amount(50_000.0) == "₹50,000"


@pytest.mark.asyncio
async def test_compare_properties_2_props_success():
    session = AsyncMock()
    service = ComparisonService(session)

    p1 = make_dummy_property(1, "2 BHK HSR", 6_800_000.0, 1100.0, 2, "HSR Layout", 12.9121, 77.6446)
    p2 = make_dummy_property(
        2, "3 BHK Indiranagar", 18_500_000.0, 2400.0, 3, "Indiranagar", 12.9716, 77.6412
    )

    service.property_repo.get_by_id = AsyncMock(
        side_effect=lambda pid: p1 if pid == 1 else (p2 if pid == 2 else None)
    )

    intel_resp_p1 = LocationIntelligenceResponse(
        property_id=1,
        radius_km=3.0,
        categories={
            "hospital": CategoryIntelligence(nearest_distance_km=3.91, count_within_radius=2),
            "school": CategoryIntelligence(nearest_distance_km=3.53, count_within_radius=5),
        },
    )
    intel_resp_p2 = LocationIntelligenceResponse(
        property_id=2,
        radius_km=3.0,
        categories={
            "hospital": CategoryIntelligence(nearest_distance_km=0.85, count_within_radius=4),
            "school": CategoryIntelligence(nearest_distance_km=1.20, count_within_radius=8),
        },
    )
    service.poi_service.get_location_intelligence = AsyncMock(
        side_effect=lambda pid, radius_km=3.0: intel_resp_p1 if pid == 1 else intel_resp_p2
    )

    from app.schemas.commute import CommuteDestination, CommuteOrigin
    from app.services.routing.models import RouteGeometry

    commute_p1 = CommuteResponse(
        property_id=1,
        origin=CommuteOrigin(latitude=12.9121, longitude=77.6446),
        destination=CommuteDestination(name="MG Road", latitude=12.9744, longitude=77.6084),
        mode=TravelMode.DRIVING,
        distance_meters=10630.0,
        distance_km=10.63,
        duration_seconds=1194.0,
        duration_minutes=19.9,
        geometry=RouteGeometry(
            type="LineString", coordinates=[[77.6446, 12.9121], [77.6084, 12.9744]]
        ),
        provider="mock",
        cached=False,
    )
    commute_p2 = CommuteResponse(
        property_id=2,
        origin=CommuteOrigin(latitude=12.9716, longitude=77.6412),
        destination=CommuteDestination(name="MG Road", latitude=12.9744, longitude=77.6084),
        mode=TravelMode.DRIVING,
        distance_meters=5400.0,
        distance_km=5.40,
        duration_seconds=750.0,
        duration_minutes=12.5,
        geometry=RouteGeometry(
            type="LineString", coordinates=[[77.6412, 12.9716], [77.6084, 12.9744]]
        ),
        provider="mock",
        cached=False,
    )
    service.commute_service.get_property_commute = AsyncMock(
        side_effect=lambda property_id,
        dest_lat,
        dest_lng,
        dest_name=None,
        mode=TravelMode.DRIVING: commute_p1 if property_id == 1 else commute_p2
    )

    req = PropertyComparisonRequest(
        property_ids=[1, 2],
        destination_lat=12.9744,
        destination_lng=77.6084,
        destination_name="MG Road",
        travel_mode=TravelMode.DRIVING,
    )

    with (
        patch("app.cache.CacheService.get_json", return_value=None),
        patch("app.cache.CacheService.set_json", return_value=True),
    ):
        result = await service.compare_properties(req)

    assert len(result.properties) == 2
    assert result.properties[0].label == "Property A"
    assert result.properties[1].label == "Property B"

    # Price assertions
    assert result.properties[0].price == 6_800_000.0
    assert result.properties[0].price_per_sqft == round(6_800_000.0 / 1100.0, 2)
    assert result.best_by_dimension["price"] == "Property A"

    # Space assertions
    assert result.best_by_dimension["space"] == "Property B"
    assert result.properties[1].area_sqft == 2400.0

    # Commute assertions
    assert result.best_by_dimension["commute"] == "Property B"
    assert result.properties[1].commute_duration_mins == 12.5

    # Deterministic summary statements exist
    assert len(result.deterministic_summary) > 0
    assert any("cheaper than" in s for s in result.deterministic_summary)
    assert any("living area" in s for s in result.deterministic_summary)

    # Ranking contribution deltas
    assert len(result.ranking_deltas) == 1
    delta = result.ranking_deltas[0]
    assert delta.winner_label in ["Property A", "Property B"]
    assert "factor_deltas" in delta.model_dump()


@pytest.mark.asyncio
async def test_compare_properties_missing_property_raises_404():
    session = AsyncMock()
    service = ComparisonService(session)
    service.property_repo.get_by_id = AsyncMock(return_value=None)

    req = PropertyComparisonRequest(property_ids=[999, 1000])

    with patch("app.cache.CacheService.get_json", return_value=None):
        with pytest.raises(EntityNotFoundException):
            await service.compare_properties(req)


@pytest.mark.asyncio
async def test_compare_properties_missing_commute_handling():
    session = AsyncMock()
    service = ComparisonService(session)

    p1 = make_dummy_property(1, "2 BHK HSR", 6_800_000.0, 1100.0, 2, "HSR Layout")
    p2 = make_dummy_property(2, "2 BHK Kora", 9_500_000.0, 1350.0, 2, "Koramangala")
    service.property_repo.get_by_id = AsyncMock(side_effect=lambda pid: p1 if pid == 1 else p2)

    service.poi_service.get_location_intelligence = AsyncMock(
        return_value=LocationIntelligenceResponse(property_id=1, radius_km=3.0, categories={})
    )
    # No destination in request -> commute not evaluated
    req = PropertyComparisonRequest(property_ids=[1, 2])

    with (
        patch("app.cache.CacheService.get_json", return_value=None),
        patch("app.cache.CacheService.set_json", return_value=True),
    ):
        result = await service.compare_properties(req)

    assert result.best_by_dimension["commute"] is None
    assert result.properties[0].commute_duration_mins is None
    assert result.properties[1].commute_duration_mins is None
    # Ranking match score is still calculated by redistributing missing commute weight
    assert result.properties[0].ranking_score is not None
    assert result.properties[1].ranking_score is not None

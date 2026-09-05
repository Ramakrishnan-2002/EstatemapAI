from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.comparison import (
    ComparisonDimensionSummary,
    ComparisonResult,
    PropertyComparisonFact,
    PropertyComparisonRequest,
    RankingContributionDelta,
)
from app.schemas.ranking import FactorScoreDetail, RankingWeights
from app.services.routing.models import TravelMode


def test_property_comparison_request_valid_2_properties():
    req = PropertyComparisonRequest(
        property_ids=[1, 2],
        destination_lat=12.9716,
        destination_lng=77.5946,
        destination_name="MG Road",
        travel_mode=TravelMode.DRIVING,
    )
    assert req.property_ids == [1, 2]
    assert req.destination_lat == 12.9716
    assert req.destination_lng == 77.5946
    assert req.travel_mode == TravelMode.DRIVING


def test_property_comparison_request_valid_3_properties():
    req = PropertyComparisonRequest(
        property_ids=[1, 2, 3],
        weights=RankingWeights(price=0.4, commute=0.6),
    )
    assert len(req.property_ids) == 3
    assert req.weights.price == 0.4


def test_property_comparison_request_rejects_under_2_properties():
    with pytest.raises(ValidationError) as exc:
        PropertyComparisonRequest(property_ids=[1])
    assert "at least 2" in str(exc.value).lower()


def test_property_comparison_request_rejects_over_3_properties():
    with pytest.raises(ValidationError) as exc:
        PropertyComparisonRequest(property_ids=[1, 2, 3, 4])
    assert "at most 3" in str(exc.value).lower()


def test_property_comparison_request_rejects_duplicate_ids():
    with pytest.raises(ValidationError) as exc:
        PropertyComparisonRequest(property_ids=[1, 1])
    assert "Duplicate property IDs" in str(exc.value)


def test_property_comparison_request_rejects_incomplete_destination():
    with pytest.raises(ValidationError) as exc:
        PropertyComparisonRequest(
            property_ids=[1, 2],
            destination_lat=12.9716,
            destination_lng=None,
        )
    assert "Both destination_lat and destination_lng must be provided together" in str(exc.value)


def test_comparison_result_structure():
    fact_a = PropertyComparisonFact(
        id=1,
        label="Property A",
        title="Modern 2 BHK",
        price=6_800_000.0,
        price_formatted="₹68.0 L",
        price_per_sqft=6181.82,
        bedrooms=2,
        bathrooms=2.0,
        area_sqft=1100.0,
        property_type="apartment",
        address="100 Feet Rd",
        locality="HSR Layout",
        city="Bengaluru",
        latitude=12.9121,
        longitude=77.6446,
        location_intelligence={"hospital": 3.91, "school": 3.53},
        commute_duration_mins=19.9,
        commute_distance_km=10.63,
        commute_destination="MG Road",
        ranking_score=82.5,
        score_breakdown={
            "price": FactorScoreDetail(
                score=0.91, weight=0.25, weighted_contribution=22.75, available=True
            )
        },
    )
    dim_price = ComparisonDimensionSummary(
        dimension="price",
        best_property_label="Property A",
        best_metric_label="Lowest price (₹68.0 L)",
        metric_name="Price",
        details={"cheapest_label": "Property A"},
        comparison_notes=["Property A is ₹6.0 L cheaper than Property B."],
    )
    ranking_delta = RankingContributionDelta(
        winner_label="Property A",
        loser_label="Property B",
        winner_score=82.5,
        loser_score=78.5,
        net_score_delta=4.0,
        factor_deltas={"commute": 6.5, "price": 2.5, "area": -5.0},
        summary="Property A ranks 4.0 points higher than Property B due to commute and price fit.",
    )
    result = ComparisonResult(
        properties=[fact_a],
        dimensions={"price": dim_price},
        ranking_deltas=[ranking_delta],
        deterministic_summary=["Property A is ₹6.0 L cheaper than Property B."],
        best_by_dimension={"price": "Property A"},
    )
    assert len(result.properties) == 1
    assert result.best_by_dimension["price"] == "Property A"
    assert result.ranking_deltas[0].net_score_delta == 4.0

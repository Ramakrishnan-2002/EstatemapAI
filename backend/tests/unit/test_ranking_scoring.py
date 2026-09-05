import pytest
from pydantic import ValidationError

from app.models.poi_category import POICategory
from app.schemas.geo import CategoryIntelligence
from app.schemas.ranking import RankingWeights
from app.utils.ranking import (
    calculate_area_score,
    calculate_bedroom_score,
    calculate_commute_score,
    calculate_locality_score,
    calculate_location_score,
    calculate_price_score,
    clamp,
)


def test_ranking_weights_defaults_and_normalization():
    weights = RankingWeights()
    assert weights.price == 0.25
    assert weights.bedrooms == 0.20
    assert weights.area == 0.10
    assert weights.location == 0.20
    assert weights.commute == 0.25
    assert weights.locality == 0.00

    normalized = weights.normalize()
    total = sum(normalized.values())
    assert pytest.approx(total, 0.0001) == 1.0
    assert pytest.approx(normalized["price"], 0.0001) == 0.25


def test_ranking_weights_custom_normalization():
    weights = RankingWeights(
        price=10.0, bedrooms=10.0, area=0.0, location=0.0, commute=0.0, locality=0.0
    )
    normalized = weights.normalize()
    assert pytest.approx(normalized["price"], 0.0001) == 0.50
    assert pytest.approx(normalized["bedrooms"], 0.0001) == 0.50
    assert pytest.approx(sum(normalized.values()), 0.0001) == 1.0


def test_ranking_weights_zero_sum_rejected():
    with pytest.raises(ValidationError):
        RankingWeights(price=0.0, bedrooms=0.0, area=0.0, location=0.0, commute=0.0, locality=0.0)


def test_ranking_weights_negative_rejected():
    with pytest.raises(ValidationError):
        RankingWeights(price=-0.5)


def test_clamp_utility():
    assert clamp(0.5) == 0.5
    assert clamp(-0.2) == 0.0
    assert clamp(1.8) == 1.0
    assert clamp(float("nan")) == 0.0
    assert clamp(float("inf")) == 0.0


def test_price_scoring_target_budget():
    # Target: 50 Lakhs
    target = 5000000.0

    # Under budget (40 Lakhs) -> high score (0.92)
    s_under, d_under = calculate_price_score(price=4000000.0, target_price=target)
    assert 0.90 <= s_under <= 1.0
    assert "Within target budget" in d_under

    # Exactly on budget (50 Lakhs) -> 0.90
    s_exact, _ = calculate_price_score(price=5000000.0, target_price=target)
    assert s_exact == 0.90

    # Slightly over budget (55 Lakhs) -> lower score
    s_over, _ = calculate_price_score(price=5500000.0, target_price=target)
    assert s_over < s_exact

    # Far over budget (80 Lakhs) -> 0.0
    s_far, _ = calculate_price_score(price=8000000.0, target_price=target)
    assert s_far == 0.0


def test_bedroom_scoring():
    # Preferred 3 BHK
    s_match, desc = calculate_bedroom_score(bedrooms=3, preferred_bedrooms=3)
    assert s_match == 1.0
    assert "Exact" in desc

    s_1off, _ = calculate_bedroom_score(bedrooms=2, preferred_bedrooms=3)
    assert s_1off == 0.60

    s_2off, _ = calculate_bedroom_score(bedrooms=1, preferred_bedrooms=3)
    assert s_2off == 0.30

    s_none, _ = calculate_bedroom_score(bedrooms=3, preferred_bedrooms=None)
    assert s_none == 1.0


def test_area_scoring():
    # Preferred 1200 sq ft
    s_exceeds, _ = calculate_area_score(area_sqft=1500.0, min_area_sqft=1200.0)
    assert s_exceeds >= 0.85

    s_exact, _ = calculate_area_score(area_sqft=1200.0, min_area_sqft=1200.0)
    assert s_exact == 0.85

    s_below, _ = calculate_area_score(area_sqft=600.0, min_area_sqft=1200.0)
    assert s_below < 0.85


def test_locality_scoring():
    s_match, _ = calculate_locality_score("Indiranagar", "Indiranagar")
    assert s_match == 1.0

    s_sub, _ = calculate_locality_score("Indiranagar 100ft Road", "Indiranagar")
    assert s_sub == 1.0

    s_diff, _ = calculate_locality_score("Whitefield", "Indiranagar")
    assert s_diff == 0.30


def test_location_scoring():
    intel = {
        POICategory.HOSPITAL: CategoryIntelligence(nearest_distance_km=0.8, count_within_radius=2),
        POICategory.SCHOOL: CategoryIntelligence(nearest_distance_km=1.5, count_within_radius=3),
        POICategory.TRANSIT: CategoryIntelligence(nearest_distance_km=None, count_within_radius=0),
    }

    s, avail, desc = calculate_location_score(
        categories_intel=intel,
        preferred_categories=[POICategory.HOSPITAL, POICategory.SCHOOL],
    )
    assert avail is True
    assert 0.70 <= s <= 1.0
    assert "Hospital" in desc

    # Unavailable data
    s_unavail, avail_false, _ = calculate_location_score(None)
    assert avail_false is False
    assert s_unavail == 0.5


def test_commute_scoring():
    # 12 min commute -> 1.0
    s_fast, avail, _ = calculate_commute_score(duration_minutes=12.0, destination_name="Office")
    assert avail is True
    assert s_fast == 1.0

    # 25 min commute -> ~0.833
    s_med, _, _ = calculate_commute_score(duration_minutes=25.0)
    assert 0.75 <= s_med < 1.0

    # 50 min commute -> ~0.416
    s_long, _, _ = calculate_commute_score(duration_minutes=50.0)
    assert 0.25 <= s_long < 0.75

    # No destination
    s_none, avail_none, _ = calculate_commute_score(duration_minutes=None)
    assert avail_none is False
    assert s_none == 0.5

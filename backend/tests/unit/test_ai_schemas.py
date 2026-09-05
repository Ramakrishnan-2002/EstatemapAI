import pytest
from pydantic import ValidationError

from app.models.poi_category import POICategory
from app.schemas.ai import (
    ParseSearchRequest,
    PropertySearchIntent,
)


def test_property_search_intent_valid():
    intent = PropertySearchIntent(
        raw_query="2 BHK in Whitefield under 70 lakh",
        bedrooms=2,
        max_price=7000000.0,
        locality="Whitefield",
        preferred_poi_categories=[POICategory.HOSPITAL],
    )
    assert intent.bedrooms == 2
    assert intent.max_price == 7_000_000.0
    assert intent.locality == "Whitefield"
    assert intent.preferred_poi_categories == ["hospital"]


def test_property_search_intent_string_price_normalization():
    intent = PropertySearchIntent(
        raw_query="3 BHK around 1.5 crore",
        bedrooms=3,
        max_price="1.5 crore",  # type: ignore[arg-type]
        min_price="80 lakh",  # type: ignore[arg-type]
    )
    assert intent.max_price == 15_000_000.0
    assert intent.min_price == 8_000_000.0


def test_property_search_intent_poi_synonym_normalization():
    intent = PropertySearchIntent(
        raw_query="near metro and clinic",
        preferred_poi_categories=["metro", "clinic"],  # type: ignore[arg-type]
    )
    assert POICategory.TRANSIT in intent.preferred_poi_categories
    assert POICategory.HOSPITAL in intent.preferred_poi_categories


def test_property_search_intent_bounds_validation():
    # Negative bedrooms rejected
    with pytest.raises(ValidationError):
        PropertySearchIntent(raw_query="test", bedrooms=-1)

    # Excessive bedrooms rejected
    with pytest.raises(ValidationError):
        PropertySearchIntent(raw_query="test", bedrooms=99)

    # Negative price rejected
    with pytest.raises(ValidationError):
        PropertySearchIntent(raw_query="test", max_price=-500)


def test_parse_search_request_length_bounds():
    # Too short
    with pytest.raises(ValidationError):
        ParseSearchRequest(query="hi")

    # Valid
    req = ParseSearchRequest(query="2 BHK near metro")
    assert req.query == "2 BHK near metro"

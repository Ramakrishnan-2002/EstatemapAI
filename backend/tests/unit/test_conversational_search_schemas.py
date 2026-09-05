from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.poi_category import POICategory
from app.schemas.conversational_search import (
    AllowedSearchField,
    AppliedPatchFeedback,
    AskMapRequest,
    AskMapResponse,
    ConversationAction,
    ConversationalSearchState,
    SearchStatePatch,
)
from app.services.routing.models import TravelMode


def test_conversational_search_state_defaults():
    """Verify default values for ConversationalSearchState."""
    state = ConversationalSearchState()
    assert state.min_price is None
    assert state.max_price is None
    assert state.bedrooms is None
    assert state.bathrooms is None
    assert state.locality is None
    assert state.city is None
    assert state.preferred_poi_categories == []
    assert state.commute_destination is None
    assert state.destination_lat is None
    assert state.destination_lng is None
    assert state.travel_mode == TravelMode.DRIVING
    assert state.max_commute_minutes is None
    assert state.ranking_preset == "balanced"
    assert state.ranking_weights.price == 0.25
    assert state.ranking_weights.bedrooms == 0.20


def test_search_state_patch_price_normalization():
    """Verify Indian currency string normalization in SearchStatePatch."""
    # Test numeric values
    patch_num = SearchStatePatch(min_price=5000000, max_price=12000000)
    assert patch_num.min_price == 5_000_000.0
    assert patch_num.max_price == 12_000_000.0

    # Test string parsing (lakhs & crores)
    patch_str = SearchStatePatch.model_validate({"min_price": "70 Lakhs", "max_price": "1.5 Cr"})
    assert patch_str.min_price == 7_000_000.0
    assert patch_str.max_price == 15_000_000.0


def test_search_state_patch_poi_normalization():
    """Verify POI synonyms normalization in SearchStatePatch."""
    patch = SearchStatePatch.model_validate(
        {
            "add_poi_categories": ["metro", "grocery", "hospital"],
            "remove_poi_categories": ["playground"],
        }
    )
    assert patch.add_poi_categories == [
        POICategory.TRANSIT,
        POICategory.SUPERMARKET,
        POICategory.HOSPITAL,
    ]
    assert patch.remove_poi_categories == [POICategory.PARK]


def test_search_state_patch_bounds_and_actions():
    """Verify enum validations and numerical bounds."""
    patch = SearchStatePatch(
        bedrooms=3,
        bathrooms=2.0,
        min_area_sqft=1200.0,
        max_commute_minutes=45.0,
        requested_action=ConversationAction.REFINE,
        clear_fields=[AllowedSearchField.PRICE],
        target_property_indices=[1, 2],
    )
    assert patch.bedrooms == 3
    assert patch.requested_action == ConversationAction.REFINE
    assert AllowedSearchField.PRICE in patch.clear_fields
    assert patch.target_property_indices == [1, 2]

    # Out of bounds bedrooms validation
    with pytest.raises(ValidationError):
        SearchStatePatch(bedrooms=15)


def test_ask_map_request_and_response_schemas():
    """Verify AskMapRequest and AskMapResponse serialization."""
    req = AskMapRequest(
        message="Find 3 BHK flats in Indiranagar under 2 Cr",
        session_id="session-123",
        current_state=ConversationalSearchState(locality="Indiranagar"),
    )
    assert req.message == "Find 3 BHK flats in Indiranagar under 2 Cr"
    assert req.current_state.locality == "Indiranagar"

    feedback = AppliedPatchFeedback(
        added=["3 BHK requirement", "Budget under ₹2.00 Cr"],
        preserved=["In Indiranagar"],
    )
    res = AskMapResponse(
        session_id="session-123",
        message="Found 2 properties in Indiranagar.",
        action=ConversationAction.REFINE,
        state=ConversationalSearchState(bedrooms=3, max_price=20000000.0, locality="Indiranagar"),
        feedback=feedback,
        total_matches=2,
        map_geojson={"type": "FeatureCollection", "features": []},
    )
    assert res.total_matches == 2
    assert len(res.feedback.added) == 2
    assert res.feedback.preserved == ["In Indiranagar"]

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.poi_category import POICategory
from app.schemas.conversational_search import (
    AllowedSearchField,
    ConversationAction,
    ConversationalSearchState,
    SearchStatePatch,
)
from app.schemas.property import PropertyResponse
from app.schemas.ranking import (
    FactorScoreDetail,
    RankedPropertyItem,
    RankedSearchResponse,
    RankingConfigResponse,
    RankingWeights,
)
from app.services.search_orchestrator import RANKING_PRESETS, SearchOrchestrator


def test_orchestrator_apply_patch_set_operations():
    """Verify state patch SET and REPLACE mutations."""
    current = ConversationalSearchState(locality="Whitefield", bedrooms=2, max_price=7000000.0)
    patch = SearchStatePatch(
        bedrooms=3,
        max_price=12000000.0,
        commute_destination="EcoSpace",
    )

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert new_state.bedrooms == 3
    assert new_state.max_price == 12_000_000.0
    assert new_state.locality == "Whitefield"  # Preserved
    assert new_state.commute_destination == "RMZ EcoSpace"
    assert new_state.destination_lat is not None
    assert unres is None
    assert any("Bedrooms changed to 3 BHK" in m for m in feedback.modified)
    assert any("In Whitefield" in p for p in feedback.preserved)


def test_orchestrator_apply_patch_clear_operations():
    """Verify explicit CLEAR mutations."""
    current = ConversationalSearchState(
        bedrooms=3,
        max_price=15000000.0,
        locality="Indiranagar",
        commute_destination="Manyata Tech Park",
    )
    patch = SearchStatePatch(
        clear_fields=[AllowedSearchField.PRICE, AllowedSearchField.COMMUTE],
        requested_action=ConversationAction.CLEAR_FILTER,
    )

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert new_state.max_price is None
    assert new_state.min_price is None
    assert new_state.commute_destination is None
    assert new_state.destination_lat is None
    assert new_state.bedrooms == 3  # Retained
    assert any("Removed price constraints" in r for r in feedback.removed)


def test_orchestrator_apply_patch_poi_append_and_remove():
    """Verify APPEND and REMOVE POI operations."""
    current = ConversationalSearchState(
        preferred_poi_categories=[POICategory.HOSPITAL, POICategory.PARK]
    )
    patch = SearchStatePatch(
        add_poi_categories=[POICategory.TRANSIT],
        remove_poi_categories=[POICategory.PARK],
    )

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert POICategory.HOSPITAL in new_state.preferred_poi_categories
    assert POICategory.TRANSIT in new_state.preferred_poi_categories
    assert POICategory.PARK not in new_state.preferred_poi_categories


def test_orchestrator_apply_patch_reset_search():
    """Verify RESET_SEARCH resets canonical state to defaults."""
    current = ConversationalSearchState(
        bedrooms=3,
        max_price=15000000.0,
        locality="Indiranagar",
        preferred_poi_categories=[POICategory.HOSPITAL],
    )
    patch = SearchStatePatch(requested_action=ConversationAction.RESET_SEARCH)

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert new_state.bedrooms is None
    assert new_state.max_price is None
    assert new_state.locality is None
    assert new_state.preferred_poi_categories == []
    assert len(feedback.removed) > 0


def test_orchestrator_ranking_preset_mutation():
    """Verify switching ranking presets updates weights."""
    current = ConversationalSearchState()
    patch = SearchStatePatch(
        ranking_preset="commute_first",
        requested_action=ConversationAction.RANK,
    )

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert new_state.ranking_preset == "commute_first"
    assert new_state.ranking_weights.commute == RANKING_PRESETS["commute_first"].commute


def test_unresolved_destination_preserves_state():
    """Verify that an unresolved destination does not corrupt canonical search state."""
    current = ConversationalSearchState(
        bedrooms=2,
        locality="HSR Layout",
        max_price=8000000.0,
        commute_destination="Electronic City",
        destination_lat=12.8452,
        destination_lng=77.6602,
    )
    patch = SearchStatePatch(
        commute_destination="Atlantis Under the Sea",
        max_commute_minutes=30.0,
    )

    new_state, feedback, notes, unres = SearchOrchestrator.apply_patch(current, patch)
    assert unres == "Atlantis Under the Sea"
    # Canonical state destination must remain exactly what it was before
    assert new_state.commute_destination == "Electronic City"
    assert new_state.destination_lat == 12.8452
    assert new_state.destination_lng == 77.6602
    assert new_state.bedrooms == 2
    assert new_state.locality == "HSR Layout"


@pytest.mark.asyncio
async def test_typed_commute_hard_filtering_and_response_consistency():
    """
    Verify hard commute filtering uses typed numeric commute duration:
    - dur <= max_commute -> kept
    - dur > max_commute -> excluded
    - dur is None -> excluded (fail closed)
    - ranked_search_response and items are consistent.
    """
    mock_session = MagicMock()
    orchestrator = SearchOrchestrator(mock_session)

    def create_mock_item(prop_id: int, title: str, duration: float | None) -> RankedPropertyItem:
        return RankedPropertyItem(
            rank=1,
            property=PropertyResponse(
                id=prop_id,
                title=title,
                price=7500000.0,
                property_type="apartment",
                bedrooms=2,
                bathrooms=2,
                area_sqft=1200.0,
                address="Test Road",
                locality="HSR Layout",
                city="Bengaluru",
                latitude=12.9121,
                longitude=77.6446,
                status="active",
                owner_id=1,
                created_at="2026-01-01T00:00:00",
                images=[],
                amenities=[],
            ),
            final_score=85.0,
            score_breakdown={
                "commute": FactorScoreDetail(
                    score=0.8,
                    weight=0.25,
                    weighted_contribution=20.0,
                    available=duration is not None,
                    description=f"{duration} mins"
                    if duration is not None
                    else "Commute unavailable",
                    raw_value=duration,
                )
            },
            commute_duration_minutes=duration,
            explanations=[],
        )

    mock_items = [
        create_mock_item(101, "Fast Commute (20m)", 20.0),
        create_mock_item(102, "Boundary Commute (30m)", 30.0),
        create_mock_item(103, "Too Far (31m)", 31.0),
        create_mock_item(104, "Missing Commute (None)", None),
    ]

    mock_ranked_res = RankedSearchResponse(
        total_candidates=4,
        ranking_config=RankingConfigResponse(
            algorithm_version="v1.0",
            weights=RankingWeights(),
            candidate_pool_size=4,
        ),
        items=mock_items,
        page=1,
        page_size=10,
        total_pages=1,
    )

    orchestrator.ranking_service.rank_properties = AsyncMock(return_value=mock_ranked_res)

    current_state = ConversationalSearchState(
        locality="HSR Layout",
        commute_destination="Electronic City",
        destination_lat=12.8452,
        destination_lng=77.6602,
    )
    patch = SearchStatePatch(max_commute_minutes=30.0, requested_action=ConversationAction.SEARCH)

    response = await orchestrator.execute(
        current_state=current_state,
        patch=patch,
        user_message="Within 30 minutes of Electronic City",
    )

    assert response.total_matches == 2
    assert len(response.items) == 2
    assert response.items[0].property.id == 101
    assert response.items[0].rank == 1
    assert response.items[0].commute_duration_minutes == 20.0

    assert response.items[1].property.id == 102
    assert response.items[1].rank == 2
    assert response.items[1].commute_duration_minutes == 30.0

    # Verify ranked_search_response matches the hard-filtered items exactly
    assert response.ranked_search_response is not None
    assert response.ranked_search_response.total_candidates == 2
    assert len(response.ranked_search_response.items) == 2

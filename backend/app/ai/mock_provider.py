from __future__ import annotations

import re
from typing import Any

from app.ai.base import AIProvider
from app.models.poi_category import POICategory
from app.schemas.ai import PropertySearchIntent
from app.schemas.conversational_search import (
    AllowedSearchField,
    ConversationAction,
    SearchStatePatch,
)


class MockAIProvider(AIProvider):
    """
    Mock AI Provider for deterministic offline testing and CI environments.
    """

    def __init__(self, model_name: str = "mock-model") -> None:
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    async def check_health(self) -> dict[str, Any]:
        return {
            "reachable": True,
            "model_available": True,
            "available_models": [self._model_name],
            "latency_ms": 1.0,
            "error": None,
        }

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        # Simple heuristic parser for mock testing
        intent = PropertySearchIntent(
            raw_query=user_query,
            bedrooms=2
            if "2" in user_query or "two" in user_query.lower()
            else (3 if "3" in user_query else None),
            max_price=7_000_000.0 if "70" in user_query else None,
            locality="Whitefield" if "whitefield" in user_query.lower() else None,
            city="Bengaluru",
            preferred_poi_categories=[POICategory.HOSPITAL]
            if "hospital" in user_query.lower()
            else [],
            confidence=0.95,
        )
        return intent, 2.5

    async def parse_search_patch(
        self, current_state: dict[str, Any], user_message: str
    ) -> tuple[SearchStatePatch, float]:
        """Heuristic patch parser for mock unit and integration testing."""
        msg = user_message.lower()

        # Dedicated action routing
        if "reset" in msg or "start over" in msg or "clear all" in msg:
            return SearchStatePatch(
                requested_action=ConversationAction.RESET_SEARCH,
                clear_fields=[
                    AllowedSearchField.PRICE,
                    AllowedSearchField.BEDROOMS,
                    AllowedSearchField.LOCALITY,
                    AllowedSearchField.COMMUTE,
                    AllowedSearchField.POI_CATEGORIES,
                ],
                confidence=1.0,
            ), 1.5

        if "compare" in msg:
            return SearchStatePatch(
                requested_action=ConversationAction.COMPARE,
                target_property_indices=[1, 2],
                confidence=1.0,
            ), 1.5

        if "explain" in msg or "why" in msg:
            return SearchStatePatch(
                requested_action=ConversationAction.EXPLAIN,
                target_property_indices=[1],
                confidence=1.0,
            ), 1.5

        # Clear filters
        clear_fields: list[AllowedSearchField] = []
        if (
            "remove budget" in msg
            or "clear budget" in msg
            or "remove price" in msg
            or "no budget" in msg
            or "remove the budget" in msg
            or "budget limit" in msg
            or "no price" in msg
        ):
            clear_fields.append(AllowedSearchField.PRICE)
        if "remove bedroom" in msg or "any bedroom" in msg:
            clear_fields.append(AllowedSearchField.BEDROOMS)
        if "remove location" in msg or "any location" in msg or "clear locality" in msg:
            clear_fields.append(AllowedSearchField.LOCALITY)
        if "remove commute" in msg or "clear commute" in msg:
            clear_fields.append(AllowedSearchField.COMMUTE)

        action = ConversationAction.CLEAR_FILTER if clear_fields else ConversationAction.REFINE

        # Presets
        ranking_preset = None
        if "commute" in msg and ("prioritize" in msg or "first" in msg or "preference" in msg):
            ranking_preset = "commute_first"
            action = ConversationAction.RANK
        elif "budget" in msg and ("prioritize" in msg or "first" in msg or "preference" in msg):
            ranking_preset = "budget_first"
            action = ConversationAction.RANK
        elif "space" in msg and ("prioritize" in msg or "first" in msg):
            ranking_preset = "space_first"
            action = ConversationAction.RANK

        # Bedrooms
        bedrooms = None
        if "3 bhk" in msg or "3 bedroom" in msg or "3-bedroom" in msg or "3bhk" in msg:
            bedrooms = 3
        elif "2 bhk" in msg or "2 bedroom" in msg or "2-bedroom" in msg or "2bhk" in msg:
            bedrooms = 2
        elif "4 bhk" in msg or "4 bedroom" in msg or "4-bedroom" in msg or "4bhk" in msg:
            bedrooms = 4
        elif "1 bhk" in msg or "1 bedroom" in msg or "1-bedroom" in msg or "1bhk" in msg:
            bedrooms = 1

        # Price
        max_price = None
        if "70 lakh" in msg or "70l" in msg or "70 l" in msg:
            max_price = 7_000_000.0
        elif "80 lakh" in msg or "80l" in msg:
            max_price = 8_000_000.0
        elif "1.2 crore" in msg or "1.2 cr" in msg or "1.2cr" in msg:
            max_price = 12_000_000.0
        elif "1.5 crore" in msg or "1.5 cr" in msg or "1.5cr" in msg:
            max_price = 15_000_000.0
        elif "2 crore" in msg or "2 cr" in msg or "2cr" in msg:
            max_price = 20_000_000.0
        elif "2.5 crore" in msg or "2.5 cr" in msg:
            max_price = 25_000_000.0

        # Locality
        locality = None
        if "whitefield" in msg:
            locality = "Whitefield"
        elif "indiranagar" in msg:
            locality = "Indiranagar"
        elif "koramangala" in msg:
            locality = "Koramangala"
        elif "hsr" in msg:
            locality = "HSR Layout"
        elif "bellandur" in msg:
            locality = "Bellandur"

        # Commute
        commute_destination = None
        if "ecospace" in msg or "eco space" in msg:
            commute_destination = "EcoSpace"
        elif "manyata" in msg:
            commute_destination = "Manyata Tech Park"
        elif "electronic city" in msg or "e-city" in msg:
            commute_destination = "Electronic City"
        elif "bagmane" in msg:
            commute_destination = "Bagmane Tech Park"
        elif "atlantis" in msg:
            commute_destination = "Atlantis Unknown"

        # POIs
        add_pois: list[POICategory] = []
        remove_pois: list[POICategory] = []
        if "hospital" in msg or "clinic" in msg:
            add_pois.append(POICategory.HOSPITAL)
        if "school" in msg:
            add_pois.append(POICategory.SCHOOL)
        if "metro" in msg or "transit" in msg:
            add_pois.append(POICategory.TRANSIT)
        if "park" in msg or "garden" in msg:
            add_pois.append(POICategory.PARK)
        if "supermarket" in msg or "grocery" in msg:
            add_pois.append(POICategory.SUPERMARKET)

        # Commute duration limit (e.g. "within 30 minutes", "under 20 mins")
        max_commute_minutes = None
        comm_match = re.search(r"(?:within|under|less than|max)\s+(\d+)\s*(?:mins?|minutes?)", msg)
        if comm_match:
            max_commute_minutes = float(comm_match.group(1))

        patch = SearchStatePatch(
            bedrooms=bedrooms,
            max_price=max_price,
            locality=locality,
            commute_destination=commute_destination,
            max_commute_minutes=max_commute_minutes,
            add_poi_categories=add_pois,
            remove_poi_categories=remove_pois,
            ranking_preset=ranking_preset,
            clear_fields=clear_fields,
            requested_action=action,
            confidence=0.95,
        )
        return patch, 2.0

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        prop = context.get("property", {})
        title = prop.get("title", "this property")
        price = prop.get("price", "fair price")
        return (
            f"Factual Summary: {title} listed at ₹{price} matches your search criteria with direct road access.",
            3.0,
        )

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        props = context.get("properties", {})
        prop_labels = (
            list(props.keys()) if isinstance(props, dict) else ["Property A", "Property B"]
        )
        diffs = context.get("verified_statements", [])
        diff_text = (
            " ".join(diffs[:2])
            if diffs
            else "Both properties offer distinct trade-offs across budget and space."
        )
        return (
            f"Comparison Narrative: Evaluating {', '.join(prop_labels)}. {diff_text}",
            2.0,
        )

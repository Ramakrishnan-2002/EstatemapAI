from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import patch

import pytest
from geoalchemy2.shape import from_shape
from httpx import AsyncClient
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.ai.router import AIRouter
from app.core.exceptions import AIProviderUnavailableException
from app.models.poi_category import POICategory
from app.models.property import Property
from app.models.user import User
from app.schemas.ai import PropertySearchIntent
from app.schemas.conversational_search import (
    AllowedSearchField,
    ConversationAction,
    ConversationalSearchState,
    SearchStatePatch,
)


class SpyAskMapAIProvider(AIProvider):
    """Spy provider for multi-turn conversational testing."""

    def __init__(self, name: str = "ollama") -> None:
        self._name = name
        self.last_received_state: dict[str, Any] | None = None
        self.last_received_message: str | None = None

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return "spy-conversational-model"

    async def check_health(self) -> dict[str, Any]:
        return {
            "reachable": True,
            "model_available": True,
            "available_models": ["spy-conversational-model"],
        }

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        return PropertySearchIntent(raw_query=user_query, confidence=1.0), 1.0

    async def parse_search_patch(
        self, current_state: dict[str, Any], user_message: str
    ) -> tuple[SearchStatePatch, float]:
        self.last_received_state = current_state
        self.last_received_message = user_message
        msg = user_message.lower()

        if "reset" in msg or "start over" in msg:
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
            ), 1.0

        if "compare" in msg:
            return SearchStatePatch(
                requested_action=ConversationAction.COMPARE,
                target_property_indices=[1, 2],
                confidence=1.0,
            ), 1.0

        if "explain" in msg or "why" in msg:
            return SearchStatePatch(
                requested_action=ConversationAction.EXPLAIN,
                target_property_indices=[1],
                confidence=1.0,
            ), 1.0

        clear_fields: list[AllowedSearchField] = []
        if (
            "remove price" in msg
            or "remove budget" in msg
            or "no budget" in msg
            or "remove the price" in msg
        ):
            clear_fields.append(AllowedSearchField.PRICE)

        action = ConversationAction.CLEAR_FILTER if clear_fields else ConversationAction.REFINE

        bedrooms = None
        if "3 bhk" in msg:
            bedrooms = 3
        elif "2 bhk" in msg:
            bedrooms = 2

        max_price = None
        if "70 lakh" in msg or "70l" in msg:
            max_price = 7_000_000.0

        locality = None
        if "whitefield" in msg:
            locality = "Whitefield"
        elif "indiranagar" in msg:
            locality = "Indiranagar"

        commute_dest = None
        if "ecospace" in msg:
            commute_dest = "EcoSpace"
        elif "atlantis" in msg:
            commute_dest = "Atlantis Unknown"

        add_pois: list[POICategory] = []
        if "metro" in msg or "transit" in msg:
            add_pois.append(POICategory.TRANSIT)

        return SearchStatePatch(
            bedrooms=bedrooms,
            max_price=max_price,
            locality=locality,
            commute_destination=commute_dest,
            add_poi_categories=add_pois,
            clear_fields=clear_fields,
            requested_action=action,
            confidence=1.0,
        ), 1.0

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        return "Single explanation", 1.0

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        return "Comparison narrative", 1.0


async def get_or_create_demo_properties(db_session: AsyncSession) -> list[int]:
    user_email = f"ask_tester_{uuid.uuid4().hex[:8]}@estatemap.ai"
    user = User(
        email=user_email,
        hashed_password="hashed_secret_password",
        full_name="Ask Map Tester",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    p1 = Property(
        owner_id=user.id,
        title="2 BHK Palm Grove Whitefield",
        description="Comfortable 2 BHK in Whitefield",
        price=6500000.0,
        property_type="apartment",
        bedrooms=2,
        bathrooms=2.0,
        area_sqft=1050.0,
        address="Whitefield Main Road",
        locality="Whitefield",
        city="Bengaluru",
        location=from_shape(Point(77.7499, 12.9698), srid=4326),
        status="active",
    )
    p2 = Property(
        owner_id=user.id,
        title="3 BHK Prestige Whitefield",
        description="Spacious 3 BHK in Whitefield",
        price=11000000.0,
        property_type="apartment",
        bedrooms=3,
        bathrooms=3.0,
        area_sqft=1800.0,
        address="ECC Road, Whitefield",
        locality="Whitefield",
        city="Bengaluru",
        location=from_shape(Point(77.7505, 12.9710), srid=4326),
        status="active",
    )
    p3 = Property(
        owner_id=user.id,
        title="3 BHK Indiranagar Residence",
        description="Luxury apartment in Indiranagar",
        price=18500000.0,
        property_type="apartment",
        bedrooms=3,
        bathrooms=3.0,
        area_sqft=2200.0,
        address="100ft Road, Indiranagar",
        locality="Indiranagar",
        city="Bengaluru",
        location=from_shape(Point(77.6412, 12.9716), srid=4326),
        status="active",
    )
    db_session.add_all([p1, p2, p3])
    await db_session.commit()
    return [p1.id, p2.id, p3.id]


@pytest.mark.asyncio
async def test_ask_map_multi_turn_conversational_discovery(
    async_client: AsyncClient, db_session: AsyncSession
):
    """
    Test 6-turn multi-turn conversational search orchestration flow:
    1. Search initial: '2 BHK in Whitefield under 70 Lakhs'
    2. Refine criteria: 'Actually make it 3 BHK and commute to EcoSpace'
    3. Clear & Add: 'Remove the price limit and add metro nearby'
    4. Action compare: 'Compare the top two'
    5. Action explain: 'Explain why #1 is ranked first'
    6. Action reset: 'Reset search'
    """
    await get_or_create_demo_properties(db_session)
    spy_provider = SpyAskMapAIProvider("ollama")

    with patch.object(AIRouter, "get_provider", return_value=spy_provider):
        # Turn 1: Initial query
        state_0 = ConversationalSearchState().model_dump()
        r1 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Show me 2 BHK in Whitefield under 70 Lakhs",
                "session_id": "conv-test-1",
                "current_state": state_0,
            },
        )
        assert r1.status_code == 200
        d1 = r1.json()
        assert d1["state"]["bedrooms"] == 2
        assert d1["state"]["max_price"] == 7_000_000.0
        assert d1["state"]["locality"] == "Whitefield"
        assert d1["total_matches"] >= 1
        assert "map_geojson" in d1
        assert len(d1["map_geojson"]["features"]) >= 1

        # Turn 2: Refine bedrooms to 3 and add commute destination EcoSpace
        state_1 = d1["state"]
        r2 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Actually make it 3 BHK and commute to EcoSpace",
                "session_id": "conv-test-1",
                "current_state": state_1,
            },
        )
        assert r2.status_code == 200
        d2 = r2.json()
        assert d2["state"]["bedrooms"] == 3
        assert d2["state"]["commute_destination"] == "RMZ EcoSpace"
        assert d2["state"]["destination_lat"] is not None
        assert d2["state"]["locality"] == "Whitefield"  # Preserved
        assert any("In Whitefield" in p for p in d2["feedback"]["preserved"])

        # Turn 3: Clear price limit and add transit/metro POI
        state_2 = d2["state"]
        r3 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Remove the price limit and add metro nearby",
                "session_id": "conv-test-1",
                "current_state": state_2,
            },
        )
        assert r3.status_code == 200
        d3 = r3.json()
        assert d3["state"]["max_price"] is None
        assert d3["state"]["bedrooms"] == 3  # Preserved
        assert "transit" in d3["state"]["preferred_poi_categories"]
        assert any("Removed price constraints" in r for r in d3["feedback"]["removed"])

        # Turn 4: Dedicated action COMPARE
        state_3 = d3["state"]
        r4 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Compare the top two",
                "session_id": "conv-test-1",
                "current_state": state_3,
            },
        )
        assert r4.status_code == 200
        d4 = r4.json()
        assert d4["action"] == "compare"
        assert d4["comparison_result"] is not None
        assert len(d4["comparison_result"]["properties"]) == 2

        # Turn 5: Dedicated action EXPLAIN
        r5 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Explain why #1 is ranked first",
                "session_id": "conv-test-1",
                "current_state": state_3,
            },
        )
        assert r5.status_code == 200
        d5 = r5.json()
        assert d5["action"] == "explain"
        assert len(d5["explanation_bullets"]) >= 1

        # Turn 6: Dedicated action RESET_SEARCH
        r6 = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Reset search",
                "session_id": "conv-test-1",
                "current_state": state_3,
            },
        )
        assert r6.status_code == 200
        d6 = r6.json()
        assert d6["action"] == "reset_search"
        assert d6["state"]["bedrooms"] is None
        assert d6["state"]["locality"] is None
        assert d6["state"]["max_price"] is None


@pytest.mark.asyncio
async def test_ask_map_unknown_destination_clarification(async_client: AsyncClient):
    """
    Verify unknown destination returns needs_clarification=True
    AND preserves pre-existing canonical search state intact.
    """
    spy_provider = SpyAskMapAIProvider("ollama")

    initial_state = ConversationalSearchState(
        bedrooms=2,
        locality="HSR Layout",
        max_price=8000000.0,
    ).model_dump()

    with patch.object(AIRouter, "get_provider", return_value=spy_provider):
        resp = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Show apartments commuting to Atlantis",
                "current_state": initial_state,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["needs_clarification"] is True
        assert "Atlantis" in data["message"]
        assert data["clarification_prompt"] is not None

        # Critical: Verify canonical search state is NOT contaminated with unresolved destination
        assert data["state"]["bedrooms"] == 2
        assert data["state"]["locality"] == "HSR Layout"
        assert data["state"]["max_price"] == 8000000.0
        assert data["state"]["commute_destination"] is None
        assert data["state"]["destination_lat"] is None


@pytest.mark.asyncio
async def test_ask_map_privacy_allowlist(async_client: AsyncClient):
    """Verify internal database IDs and PII are never passed into AI context."""
    spy_provider = SpyAskMapAIProvider("ollama")

    with patch.object(AIRouter, "get_provider", return_value=spy_provider):
        await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Find 2 BHK in Whitefield",
                "current_state": ConversationalSearchState(
                    bedrooms=2, locality="Whitefield", max_price=8000000.0
                ).model_dump(),
            },
        )
        assert spy_provider.last_received_state is not None
        # Check no internal DB keys
        assert "id" not in spy_provider.last_received_state
        assert "owner_id" not in spy_provider.last_received_state
        assert "user_id" not in spy_provider.last_received_state


@pytest.mark.asyncio
async def test_ask_map_failover_to_deterministic_fallback(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Verify graceful fallback when AI providers fail or timeout."""
    await get_or_create_demo_properties(db_session)

    class FailingProvider(AIProvider):
        @property
        def provider_name(self) -> str:
            return "failing"

        @property
        def model_name(self) -> str:
            return "failing-model"

        async def check_health(self) -> dict[str, Any]:
            return {"reachable": False, "model_available": False}

        async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
            raise AIProviderUnavailableException("failing", "Down")

        async def parse_search_patch(
            self, current_state: dict[str, Any], user_message: str
        ) -> tuple[SearchStatePatch, float]:
            raise AIProviderUnavailableException("failing", "Down")

        async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
            raise AIProviderUnavailableException("failing", "Down")

        async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
            raise AIProviderUnavailableException("failing", "Down")

    with patch.object(AIRouter, "get_provider", return_value=FailingProvider()):
        resp = await async_client.post(
            "/api/v1/ai/ask-map",
            json={
                "message": "Find 2 BHK apartments in Whitefield under 70 Lakhs",
                "current_state": ConversationalSearchState().model_dump(),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["fallback_used"] is True
        assert data["state"]["bedrooms"] == 2
        assert data["state"]["max_price"] == 7_000_000.0

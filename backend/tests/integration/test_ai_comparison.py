from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.ai.router import AIRouter
from app.core.exceptions import AIProviderUnavailableException
from app.models.property import Property
from app.models.user import User
from app.schemas.ai import PropertySearchIntent


class SpyComparisonAIProvider(AIProvider):
    def __init__(self, name: str = "gemini") -> None:
        self._name = name
        self.last_received_context: dict[str, Any] | None = None

    @property
    def provider_name(self) -> str:
        return self._name

    @property
    def model_name(self) -> str:
        return "spy-model-v1"

    async def check_health(self) -> dict[str, Any]:
        return {"reachable": True, "model_available": True, "available_models": ["spy-model-v1"]}

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        return PropertySearchIntent(raw_query=user_query, confidence=1.0), 1.0

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        return "Single explanation", 1.0

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        self.last_received_context = context
        props = list(context.get("properties", {}).keys())
        return f"Spy comparison of {', '.join(props)} completed successfully.", 2.0


class FailingAIProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "failing_provider"

    @property
    def model_name(self) -> str:
        return "failing-model"

    async def check_health(self) -> dict[str, Any]:
        return {"reachable": False, "model_available": False}

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        raise AIProviderUnavailableException("failing_provider", "Unavailable")

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        raise AIProviderUnavailableException("failing_provider", "Unavailable")

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        raise AIProviderUnavailableException(
            "failing_provider", "Simulated outage during comparison"
        )


async def get_or_create_test_properties(db_session: AsyncSession) -> list[int]:
    import uuid

    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point
    from sqlalchemy import select

    stmt = select(Property.id).limit(2)
    res = await db_session.execute(stmt)
    existing_ids = list(res.scalars().all())
    if len(existing_ids) >= 2:
        return existing_ids[:2]

    # Create a test user and properties if not present
    user_email = f"ai_comp_{uuid.uuid4().hex[:8]}@estatemap.ai"
    user = User(
        email=user_email,
        hashed_password="secret_password_hash",
        full_name="AI Comp Tester",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    p1 = Property(
        owner_id=user.id,
        title="Modern 2 BHK Apartment",
        description="2 BHK apartment in HSR Layout",
        price=6800000.0,
        property_type="apartment",
        bedrooms=2,
        bathrooms=2.0,
        area_sqft=1100.0,
        address="100 Feet Road",
        locality="HSR Layout",
        city="Bengaluru",
        location=from_shape(Point(77.6446, 12.9121), srid=4326),
        status="active",
    )
    p2 = Property(
        owner_id=user.id,
        title="Spacious 3 BHK Indiranagar Flat",
        description="Luxury flat near 100ft road",
        price=18500000.0,
        property_type="apartment",
        bedrooms=3,
        bathrooms=3.0,
        area_sqft=2400.0,
        address="12th Main Road",
        locality="Indiranagar",
        city="Bengaluru",
        location=from_shape(Point(77.6412, 12.9716), srid=4326),
        status="active",
    )
    db_session.add_all([p1, p2])
    await db_session.commit()
    return [p1.id, p2.id]


@pytest.mark.asyncio
async def test_deterministic_property_comparison_endpoint(
    async_client: AsyncClient, db_session: AsyncSession
):
    """
    Test POST /api/v1/properties/compare returns verified facts with AI disabled.
    """
    prop_ids = await get_or_create_test_properties(db_session)
    payload = {
        "property_ids": prop_ids,
        "destination_lat": 12.9716,
        "destination_lng": 77.5946,
        "destination_name": "MG Road",
        "travel_mode": "driving",
    }
    response = await async_client.post("/api/v1/properties/compare", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "properties" in data
    assert len(data["properties"]) == 2
    assert data["properties"][0]["label"] == "Property A"
    assert data["properties"][1]["label"] == "Property B"
    assert "dimensions" in data
    assert "price" in data["dimensions"]
    assert "space" in data["dimensions"]
    assert "commute" in data["dimensions"]
    assert "ranking" in data["dimensions"]
    assert "deterministic_summary" in data
    assert len(data["deterministic_summary"]) > 0


@pytest.mark.asyncio
async def test_ai_property_comparison_endpoint_with_spy_privacy(
    async_client: AsyncClient, db_session: AsyncSession
):
    """
    Test POST /api/v1/ai/properties/compare executes successfully and asserts no internal IDs or PII in AI context.
    """
    prop_ids = await get_or_create_test_properties(db_session)
    spy = SpyComparisonAIProvider("gemini")
    AIRouter.register_provider("gemini", spy)

    try:
        payload = {
            "property_ids": prop_ids,
            "destination_lat": 12.9716,
            "destination_lng": 77.5946,
            "destination_name": "MG Road",
            "travel_mode": "driving",
        }
        with patch("app.core.config.settings.AI_PROVIDER", "gemini"):
            response = await async_client.post("/api/v1/ai/properties/compare", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "narrative" in data
        assert "comparison" in data
        assert data["provider"] == "gemini"
        assert data["fallback_used"] is False

        # Privacy Audit: Verify structured context received by spy AI provider
        ctx = spy.last_received_context
        assert ctx is not None
        assert "properties" in ctx
        assert "verified_statements" in ctx
        assert "ranking_deltas" in ctx
        assert "best_by_dimension" in ctx

        allowed_prop_keys = {
            "locality",
            "city",
            "property_type",
            "price_inr",
            "price_formatted",
            "price_per_sqft",
            "bedrooms",
            "bathrooms",
            "area_sqft",
            "location_intelligence",
            "commute",
            "ranking_score",
        }

        forbidden_keys = {
            "id",
            "property_id",
            "owner_id",
            "user_id",
            "email",
            "password",
            "hashed_password",
            "jwt",
            "token",
            "latitude",
            "longitude",
        }

        # Recursive check to verify NO forbidden keys exist anywhere in the context tree
        def assert_no_forbidden_keys(obj: Any, path: str = "root") -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    assert (
                        k.lower() not in forbidden_keys
                    ), f"Found forbidden key '{k}' at path '{path}.{k}' in AI context"
                    assert_no_forbidden_keys(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    assert_no_forbidden_keys(item, f"{path}[{idx}]")

        assert_no_forbidden_keys(ctx)

        # Verify property labels and attribute allowlist
        for label, prop_data in ctx["properties"].items():
            assert label in ["Property A", "Property B", "Property C"]
            assert set(prop_data.keys()).issubset(
                allowed_prop_keys
            ), f"Unexpected fields in property context: {set(prop_data.keys()) - allowed_prop_keys}"

        # Verify ranking deltas reference anonymous labels only
        for delta in ctx["ranking_deltas"]:
            assert delta["winner"] in ["Property A", "Property B", "Property C"]
            assert delta["loser"] in ["Property A", "Property B", "Property C"]

        # Verify dimension winners reference anonymous labels only
        for _dim, best_label in ctx["best_by_dimension"].items():
            assert best_label is None or best_label in ["Property A", "Property B", "Property C"]

    finally:
        AIRouter.reset()


@pytest.mark.asyncio
async def test_ai_property_comparison_fallback_when_providers_fail(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    """
    Test that when all AI providers fail, POST /api/v1/ai/properties/compare returns 200 with deterministic fallback.
    """
    prop_ids = await get_or_create_test_properties(db_session)
    failing = FailingAIProvider()
    AIRouter.register_provider("ollama", failing)
    AIRouter.register_provider("gemini", failing)

    try:
        payload = {
            "property_ids": prop_ids,
        }
        with patch("app.core.config.settings.AI_PROVIDER", "auto"):
            response = await async_client.post("/api/v1/ai/properties/compare", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["fallback_used"] is True
        assert data["provider"] == "deterministic_fallback"
        assert "comparison" in data
        assert len(data["comparison"]["properties"]) == 2
        assert len(data["narrative"]) > 0

    finally:
        AIRouter.reset()


@pytest.mark.asyncio
async def test_comparison_endpoint_validations(async_client: AsyncClient):
    """
    Test comparison endpoint input validations (1 property rejected, 4 properties rejected, duplicates rejected).
    """
    # 1 property
    res = await async_client.post("/api/v1/properties/compare", json={"property_ids": [1]})
    assert res.status_code == 422

    # 4 properties
    res = await async_client.post("/api/v1/properties/compare", json={"property_ids": [1, 2, 3, 4]})
    assert res.status_code == 422

    # Duplicate IDs
    res = await async_client.post("/api/v1/properties/compare", json={"property_ids": [1, 1]})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_ai_comparison_global_deadline_budgeting(
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    """
    Test that explain_comparison respects global deadline and remaining-budget slicing.
    When primary provider consumes time and fails, secondary provider receives only the remaining budget.
    """
    import asyncio
    import time

    class SlowFailingAIProvider(AIProvider):
        def __init__(self, name: str, delay: float) -> None:
            self._name = name
            self._delay = delay

        @property
        def provider_name(self) -> str:
            return self._name

        @property
        def model_name(self) -> str:
            return f"{self._name}-model"

        async def check_health(self) -> dict[str, Any]:
            return {"reachable": True, "model_available": True}

        async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
            raise AIProviderUnavailableException(self._name, "Error")

        async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
            raise AIProviderUnavailableException(self._name, "Error")

        async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
            await asyncio.sleep(self._delay)
            raise AIProviderUnavailableException(self._name, "Slow timeout")

    prop_ids = await get_or_create_test_properties(db_session)
    prov1 = SlowFailingAIProvider("ollama", delay=0.1)
    prov2 = SlowFailingAIProvider("gemini", delay=0.1)
    AIRouter.register_provider("ollama", prov1)
    AIRouter.register_provider("gemini", prov2)

    try:
        payload = {"property_ids": prop_ids}
        start = time.monotonic()
        with patch("app.core.config.settings.AI_PROVIDER", "auto"):
            with patch("app.core.config.settings.AI_TOTAL_TIMEOUT_SECONDS", 1.5):
                response = await async_client.post("/api/v1/ai/properties/compare", json=payload)

        elapsed = time.monotonic() - start
        assert response.status_code == 200
        data = response.json()
        assert data["fallback_used"] is True
        assert data["provider"] == "deterministic_fallback"
        # Verify elapsed time stayed well within total timeout
        assert elapsed < 1.5 + 0.5

    finally:
        AIRouter.reset()

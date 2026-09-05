from unittest.mock import AsyncMock, patch

import pytest

from app.ai.mock_provider import MockAIProvider
from app.models.property import Property
from app.schemas.ai import AIExplanationRequest
from app.services.ai_service import AIService


@pytest.mark.asyncio
async def test_ai_service_parse_intent():
    service = AIService(db=None, ai_provider=MockAIProvider())  # type: ignore[arg-type]
    res = await service.parse_search_intent(
        "2 BHK under 70 lakh in Whitefield with hospital access"
    )
    assert res.provider == "mock"
    assert res.intent.bedrooms == 2
    assert res.intent.max_price == 7_000_000.0
    assert res.intent.locality == "Whitefield"
    assert res.intent.preferred_poi_categories == ["hospital"]


@pytest.mark.asyncio
async def test_ai_service_explain_property_fallback_on_error():
    # Setup mock property and db
    mock_prop = Property(
        id=101,
        title="Brigade Metropolis",
        price=6500000.0,
        bedrooms=2,
        bathrooms=2.0,
        area_sqft=1100.0,
        locality="Whitefield",
        city="Bengaluru",
        property_type="apartment",
        owner_id=1,
    )

    # Provider that throws exception
    faulty_provider = MockAIProvider()
    faulty_provider.explain_property = AsyncMock(side_effect=RuntimeError("Ollama crashed"))  # type: ignore[method-assign]

    service = AIService(db=None, ai_provider=faulty_provider)  # type: ignore[arg-type]

    with patch(
        "app.repositories.property_repository.PropertyRepository.get_by_id",
        new_callable=AsyncMock,
        return_value=mock_prop,
    ):
        with patch(
            "app.services.poi_service.POIService.get_location_intelligence", new_callable=AsyncMock
        ) as mock_poi:
            from app.schemas.geo import CategoryIntelligence, LocationIntelligenceResponse

            mock_poi.return_value = LocationIntelligenceResponse(
                property_id=101,
                radius_km=3.0,
                categories={
                    "hospital": CategoryIntelligence(
                        nearest_distance_km=1.2, count_within_radius=3
                    ),
                },
            )

            res = await service.explain_property(
                property_id=101,
                request=AIExplanationRequest(),
            )

            # Must fallback gracefully to deterministic explanation
            assert res.property_id == 101
            assert res.fallback_used is True
            assert res.provider == "deterministic_fallback"
            assert "2 BHK apartment in Whitefield" in res.explanation
            assert "₹6,500,000" in res.explanation
            assert "hospital (1.2 km)" in res.explanation

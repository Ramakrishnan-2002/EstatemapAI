import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.genai import errors as genai_errors

from app.ai.gemini_provider import GeminiProvider
from app.core.exceptions import (
    AIInvalidResponseException,
    AIProviderAuthFailedException,
    AIProviderRateLimitedException,
    AIProviderTimeoutException,
)
from app.schemas.ai import PropertySearchIntent


@pytest.fixture
def gemini_provider():
    provider = GeminiProvider(
        api_key="test_dummy_key", model_name="gemini-flash-latest", timeout_seconds=5.0
    )
    # Attach mock async client
    mock_client = MagicMock()
    mock_client.aio = MagicMock()
    mock_client.aio.models = MagicMock()
    provider._client = mock_client
    return provider


@pytest.mark.asyncio
async def test_gemini_provider_init():
    provider = GeminiProvider(api_key="test_key", model_name="gemini-flash-latest")
    assert provider.provider_name == "gemini"
    assert provider.model_name == "gemini-flash-latest"


@pytest.mark.asyncio
async def test_gemini_missing_api_key():
    provider = GeminiProvider(api_key="", model_name="gemini-flash-latest")
    health = await provider.check_health()
    assert health["configured"] is False
    assert health["reachable"] is False
    assert health["authenticated"] is False

    with pytest.raises(AIProviderAuthFailedException):
        await provider.parse_search_intent("2 BHK in Indiranagar")

    with pytest.raises(AIProviderAuthFailedException):
        await provider.explain_property({"property": {"title": "2 BHK"}})


@pytest.mark.asyncio
async def test_gemini_health_success(gemini_provider):
    mock_model = MagicMock()
    mock_model.name = "models/gemini-flash-latest"
    gemini_provider._client.aio.models.get = AsyncMock(return_value=mock_model)

    health = await gemini_provider.check_health()
    assert health["configured"] is True
    assert health["reachable"] is True
    assert health["model_available"] is True
    assert health["authenticated"] is True
    assert "models/gemini-flash-latest" in health["available_models"]


@pytest.mark.asyncio
async def test_gemini_parse_search_intent_success(gemini_provider):
    mock_payload = {
        "raw_query": "2 BHK in Indiranagar under 80 lakh near hospital",
        "bedrooms": 2,
        "bathrooms": None,
        "min_price": None,
        "max_price": 8000000,
        "min_area_sqft": None,
        "property_type": "apartment",
        "locality": "Indiranagar",
        "city": "Bengaluru",
        "preferred_poi_categories": ["hospital"],
        "commute_destination": None,
        "confidence": 0.95,
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(mock_payload)
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=45, candidates_token_count=60, total_token_count=105
    )

    gemini_provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    intent, latency_ms = await gemini_provider.parse_search_intent(
        "2 BHK in Indiranagar under 80 lakh near hospital"
    )

    assert isinstance(intent, PropertySearchIntent)
    assert intent.bedrooms == 2
    assert intent.max_price == 8000000
    assert intent.locality == "Indiranagar"
    assert intent.preferred_poi_categories == ["hospital"]
    assert latency_ms >= 0
    assert gemini_provider.last_usage is not None
    assert gemini_provider.last_usage.total_tokens == 105


@pytest.mark.asyncio
async def test_gemini_explain_property_success(gemini_provider):
    mock_response = MagicMock()
    mock_response.text = "This 2 BHK apartment in Indiranagar offers great proximity to hospitals."
    mock_response.usage_metadata = MagicMock(
        prompt_token_count=80, candidates_token_count=30, total_token_count=110
    )

    gemini_provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    context = {
        "property": {"title": "2BHK Indiranagar", "bedrooms": 2, "price_inr": 8000000},
        "location_intelligence_3km": {"hospital": {"nearest_distance_km": 0.5, "count_nearby": 3}},
    }
    text, latency = await gemini_provider.explain_property(context)

    assert "Indiranagar" in text
    assert latency >= 0
    assert gemini_provider.last_usage.total_tokens == 110


@pytest.mark.asyncio
async def test_gemini_rate_limit_exception(gemini_provider):
    err = genai_errors.ClientError(
        429, {"error": {"message": "RESOURCE_EXHAUSTED: Quota exceeded", "code": 429}}
    )
    gemini_provider._client.aio.models.generate_content = AsyncMock(side_effect=err)

    with pytest.raises(AIProviderRateLimitedException):
        await gemini_provider.parse_search_intent("2 BHK flat")


@pytest.mark.asyncio
async def test_gemini_auth_failure_exception(gemini_provider):
    err = genai_errors.ClientError(
        400, {"error": {"message": "API key not valid. INVALID_ARGUMENT", "code": 400}}
    )
    gemini_provider._client.aio.models.generate_content = AsyncMock(side_effect=err)

    with pytest.raises(AIProviderAuthFailedException):
        await gemini_provider.parse_search_intent("2 BHK flat")


@pytest.mark.asyncio
async def test_gemini_timeout_exception(gemini_provider):
    gemini_provider._client.aio.models.generate_content = AsyncMock(side_effect=TimeoutError())

    with pytest.raises(AIProviderTimeoutException):
        await gemini_provider.parse_search_intent("2 BHK flat")


@pytest.mark.asyncio
async def test_gemini_invalid_json_exception(gemini_provider):
    mock_response = MagicMock()
    mock_response.text = "NOT VALID JSON {foo: bar"

    gemini_provider._client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    with pytest.raises(AIInvalidResponseException):
        await gemini_provider.parse_search_intent("2 BHK flat")

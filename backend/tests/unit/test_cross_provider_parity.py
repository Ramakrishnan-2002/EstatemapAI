import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.gemini_provider import GeminiProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.ollama_provider import OllamaProvider
from app.schemas.ai import PropertySearchIntent


@pytest.fixture
def mock_ollama_client():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {
            "content": json.dumps(
                {
                    "raw_query": "2 BHK in Indiranagar under 80 lakh",
                    "bedrooms": 2,
                    "bathrooms": None,
                    "min_price": None,
                    "max_price": 8000000,
                    "min_area_sqft": None,
                    "property_type": "apartment",
                    "locality": "Indiranagar",
                    "city": "Bengaluru",
                    "preferred_poi_categories": [],
                    "commute_destination": None,
                    "confidence": 1.0,
                }
            )
        }
    }
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.get = AsyncMock(
        return_value=MagicMock(status_code=200, json=lambda: {"models": [{"name": "llama3.2:3b"}]})
    )
    return mock_client


@pytest.mark.asyncio
async def test_provider_contract_parity_intent(mock_ollama_client):
    providers = [
        MockAIProvider(),
    ]

    # Test mock provider
    for prov in providers:
        intent, latency = await prov.parse_search_intent("2 BHK in Indiranagar")
        assert isinstance(intent, PropertySearchIntent)
        assert isinstance(latency, int | float)
        assert latency >= 0

    # Test Ollama with mocked HTTP client
    ollama = OllamaProvider(base_url="http://mock:11434", model_name="llama3.2:3b")
    with patch.object(ollama, "_get_client", return_value=mock_ollama_client):
        intent, latency = await ollama.parse_search_intent("2 BHK in Indiranagar")
        assert isinstance(intent, PropertySearchIntent)
        assert intent.bedrooms == 2
        assert latency >= 0

    # Test Gemini with mocked SDK
    gemini = GeminiProvider(api_key="test_key", model_name="gemini-flash-latest")
    mock_gemini_resp = MagicMock()
    mock_gemini_resp.text = json.dumps(
        {
            "raw_query": "2 BHK in Indiranagar",
            "bedrooms": 2,
            "bathrooms": None,
            "min_price": None,
            "max_price": None,
            "min_area_sqft": None,
            "property_type": "apartment",
            "locality": "Indiranagar",
            "city": "Bengaluru",
            "preferred_poi_categories": [],
            "commute_destination": None,
            "confidence": 1.0,
        }
    )
    mock_gemini_resp.usage_metadata = MagicMock(
        prompt_token_count=10, candidates_token_count=10, total_token_count=20
    )

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_gemini_resp)
    gemini._client = mock_client

    intent, latency = await gemini.parse_search_intent("2 BHK in Indiranagar")
    assert isinstance(intent, PropertySearchIntent)
    assert intent.bedrooms == 2
    assert latency >= 0


@pytest.mark.asyncio
async def test_provider_contract_parity_health():
    mock_prov = MockAIProvider()
    health = await mock_prov.check_health()
    assert health["reachable"] is True
    assert health["model_available"] is True
    assert any("mock" in m for m in health["available_models"])

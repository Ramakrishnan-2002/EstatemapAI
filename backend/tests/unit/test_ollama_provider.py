import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.ai.ollama_provider import OllamaProvider
from app.core.exceptions import (
    AIInvalidResponseException,
    AIProviderTimeoutException,
    AIProviderUnavailableException,
)


@pytest.mark.asyncio
async def test_ollama_health_check_success():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    mock_response = httpx.Response(
        status_code=200,
        json={"models": [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text:latest"}]},
        request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        health = await provider.check_health()
        assert health["reachable"] is True
        assert health["model_available"] is True
        assert "llama3.2:3b" in health["available_models"]
        assert health["error"] is None


@pytest.mark.asyncio
async def test_ollama_health_check_model_missing():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    mock_response = httpx.Response(
        status_code=200,
        json={"models": [{"name": "mistral:7b"}]},
        request=httpx.Request("GET", "http://test-ollama:11434/api/tags"),
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
        health = await provider.check_health()
        assert health["reachable"] is True
        assert health["model_available"] is False
        assert "Model 'llama3.2:3b' not in installed models" in health["error"]


@pytest.mark.asyncio
async def test_ollama_parse_intent_success():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    mock_chat_response = {
        "message": {
            "content": json.dumps(
                {
                    "raw_query": "2 BHK under 70 lakh in Whitefield with hospital access",
                    "bedrooms": 2,
                    "max_price": 7000000,
                    "locality": "Whitefield",
                    "preferred_poi_categories": ["hospital"],
                    "confidence": 0.95,
                }
            )
        }
    }

    mock_response = httpx.Response(
        status_code=200,
        json=mock_chat_response,
        request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        intent, latency = await provider.parse_search_intent(
            "2 BHK under 70 lakh in Whitefield with hospital access"
        )
        assert intent.bedrooms == 2
        assert intent.max_price == 7_000_000.0
        assert intent.locality == "Whitefield"
        assert intent.preferred_poi_categories == ["hospital"]
        assert latency >= 0.0


@pytest.mark.asyncio
async def test_ollama_parse_intent_connection_failure():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    with patch(
        "httpx.AsyncClient.post",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        with pytest.raises(AIProviderUnavailableException):
            await provider.parse_search_intent("2 BHK in Indiranagar")


@pytest.mark.asyncio
async def test_ollama_parse_intent_timeout():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    with patch(
        "httpx.AsyncClient.post",
        side_effect=httpx.TimeoutException("Read timed out"),
    ):
        with pytest.raises(AIProviderTimeoutException):
            await provider.parse_search_intent("3 BHK near metro")


@pytest.mark.asyncio
async def test_ollama_parse_intent_malformed_json():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    mock_response = httpx.Response(
        status_code=200,
        json={"message": {"content": "Sure, here is your json: {not valid json"}},
        request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(AIInvalidResponseException):
            await provider.parse_search_intent("2 BHK near park")


@pytest.mark.asyncio
async def test_ollama_explain_property_success():
    provider = OllamaProvider(base_url="http://test-ollama:11434", model_name="llama3.2:3b")

    mock_chat_response = {
        "message": {
            "content": "This 2 BHK apartment in Whitefield is listed at ₹68 Lakhs and is 1.2 km from the nearest hospital."
        }
    }

    mock_response = httpx.Response(
        status_code=200,
        json=mock_chat_response,
        request=httpx.Request("POST", "http://test-ollama:11434/api/chat"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        explanation, latency = await provider.explain_property({"property": {"price": 6800000}})
        assert "68 Lakhs" in explanation
        assert latency >= 0.0

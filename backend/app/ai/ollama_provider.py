from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from app.ai.base import AIProvider
from app.core.config import settings
from app.core.exceptions import (
    AIInvalidResponseException,
    AIModelNotAvailableException,
    AIOutputValidationException,
    AIProviderTimeoutException,
    AIProviderUnavailableException,
)
from app.core.logging import logger
from app.schemas.ai import PropertySearchIntent
from app.schemas.conversational_search import SearchStatePatch


class OllamaProvider(AIProvider):
    """
    Production-grade Ollama implementation of the AIProvider protocol.
    Communicates asynchronously via HTTP with a local Ollama daemon.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float | None = None,
        keep_alive: str | None = None,
    ) -> None:
        self._base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._model_name = model_name or settings.OLLAMA_MODEL
        self._timeout_seconds = timeout_seconds or settings.OLLAMA_TIMEOUT_SECONDS
        self._keep_alive = keep_alive or settings.OLLAMA_KEEP_ALIVE
        self._prompts_dir = Path(__file__).parent / "prompts"

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load_prompt(self, filename: str) -> str:
        """Load a prompt template from disk."""
        path = self._prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found at {path}")
        return path.read_text(encoding="utf-8")

    async def _get_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout_seconds, connect=5.0),
        )

    async def check_health(self) -> dict[str, Any]:
        """
        Verify Ollama daemon connectivity and check whether the target model is installed.
        """
        is_configured = bool(self._base_url and self._model_name)
        if not is_configured:
            return {
                "configured": False,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": None,
                "error": "OLLAMA_BASE_URL or OLLAMA_MODEL is not configured",
            }

        start = time.perf_counter()
        try:
            async with await self._get_client() as client:
                res = await client.get("/api/tags")
                latency = round((time.perf_counter() - start) * 1000, 2)
                if res.status_code != 200:
                    return {
                        "configured": True,
                        "reachable": False,
                        "model_available": False,
                        "available_models": [],
                        "latency_ms": latency,
                        "error": f"Ollama returned HTTP {res.status_code}",
                    }
                data = res.json()
                models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                # Match model name e.g. "llama3.2:3b" or "llama3.2:3b-latest"
                target_base = self._model_name.split(":")[0]
                model_found = any(self._model_name in m or target_base in m for m in models)
                return {
                    "configured": True,
                    "reachable": True,
                    "model_available": model_found,
                    "available_models": models,
                    "latency_ms": latency,
                    "error": None
                    if model_found
                    else f"Model '{self._model_name}' not in installed models",
                }
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            return {
                "configured": True,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": None,
                "error": f"Cannot connect to Ollama at {self._base_url}: {e}",
            }
        except httpx.TimeoutException:
            return {
                "configured": True,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": None,
                "error": f"Health check timed out after {self._timeout_seconds}s",
            }
        except Exception as e:
            return {
                "configured": True,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": None,
                "error": f"Unexpected health check error: {e}",
            }

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        """
        Extract structured search filters from natural language query using Ollama JSON mode.
        """
        template = self._load_prompt("search_intent_v1.txt")
        prompt = template.replace("{query}", user_query)

        payload = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0,  # Zero temperature for deterministic extraction
            },
            "keep_alive": self._keep_alive,
        }

        start = time.perf_counter()
        try:
            async with await self._get_client() as client:
                res = await client.post("/api/chat", json=payload)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if res.status_code == 404:
                    raise AIModelNotAvailableException(
                        model=self._model_name,
                        provider="ollama",
                        message=f"Ollama model '{self._model_name}' not found. Please run 'ollama pull {self._model_name}'.",
                    )
                if res.status_code != 200:
                    raise AIInvalidResponseException(
                        message=f"Ollama API returned HTTP {res.status_code}: {res.text}",
                        details={"status_code": res.status_code},
                    )

                body = res.json()
                content = body.get("message", {}).get("content", "")
                if not content:
                    raise AIInvalidResponseException(
                        message="Ollama returned an empty response.",
                        details={"response": body},
                    )

                # Parse JSON content
                try:
                    raw_dict = json.loads(content)
                except json.JSONDecodeError as e:
                    logger.warning("Ollama returned invalid JSON: %s | text: %s", e, content)
                    raise AIInvalidResponseException(
                        message="Ollama returned invalid JSON output.",
                        details={"content": content, "error": str(e)},
                    ) from e

                # Inject original query if missing in raw_dict
                if not raw_dict.get("raw_query"):
                    raw_dict["raw_query"] = user_query

                # Validate with Pydantic
                try:
                    intent = PropertySearchIntent.model_validate(raw_dict)
                    return intent, latency_ms
                except ValidationError as e:
                    logger.warning("Ollama output validation failed: %s | raw: %s", e, raw_dict)
                    raise AIOutputValidationException(
                        message="AI-extracted search criteria failed schema validation.",
                        details={"errors": e.errors(include_url=False), "raw": raw_dict},
                    ) from e

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.warning("Ollama connection failed at %s: %s", self._base_url, e)
            raise AIProviderUnavailableException(
                provider="ollama",
                message=f"Cannot connect to Ollama server at {self._base_url}.",
            ) from e
        except httpx.TimeoutException as e:
            logger.warning("Ollama request timed out after %ss", self._timeout_seconds)
            raise AIProviderTimeoutException(
                provider="ollama",
                timeout_seconds=self._timeout_seconds,
            ) from e

    async def parse_search_patch(
        self, current_state: dict[str, Any], user_message: str
    ) -> tuple[SearchStatePatch, float]:
        """
        Extract structured search state patch from conversational query using Ollama JSON mode.
        """
        template = self._load_prompt("conversational_search_patch_v1.txt")
        prompt = template.replace(
            "{current_state}", json.dumps(current_state, indent=2, default=str)
        ).replace("{user_message}", user_message)

        payload = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.0,
            },
            "keep_alive": self._keep_alive,
        }

        start = time.perf_counter()
        try:
            async with await self._get_client() as client:
                res = await client.post("/api/chat", json=payload)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if res.status_code == 404:
                    raise AIModelNotAvailableException(
                        model=self._model_name,
                        provider="ollama",
                        message=f"Ollama model '{self._model_name}' not found. Please run 'ollama pull {self._model_name}'.",
                    )
                if res.status_code != 200:
                    raise AIInvalidResponseException(
                        message=f"Ollama API returned HTTP {res.status_code}: {res.text}",
                        details={"status_code": res.status_code},
                    )

                body = res.json()
                content = body.get("message", {}).get("content", "")
                if not content:
                    raise AIInvalidResponseException(
                        message="Ollama returned an empty response.",
                        details={"response": body},
                    )

                try:
                    raw_dict = json.loads(content)
                except json.JSONDecodeError as e:
                    logger.warning("Ollama invalid JSON: %s | content: %s", e, content)
                    raise AIInvalidResponseException(
                        message="Ollama returned invalid JSON.",
                        details={"content": content, "error": str(e)},
                    ) from e

                try:
                    patch = SearchStatePatch.model_validate(raw_dict)
                    return patch, latency_ms
                except ValidationError as e:
                    logger.warning(
                        "Ollama search patch schema validation failed: %s | raw: %s", e, raw_dict
                    )
                    raise AIOutputValidationException(
                        message="AI-extracted search state patch failed schema validation.",
                        details={"errors": e.errors(include_url=False), "raw": raw_dict},
                    ) from e

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.warning("Ollama connection failed at %s: %s", self._base_url, e)
            raise AIProviderUnavailableException(
                provider="ollama",
                message=f"Cannot connect to Ollama server at {self._base_url}.",
            ) from e
        except httpx.TimeoutException as e:
            logger.warning("Ollama request timed out after %ss", self._timeout_seconds)
            raise AIProviderTimeoutException(
                provider="ollama",
                timeout_seconds=self._timeout_seconds,
            ) from e

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate factual property explanation using bounded context.
        """
        template = self._load_prompt("property_explanation_v1.txt")
        context_json = json.dumps(context, indent=2, default=str)
        prompt = template.replace("{context_json}", context_json)

        payload = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.2,  # Low temperature for factual precision
            },
            "keep_alive": self._keep_alive,
        }

        start = time.perf_counter()
        try:
            async with await self._get_client() as client:
                res = await client.post("/api/chat", json=payload)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if res.status_code == 404:
                    raise AIModelNotAvailableException(
                        model=self._model_name,
                        provider="ollama",
                    )
                if res.status_code != 200:
                    raise AIInvalidResponseException(
                        message=f"Ollama returned HTTP {res.status_code}: {res.text}",
                        details={"status_code": res.status_code},
                    )

                body = res.json()
                content = body.get("message", {}).get("content", "").strip()
                if not content:
                    raise AIInvalidResponseException(
                        message="Ollama returned an empty explanation."
                    )
                return content, latency_ms

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.warning("Ollama connection failed at %s: %s", self._base_url, e)
            raise AIProviderUnavailableException(
                provider="ollama",
                message=f"Cannot connect to Ollama server at {self._base_url}.",
            ) from e
        except httpx.TimeoutException as e:
            logger.warning("Ollama explanation request timed out after %ss", self._timeout_seconds)
            raise AIProviderTimeoutException(
                provider="ollama",
                timeout_seconds=self._timeout_seconds,
            ) from e

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate factual property comparison narrative using bounded context.
        """
        template = self._load_prompt("property_comparison_v1.txt")
        context_json = json.dumps(context, indent=2, default=str)
        prompt = template.replace("{context_json}", context_json)

        payload = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.2,  # Low temperature for factual precision
            },
            "keep_alive": self._keep_alive,
        }

        start = time.perf_counter()
        try:
            async with await self._get_client() as client:
                res = await client.post("/api/chat", json=payload)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if res.status_code == 404:
                    raise AIModelNotAvailableException(
                        model=self._model_name,
                        provider="ollama",
                    )
                if res.status_code != 200:
                    raise AIInvalidResponseException(
                        message=f"Ollama returned HTTP {res.status_code}: {res.text}",
                        details={"status_code": res.status_code},
                    )

                body = res.json()
                content = body.get("message", {}).get("content", "").strip()
                if not content:
                    raise AIInvalidResponseException(
                        message="Ollama returned an empty comparison narrative."
                    )
                return content, latency_ms

        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            logger.warning("Ollama connection failed at %s: %s", self._base_url, e)
            raise AIProviderUnavailableException(
                provider="ollama",
                message=f"Cannot connect to Ollama server at {self._base_url}.",
            ) from e
        except httpx.TimeoutException as e:
            logger.warning("Ollama comparison request timed out after %ss", self._timeout_seconds)
            raise AIProviderTimeoutException(
                provider="ollama",
                timeout_seconds=self._timeout_seconds,
            ) from e

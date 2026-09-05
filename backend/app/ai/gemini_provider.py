from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from pydantic import ValidationError

from app.ai.base import AIProvider
from app.core.config import settings
from app.core.exceptions import (
    AIInvalidResponseException,
    AIModelNotAvailableException,
    AIOutputValidationException,
    AIProviderAuthFailedException,
    AIProviderRateLimitedException,
    AIProviderTimeoutException,
    AIProviderUnavailableException,
)
from app.core.logging import logger
from app.schemas.ai import AIUsageMetadata, PropertySearchIntent
from app.schemas.conversational_search import SearchStatePatch


class GeminiProvider(AIProvider):
    """
    Hosted Google Gemini implementation of the AIProvider protocol using the official Google GenAI SDK (google-genai).
    Provides higher reasoning capability for complex natural language queries and grounded explanations.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self._api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL
        self._timeout_seconds = timeout_seconds or settings.GEMINI_TIMEOUT_SECONDS
        self._prompts_dir = Path(__file__).parent / "prompts"
        self._last_usage: AIUsageMetadata | None = None

        if self._api_key:
            self._client = genai.Client(api_key=self._api_key)
        else:
            self._client = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def last_usage(self) -> AIUsageMetadata | None:
        return self._last_usage

    def _load_prompt(self, filename: str) -> str:
        path = self._prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found at {path}")
        return path.read_text(encoding="utf-8")

    async def check_health(self) -> dict[str, Any]:
        """
        Lightweight health check probing model availability without generating tokens.
        Accurately separates configured, reachable, authenticated, and model_available semantics.
        """
        if not self._api_key or not self._client:
            return {
                "configured": False,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": None,
                "authenticated": False,
                "error": "GEMINI_API_KEY is not configured",
            }

        start = time.perf_counter()
        lookup_name = (
            self._model_name
            if self._model_name.startswith("models/")
            else f"models/{self._model_name}"
        )

        try:
            model_info = await self._client.aio.models.get(model=lookup_name)
            latency = round((time.perf_counter() - start) * 1000, 2)
            return {
                "configured": True,
                "reachable": True,
                "model_available": True,
                "available_models": [getattr(model_info, "name", lookup_name)],
                "latency_ms": latency,
                "authenticated": True,
                "error": None,
            }
        except genai_errors.APIError as e:
            latency = round((time.perf_counter() - start) * 1000, 2)
            code = getattr(e, "code", None)
            message = str(e)
            if code in (400, 401, 403) or "API key" in message:
                logger.warning("Gemini authentication probe failed: %s", e)
                return {
                    "configured": True,
                    "reachable": False,
                    "model_available": False,
                    "available_models": [],
                    "latency_ms": latency,
                    "authenticated": False,
                    "error": "Invalid or unauthorized GEMINI_API_KEY",
                }
            if code == 404 or "NOT_FOUND" in message:
                return {
                    "configured": True,
                    "reachable": True,
                    "model_available": False,
                    "available_models": [],
                    "latency_ms": latency,
                    "authenticated": True,
                    "error": f"Configured Gemini model '{self._model_name}' not found",
                }
            return {
                "configured": True,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": latency,
                "authenticated": None,
                "error": f"Gemini API error: {e}",
            }
        except Exception as e:
            latency = round((time.perf_counter() - start) * 1000, 2)
            logger.warning("Gemini health check error: %s", e)
            return {
                "configured": True,
                "reachable": False,
                "model_available": False,
                "available_models": [],
                "latency_ms": latency,
                "authenticated": None,
                "error": f"Cannot reach Gemini API: {e}",
            }

    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        """
        Extract structured property search intent using Google GenAI SDK with structured JSON output.
        """
        if not self._api_key or not self._client:
            raise AIProviderAuthFailedException(
                provider="gemini",
                message="Cannot execute Gemini parse_search_intent: GEMINI_API_KEY is not configured.",
            )

        template = self._load_prompt("search_intent_v1.txt")
        prompt = template.replace("{query}", user_query)

        config = genai_types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE_INTENT,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
        )

        start = time.perf_counter()
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self._timeout_seconds,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            # Capture token usage
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                self._last_usage = AIUsageMetadata(
                    input_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                    output_tokens=getattr(response.usage_metadata, "candidates_token_count", None),
                    total_tokens=getattr(response.usage_metadata, "total_token_count", None),
                )
            else:
                self._last_usage = None

            raw_text = response.text if hasattr(response, "text") and response.text else ""
            if not raw_text:
                raise AIInvalidResponseException(
                    message="Gemini returned an empty response.",
                    details={"provider": "gemini"},
                )

            # Parse JSON
            try:
                raw_dict = json.loads(raw_text)
            except json.JSONDecodeError as e:
                logger.warning("Gemini invalid JSON: %s | text: %s", e, raw_text)
                raise AIInvalidResponseException(
                    message="Gemini returned invalid JSON output.",
                    details={"raw_text": raw_text, "error": str(e)},
                ) from e

            # Inject query if missing
            if not raw_dict.get("raw_query"):
                raw_dict["raw_query"] = user_query

            # Validate against Pydantic schema
            try:
                intent = PropertySearchIntent.model_validate(raw_dict)
                return intent, latency_ms
            except ValidationError as e:
                logger.warning("Gemini output schema validation failed: %s | raw: %s", e, raw_dict)
                raise AIOutputValidationException(
                    message="AI-extracted search criteria failed schema validation.",
                    details={"errors": e.errors(include_url=False), "raw": raw_dict},
                ) from e

        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            msg = str(e)
            if code in (400, 401, 403) or "API key" in msg:
                raise AIProviderAuthFailedException(
                    provider="gemini",
                    message=f"Gemini API authentication failed: {e}",
                ) from e
            if code == 429 or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                raise AIProviderRateLimitedException(
                    provider="gemini",
                    message=f"Gemini API rate limit or quota exceeded: {e}",
                ) from e
            if code == 404 or "NOT_FOUND" in msg:
                raise AIModelNotAvailableException(
                    model=self._model_name,
                    provider="gemini",
                    message=f"Gemini model '{self._model_name}' not found: {e}",
                ) from e
            logger.warning("Gemini API call failed with APIError: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini API error: {e}",
            ) from e
        except TimeoutError as e:
            raise AIProviderTimeoutException(
                provider="gemini",
                timeout_seconds=self._timeout_seconds,
            ) from e
        except Exception as e:
            if isinstance(e, AIOutputValidationException | AIInvalidResponseException):
                raise
            logger.warning("Gemini API call failed: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Cannot reach Gemini API: {e}",
            ) from e

    async def parse_search_patch(
        self, current_state: dict[str, Any], user_message: str
    ) -> tuple[SearchStatePatch, float]:
        """
        Extract structured search state patch using Google GenAI SDK with structured JSON output.
        """
        if not self._api_key or not self._client:
            raise AIProviderAuthFailedException(
                provider="gemini",
                message="Cannot execute Gemini parse_search_patch: GEMINI_API_KEY is not configured.",
            )

        template = self._load_prompt("conversational_search_patch_v1.txt")
        prompt = template.replace(
            "{current_state}", json.dumps(current_state, indent=2, default=str)
        ).replace("{user_message}", user_message)

        config = genai_types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE_INTENT,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
        )

        start = time.perf_counter()
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self._timeout_seconds,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            # Capture token usage
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                self._last_usage = AIUsageMetadata(
                    input_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                    output_tokens=getattr(response.usage_metadata, "candidates_token_count", None),
                    total_tokens=getattr(response.usage_metadata, "total_token_count", None),
                )
            else:
                self._last_usage = None

            raw_text = response.text if hasattr(response, "text") and response.text else ""
            if not raw_text:
                raise AIInvalidResponseException(
                    message="Gemini returned an empty response.",
                    details={"provider": "gemini"},
                )

            # Parse JSON
            try:
                raw_dict = json.loads(raw_text)
            except json.JSONDecodeError as e:
                logger.warning("Gemini invalid JSON: %s | text: %s", e, raw_text)
                raise AIInvalidResponseException(
                    message="Gemini returned invalid JSON output.",
                    details={"raw_text": raw_text, "error": str(e)},
                ) from e

            # Validate against Pydantic schema
            try:
                patch = SearchStatePatch.model_validate(raw_dict)
                return patch, latency_ms
            except ValidationError as e:
                logger.warning(
                    "Gemini search patch schema validation failed: %s | raw: %s", e, raw_dict
                )
                raise AIOutputValidationException(
                    message="AI-extracted search state patch failed schema validation.",
                    details={"errors": e.errors(include_url=False), "raw": raw_dict},
                ) from e

        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            msg = str(e)
            if code in (400, 401, 403) or "API key" in msg:
                raise AIProviderAuthFailedException(
                    provider="gemini",
                    message=f"Gemini API authentication failed: {e}",
                ) from e
            if code == 429 or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                raise AIProviderRateLimitedException(
                    provider="gemini",
                    message=f"Gemini API rate limit or quota exceeded: {e}",
                ) from e
            if code == 404 or "NOT_FOUND" in msg:
                raise AIModelNotAvailableException(
                    model=self._model_name,
                    provider="gemini",
                    message=f"Gemini model '{self._model_name}' not found: {e}",
                ) from e
            logger.warning("Gemini API call failed with APIError: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini API error: {e}",
            ) from e
        except TimeoutError as e:
            raise AIProviderTimeoutException(
                provider="gemini",
                timeout_seconds=self._timeout_seconds,
            ) from e
        except Exception as e:
            if isinstance(
                e,
                AIOutputValidationException
                | AIInvalidResponseException
                | AIProviderAuthFailedException
                | AIProviderRateLimitedException
                | AIModelNotAvailableException
                | AIProviderTimeoutException
                | AIProviderUnavailableException,
            ):
                raise

            logger.warning("Gemini API call failed: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Cannot reach Gemini API: {e}",
            ) from e

    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate a factual property explanation using bounded context without PII or internal database IDs.
        """
        if not self._api_key or not self._client:
            raise AIProviderAuthFailedException(
                provider="gemini",
                message="Cannot execute Gemini explain_property: GEMINI_API_KEY is not configured.",
            )

        template = self._load_prompt("property_explanation_v1.txt")
        context_json = json.dumps(context, indent=2, default=str)
        prompt = template.replace("{context_json}", context_json)

        config = genai_types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE_EXPLANATION,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        )

        start = time.perf_counter()
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self._timeout_seconds,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            if hasattr(response, "usage_metadata") and response.usage_metadata:
                self._last_usage = AIUsageMetadata(
                    input_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                    output_tokens=getattr(response.usage_metadata, "candidates_token_count", None),
                    total_tokens=getattr(response.usage_metadata, "total_token_count", None),
                )
            else:
                self._last_usage = None

            content = response.text.strip() if hasattr(response, "text") and response.text else ""
            if not content:
                raise AIInvalidResponseException(
                    message="Gemini returned an empty explanation text.",
                    details={"provider": "gemini"},
                )
            return content, latency_ms

        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            msg = str(e)
            if code in (400, 401, 403) or "API key" in msg:
                raise AIProviderAuthFailedException(
                    provider="gemini",
                    message=f"Gemini authentication failed: {e}",
                ) from e
            if code == 429 or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                raise AIProviderRateLimitedException(
                    provider="gemini",
                    message=f"Gemini rate limit or quota exceeded: {e}",
                ) from e
            if code == 404 or "NOT_FOUND" in msg:
                raise AIModelNotAvailableException(
                    model=self._model_name,
                    provider="gemini",
                    message=f"Gemini model '{self._model_name}' not found: {e}",
                ) from e
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini API error: {e}",
            ) from e
        except TimeoutError as e:
            raise AIProviderTimeoutException(
                provider="gemini",
                timeout_seconds=self._timeout_seconds,
            ) from e
        except Exception as e:
            if isinstance(e, AIInvalidResponseException):
                raise
            logger.warning("Gemini explanation generation failed: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini explanation error: {e}",
            ) from e

    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate a factual comparative narrative for 2–3 properties using allowlisted context.
        """
        if not self._api_key or not self._client:
            raise AIProviderAuthFailedException(
                provider="gemini",
                message="Cannot execute Gemini explain_comparison: GEMINI_API_KEY is not configured.",
            )

        template = self._load_prompt("property_comparison_v1.txt")
        context_json = json.dumps(context, indent=2, default=str)
        prompt = template.replace("{context_json}", context_json)

        config = genai_types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE_EXPLANATION,
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
        )

        start = time.perf_counter()
        try:
            response = await asyncio.wait_for(
                self._client.aio.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=config,
                ),
                timeout=self._timeout_seconds,
            )
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            if hasattr(response, "usage_metadata") and response.usage_metadata:
                self._last_usage = AIUsageMetadata(
                    input_tokens=getattr(response.usage_metadata, "prompt_token_count", None),
                    output_tokens=getattr(response.usage_metadata, "candidates_token_count", None),
                    total_tokens=getattr(response.usage_metadata, "total_token_count", None),
                )
            else:
                self._last_usage = None

            content = response.text.strip() if hasattr(response, "text") and response.text else ""
            if not content:
                raise AIInvalidResponseException(
                    message="Gemini returned an empty comparison narrative.",
                    details={"provider": "gemini"},
                )
            return content, latency_ms

        except genai_errors.APIError as e:
            code = getattr(e, "code", None)
            msg = str(e)
            if code in (400, 401, 403) or "API key" in msg:
                raise AIProviderAuthFailedException(
                    provider="gemini",
                    message=f"Gemini authentication failed: {e}",
                ) from e
            if code == 429 or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                raise AIProviderRateLimitedException(
                    provider="gemini",
                    message=f"Gemini rate limit or quota exceeded: {e}",
                ) from e
            if code == 404 or "NOT_FOUND" in msg:
                raise AIModelNotAvailableException(
                    model=self._model_name,
                    provider="gemini",
                    message=f"Gemini model '{self._model_name}' not found: {e}",
                ) from e
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini API error: {e}",
            ) from e
        except TimeoutError as e:
            raise AIProviderTimeoutException(
                provider="gemini",
                timeout_seconds=self._timeout_seconds,
            ) from e
        except Exception as e:
            if isinstance(e, AIInvalidResponseException):
                raise
            logger.warning("Gemini comparison narrative generation failed: %s", e)
            raise AIProviderUnavailableException(
                provider="gemini",
                message=f"Gemini comparison error: {e}",
            ) from e

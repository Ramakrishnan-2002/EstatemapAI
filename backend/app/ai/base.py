from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.schemas.ai import PropertySearchIntent
from app.schemas.conversational_search import SearchStatePatch


class AIProvider(ABC):
    """
    Abstract Base Class / Protocol for all AI Providers (Ollama, Gemini, Mock).
    Defines the contract for natural language interpretation, conversational search orchestration,
    factual explanations, and provider health diagnostics.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'ollama', 'gemini', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Configured model identifier (e.g. 'llama3.2:3b')."""
        pass

    @abstractmethod
    async def check_health(self) -> dict[str, Any]:
        """
        Verify provider reachability and whether the configured model is installed.
        Returns: {
            'reachable': bool,
            'model_available': bool,
            'available_models': list[str],
            'latency_ms': float | None,
            'error': str | None
        }
        """
        pass

    @abstractmethod
    async def parse_search_intent(self, user_query: str) -> tuple[PropertySearchIntent, float]:
        """
        Extract structured property search criteria from a natural language query.
        Returns: (validated_intent, latency_ms)
        """
        pass

    async def parse_search_patch(
        self, current_state: dict[str, Any], user_message: str
    ) -> tuple[SearchStatePatch, float]:
        """
        Extract a validated SearchStatePatch from a conversational query given current canonical state.
        Returns: (validated_patch, latency_ms)
        """
        raise NotImplementedError("parse_search_patch not implemented on this provider")

    @abstractmethod
    async def explain_property(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate a concise, factual explanation of a property based strictly on verified context.
        Returns: (explanation_text, latency_ms)
        """
        pass

    @abstractmethod
    async def explain_comparison(self, context: dict[str, Any]) -> tuple[str, float]:
        """
        Generate a concise, comparative narrative for 2–3 properties based strictly on verified comparison context.
        Returns: (comparison_narrative, latency_ms)
        """
        pass

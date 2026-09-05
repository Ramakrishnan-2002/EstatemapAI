from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.mock_provider import MockAIProvider
from app.ai.ollama_provider import OllamaProvider
from app.core.config import settings
from app.core.exceptions import AIDisabledException


class AIRouter:
    """
    Factory & Dispatcher for Multi-Provider resolution.
    Encapsulates provider lifecycle, lazy instantiation, and caching.
    """

    _providers: dict[str, AIProvider] = {}

    @classmethod
    def get_provider(cls, name: str | None = None, force_refresh: bool = False) -> AIProvider:
        """
        Resolve and return the requested or primary AIProvider instance.
        """
        if not settings.AI_ENABLED:
            raise AIDisabledException()

        provider_name = (name or settings.AI_PROVIDER).lower()
        if provider_name == "auto":
            provider_name = settings.AI_PRIMARY_PROVIDER.lower()

        if not force_refresh and provider_name in cls._providers:
            return cls._providers[provider_name]

        if provider_name == "ollama":
            instance = OllamaProvider(
                base_url=settings.OLLAMA_BASE_URL,
                model_name=settings.OLLAMA_MODEL,
                timeout_seconds=settings.OLLAMA_TIMEOUT_SECONDS,
                keep_alive=settings.OLLAMA_KEEP_ALIVE,
            )
        elif provider_name == "gemini":
            instance = GeminiProvider(
                api_key=settings.GEMINI_API_KEY,
                model_name=settings.GEMINI_MODEL,
                timeout_seconds=settings.GEMINI_TIMEOUT_SECONDS,
            )
        elif provider_name == "mock":
            instance = MockAIProvider()
        else:
            from app.core.exceptions import AIProviderConfigurationException

            raise AIProviderConfigurationException(
                f"Unsupported AI provider: '{provider_name}'. Supported providers: ['ollama', 'gemini', 'mock', 'auto']"
            )

        cls._providers[provider_name] = instance
        return instance

    @classmethod
    def get_all_configured_providers(cls) -> dict[str, AIProvider]:
        """
        Return instances of all configured providers for health probing and diagnostics.
        """
        providers: dict[str, AIProvider] = {}
        # Ollama
        providers["ollama"] = cls.get_provider("ollama")
        # Gemini (only if configured or in mock/auto)
        providers["gemini"] = cls.get_provider("gemini")
        return providers

    @classmethod
    def register_provider(cls, name: str, provider: AIProvider) -> None:
        """Explicitly register a provider instance (useful for test mocks)."""
        cls._providers[name.lower()] = provider

    @classmethod
    def reset(cls) -> None:
        """Reset cached provider instances."""
        cls._providers.clear()


def get_ai_provider() -> AIProvider:
    """FastAPI dependency for accessing the active default AIProvider."""
    return AIRouter.get_provider()

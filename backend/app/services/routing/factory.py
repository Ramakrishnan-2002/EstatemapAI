from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.services.routing.mock_provider import MockRoutingProvider
from app.services.routing.osrm_provider import OSRMProvider
from app.services.routing.protocol import RoutingProvider


def get_routing_provider(provider_type: str | None = None) -> RoutingProvider:
    """
    Resolve and instantiate the configured routing provider.
    Defaults to settings.ROUTING_PROVIDER ("mock" or "osrm").
    """
    selected = (provider_type or settings.ROUTING_PROVIDER).strip().lower()

    if selected == "mock":
        return MockRoutingProvider()
    elif selected == "osrm":
        return OSRMProvider(base_url=settings.OSRM_BASE_URL)
    else:
        raise ValidationException(
            f"Unsupported routing provider '{selected}'. Supported options: 'mock', 'osrm'.",
            details={"provider": selected},
        )

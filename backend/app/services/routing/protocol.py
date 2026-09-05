from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.services.routing.models import RouteResult, TravelMode


@runtime_checkable
class RoutingProvider(Protocol):
    """
    Abstract interface for pluggable road network routing engines.
    Concrete providers can include Mock, OSRM, OpenRouteService, Google Maps, Mapbox, etc.
    """

    @property
    def provider_name(self) -> str:
        """Unique identifier of the routing engine."""
        ...

    @property
    def supported_modes(self) -> set[TravelMode]:
        """Set of TravelModes supported by this provider."""
        ...

    async def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> RouteResult:
        """
        Calculate road network route, distance, duration, and GeoJSON path geometry
        between origin and destination.
        """
        ...

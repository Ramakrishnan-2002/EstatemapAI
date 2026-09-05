from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException, ValidationException
from app.core.logging import logger
from app.repositories.property_repository import PropertyRepository
from app.schemas.commute import (
    BatchCommuteResponse,
    CommuteCompareResponse,
    CommuteDestination,
    CommuteOrigin,
    CommuteResponse,
)
from app.services.geo_service import GeoService
from app.services.routing.factory import get_routing_provider
from app.services.routing.models import RouteResult, TravelMode
from app.services.routing.protocol import RoutingProvider
from app.utils.geo import coords_from_point


class CommuteService:
    """
    Domain service for commute and road-network travel intelligence.
    Coordinates routing provider execution, Redis route caching, coordinate extraction
    from verified Property entities, and multi-destination batching/comparisons.
    """

    def __init__(
        self,
        session: AsyncSession,
        routing_provider: RoutingProvider | None = None,
    ) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)
        self.routing_provider = routing_provider or get_routing_provider()

    async def calculate_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> tuple[RouteResult, bool]:
        """
        Compute route between coordinates with Redis caching and graceful degradation.
        Returns tuple of (RouteResult, is_cached).
        """
        GeoService.validate_coordinates(origin_lat, origin_lng)
        GeoService.validate_coordinates(dest_lat, dest_lng)

        cache_key = CacheKeys.route(
            self.routing_provider.provider_name,
            mode.value,
            origin_lat,
            origin_lng,
            dest_lat,
            dest_lng,
        )

        cached_route: RouteResult | None = await CacheService.get_json(
            cache_key, target_cls=RouteResult
        )
        if cached_route is not None:
            logger.debug("Commute route cache HIT for key '%s'", cache_key)
            return cached_route, True

        logger.debug("Commute route cache MISS for key '%s'", cache_key)
        # Fresh provider calculation
        route_result = await self.routing_provider.get_route(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            mode=mode,
        )

        # Save to Redis asynchronously with configured route TTL
        await CacheService.set_json(
            cache_key,
            route_result,
            ttl=settings.CACHE_ROUTE_TTL_SECONDS,
        )

        return route_result, False

    async def get_property_commute(
        self,
        property_id: int,
        dest_lat: float,
        dest_lng: float,
        dest_name: str | None = None,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> CommuteResponse:
        """
        Calculate commute from a verified property location to a target destination.
        """
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise ResourceNotFoundException("Property", property_id)

        orig_lat, orig_lng = coords_from_point(property_obj.location)

        route, is_cached = await self.calculate_route(
            origin_lat=orig_lat,
            origin_lng=orig_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            mode=mode,
        )

        return CommuteResponse(
            property_id=property_id,
            origin=CommuteOrigin(latitude=orig_lat, longitude=orig_lng),
            destination=CommuteDestination(
                name=dest_name or f"Destination ({round(dest_lat, 4)}, {round(dest_lng, 4)})",
                latitude=dest_lat,
                longitude=dest_lng,
            ),
            mode=mode,
            distance_meters=route.distance_meters,
            distance_km=route.distance_km,
            duration_seconds=route.duration_seconds,
            duration_minutes=route.duration_minutes,
            geometry=route.geometry,
            summary=route.summary,
            provider=route.provider,
            cached=is_cached,
        )

    async def get_batch_property_commute(
        self,
        property_id: int,
        destinations: list[CommuteDestination],
        mode: TravelMode = TravelMode.DRIVING,
    ) -> BatchCommuteResponse:
        """
        Calculate commutes from a single property to a list of up to 5 destinations.
        """
        if len(destinations) > settings.MAX_COMMUTE_DESTINATIONS:
            raise ValidationException(
                f"Maximum of {settings.MAX_COMMUTE_DESTINATIONS} destinations permitted per batch request.",
                details={
                    "max_allowed": settings.MAX_COMMUTE_DESTINATIONS,
                    "received": len(destinations),
                },
            )

        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise ResourceNotFoundException("Property", property_id)

        orig_lat, orig_lng = coords_from_point(property_obj.location)

        results: list[CommuteResponse] = []
        for dest in destinations:
            route, is_cached = await self.calculate_route(
                origin_lat=orig_lat,
                origin_lng=orig_lng,
                dest_lat=dest.latitude,
                dest_lng=dest.longitude,
                mode=mode,
            )
            results.append(
                CommuteResponse(
                    property_id=property_id,
                    origin=CommuteOrigin(latitude=orig_lat, longitude=orig_lng),
                    destination=dest,
                    mode=mode,
                    distance_meters=route.distance_meters,
                    distance_km=route.distance_km,
                    duration_seconds=route.duration_seconds,
                    duration_minutes=route.duration_minutes,
                    geometry=route.geometry,
                    summary=route.summary,
                    provider=route.provider,
                    cached=is_cached,
                )
            )

        return BatchCommuteResponse(
            property_id=property_id,
            origin=CommuteOrigin(latitude=orig_lat, longitude=orig_lng),
            mode=mode,
            results=results,
            total_destinations=len(results),
        )

    async def compare_properties_commute(
        self,
        property_ids: list[int],
        destination: CommuteDestination,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> CommuteCompareResponse:
        """
        Compare commute metrics from multiple properties to a single destination.
        """
        if len(property_ids) < 2:
            raise ValidationException(
                "Commute comparison requires at least 2 property IDs.",
                details={"received_count": len(property_ids)},
            )
        if len(property_ids) > settings.MAX_COMMUTE_COMPARE_PROPERTIES:
            raise ValidationException(
                f"Maximum of {settings.MAX_COMMUTE_COMPARE_PROPERTIES} properties permitted for comparison.",
                details={
                    "max_allowed": settings.MAX_COMMUTE_COMPARE_PROPERTIES,
                    "received": len(property_ids),
                },
            )

        comparisons: list[CommuteResponse] = []
        for pid in property_ids:
            commute_resp = await self.get_property_commute(
                property_id=pid,
                dest_lat=destination.latitude,
                dest_lng=destination.longitude,
                dest_name=destination.name,
                mode=mode,
            )
            comparisons.append(commute_resp)

        # Identify fastest and shortest options
        fastest_item = min(comparisons, key=lambda c: c.duration_seconds)
        shortest_item = min(comparisons, key=lambda c: c.distance_meters)

        return CommuteCompareResponse(
            destination=destination,
            mode=mode,
            comparisons=comparisons,
            fastest_property_id=fastest_item.property_id,
            shortest_property_id=shortest_item.property_id,
        )

    async def get_direct_commute(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        dest_name: str | None = None,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> CommuteResponse:
        """
        Compute direct commute route between arbitrary coordinate pairs.
        """
        route, is_cached = await self.calculate_route(
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            dest_lat=dest_lat,
            dest_lng=dest_lng,
            mode=mode,
        )

        return CommuteResponse(
            property_id=None,
            origin=CommuteOrigin(latitude=origin_lat, longitude=origin_lng),
            destination=CommuteDestination(
                name=dest_name or f"Destination ({round(dest_lat, 4)}, {round(dest_lng, 4)})",
                latitude=dest_lat,
                longitude=dest_lng,
            ),
            mode=mode,
            distance_meters=route.distance_meters,
            distance_km=route.distance_km,
            duration_seconds=route.duration_seconds,
            duration_minutes=route.duration_minutes,
            geometry=route.geometry,
            summary=route.summary,
            provider=route.provider,
            cached=is_cached,
        )

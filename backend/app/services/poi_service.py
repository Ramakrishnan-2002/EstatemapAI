"""
POI Service — business logic for Point of Interest operations.

Responsibilities:
- POI creation (coordinate validation, category normalization)
- POI retrieval and listing
- Proximity search (lat/lng based)
- Property-relative proximity (uses stored Property.location as origin)
- Location intelligence orchestration (one query per category, no N+1)

Spatial performance contract:
  All spatial filtering occurs in PostGIS (GiST index).
  Python post-processing is limited to response serialization.

Location intelligence strategy:
  For a single property, the method issues 2 queries per category:
    1. get_nearest_by_category  → nearest POI + distance
    2. count_within_radius      → count of POIs in radius
  With 7 categories this is 14 queries. Each query hits the GiST index on
  `pois.location` and typically completes in < 5 ms on local PostGIS.
  For higher throughput, a single CTE-based query grouping all categories
  can replace these in a future optimization pass — the interface is stable.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import logger
from app.models.poi import PointOfInterest
from app.models.poi_category import POICategory
from app.repositories.poi_repository import POIRepository
from app.repositories.property_repository import PropertyRepository
from app.schemas.geo import (
    CategoryIntelligence,
    LocationIntelligenceResponse,
    NearbyPOIsResponse,
    POICreate,
    POIResponse,
    POIWithDistance,
)
from app.services.geo_service import GeoService
from app.utils.geo import coords_from_point, point_from_coords

# Default search radius for location intelligence count queries
LOCATION_INTELLIGENCE_RADIUS_KM = 3.0


class POIService:
    """
    Service layer for POI business logic.
    Coordinates between POIRepository, PropertyRepository, and GeoService.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.poi_repo = POIRepository(session)
        self.property_repo = PropertyRepository(session)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _poi_to_response(poi: PointOfInterest) -> POIResponse:
        """Convert ORM POI to typed API response. Extracts lat/lng from geometry."""
        lat, lng = coords_from_point(poi.location)
        return POIResponse(
            id=poi.id,
            name=poi.name,
            category=POICategory(poi.category),
            subcategory=poi.subcategory,
            latitude=lat,
            longitude=lng,
            address=poi.address,
            city=poi.city,
            locality=poi.locality,
            is_active=poi.is_active,
            created_at=poi.created_at.isoformat() if poi.created_at else "",
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def _invalidate_poi_caches(self) -> None:
        """Invalidate all POI intelligence, map, and ranking caches on POI mutations."""
        await CacheService.delete_pattern(CacheKeys.pattern_poi())
        await CacheService.delete_pattern(CacheKeys.pattern_map())
        await CacheService.delete_pattern(CacheKeys.pattern_ranking())

    async def create_poi(self, poi_in: POICreate) -> POIResponse:
        """
        Create a new POI after validating coordinates and constructing PostGIS geometry.
        Requires authentication at the router level — this method trusts the caller.
        """
        GeoService.validate_coordinates(poi_in.latitude, poi_in.longitude)
        location_point = point_from_coords(poi_in.latitude, poi_in.longitude)

        poi_data = poi_in.model_dump(exclude={"latitude", "longitude"})
        poi_data["category"] = poi_in.category.value
        poi_data["location"] = location_point

        poi = await self.poi_repo.create(poi_data)
        await self.session.commit()
        await self._invalidate_poi_caches()
        logger.info("POI created | poi_id=%s name=%s category=%s", poi.id, poi.name, poi.category)
        return self._poi_to_response(poi)

    async def get_poi(self, poi_id: int) -> POIResponse:
        """Fetch a single POI by ID. Raises ResourceNotFoundException if absent."""
        poi = await self.poi_repo.get_by_id(poi_id)
        if not poi:
            raise ResourceNotFoundException(resource="POI", identifier=poi_id)
        return self._poi_to_response(poi)

    async def list_pois(
        self,
        category: POICategory | None = None,
        city: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[POIResponse], int]:
        """List active POIs with optional category/city filters."""
        items, total = await self.poi_repo.list(
            category=category, city=city, limit=limit, offset=offset
        )
        return [self._poi_to_response(p) for p in items], total

    # ------------------------------------------------------------------
    # Spatial Proximity
    # ------------------------------------------------------------------

    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        category: POICategory | None = None,
        limit: int = 50,
    ) -> NearbyPOIsResponse:
        """
        Find active POIs within radius_km of (latitude, longitude).
        Validates coordinates and radius before delegating to PostGIS.
        """
        GeoService.validate_coordinates(latitude, longitude)
        GeoService.validate_radius(radius_km)

        rows = await self.poi_repo.search_nearby(latitude, longitude, radius_km, category, limit)
        items = [
            POIWithDistance(poi=self._poi_to_response(poi), distance_km=round(dist, 3))
            for poi, dist in rows
        ]
        return NearbyPOIsResponse(
            items=items,
            total=len(items),
            radius_km=radius_km,
            category=category,
        )

    async def search_pois_bbox(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        category: POICategory | None = None,
        limit: int = 200,
    ) -> list[PointOfInterest]:
        """
        Find active POIs within a geographic bounding box.
        Returns ORM instances (caller converts to GeoJSON via GeoService).
        """
        GeoService.validate_coordinates(south, west)
        GeoService.validate_coordinates(north, east)
        if south > north:
            from app.core.exceptions import ValidationException

            raise ValidationException(
                f"south ({south}) cannot be greater than north ({north}).",
                details={"south": south, "north": north},
            )
        return await self.poi_repo.search_bbox(north, south, east, west, category, limit)

    # ------------------------------------------------------------------
    # Property-Relative Proximity
    # ------------------------------------------------------------------

    async def get_nearby_for_property(
        self,
        property_id: int,
        category: POICategory | None = None,
        radius_km: float = 5.0,
        limit: int = 20,
    ) -> NearbyPOIsResponse:
        """
        Find POIs near a property's stored location.
        The property coordinates come from the database — extracted via coords_from_point.
        The client cannot spoof the property's coordinates for property-specific queries.
        Raises ResourceNotFoundException if property does not exist.
        """
        GeoService.validate_radius(radius_km)
        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise ResourceNotFoundException(resource="Property", identifier=property_id)

        # Extract authoritative coordinates from the stored PostGIS geometry
        lat, lng = coords_from_point(prop.location)

        rows = await self.poi_repo.search_around_property(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            category=category,
            limit=limit,
        )
        items = [
            POIWithDistance(poi=self._poi_to_response(poi), distance_km=round(dist, 3))
            for poi, dist in rows
        ]
        return NearbyPOIsResponse(
            items=items,
            total=len(items),
            radius_km=radius_km,
            category=category,
        )

    async def get_location_intelligence(
        self,
        property_id: int,
        radius_km: float = LOCATION_INTELLIGENCE_RADIUS_KM,
    ) -> LocationIntelligenceResponse:
        """
        Return a deterministic location intelligence summary for a property.
        Caches results in Redis with CACHE_POI_TTL_SECONDS.
        """
        GeoService.validate_radius(radius_km)

        cache_key = CacheKeys.poi_intelligence(property_id, radius_km)
        cached: LocationIntelligenceResponse | None = await CacheService.get_json(
            cache_key, target_cls=LocationIntelligenceResponse
        )
        if cached is not None:
            logger.debug("Location intelligence cache HIT for key '%s'", cache_key)
            return cached

        logger.debug("Location intelligence cache MISS for key '%s'", cache_key)
        prop = await self.property_repo.get_by_id(property_id)
        if not prop:
            raise ResourceNotFoundException(resource="Property", identifier=property_id)

        # Extract authoritative coordinates from the stored PostGIS geometry
        prop_lat, prop_lng = coords_from_point(prop.location)

        category_intelligence: dict[POICategory, CategoryIntelligence] = {}

        for category in POICategory:
            nearest = await self.poi_repo.get_nearest_by_category(
                latitude=prop_lat,
                longitude=prop_lng,
                category=category,
            )
            count = await self.poi_repo.count_within_radius(
                latitude=prop_lat,
                longitude=prop_lng,
                radius_km=radius_km,
                category=category,
            )
            category_intelligence[category] = CategoryIntelligence(
                nearest_distance_km=round(nearest[1], 3) if nearest else None,
                count_within_radius=count,
            )

        response = LocationIntelligenceResponse(
            property_id=property_id,
            radius_km=radius_km,
            categories=category_intelligence,
        )

        # Cache asynchronously with configured POI TTL
        await CacheService.set_json(
            cache_key,
            response,
            ttl=settings.CACHE_POI_TTL_SECONDS,
        )

        logger.debug(
            "Location intelligence computed | property_id=%s radius_km=%s",
            property_id,
            radius_km,
        )
        return response

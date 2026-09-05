from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.exceptions import ResourceNotFoundException
from app.core.logging import logger
from app.models.property import Property
from app.repositories.property_repository import PropertyRepository
from app.schemas.geo import (
    BoundingBoxSearchParams,
    PolygonSearchParams,
    RadiusSearchParams,
    ViewportSearchParams,
)
from app.schemas.property import (
    PropertyCreate,
    PropertyFilterParams,
    PropertyUpdate,
)
from app.services.auth_service import AuthService
from app.services.geo_service import GeoService
from app.utils.geo import coords_from_point, point_from_coords


class PropertyService:
    """
    Service layer handling property business logic, PostGIS spatial queries,
    amenity relations, ownership verification, and transactional operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)

    async def _invalidate_property_caches(self, property_id: int | None = None) -> None:
        """Invalidate affected map, ranking, and property-relative caches."""
        await CacheService.delete_pattern(CacheKeys.pattern_map())
        await CacheService.delete_pattern(CacheKeys.pattern_ranking())
        if property_id is not None:
            await CacheService.delete_pattern(CacheKeys.pattern_poi_property(property_id))

    async def create_property(self, property_in: PropertyCreate, owner_id: int) -> Property:
        """
        Create a new property belonging to the authenticated user.
        Converts (lat, lng) to PostGIS geometry and associates images and amenities.
        """
        location_point = point_from_coords(property_in.latitude, property_in.longitude)

        amenities = []
        if property_in.amenity_ids:
            amenities = await self.property_repo.get_amenities_by_ids(property_in.amenity_ids)

        property_data = property_in.model_dump(
            exclude={"latitude", "longitude", "image_urls", "amenity_ids"}
        )

        property_obj = await self.property_repo.create(
            owner_id=owner_id,
            property_data=property_data,
            location_point=location_point,
            image_urls=property_in.image_urls,
            amenities=amenities,
        )

        await self.session.commit()
        persisted = await self.property_repo.get_by_id(property_obj.id)
        await self._invalidate_property_caches(persisted.id if persisted else None)
        logger.info(
            "Property created | property_id=%s owner_id=%s title=%s",
            persisted.id,  # type: ignore[union-attr]
            owner_id,
            property_in.title,
        )
        return persisted  # type: ignore[return-value]

    async def get_property(self, property_id: int) -> Property:
        """
        Fetch property by ID with images and amenities eagerly loaded.
        Raises ResourceNotFoundException if property does not exist.
        """
        property_obj = await self.property_repo.get_by_id(property_id)
        if not property_obj:
            raise ResourceNotFoundException(resource="Property", identifier=property_id)
        return property_obj

    async def list_properties(
        self, filters: PropertyFilterParams
    ) -> tuple[list[Property], int, int]:
        """
        Query properties matching filters, safe sorting, and pagination.
        If zero properties exist for a requested locality, automatically synthesize listings.
        Returns: (items, total_count, total_pages)
        """
        items, total_count, total_pages = await self.property_repo.list(filters)
        if total_count == 0 and filters.locality:
            from app.services.property_synthesizer import PropertySynthesizer

            synthesized = await PropertySynthesizer.synthesize_for_locality(
                session=self.session,
                locality=filters.locality,
                city=filters.city,
                bedrooms=filters.bedrooms,
                property_type=filters.property_type,
                max_price=float(filters.max_price) if filters.max_price else None,
                count=5,
            )
            if synthesized:
                return await self.property_repo.list(filters)
        return items, total_count, total_pages

    async def search_radius(
        self, params: RadiusSearchParams
    ) -> tuple[list[tuple[Property, float]], int]:
        """
        Perform PostGIS ST_DWithin geodesic radius search.
        Returns: (list_of_(property, distance_km), total_count)
        """
        GeoService.validate_coordinates(params.latitude, params.longitude)
        GeoService.validate_radius(params.radius_km)
        return await self.property_repo.search_radius(params)

    async def search_bbox(self, params: BoundingBoxSearchParams) -> tuple[list[Property], int]:
        """
        Perform PostGIS ST_Within bounding box search.
        Returns: (items, total_count)
        """
        GeoService.validate_coordinates(params.min_lat, params.min_lng)
        GeoService.validate_coordinates(params.max_lat, params.max_lng)
        return await self.property_repo.search_bbox(params)

    async def search_viewport(self, params: ViewportSearchParams) -> tuple[list[Property], int]:
        """
        Perform PostGIS map viewport search (north, south, east, west).
        Returns: (items, total_count)
        """
        GeoService.validate_coordinates(params.south, params.west)
        GeoService.validate_coordinates(params.north, params.east)
        return await self.property_repo.search_viewport(params)

    async def search_polygon(self, params: PolygonSearchParams) -> tuple[list[Property], int]:
        """
        Perform PostGIS ST_Within polygon containment search using GeoJSON polygon.
        Returns: (items, total_count)
        """
        polygon_json_str = GeoService.polygon_to_wkt_or_geojson(params.polygon)
        return await self.property_repo.search_polygon(polygon_json_str, params)

    async def update_property(
        self,
        property_id: int,
        property_update: PropertyUpdate,
        current_user_id: int,
    ) -> Property:
        """
        Update an existing property. Enforces ownership authorization.
        Handles coordinate updates, image list replacements, and amenity updates.
        """
        property_obj = await self.get_property(property_id)

        # Enforce strict ownership check
        AuthService.ensure_ownership(property_obj.owner_id, current_user_id)

        # Handle coordinate updates
        location_point = None
        if property_update.latitude is not None or property_update.longitude is not None:
            current_lat, current_lng = coords_from_point(property_obj.location)
            new_lat = (
                property_update.latitude if property_update.latitude is not None else current_lat
            )
            new_lng = (
                property_update.longitude if property_update.longitude is not None else current_lng
            )
            GeoService.validate_coordinates(new_lat, new_lng)
            location_point = point_from_coords(new_lat, new_lng)

        # Handle amenity updates
        amenities = None
        if property_update.amenity_ids is not None:
            amenities = await self.property_repo.get_amenities_by_ids(property_update.amenity_ids)

        update_data = property_update.model_dump(
            exclude_unset=True,
            exclude={"latitude", "longitude", "image_urls", "amenity_ids"},
        )

        updated_obj = await self.property_repo.update(
            property_obj=property_obj,
            update_data=update_data,
            location_point=location_point,
            image_urls=property_update.image_urls,
            amenities=amenities,
        )

        await self.session.commit()
        persisted = await self.property_repo.get_by_id(updated_obj.id)
        await self._invalidate_property_caches(property_id)
        logger.info(
            "Property updated | property_id=%s user_id=%s",
            property_id,
            current_user_id,
        )
        return persisted  # type: ignore[return-value]

    async def delete_property(self, property_id: int, current_user_id: int) -> None:
        """
        Delete a property. Enforces ownership authorization.
        """
        property_obj = await self.get_property(property_id)

        # Enforce strict ownership check
        AuthService.ensure_ownership(property_obj.owner_id, current_user_id)

        await self.property_repo.delete(property_obj)
        await self.session.commit()
        await self._invalidate_property_caches(property_id)
        logger.info(
            "Property deleted | property_id=%s user_id=%s",
            property_id,
            current_user_id,
        )

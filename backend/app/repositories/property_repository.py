from __future__ import annotations

import math
from typing import Any

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.amenity import Amenity
from app.models.property import Property
from app.models.property_image import PropertyImage
from app.schemas.geo import (
    BoundingBoxSearchParams,
    PolygonSearchParams,
    RadiusSearchParams,
    SpatialFilterBase,
    ViewportSearchParams,
)
from app.schemas.property import PropertyFilterParams


class PropertyRepository:
    """
    Data access repository for Property entities, associated images, and amenities.
    Encapsulates database operations, PostGIS spatial queries, and eager loading.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, property_id: int) -> Property | None:
        """Fetch a property by ID with eagerly loaded images and amenities."""
        stmt = (
            select(Property)
            .options(
                selectinload(Property.images),
                selectinload(Property.amenities),
            )
            .where(Property.id == property_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_amenities_by_ids(self, amenity_ids: list[int]) -> list[Amenity]:
        """Fetch amenities matching a list of primary key IDs."""
        if not amenity_ids:
            return []
        stmt = select(Amenity).where(Amenity.id.in_(amenity_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        owner_id: int,
        property_data: dict[str, Any],
        location_point: WKBElement,
        image_urls: list[str],
        amenities: list[Amenity],
    ) -> Property:
        """
        Create and persist a new Property with PostGIS location, images, and amenities.
        """
        property_obj = Property(
            owner_id=owner_id,
            location=location_point,
            **property_data,
        )

        # Attach amenities
        if amenities:
            property_obj.amenities = amenities

        # Attach images with sequential display_order
        if image_urls:
            property_obj.images = [
                PropertyImage(image_url=url, display_order=idx)
                for idx, url in enumerate(image_urls)
            ]

        self.session.add(property_obj)
        await self.session.flush()
        await self.session.refresh(property_obj)
        return property_obj

    def _apply_common_filters(
        self, stmt: Any, filters: SpatialFilterBase | PropertyFilterParams
    ) -> Any:
        """Apply shared property criteria filters (price, bedrooms, property_type, status)."""
        if hasattr(filters, "city") and filters.city:
            stmt = stmt.where(func.lower(Property.city) == filters.city.strip().lower())
        if hasattr(filters, "locality") and filters.locality:
            term = filters.locality.strip()
            stmt = stmt.where(
                or_(
                    func.lower(Property.locality) == term.lower(),
                    Property.locality.ilike(f"%{term}%"),
                    Property.address.ilike(f"%{term}%"),
                    Property.city.ilike(f"%{term}%"),
                    Property.title.ilike(f"%{term}%"),
                    Property.description.ilike(f"%{term}%"),
                )
            )
        if filters.property_type:
            stmt = stmt.where(
                func.lower(Property.property_type) == filters.property_type.strip().lower()
            )
        if filters.min_price is not None:
            stmt = stmt.where(Property.price >= filters.min_price)
        if filters.max_price is not None:
            stmt = stmt.where(Property.price <= filters.max_price)
        if filters.bedrooms is not None:
            stmt = stmt.where(Property.bedrooms == filters.bedrooms)
        if filters.bathrooms is not None:
            stmt = stmt.where(Property.bathrooms == filters.bathrooms)
        if filters.status:
            stmt = stmt.where(Property.status == filters.status)
        return stmt

    def _apply_sorting(self, stmt: Any, sort_by: str, distance_expr: Any = None) -> Any:
        """Apply whitelisted sorting rules."""
        sort_map: dict[str, list[Any]] = {
            "newest": [Property.created_at.desc(), Property.id.desc()],
            "oldest": [Property.created_at.asc(), Property.id.asc()],
            "price_asc": [Property.price.asc(), Property.id.asc()],
            "price_desc": [Property.price.desc(), Property.id.desc()],
            "area_asc": [Property.area_sqft.asc(), Property.id.asc()],
            "area_desc": [Property.area_sqft.desc(), Property.id.desc()],
        }

        if distance_expr is not None:
            sort_map["distance_asc"] = [distance_expr.asc(), Property.id.asc()]
            sort_map["distance_desc"] = [distance_expr.desc(), Property.id.desc()]

        default_sort = (
            [distance_expr.asc(), Property.id.asc()]
            if distance_expr is not None
            else [Property.created_at.desc(), Property.id.desc()]
        )
        order_clauses = sort_map.get(sort_by, default_sort)
        return stmt.order_by(*order_clauses)

    async def list(self, filters: PropertyFilterParams) -> tuple[list[Property], int, int]:
        """
        Query properties with database-side filtering, safe whitelisted sorting,
        and LIMIT/OFFSET pagination.
        Returns: (items, total_count, total_pages)
        """
        stmt = select(Property).options(
            selectinload(Property.images),
            selectinload(Property.amenities),
        )

        stmt = self._apply_common_filters(stmt, filters)

        # Compute total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = self._apply_sorting(stmt, filters.sort_by)

        # Apply LIMIT / OFFSET pagination
        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.offset(offset).limit(filters.page_size)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())

        total_pages = math.ceil(total / filters.page_size) if total > 0 else 1
        return items, total, total_pages

    async def search_radius(
        self,
        params: RadiusSearchParams,
    ) -> tuple[list[tuple[Property, float]], int]:
        """
        Perform PostGIS ST_DWithin geodesic radius search using geography casting and GiST index.
        Returns: (items_with_distance_km, total_count)
        """
        # Construct origin point in 4326 and cast to geography
        origin_geom = func.ST_SetSRID(func.ST_MakePoint(params.longitude, params.latitude), 4326)
        origin_geog = func.cast(origin_geom, Geography)
        prop_geog = func.cast(Property.location, Geography)

        radius_meters = params.radius_km * 1000.0
        distance_km_expr = (func.ST_Distance(prop_geog, origin_geog) / 1000.0).label("distance_km")

        # Select Property object and distance expression
        stmt = (
            select(Property, distance_km_expr)
            .options(
                selectinload(Property.images),
                selectinload(Property.amenities),
            )
            .where(func.ST_DWithin(prop_geog, origin_geog, radius_meters))
        )

        stmt = self._apply_common_filters(stmt, params)

        # Compute count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Sort and paginate
        stmt = self._apply_sorting(stmt, params.sort_by, distance_expr=distance_km_expr)
        stmt = stmt.offset(params.offset).limit(params.limit)

        result = await self.session.execute(stmt)
        rows = result.all()
        items = [(row[0], float(row[1])) for row in rows]
        return items, total

    async def search_bbox(
        self,
        params: BoundingBoxSearchParams,
    ) -> tuple[list[Property], int]:
        """
        Perform PostGIS ST_Within bounding box search using ST_MakeEnvelope and GiST index.
        Handles both standard (min_lng <= max_lng) and antimeridian-crossing (min_lng > max_lng) bounds.
        Returns: (items, total_count)
        """
        stmt = select(Property).options(
            selectinload(Property.images),
            selectinload(Property.amenities),
        )

        if params.min_lng <= params.max_lng:
            # Standard bounding box
            envelope = func.ST_MakeEnvelope(
                params.min_lng, params.min_lat, params.max_lng, params.max_lat, 4326
            )
            stmt = stmt.where(func.ST_Within(Property.location, envelope))
        else:
            # Crosses 180° antimeridian: split into [min_lng -> 180] OR [-180 -> max_lng]
            env_east = func.ST_MakeEnvelope(
                params.min_lng, params.min_lat, 180.0, params.max_lat, 4326
            )
            env_west = func.ST_MakeEnvelope(
                -180.0, params.min_lat, params.max_lng, params.max_lat, 4326
            )
            stmt = stmt.where(
                or_(
                    func.ST_Within(Property.location, env_east),
                    func.ST_Within(Property.location, env_west),
                )
            )

        stmt = self._apply_common_filters(stmt, params)

        # Compute total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = self._apply_sorting(stmt, params.sort_by)
        stmt = stmt.offset(params.offset).limit(params.limit)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def search_viewport(
        self,
        params: ViewportSearchParams,
    ) -> tuple[list[Property], int]:
        """
        Perform map viewport search by mapping north/south/east/west to BoundingBoxSearchParams.
        """
        bbox_params = BoundingBoxSearchParams(
            min_lat=params.south,
            min_lng=params.west,
            max_lat=params.north,
            max_lng=params.east,
            min_price=params.min_price,
            max_price=params.max_price,
            property_type=params.property_type,
            bedrooms=params.bedrooms,
            bathrooms=params.bathrooms,
            status=params.status,
            sort_by=params.sort_by,
            limit=params.limit,
            offset=params.offset,
        )
        return await self.search_bbox(bbox_params)

    async def search_polygon(
        self,
        polygon_geojson_str: str,
        params: PolygonSearchParams,
    ) -> tuple[list[Property], int]:
        """
        Perform PostGIS polygon containment search using ST_Within / ST_SetSRID(ST_GeomFromGeoJSON(...), 4326).
        Returns: (items, total_count)
        """
        poly_geom = func.ST_SetSRID(func.ST_GeomFromGeoJSON(polygon_geojson_str), 4326)

        stmt = (
            select(Property)
            .options(
                selectinload(Property.images),
                selectinload(Property.amenities),
            )
            .where(func.ST_Within(Property.location, poly_geom))
        )

        stmt = self._apply_common_filters(stmt, params)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = self._apply_sorting(stmt, params.sort_by)
        stmt = stmt.offset(params.offset).limit(params.limit)

        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def update(
        self,
        property_obj: Property,
        update_data: dict[str, Any],
        location_point: WKBElement | None = None,
        image_urls: list[str] | None = None,
        amenities: list[Amenity] | None = None,
    ) -> Property:
        """Update property attributes, coordinates, images, and amenities."""
        for key, value in update_data.items():
            if hasattr(property_obj, key):
                setattr(property_obj, key, value)

        if location_point is not None:
            property_obj.location = location_point

        if amenities is not None:
            property_obj.amenities = amenities

        if image_urls is not None:
            property_obj.images = [
                PropertyImage(image_url=url, display_order=idx)
                for idx, url in enumerate(image_urls)
            ]

        await self.session.flush()
        await self.session.refresh(property_obj)
        return property_obj

    async def delete(self, property_obj: Property) -> None:
        """Delete a property instance (cascades to images and amenity associations)."""
        await self.session.delete(property_obj)
        await self.session.flush()

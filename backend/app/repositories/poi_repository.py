"""
POI Repository — all database operations for Points of Interest.

Design principles:
- All spatial filtering is performed in PostGIS; no Python-side filtering.
- Distances are computed via ST_Distance on the geography type (meter-accurate).
- Results are always filtered to is_active=True unless explicitly requested otherwise.
- No N+1 queries: the location_intelligence use-case issues one well-scoped query
  per category (O(GiST index) each), not one query per POI.

PostGIS functions used:
  ST_DWithin(geography, geography, meters)  — radius containment check (uses GiST)
  ST_Distance(geography, geography)         — geodesic distance in meters
  ST_MakeEnvelope(xmin, ymin, xmax, ymax, srid) — bounding box geometry
  ST_Within(geometry, geometry)             — bbox containment check
  ST_SetSRID(ST_MakePoint(lng, lat), 4326) — construct a geometry point
  cast(col, Geography)                      — cast geometry to geography for meter accuracy

Unit convention:
  API layer  — distances in kilometres (km)
  PostGIS    — ST_Distance returns metres; divide by 1000 for km
"""

from __future__ import annotations

from geoalchemy2 import Geography
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.poi import PointOfInterest
from app.models.poi_category import POICategory


class POIRepository:
    """
    Data access layer for PointOfInterest entities.
    All raw SQL / PostGIS expressions live here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_origin_geog(latitude: float, longitude: float):
        """Construct an origin geography point from (lat, lng)."""
        geom = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        return func.cast(geom, Geography)

    @staticmethod
    def _poi_geog():
        """Cast POI location geometry to geography for meter-accurate distance."""
        return func.cast(PointOfInterest.location, Geography)

    @staticmethod
    def _distance_km_expr(origin_geog):
        """Expression: geodesic distance in km from POI location to origin."""
        return (func.ST_Distance(POIRepository._poi_geog(), origin_geog) / 1000.0).label(
            "distance_km"
        )

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def create(self, poi_data: dict) -> PointOfInterest:
        """Persist a new POI. Caller must commit the session."""
        poi = PointOfInterest(**poi_data)
        self.session.add(poi)
        await self.session.flush()
        await self.session.refresh(poi)
        return poi

    async def get_by_id(self, poi_id: int) -> PointOfInterest | None:
        """Fetch a single POI by primary key."""
        stmt = select(PointOfInterest).where(PointOfInterest.id == poi_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        category: POICategory | None = None,
        city: str | None = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[PointOfInterest], int]:
        """List POIs with optional filters. Returns (items, total_count)."""
        stmt = select(PointOfInterest)
        if is_active is not None:
            stmt = stmt.where(PointOfInterest.is_active == is_active)
        if category is not None:
            stmt = stmt.where(PointOfInterest.category == category.value)
        if city:
            stmt = stmt.where(func.lower(PointOfInterest.city) == city.strip().lower())

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        stmt = stmt.order_by(PointOfInterest.name.asc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    # ------------------------------------------------------------------
    # Spatial Queries
    # ------------------------------------------------------------------

    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        category: POICategory | None = None,
        limit: int = 50,
    ) -> list[tuple[PointOfInterest, float]]:
        """
        Find active POIs within radius_km of (latitude, longitude).
        Uses ST_DWithin on geography for geodesic accuracy.
        Returns list of (poi, distance_km) sorted by distance ascending.
        """
        origin_geog = self._make_origin_geog(latitude, longitude)
        distance_km = self._distance_km_expr(origin_geog)
        radius_meters = radius_km * 1000.0

        stmt = (
            select(PointOfInterest, distance_km)
            .where(PointOfInterest.is_active.is_(True))
            .where(func.ST_DWithin(self._poi_geog(), origin_geog, radius_meters))
        )

        if category is not None:
            stmt = stmt.where(PointOfInterest.category == category.value)

        stmt = stmt.order_by(distance_km.asc()).limit(limit)
        result = await self.session.execute(stmt)
        rows = result.all()
        return [(row[0], float(row[1])) for row in rows]

    async def search_bbox(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        category: POICategory | None = None,
        limit: int = 200,
    ) -> list[PointOfInterest]:
        """
        Find active POIs inside a geographic bounding box.
        Uses ST_Within + ST_MakeEnvelope with GiST index.
        Returns list of POIs (no distance — map viewport context).
        """
        envelope = func.ST_MakeEnvelope(west, south, east, north, 4326)

        stmt = (
            select(PointOfInterest)
            .where(PointOfInterest.is_active.is_(True))
            .where(func.ST_Within(PointOfInterest.location, envelope))
        )

        if category is not None:
            stmt = stmt.where(PointOfInterest.category == category.value)

        stmt = stmt.order_by(PointOfInterest.name.asc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_around_property(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        category: POICategory | None = None,
        limit: int = 20,
    ) -> list[tuple[PointOfInterest, float]]:
        """
        Find active POIs within radius_km of a property at (latitude, longitude).
        Coordinates are extracted from the stored Property.location geometry by the
        service layer — the client cannot supply them directly.
        Returns list of (poi, distance_km) sorted by distance ascending.
        """
        origin_geog = self._make_origin_geog(latitude, longitude)
        distance_km = self._distance_km_expr(origin_geog)
        radius_meters = radius_km * 1000.0

        stmt = (
            select(PointOfInterest, distance_km)
            .where(PointOfInterest.is_active.is_(True))
            .where(func.ST_DWithin(self._poi_geog(), origin_geog, radius_meters))
        )

        if category is not None:
            stmt = stmt.where(PointOfInterest.category == category.value)

        stmt = stmt.order_by(distance_km.asc()).limit(limit)
        result = await self.session.execute(stmt)
        rows = result.all()
        return [(row[0], float(row[1])) for row in rows]

    async def get_nearest_by_category(
        self,
        latitude: float,
        longitude: float,
        category: POICategory,
    ) -> tuple[PointOfInterest, float] | None:
        """
        Find the single nearest active POI of a specific category to a coordinate point.
        No radius limit — returns globally nearest (or None if no POI of that category exists).
        Used for the location intelligence nearest_distance_km field.
        """
        origin_geog = self._make_origin_geog(latitude, longitude)
        distance_km = self._distance_km_expr(origin_geog)

        stmt = (
            select(PointOfInterest, distance_km)
            .where(PointOfInterest.is_active.is_(True))
            .where(PointOfInterest.category == category.value)
            .order_by(distance_km.asc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        row = result.first()
        if row is None:
            return None
        return row[0], float(row[1])

    async def count_within_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        category: POICategory,
    ) -> int:
        """
        Count active POIs of a category within radius_km of a coordinate point.
        Used for location intelligence count_within_radius field.
        Runs as a COUNT() query — no row fetching overhead.
        """
        origin_geog = self._make_origin_geog(latitude, longitude)
        radius_meters = radius_km * 1000.0

        stmt = select(func.count()).where(
            PointOfInterest.is_active.is_(True),
            PointOfInterest.category == category.value,
            func.ST_DWithin(self._poi_geog(), origin_geog, radius_meters),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

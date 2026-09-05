from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.poi_category import POICategory
from app.schemas.geo import (
    GeoJSONFeatureCollection,
    POIGeoJSONFeatureCollection,
    PolygonSearchParams,
    RadiusSearchParams,
    ViewportSearchParams,
)
from app.services.geo_service import GeoService
from app.services.poi_service import POIService
from app.services.property_service import PropertyService

router = APIRouter()


@router.get(
    "/properties",
    response_model=GeoJSONFeatureCollection,
    summary="Map Viewport Properties (GeoJSON)",
    description="Query properties located inside current map viewport bounds (north, south, east, west) and return as RFC 7946 GeoJSON FeatureCollection.",
)
async def get_viewport_properties(
    north: Annotated[float, Query(ge=-90.0, le=90.0, description="North latitude")],
    south: Annotated[float, Query(ge=-90.0, le=90.0, description="South latitude")],
    east: Annotated[float, Query(ge=-180.0, le=180.0, description="East longitude")],
    west: Annotated[float, Query(ge=-180.0, le=180.0, description="West longitude")],
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    property_type: Annotated[str | None, Query()] = None,
    bedrooms: Annotated[int | None, Query(ge=0)] = None,
    bathrooms: Annotated[float | None, Query(ge=0)] = None,
    status: Annotated[str | None, Query()] = "active",
    sort_by: Annotated[str, Query()] = "newest",
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
) -> GeoJSONFeatureCollection:
    filters_dict = {
        "min_price": min_price,
        "max_price": max_price,
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "status": status,
        "sort_by": sort_by,
        "limit": limit,
        "offset": offset,
    }
    cache_key = CacheKeys.map_properties(north, south, east, west, filters_dict)
    cached: GeoJSONFeatureCollection | None = await CacheService.get_json(
        cache_key, target_cls=GeoJSONFeatureCollection
    )
    if cached is not None:
        logger.debug("Map properties cache HIT for key '%s'", cache_key)
        return cached

    params = ViewportSearchParams(
        north=north,
        south=south,
        east=east,
        west=west,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        status=status,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    property_service = PropertyService(db)
    items, total = await property_service.search_viewport(params)
    fc = GeoService.properties_to_feature_collection(items, total=total)
    await CacheService.set_json(cache_key, fc, ttl=settings.CACHE_MAP_TTL_SECONDS)
    return fc


@router.get(
    "/radius",
    response_model=GeoJSONFeatureCollection,
    summary="Map Radius Properties (GeoJSON)",
    description="Query properties within radius and return GeoJSON FeatureCollection with distance_km embedded in feature properties.",
)
async def get_radius_geojson(
    latitude: Annotated[float, Query(ge=-90.0, le=90.0, description="Center latitude")],
    longitude: Annotated[float, Query(ge=-180.0, le=180.0, description="Center longitude")],
    radius_km: Annotated[float, Query(gt=0.0, le=200.0, description="Radius in km")] = 10.0,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    property_type: Annotated[str | None, Query()] = None,
    bedrooms: Annotated[int | None, Query(ge=0)] = None,
    bathrooms: Annotated[float | None, Query(ge=0)] = None,
    status: Annotated[str | None, Query()] = "active",
    sort_by: Annotated[str, Query()] = "distance_asc",
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
) -> GeoJSONFeatureCollection:
    params = RadiusSearchParams(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        status=status,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )
    property_service = PropertyService(db)
    items_with_dist, total = await property_service.search_radius(params)
    return GeoService.properties_to_feature_collection(items_with_dist, total=total)


@router.post(
    "/polygon",
    response_model=GeoJSONFeatureCollection,
    summary="Map Polygon Properties (GeoJSON)",
    description="Query properties inside a polygon boundary and return as GeoJSON FeatureCollection.",
)
async def get_polygon_geojson(
    payload: PolygonSearchParams,
    db: AsyncSession = Depends(get_db),
) -> GeoJSONFeatureCollection:
    property_service = PropertyService(db)
    items, total = await property_service.search_polygon(payload)
    return GeoService.properties_to_feature_collection(items, total=total)


@router.get(
    "/pois",
    response_model=POIGeoJSONFeatureCollection,
    summary="Map POIs (GeoJSON)",
    description=(
        "Query active Points of Interest inside the current map viewport "
        "(north, south, east, west) and return as an RFC 7946 GeoJSON FeatureCollection. "
        "Optionally filter by POI category. "
        "Uses PostGIS ST_Within with GiST index for efficient bbox filtering."
    ),
)
async def get_viewport_pois(
    north: Annotated[float, Query(ge=-90.0, le=90.0, description="North latitude")],
    south: Annotated[float, Query(ge=-90.0, le=90.0, description="South latitude")],
    east: Annotated[float, Query(ge=-180.0, le=180.0, description="East longitude")],
    west: Annotated[float, Query(ge=-180.0, le=180.0, description="West longitude")],
    category: Annotated[
        POICategory | None, Query(description="Optional POI category filter")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500, description="Maximum POIs (max 500)")] = 200,
    db: AsyncSession = Depends(get_db),
) -> POIGeoJSONFeatureCollection:
    cache_key = CacheKeys.map_pois(north, south, east, west, category.value if category else None)
    cached: POIGeoJSONFeatureCollection | None = await CacheService.get_json(
        cache_key, target_cls=POIGeoJSONFeatureCollection
    )
    if cached is not None:
        logger.debug("Map POIs cache HIT for key '%s'", cache_key)
        return cached

    poi_service = POIService(db)
    pois = await poi_service.search_pois_bbox(
        north=north,
        south=south,
        east=east,
        west=west,
        category=category,
        limit=limit,
    )
    fc = GeoService.pois_to_feature_collection(pois)
    await CacheService.set_json(cache_key, fc, ttl=settings.CACHE_MAP_TTL_SECONDS)
    return fc

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.geo import (
    BoundingBoxSearchParams,
    PolygonSearchParams,
    RadiusSearchParams,
    RadiusSearchResponse,
)
from app.schemas.property import PaginatedPropertyResponse, PropertyResponse
from app.schemas.ranking import RankedSearchRequest, RankedSearchResponse
from app.services.geo_service import GeoService
from app.services.property_service import PropertyService
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get(
    "/radius",
    response_model=RadiusSearchResponse,
    summary="Geodesic Radius Search",
    description="Query properties within radius_km from center (latitude, longitude) using PostGIS ST_DWithin on geography.",
)
async def search_by_radius(
    latitude: Annotated[float, Query(ge=-90.0, le=90.0, description="Center latitude")],
    longitude: Annotated[float, Query(ge=-180.0, le=180.0, description="Center longitude")],
    radius_km: Annotated[
        float, Query(gt=0.0, le=200.0, description="Radius in km (max 200)")
    ] = 10.0,
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    property_type: Annotated[str | None, Query()] = None,
    bedrooms: Annotated[int | None, Query(ge=0)] = None,
    bathrooms: Annotated[float | None, Query(ge=0)] = None,
    status: Annotated[str | None, Query()] = "active",
    sort_by: Annotated[
        str,
        Query(
            description="Sort: distance_asc, distance_desc, newest, oldest, price_asc, price_desc, area_asc, area_desc",
        ),
    ] = "distance_asc",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
) -> RadiusSearchResponse:
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
    return GeoService.format_radius_response(
        items_with_distance=items_with_dist,
        total=total,
        center_lat=latitude,
        center_lng=longitude,
        radius_km=radius_km,
    )


@router.get(
    "/bbox",
    response_model=PaginatedPropertyResponse,
    summary="Bounding Box Search",
    description="Query properties within bounding box [min_lat, min_lng, max_lat, max_lng] using PostGIS ST_MakeEnvelope and GiST index.",
)
async def search_by_bbox(
    min_lat: Annotated[float, Query(ge=-90.0, le=90.0, description="South latitude")],
    min_lng: Annotated[float, Query(ge=-180.0, le=180.0, description="West longitude")],
    max_lat: Annotated[float, Query(ge=-90.0, le=90.0, description="North latitude")],
    max_lng: Annotated[float, Query(ge=-180.0, le=180.0, description="East longitude")],
    min_price: Annotated[float | None, Query(ge=0)] = None,
    max_price: Annotated[float | None, Query(ge=0)] = None,
    property_type: Annotated[str | None, Query()] = None,
    bedrooms: Annotated[int | None, Query(ge=0)] = None,
    bathrooms: Annotated[float | None, Query(ge=0)] = None,
    status: Annotated[str | None, Query()] = "active",
    sort_by: Annotated[str, Query()] = "newest",
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
) -> PaginatedPropertyResponse:
    params = BoundingBoxSearchParams(
        min_lat=min_lat,
        min_lng=min_lng,
        max_lat=max_lat,
        max_lng=max_lng,
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
    items, total = await property_service.search_bbox(params)
    page_num = (offset // limit) + 1
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return PaginatedPropertyResponse(
        items=[PropertyResponse.model_validate(p) for p in items],
        total=total,
        page=page_num,
        page_size=limit,
        total_pages=total_pages,
    )


@router.post(
    "/polygon",
    response_model=PaginatedPropertyResponse,
    summary="Polygon Search",
    description="Query properties contained within a GeoJSON polygon boundary using PostGIS ST_Within and GiST index.",
)
async def search_by_polygon(
    payload: PolygonSearchParams,
    db: AsyncSession = Depends(get_db),
) -> PaginatedPropertyResponse:
    property_service = PropertyService(db)
    items, total = await property_service.search_polygon(payload)
    page_num = (payload.offset // payload.limit) + 1
    total_pages = (total + payload.limit - 1) // payload.limit if total > 0 else 1

    return PaginatedPropertyResponse(
        items=[PropertyResponse.model_validate(p) for p in items],
        total=total,
        page=page_num,
        page_size=payload.limit,
        total_pages=total_pages,
    )


@router.post(
    "/ranked",
    response_model=RankedSearchResponse,
    summary="Deterministic Ranked Property Search",
    description=(
        "Retrieve eligible properties matching hard database constraints and score them "
        "using a multi-factor deterministic ranking model (price, bedrooms, area, location intelligence, "
        "commute convenience, locality). Includes granular score breakdowns and factual rule-based explanations."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_RANKED_SEARCH_REQUESTS,
                window_seconds=settings.RATE_LIMIT_RANKED_SEARCH_WINDOW_SECONDS,
                scope="search_ranked",
            )
        )
    ],
)
async def search_ranked(
    payload: RankedSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> RankedSearchResponse:
    ranking_service = RankingService(db)
    return await ranking_service.rank_properties(payload)

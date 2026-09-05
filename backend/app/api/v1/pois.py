"""
POI API Router — Points of Interest endpoints.

Public endpoints (no auth):
  GET /api/v1/pois/nearby   — find POIs near a coordinate
  GET /api/v1/pois/{id}     — get a specific POI

Protected endpoints (JWT required):
  POST /api/v1/pois         — create a new POI (admin/internal use)

All coordinate inputs are validated at the Pydantic schema and GeoService layers.
All distances are returned in kilometres.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.poi_category import POICategory
from app.models.user import User
from app.schemas.geo import NearbyPOIsResponse, POICreate, POIResponse
from app.services.poi_service import POIService

router = APIRouter()


@router.get(
    "/nearby",
    response_model=NearbyPOIsResponse,
    summary="Nearby POI Search",
    description=(
        "Find active Points of Interest within radius_km of (latitude, longitude) "
        "using PostGIS ST_DWithin on geography. Distances returned in kilometres. "
        "Optionally filter by category."
    ),
)
async def get_nearby_pois(
    latitude: Annotated[
        float, Query(ge=-90.0, le=90.0, description="Center latitude (-90 to +90)")
    ],
    longitude: Annotated[
        float, Query(ge=-180.0, le=180.0, description="Center longitude (-180 to +180)")
    ],
    radius_km: Annotated[
        float, Query(gt=0.0, le=50.0, description="Search radius in km (max 50)")
    ] = 3.0,
    category: Annotated[
        POICategory | None, Query(description="Optional POI category filter")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=200, description="Maximum results (max 200)")] = 50,
    db: AsyncSession = Depends(get_db),
) -> NearbyPOIsResponse:
    service = POIService(db)
    return await service.search_nearby(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        category=category,
        limit=limit,
    )


@router.post(
    "",
    response_model=POIResponse,
    status_code=201,
    summary="Create POI",
    description=(
        "Create a new Point of Interest. Requires authentication. "
        "Intended for data administration — not a public consumer endpoint."
    ),
)
async def create_poi(
    poi_in: POICreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> POIResponse:
    service = POIService(db)
    return await service.create_poi(poi_in)


@router.get(
    "/{poi_id}",
    response_model=POIResponse,
    summary="Get POI by ID",
    description="Retrieve a single Point of Interest by its primary key.",
)
async def get_poi(
    poi_id: int,
    db: AsyncSession = Depends(get_db),
) -> POIResponse:
    service = POIService(db)
    return await service.get_poi(poi_id)

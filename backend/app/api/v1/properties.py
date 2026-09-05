from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_active_user, get_db
from app.core.rate_limit import RateLimiter
from app.models.poi_category import POICategory
from app.models.user import User
from app.schemas.commute import (
    BatchCommuteRequest,
    BatchCommuteResponse,
    CommuteResponse,
)
from app.schemas.comparison import (
    ComparisonResult,
    PropertyComparisonRequest,
)
from app.schemas.geo import LocationIntelligenceResponse, NearbyPOIsResponse
from app.schemas.property import (
    PaginatedPropertyResponse,
    PropertyCreate,
    PropertyFilterParams,
    PropertyResponse,
    PropertyUpdate,
)
from app.services.commute_service import CommuteService
from app.services.comparison_service import ComparisonService
from app.services.poi_service import POIService
from app.services.property_service import PropertyService
from app.services.routing.models import TravelMode

router = APIRouter()


@router.post(
    "/compare",
    response_model=ComparisonResult,
    status_code=status.HTTP_200_OK,
    summary="Deterministic Multi-Property Comparison",
    description=(
        "Compare 2 to 3 properties deterministically across price, area, price/sqft, "
        "commute travel time, location intelligence, and ranking factor scores. "
        "Operates completely independently of LLMs and works when AI is offline."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=60,
                window_seconds=60,
                scope="properties_compare",
                fail_open=True,
            )
        )
    ],
)
async def compare_properties(
    request_data: PropertyComparisonRequest,
    db: AsyncSession = Depends(get_db),
) -> ComparisonResult:
    service = ComparisonService(db)
    return await service.compare_properties(request_data)


@router.post(
    "",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new property listing",
)
async def create_property(
    property_in: PropertyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Create a new real estate property listing with spatial location,
    optional multiple image URLs, and assigned amenities.
    Requires an active authenticated user.
    """
    service = PropertyService(db)
    property_obj = await service.create_property(
        property_in=property_in,
        owner_id=current_user.id,
    )
    return PropertyResponse.model_validate(property_obj)


@router.get(
    "",
    response_model=PaginatedPropertyResponse,
    status_code=status.HTTP_200_OK,
    summary="List properties with filtering, sorting, and pagination",
)
async def list_properties(
    filters: PropertyFilterParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPropertyResponse:
    """
    Retrieve real estate property listings with database-level filtering,
    safe whitelisted sorting, and standard LIMIT/OFFSET pagination.
    """
    service = PropertyService(db)
    items, total, total_pages = await service.list_properties(filters)
    return PaginatedPropertyResponse(
        items=[PropertyResponse.model_validate(p) for p in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get property listing by ID",
)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Fetch a single property listing by its integer ID including coordinates,
    images, and amenities.
    """
    service = PropertyService(db)
    property_obj = await service.get_property(property_id)
    return PropertyResponse.model_validate(property_obj)


@router.patch(
    "/{property_id}",
    response_model=PropertyResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing property listing",
)
async def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Partially update an existing property listing.
    Only the listing owner can perform updates (enforced via 403 Forbidden).
    """
    service = PropertyService(db)
    property_obj = await service.update_property(
        property_id=property_id,
        property_update=property_update,
        current_user_id=current_user.id,
    )
    return PropertyResponse.model_validate(property_obj)


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a property listing",
)
async def delete_property(
    property_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Permanently delete a property listing and its associated images and amenity links.
    Only the listing owner can delete it (enforced via 403 Forbidden).
    """
    service = PropertyService(db)
    await service.delete_property(
        property_id=property_id,
        current_user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/status")
async def properties_status():
    return {"module": "properties", "status": "ready"}


@router.get(
    "/{property_id}/nearby",
    response_model=NearbyPOIsResponse,
    summary="Nearby POIs for Property",
    description=(
        "Find Points of Interest within radius_km of a specific property's stored location. "
        "The property coordinates are read from the database — the client cannot override them. "
        "Optionally filter by POI category. Distances returned in kilometres."
    ),
)
async def get_property_nearby_pois(
    property_id: int,
    category: Annotated[
        POICategory | None, Query(description="Optional POI category filter")
    ] = None,
    radius_km: Annotated[
        float, Query(gt=0.0, le=50.0, description="Search radius in km (max 50)")
    ] = 5.0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum POI results (max 100)")] = 20,
    db: AsyncSession = Depends(get_db),
) -> NearbyPOIsResponse:
    service = POIService(db)
    return await service.get_nearby_for_property(
        property_id=property_id,
        category=category,
        radius_km=radius_km,
        limit=limit,
    )


@router.get(
    "/{property_id}/location-intelligence",
    response_model=LocationIntelligenceResponse,
    summary="Property Location Intelligence",
    description=(
        "Return a deterministic location intelligence summary for a property. "
        "For each POI category, computes: nearest distance (km) and count within radius_km. "
        "All values come from PostGIS spatial queries — never hard-coded or AI-generated. "
        "This is the factual geographic foundation; AI layers may explain it in future phases."
    ),
)
async def get_property_location_intelligence(
    property_id: int,
    radius_km: Annotated[
        float,
        Query(
            gt=0.0,
            le=50.0,
            description="Radius in km for count_within_radius calculation (max 50, default 3)",
        ),
    ] = 3.0,
    db: AsyncSession = Depends(get_db),
) -> LocationIntelligenceResponse:
    service = POIService(db)
    return await service.get_location_intelligence(
        property_id=property_id,
        radius_km=radius_km,
    )


@router.get(
    "/{property_id}/commute",
    response_model=CommuteResponse,
    summary="Property Commute Route & Travel Intelligence",
    description=(
        "Calculate the road network travel distance, duration, and GeoJSON route geometry "
        "from a property's verified database location to a destination coordinate. "
        "Results are accelerated via Redis caching."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_COMMUTE_REQUESTS,
                window_seconds=settings.RATE_LIMIT_COMMUTE_WINDOW_SECONDS,
                scope="property_commute",
            )
        )
    ],
)
async def get_property_commute(
    property_id: int,
    destination_lat: Annotated[float, Query(ge=-90.0, le=90.0, description="Destination latitude")],
    destination_lng: Annotated[
        float, Query(ge=-180.0, le=180.0, description="Destination longitude")
    ],
    destination_name: Annotated[str | None, Query(description="Destination label")] = None,
    mode: Annotated[TravelMode, Query(description="Travel mode")] = TravelMode.DRIVING,
    db: AsyncSession = Depends(get_db),
) -> CommuteResponse:
    service = CommuteService(db)
    return await service.get_property_commute(
        property_id=property_id,
        dest_lat=destination_lat,
        dest_lng=destination_lng,
        dest_name=destination_name,
        mode=mode,
    )


@router.post(
    "/{property_id}/commute/batch",
    response_model=BatchCommuteResponse,
    summary="Property Batch Commute Routes",
    description=(
        "Calculate road network travel metrics and GeoJSON route geometries from a property "
        "to a list of up to 5 target destinations (e.g. workplace, airport, schools)."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_COMMUTE_REQUESTS,
                window_seconds=settings.RATE_LIMIT_COMMUTE_WINDOW_SECONDS,
                scope="property_commute_batch",
            )
        )
    ],
)
async def get_property_batch_commute(
    property_id: int,
    request_data: BatchCommuteRequest,
    db: AsyncSession = Depends(get_db),
) -> BatchCommuteResponse:
    service = CommuteService(db)
    return await service.get_batch_property_commute(
        property_id=property_id,
        destinations=request_data.destinations,
        mode=request_data.mode,
    )

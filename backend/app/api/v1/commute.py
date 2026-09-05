from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.commute import (
    CommuteCompareRequest,
    CommuteCompareResponse,
    CommuteResponse,
)
from app.services.commute_service import CommuteService
from app.services.routing.models import TravelMode

router = APIRouter()


@router.get(
    "/route",
    response_model=CommuteResponse,
    status_code=status.HTTP_200_OK,
    summary="Direct Point-to-Point Commute Route",
    description=(
        "Calculate road network commute metrics and GeoJSON LineString path "
        "between arbitrary origin and destination coordinate pairs."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_COMMUTE_REQUESTS,
                window_seconds=settings.RATE_LIMIT_COMMUTE_WINDOW_SECONDS,
                scope="commute_route",
            )
        )
    ],
)
async def get_direct_route(
    origin_lat: Annotated[float, Query(ge=-90.0, le=90.0, description="Origin latitude")],
    origin_lng: Annotated[float, Query(ge=-180.0, le=180.0, description="Origin longitude")],
    dest_lat: Annotated[float, Query(ge=-90.0, le=90.0, description="Destination latitude")],
    dest_lng: Annotated[float, Query(ge=-180.0, le=180.0, description="Destination longitude")],
    dest_name: Annotated[str | None, Query(description="Optional destination label")] = None,
    mode: Annotated[TravelMode, Query(description="Travel mode")] = TravelMode.DRIVING,
    db: AsyncSession = Depends(get_db),
) -> CommuteResponse:
    service = CommuteService(db)
    return await service.get_direct_commute(
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        dest_lat=dest_lat,
        dest_lng=dest_lng,
        dest_name=dest_name,
        mode=mode,
    )


@router.post(
    "/compare",
    response_model=CommuteCompareResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Commutes for Multiple Properties",
    description=(
        "Compare road network commute travel times and distances from 2 to 10 verified properties "
        "to a common target destination (e.g. workplace, school, airport)."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_COMMUTE_REQUESTS,
                window_seconds=settings.RATE_LIMIT_COMMUTE_WINDOW_SECONDS,
                scope="commute_compare",
            )
        )
    ],
)
async def compare_properties_commute(
    request_data: CommuteCompareRequest,
    db: AsyncSession = Depends(get_db),
) -> CommuteCompareResponse:
    service = CommuteService(db)
    return await service.compare_properties_commute(
        property_ids=request_data.property_ids,
        destination=request_data.destination,
        mode=request_data.mode,
    )

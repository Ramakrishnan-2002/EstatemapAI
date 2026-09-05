from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.services.routing.models import RouteGeometry, TravelMode


class CommuteDestination(BaseModel):
    """Destination target for commute routing calculations."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Human-readable destination name (e.g. 'Electronic City Phase 1', 'MG Road Metro').",
        examples=["Electronic City"],
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Destination latitude in WGS84 coordinates.",
        examples=[12.8399],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Destination longitude in WGS84 coordinates.",
        examples=[77.6770],
    )


class CommuteOrigin(BaseModel):
    """Geographic origin coordinate pair for route calculation."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class CommuteResponse(BaseModel):
    """Standardized response representing a computed commute path and travel metrics."""

    model_config = ConfigDict(from_attributes=True)

    property_id: int | None = Field(
        None,
        description="Associated Property ID if route originated from a verified listing.",
    )
    origin: CommuteOrigin
    destination: CommuteDestination
    mode: TravelMode
    distance_meters: float = Field(..., ge=0.0, description="Total travel distance in meters.")
    distance_km: float = Field(..., ge=0.0, description="Travel distance in kilometers.")
    duration_seconds: float = Field(..., ge=0.0, description="Estimated duration in seconds.")
    duration_minutes: float = Field(..., ge=0.0, description="Estimated duration in minutes.")
    geometry: RouteGeometry = Field(
        ...,
        description="GeoJSON LineString path geometry (coordinates: [[lng, lat], ...]).",
    )
    summary: str | None = Field(None, description="Road or path route summary.")
    provider: str = Field(..., description="Routing engine used to compute metrics.")
    cached: bool = Field(False, description="Whether this route was served from Redis cache.")


class BatchCommuteRequest(BaseModel):
    """Request payload to calculate commutes from a single property to multiple destinations."""

    destinations: list[CommuteDestination] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of destinations (up to 5) to compute commutes for.",
    )
    mode: TravelMode = Field(
        default=TravelMode.DRIVING,
        description="Travel mode for all route computations.",
    )


class BatchCommuteResponse(BaseModel):
    """Batch commute calculation response for a property."""

    property_id: int
    origin: CommuteOrigin
    mode: TravelMode
    results: list[CommuteResponse]
    total_destinations: int


class CommuteCompareRequest(BaseModel):
    """Request payload to compare commute travel times from multiple properties to a single destination."""

    property_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of 2 to 10 property IDs to compare against destination.",
    )
    destination: CommuteDestination
    mode: TravelMode = Field(
        default=TravelMode.DRIVING,
        description="Travel mode for comparison.",
    )


class CommuteCompareResponse(BaseModel):
    """Comparison matrix response comparing commute from multiple properties to a single target destination."""

    destination: CommuteDestination
    mode: TravelMode
    comparisons: list[CommuteResponse]
    fastest_property_id: int | None = Field(
        None, description="Property ID with the lowest commute duration."
    )
    shortest_property_id: int | None = Field(
        None, description="Property ID with the lowest commute distance."
    )

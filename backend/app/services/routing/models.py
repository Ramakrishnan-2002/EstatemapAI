from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class TravelMode(StrEnum):
    """Supported travel modes for commute calculations."""

    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"
    TRANSIT = "transit"


class RouteGeometry(BaseModel):
    """
    GeoJSON LineString geometry for road network routes.
    Strictly follows RFC 7946: coordinates are [longitude, latitude] pairs.
    """

    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]] = Field(
        ...,
        description="Array of [longitude, latitude] coordinate pairs representing the route path.",
        min_length=2,
    )


class RoutePoint(BaseModel):
    """Geographic coordinate pair for route origin/destination."""

    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class RouteResult(BaseModel):
    """Encapsulates the travel metric and path geometry returned by a routing provider."""

    distance_meters: float = Field(..., ge=0.0, description="Total travel distance in meters.")
    duration_seconds: float = Field(
        ..., ge=0.0, description="Estimated travel duration in seconds."
    )
    distance_km: float = Field(..., ge=0.0, description="Travel distance in kilometers.")
    duration_minutes: float = Field(..., ge=0.0, description="Estimated duration in minutes.")
    mode: TravelMode
    geometry: RouteGeometry
    summary: str | None = None
    provider: str

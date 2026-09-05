from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.property import PropertyResponse


class GeoPoint(BaseModel):
    """Geographic coordinate point in WGS84 (EPSG:4326)."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90.0 and +90.0")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitude between -180.0 and +180.0"
    )

    @field_validator("latitude", "longitude")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Coordinates must be finite numeric values.")
        return v


class SpatialFilterBase(BaseModel):
    """Common property filter parameters composable with spatial queries."""

    min_price: float | None = Field(default=None, ge=0, description="Minimum price filter")
    max_price: float | None = Field(default=None, ge=0, description="Maximum price filter")
    property_type: str | None = Field(
        default=None,
        max_length=50,
        description="Property type (e.g. apartment, villa, independent_house)",
    )
    bedrooms: int | None = Field(default=None, ge=0, description="Bedrooms count")
    bathrooms: float | None = Field(default=None, ge=0, description="Bathrooms count")
    status: str | None = Field(default="active", max_length=30, description="Listing status")
    sort_by: str = Field(
        default="distance_asc",
        description="Sort order: distance_asc, distance_desc, newest, oldest, price_asc, price_desc, area_asc, area_desc",
    )
    limit: int = Field(
        default=50, ge=1, le=200, description="Maximum number of properties to return (max 200)"
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset")


class RadiusSearchParams(SpatialFilterBase):
    """Parameters for radius-based proximity search."""

    latitude: float = Field(..., ge=-90.0, le=90.0, description="Center point latitude (-90 to 90)")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Center point longitude (-180 to 180)"
    )
    radius_km: float = Field(
        default=10.0,
        gt=0.0,
        le=200.0,
        description="Search radius in kilometers (must be > 0 and <= 200 km)",
    )

    @field_validator("latitude", "longitude", "radius_km")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Spatial parameters must be finite numeric values.")
        return v


class BoundingBoxSearchParams(SpatialFilterBase):
    """Parameters for geographic bounding-box search."""

    min_lat: float = Field(..., ge=-90.0, le=90.0, description="Southernmost latitude")
    min_lng: float = Field(..., ge=-180.0, le=180.0, description="Westernmost longitude")
    max_lat: float = Field(..., ge=-90.0, le=90.0, description="Northernmost latitude")
    max_lng: float = Field(..., ge=-180.0, le=180.0, description="Easternmost longitude")

    @field_validator("min_lat", "min_lng", "max_lat", "max_lng")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Bounding box coordinates must be finite numeric values.")
        return v

    @model_validator(mode="after")
    def validate_bbox(self) -> BoundingBoxSearchParams:
        if self.min_lat > self.max_lat:
            raise ValueError(
                f"min_lat ({self.min_lat}) cannot be greater than max_lat ({self.max_lat})."
            )
        return self


class ViewportSearchParams(SpatialFilterBase):
    """Parameters for map viewport search (north, south, east, west)."""

    north: float = Field(..., ge=-90.0, le=90.0, description="Northern boundary latitude")
    south: float = Field(..., ge=-90.0, le=90.0, description="Southern boundary latitude")
    east: float = Field(..., ge=-180.0, le=180.0, description="Eastern boundary longitude")
    west: float = Field(..., ge=-180.0, le=180.0, description="Western boundary longitude")

    @field_validator("north", "south", "east", "west")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Viewport coordinates must be finite numeric values.")
        return v

    @model_validator(mode="after")
    def validate_viewport(self) -> ViewportSearchParams:
        if self.south > self.north:
            raise ValueError(f"south ({self.south}) cannot be greater than north ({self.north}).")
        return self


class PolygonGeoJSON(BaseModel):
    """GeoJSON Polygon definition with validation."""

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]] = Field(
        ...,
        description="List of linear rings. First ring is exterior boundary; coordinates are [longitude, latitude].",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon_rings(cls, rings: list[list[list[float]]]) -> list[list[list[float]]]:
        if not rings:
            raise ValueError("Polygon must contain at least one linear ring.")

        exterior = rings[0]
        if len(exterior) < 4:
            raise ValueError(
                f"Polygon exterior ring must contain at least 4 positions (got {len(exterior)})."
            )

        # RFC 7946: First and last position must be equivalent
        if exterior[0] != exterior[-1]:
            raise ValueError(
                "Polygon linear ring must be closed (first coordinate must match last coordinate)."
            )

        for ring in rings:
            for pos in ring:
                if len(pos) < 2:
                    raise ValueError(
                        f"Each position must have at least [longitude, latitude], got {pos}."
                    )
                lng, lat = pos[0], pos[1]
                if math.isnan(lng) or math.isinf(lng) or math.isnan(lat) or math.isinf(lat):
                    raise ValueError("Polygon coordinates must be finite numbers.")
                if not (-180.0 <= lng <= 180.0):
                    raise ValueError(f"Longitude {lng} out of range [-180, 180].")
                if not (-90.0 <= lat <= 90.0):
                    raise ValueError(f"Latitude {lat} out of range [-90, 90].")

        return rings


class PolygonSearchParams(SpatialFilterBase):
    """Payload for polygon-based spatial query."""

    polygon: PolygonGeoJSON = Field(..., description="GeoJSON Polygon defining the search boundary")


# ==========================================
# Response Models
# ==========================================


class PropertyDistanceResponse(BaseModel):
    """Property result accompanied by calculated distance from search origin."""

    property: PropertyResponse
    distance_km: float = Field(..., ge=0.0, description="Distance in kilometers from search center")

    model_config = ConfigDict(from_attributes=True)


class RadiusSearchResponse(BaseModel):
    """Response envelope for radius search."""

    items: list[PropertyDistanceResponse]
    total: int
    center: GeoPoint
    radius_km: float


class GeoJSONPointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude] in WGS84 coordinates",
    )


class GeoJSONPropertyFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    id: int
    geometry: GeoJSONPointGeometry
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    """RFC 7946 compliant GeoJSON FeatureCollection response."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONPropertyFeature]
    total: int = Field(..., description="Total count of features in this spatial result")


# ==========================================
# POI Schemas
# ==========================================

# Import POICategory here to avoid circular imports at module level
from app.models.poi_category import POICategory  # noqa: E402


class POICreate(BaseModel):
    """Validated input for creating a new Point of Interest."""

    name: str = Field(..., min_length=1, max_length=255, description="POI name")
    category: POICategory = Field(..., description="POI category (controlled vocabulary)")
    subcategory: str | None = Field(
        default=None, max_length=100, description="Optional sub-category"
    )
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in WGS84 (-90 to +90)")
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitude in WGS84 (-180 to +180)"
    )
    address: str | None = Field(default=None, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    locality: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)

    @field_validator("latitude", "longitude")
    @classmethod
    def check_finite(cls, v: float) -> float:
        if math.isnan(v) or math.isinf(v):
            raise ValueError("POI coordinates must be finite numeric values.")
        return v

    @field_validator("name", "city")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Value cannot be blank or whitespace-only.")
        return stripped


class POIUpdate(BaseModel):
    """Partial update schema for POI — all fields optional."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    category: POICategory | None = Field(default=None)
    subcategory: str | None = Field(default=None, max_length=100)
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    locality: str | None = Field(default=None, max_length=100)
    is_active: bool | None = Field(default=None)


class POIResponse(BaseModel):
    """Full POI representation returned by API endpoints."""

    id: int
    name: str
    category: POICategory
    subcategory: str | None
    latitude: float
    longitude: float
    address: str | None
    city: str
    locality: str | None
    is_active: bool
    created_at: str  # ISO 8601

    model_config = ConfigDict(from_attributes=True)


class POIWithDistance(BaseModel):
    """POI result paired with the computed distance from an origin point."""

    poi: POIResponse
    distance_km: float = Field(..., ge=0.0, description="Distance in kilometers")


class NearbyPOIsResponse(BaseModel):
    """
    Response envelope for POI proximity queries.
    Used by both /pois/nearby and /properties/{id}/nearby.
    """

    items: list[POIWithDistance]
    total: int
    radius_km: float = Field(..., description="Search radius used for this result")
    category: POICategory | None = Field(
        default=None, description="Category filter applied (null = all categories)"
    )


class CategoryIntelligence(BaseModel):
    """
    Location intelligence summary for a single POI category relative to a property.
    Values are computed dynamically by PostGIS — they are never stored on the Property row.
    """

    nearest_distance_km: float | None = Field(
        default=None,
        ge=0.0,
        description="Distance to the nearest active POI of this category (km). "
        "None if no POI of this category exists within the search radius.",
    )
    count_within_radius: int = Field(
        ...,
        ge=0,
        description="Number of active POIs of this category within the default search radius.",
    )


class LocationIntelligenceResponse(BaseModel):
    """
    Deterministic location intelligence summary for a property.

    Contains per-category proximity information computed from PostGIS spatial
    queries. This is a factual geographic report, not an AI-generated ranking.
    The AI layer (future Phase) may explain these facts but must not override them.
    """

    property_id: int
    radius_km: float = Field(
        ...,
        description="Radius in km used for count_within_radius in each category.",
    )
    categories: dict[POICategory, CategoryIntelligence] = Field(
        ...,
        description="Per-category proximity summary. Keys are POICategory enum values.",
    )


# ==========================================
# POI GeoJSON Schemas (RFC 7946)
# ==========================================


class POIGeoJSONProperties(BaseModel):
    """Typed properties block inside a POI GeoJSON Feature."""

    id: int
    name: str
    category: str
    subcategory: str | None
    locality: str | None
    city: str
    is_active: bool


class POIGeoJSONFeature(BaseModel):
    """RFC 7946 GeoJSON Feature for a single Point of Interest."""

    type: Literal["Feature"] = "Feature"
    id: int
    geometry: GeoJSONPointGeometry
    properties: POIGeoJSONProperties


class POIGeoJSONFeatureCollection(BaseModel):
    """RFC 7946 GeoJSON FeatureCollection for POI map queries."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[POIGeoJSONFeature]
    total: int = Field(..., description="Total count of POI features in this result")

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.utils.geo import coords_from_point


class AmenityResponse(BaseModel):
    id: int
    name: str
    category: str
    icon: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PropertyImageResponse(BaseModel):
    id: int
    image_url: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    price: float = Field(..., ge=0, description="Price in INR or local currency")
    property_type: str = Field(
        ...,
        max_length=50,
        description="e.g. apartment, villa, independent_house, plot, commercial, other",
    )
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    area_sqft: float = Field(..., gt=0, description="Super built-up / total area in sqft")
    address: str = Field(..., min_length=3, max_length=500)
    city: str = Field(..., min_length=2, max_length=100)
    locality: str = Field(..., min_length=2, max_length=100)
    status: str = Field(
        default="active",
        max_length=30,
        description="active, inactive, sold, rented, draft",
    )


class PropertyCreate(PropertyBase):
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="WGS84 Latitude between -90 and +90",
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="WGS84 Longitude between -180 and +180",
    )
    image_urls: list[str] = Field(default_factory=list, description="List of image URLs")
    amenity_ids: list[int] = Field(default_factory=list, description="List of Amenity IDs")


class PropertyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    price: float | None = Field(default=None, ge=0)
    property_type: str | None = Field(default=None, max_length=50)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    area_sqft: float | None = Field(default=None, gt=0)
    address: str | None = Field(default=None, min_length=3, max_length=500)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    locality: str | None = Field(default=None, min_length=2, max_length=100)
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    status: str | None = Field(default=None, max_length=30)
    image_urls: list[str] | None = None
    amenity_ids: list[int] | None = None


class PropertyResponse(PropertyBase):
    id: int
    owner_id: int
    latitude: float = 0.0
    longitude: float = 0.0
    images: list[PropertyImageResponse] = Field(default_factory=list)
    amenities: list[AmenityResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_coordinates(cls, data: Any) -> Any:
        """Extract (latitude, longitude) from PostGIS location object if data is an ORM instance."""
        if hasattr(data, "location") and data.location is not None:
            lat, lng = coords_from_point(data.location)
            # If data is an ORM object, we can construct a dictionary or attach attributes
            if isinstance(data, dict):
                data["latitude"] = lat
                data["longitude"] = lng
            else:
                data.latitude = lat
                data.longitude = lng
        return data


class PropertyFilterParams(BaseModel):
    city: str | None = None
    locality: str | None = None
    property_type: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: float | None = Field(default=None, ge=0)
    status: str | None = "active"
    sort_by: str = Field(
        default="newest",
        description="Sort order: newest, oldest, price_asc, price_desc, area_asc, area_desc",
    )
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedPropertyResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

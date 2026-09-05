from pydantic import BaseModel, Field


class PropertyFilterParams(BaseModel):
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    property_type: str | None = None
    city: str | None = None
    locality: str | None = None
    amenity_ids: list[int] | None = None

    # Geospatial parameters
    latitude: float | None = None
    longitude: float | None = None
    radius_km: float | None = Field(default=None, gt=0)

    # Bounding box
    min_lat: float | None = None
    max_lat: float | None = None
    min_lng: float | None = None
    max_lng: float | None = None

    # Pagination & Sorting
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = "created_at"
    sort_order: str = "desc"

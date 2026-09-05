from typing import Any

from pydantic import BaseModel, Field


class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: list[float]  # [lng, lat]


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature] = Field(default_factory=list)


class ViewportBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float

from __future__ import annotations

import json
from typing import Any

from app.core.exceptions import ValidationException
from app.models.poi import PointOfInterest
from app.models.property import Property
from app.schemas.geo import (
    GeoJSONFeatureCollection,
    GeoJSONPointGeometry,
    GeoJSONPropertyFeature,
    POIGeoJSONFeature,
    POIGeoJSONFeatureCollection,
    POIGeoJSONProperties,
    PolygonGeoJSON,
    PropertyDistanceResponse,
    RadiusSearchResponse,
)
from app.schemas.property import PropertyResponse
from app.utils.geo import coords_from_point


class GeoService:
    """
    Domain service providing coordinate validations, GeoJSON RFC 7946 serialization,
    polygon parsing, and spatial query normalization.
    """

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
        """Validate that coordinates fall within standard WGS84 ranges."""
        if not (-90.0 <= latitude <= 90.0):
            raise ValidationException(
                f"Invalid latitude {latitude}. Latitude must be between -90.0 and +90.0.",
                details={"latitude": latitude},
            )
        if not (-180.0 <= longitude <= 180.0):
            raise ValidationException(
                f"Invalid longitude {longitude}. Longitude must be between -180.0 and +180.0.",
                details={"longitude": longitude},
            )
        return latitude, longitude

    @staticmethod
    def validate_radius(radius_km: float) -> float:
        """Validate that search radius is positive and does not exceed system limit."""
        if radius_km <= 0:
            raise ValidationException(
                f"Invalid radius_km {radius_km}. Radius must be greater than 0.",
                details={"radius_km": radius_km},
            )
        if radius_km > 200.0:
            raise ValidationException(
                f"Requested radius_km {radius_km} exceeds maximum permitted limit of 200.0 km.",
                details={"radius_km": radius_km, "max_allowed": 200.0},
            )
        return radius_km

    @staticmethod
    def polygon_to_wkt_or_geojson(polygon: PolygonGeoJSON) -> str:
        """Serialize validated PolygonGeoJSON to JSON string for PostGIS ST_GeomFromGeoJSON."""
        return json.dumps(polygon.model_dump())

    @staticmethod
    def property_to_geojson_feature(
        property_obj: Property,
        extra_properties: dict[str, Any] | None = None,
    ) -> GeoJSONPropertyFeature:
        """
        Convert a Property ORM instance to a GeoJSON Feature.
        Strictly enforces [longitude, latitude] coordinate ordering in geometry.
        """
        lat, lng = coords_from_point(property_obj.location)

        primary_image = (
            property_obj.images[0].image_url
            if property_obj.images and len(property_obj.images) > 0
            else None
        )

        props: dict[str, Any] = {
            "id": property_obj.id,
            "owner_id": property_obj.owner_id,
            "title": property_obj.title,
            "price": float(property_obj.price),
            "property_type": property_obj.property_type,
            "bedrooms": property_obj.bedrooms,
            "bathrooms": float(property_obj.bathrooms) if property_obj.bathrooms else None,
            "area_sqft": float(property_obj.area_sqft),
            "address": property_obj.address,
            "city": property_obj.city,
            "locality": property_obj.locality,
            "status": property_obj.status,
            "primary_image": primary_image,
            "created_at": property_obj.created_at.isoformat() if property_obj.created_at else None,
        }

        if extra_properties:
            props.update(extra_properties)

        return GeoJSONPropertyFeature(
            id=property_obj.id,
            geometry=GeoJSONPointGeometry(coordinates=[lng, lat]),  # GeoJSON standard: [lng, lat]
            properties=props,
        )

    @staticmethod
    def properties_to_feature_collection(
        items: list[Property] | list[tuple[Property, float]],
        total: int | None = None,
    ) -> GeoJSONFeatureCollection:
        """
        Convert a list of Property entities (or (Property, distance_km) tuples)
        into a GeoJSON FeatureCollection.
        """
        features: list[GeoJSONPropertyFeature] = []

        for item in items:
            if isinstance(item, tuple):
                prop, dist = item
                feature = GeoService.property_to_geojson_feature(
                    prop, extra_properties={"distance_km": round(dist, 2)}
                )
            else:
                feature = GeoService.property_to_geojson_feature(item)
            features.append(feature)

        return GeoJSONFeatureCollection(
            features=features,
            total=total if total is not None else len(features),
        )

    @staticmethod
    def format_radius_response(
        items_with_distance: list[tuple[Property, float]],
        total: int,
        center_lat: float,
        center_lng: float,
        radius_km: float,
    ) -> RadiusSearchResponse:
        """Format radius search tuples into typed RadiusSearchResponse."""
        item_responses: list[PropertyDistanceResponse] = []
        for prop, dist in items_with_distance:
            prop_resp = PropertyResponse.model_validate(prop)
            item_responses.append(
                PropertyDistanceResponse(
                    property=prop_resp,
                    distance_km=round(dist, 2),
                )
            )

        return RadiusSearchResponse(
            items=item_responses,
            total=total,
            center={"latitude": center_lat, "longitude": center_lng},  # type: ignore[arg-type]
            radius_km=radius_km,
        )

    @staticmethod
    def poi_to_geojson_feature(poi: PointOfInterest) -> POIGeoJSONFeature:
        """
        Convert a PointOfInterest ORM instance to a GeoJSON Feature.
        Strictly enforces [longitude, latitude] coordinate ordering per RFC 7946.
        """
        lat, lng = coords_from_point(poi.location)
        return POIGeoJSONFeature(
            id=poi.id,
            geometry=GeoJSONPointGeometry(coordinates=[lng, lat]),
            properties=POIGeoJSONProperties(
                id=poi.id,
                name=poi.name,
                category=poi.category,
                subcategory=poi.subcategory,
                locality=poi.locality,
                city=poi.city,
                is_active=poi.is_active,
            ),
        )

    @staticmethod
    def pois_to_feature_collection(
        pois: list[PointOfInterest],
        total: int | None = None,
    ) -> POIGeoJSONFeatureCollection:
        """
        Convert a list of PointOfInterest ORM instances into a GeoJSON FeatureCollection.
        Reuses the same RFC 7946 coordinate ordering convention as properties_to_feature_collection.
        """
        features = [GeoService.poi_to_geojson_feature(poi) for poi in pois]
        return POIGeoJSONFeatureCollection(
            features=features,
            total=total if total is not None else len(features),
        )

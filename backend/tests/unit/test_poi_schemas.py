"""
Unit tests for POI Pydantic schemas.

Tests validate:
- POICreate: valid/invalid coordinates, valid/invalid category, blank name/city
- POIUpdate: partial fields
- POIResponse: serialization
- POIWithDistance: structure
- CategoryIntelligence: nearest_distance_km optionality
- LocationIntelligenceResponse: full structure
- POIGeoJSONFeature: RFC 7946 coordinate ordering
"""

import pytest
from pydantic import ValidationError

from app.models.poi_category import POICategory
from app.schemas.geo import (
    CategoryIntelligence,
    GeoJSONPointGeometry,
    LocationIntelligenceResponse,
    NearbyPOIsResponse,
    POICreate,
    POIGeoJSONFeature,
    POIGeoJSONProperties,
    POIResponse,
    POIUpdate,
    POIWithDistance,
)

# ─── POICreate ────────────────────────────────────────────────────────────────


class TestPOICreate:
    def test_valid_create(self):
        poi = POICreate(
            name="City Hospital",
            category=POICategory.HOSPITAL,
            latitude=12.9716,
            longitude=77.5946,
            city="Bengaluru",
        )
        assert poi.name == "City Hospital"
        assert poi.category == POICategory.HOSPITAL
        assert poi.is_active is True

    def test_valid_all_fields(self):
        poi = POICreate(
            name="West End School",
            category=POICategory.SCHOOL,
            subcategory="cbse",
            latitude=12.9500,
            longitude=77.6000,
            address="123 Main Road",
            city="Bengaluru",
            locality="Koramangala",
            is_active=True,
        )
        assert poi.subcategory == "cbse"
        assert poi.locality == "Koramangala"

    def test_invalid_latitude_too_high(self):
        with pytest.raises(ValidationError) as exc_info:
            POICreate(
                name="Test",
                category=POICategory.PARK,
                latitude=91.0,
                longitude=77.5,
                city="Bengaluru",
            )
        assert "latitude" in str(exc_info.value).lower() or "91" in str(exc_info.value)

    def test_invalid_latitude_too_low(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="Test",
                category=POICategory.PARK,
                latitude=-91.0,
                longitude=77.5,
                city="Bengaluru",
            )

    def test_invalid_longitude_too_high(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="Test",
                category=POICategory.TRANSIT,
                latitude=12.9,
                longitude=181.0,
                city="Bengaluru",
            )

    def test_invalid_longitude_too_low(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="Test",
                category=POICategory.TRANSIT,
                latitude=12.9,
                longitude=-181.0,
                city="Bengaluru",
            )

    def test_invalid_category_string(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="Test",
                category="not_a_real_category",  # type: ignore[arg-type]
                latitude=12.9,
                longitude=77.5,
                city="Bengaluru",
            )

    def test_blank_name_rejected(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="   ",
                category=POICategory.SUPERMARKET,
                latitude=12.9,
                longitude=77.5,
                city="Bengaluru",
            )

    def test_blank_city_rejected(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="Test Store",
                category=POICategory.SUPERMARKET,
                latitude=12.9,
                longitude=77.5,
                city="   ",
            )

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            POICreate(
                name="A" * 256,
                category=POICategory.BANK,
                latitude=12.9,
                longitude=77.5,
                city="Bengaluru",
            )

    def test_all_valid_categories(self):
        for cat in POICategory:
            poi = POICreate(
                name=f"Test {cat.value}",
                category=cat,
                latitude=12.9716,
                longitude=77.5946,
                city="Bengaluru",
            )
            assert poi.category == cat


# ─── POIUpdate ────────────────────────────────────────────────────────────────


class TestPOIUpdate:
    def test_empty_update_valid(self):
        update = POIUpdate()
        assert update.name is None
        assert update.category is None

    def test_partial_update(self):
        update = POIUpdate(name="New Name", is_active=False)
        assert update.name == "New Name"
        assert update.is_active is False
        assert update.latitude is None

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            POIUpdate(category="garbage")  # type: ignore[arg-type]


# ─── POIResponse ──────────────────────────────────────────────────────────────


class TestPOIResponse:
    def _make_response(self, **kwargs):
        defaults = {
            "id": 1,
            "name": "Test Hospital",
            "category": POICategory.HOSPITAL,
            "subcategory": "private",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Main Road",
            "city": "Bengaluru",
            "locality": "Central",
            "is_active": True,
            "created_at": "2026-09-04T12:00:00",
        }
        defaults.update(kwargs)
        return POIResponse(**defaults)

    def test_valid_response(self):
        resp = self._make_response()
        assert resp.id == 1
        assert resp.category == POICategory.HOSPITAL

    def test_nullable_fields_allowed(self):
        resp = self._make_response(subcategory=None, address=None, locality=None)
        assert resp.subcategory is None
        assert resp.address is None


# ─── POIWithDistance ──────────────────────────────────────────────────────────


class TestPOIWithDistance:
    def test_structure(self):
        poi_resp = POIResponse(
            id=5,
            name="Metro Station",
            category=POICategory.TRANSIT,
            subcategory=None,
            latitude=12.97,
            longitude=77.60,
            address=None,
            city="Bengaluru",
            locality="Central",
            is_active=True,
            created_at="2026-09-04T10:00:00",
        )
        with_dist = POIWithDistance(poi=poi_resp, distance_km=1.42)
        assert with_dist.distance_km == 1.42
        assert with_dist.poi.name == "Metro Station"

    def test_negative_distance_rejected(self):
        poi_resp = POIResponse(
            id=5,
            name="Metro",
            category=POICategory.TRANSIT,
            subcategory=None,
            latitude=12.97,
            longitude=77.60,
            address=None,
            city="Bengaluru",
            locality="Central",
            is_active=True,
            created_at="2026-09-04T10:00:00",
        )
        with pytest.raises(ValidationError):
            POIWithDistance(poi=poi_resp, distance_km=-0.1)


# ─── NearbyPOIsResponse ───────────────────────────────────────────────────────


class TestNearbyPOIsResponse:
    def test_empty_response(self):
        resp = NearbyPOIsResponse(items=[], total=0, radius_km=3.0)
        assert resp.total == 0
        assert resp.category is None
        assert resp.radius_km == 3.0

    def test_with_category(self):
        resp = NearbyPOIsResponse(items=[], total=0, radius_km=5.0, category=POICategory.HOSPITAL)
        assert resp.category == POICategory.HOSPITAL


# ─── CategoryIntelligence ─────────────────────────────────────────────────────


class TestCategoryIntelligence:
    def test_with_data(self):
        cat = CategoryIntelligence(nearest_distance_km=0.84, count_within_radius=4)
        assert cat.nearest_distance_km == 0.84
        assert cat.count_within_radius == 4

    def test_no_nearest_poi(self):
        cat = CategoryIntelligence(nearest_distance_km=None, count_within_radius=0)
        assert cat.nearest_distance_km is None

    def test_negative_count_rejected(self):
        with pytest.raises(ValidationError):
            CategoryIntelligence(nearest_distance_km=None, count_within_radius=-1)


# ─── LocationIntelligenceResponse ─────────────────────────────────────────────


class TestLocationIntelligenceResponse:
    def test_full_response(self):
        categories = {
            POICategory.HOSPITAL: CategoryIntelligence(
                nearest_distance_km=0.84, count_within_radius=4
            ),
            POICategory.SCHOOL: CategoryIntelligence(
                nearest_distance_km=1.15, count_within_radius=7
            ),
            POICategory.TRANSIT: CategoryIntelligence(
                nearest_distance_km=0.62, count_within_radius=3
            ),
        }
        response = LocationIntelligenceResponse(
            property_id=123,
            radius_km=3.0,
            categories=categories,
        )
        assert response.property_id == 123
        assert response.radius_km == 3.0
        assert POICategory.HOSPITAL in response.categories
        assert response.categories[POICategory.HOSPITAL].nearest_distance_km == 0.84

    def test_all_categories_none_distance(self):
        """Verify that None nearest_distance_km is valid (no POIs of that category)."""
        categories = {
            cat: CategoryIntelligence(nearest_distance_km=None, count_within_radius=0)
            for cat in POICategory
        }
        response = LocationIntelligenceResponse(
            property_id=1,
            radius_km=3.0,
            categories=categories,
        )
        assert all(v.nearest_distance_km is None for v in response.categories.values())


# ─── POI GeoJSON ──────────────────────────────────────────────────────────────


class TestPOIGeoJSON:
    def test_feature_coordinate_order(self):
        """GeoJSON coordinates must be [longitude, latitude] per RFC 7946."""
        feature = POIGeoJSONFeature(
            id=10,
            geometry=GeoJSONPointGeometry(coordinates=[77.5946, 12.9716]),  # [lng, lat]
            properties=POIGeoJSONProperties(
                id=10,
                name="Test POI",
                category="hospital",
                subcategory=None,
                locality="Central",
                city="Bengaluru",
                is_active=True,
            ),
        )
        # coordinates[0] = longitude, coordinates[1] = latitude
        assert feature.geometry.coordinates[0] == 77.5946  # longitude
        assert feature.geometry.coordinates[1] == 12.9716  # latitude

    def test_feature_type_is_feature(self):
        feature = POIGeoJSONFeature(
            id=1,
            geometry=GeoJSONPointGeometry(coordinates=[77.0, 13.0]),
            properties=POIGeoJSONProperties(
                id=1,
                name="Park",
                category="park",
                subcategory=None,
                locality=None,
                city="Bengaluru",
                is_active=True,
            ),
        )
        assert feature.type == "Feature"

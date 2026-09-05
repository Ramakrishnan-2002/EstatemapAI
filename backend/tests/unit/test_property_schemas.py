import pytest
from pydantic import ValidationError

from app.schemas.property import (
    PropertyCreate,
    PropertyFilterParams,
    PropertyUpdate,
)


def test_property_create_valid():
    payload = {
        "title": "Luxury 3BHK Penthouse in Whitefield",
        "description": "Stunning top-floor unit with panoramic skyline views",
        "price": 18500000.0,
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 3.0,
        "area_sqft": 2400.0,
        "address": "ITPB Main Road, Whitefield",
        "city": "Bengaluru",
        "locality": "Whitefield",
        "latitude": 12.9698,
        "longitude": 77.7499,
        "image_urls": ["https://images.estatemap.ai/prop1.jpg"],
        "amenity_ids": [1, 2, 3],
    }
    schema = PropertyCreate(**payload)
    assert schema.title == payload["title"]
    assert schema.latitude == 12.9698
    assert schema.longitude == 77.7499
    assert schema.price == 18500000.0
    assert len(schema.image_urls) == 1
    assert len(schema.amenity_ids) == 3


def test_property_create_invalid_latitude():
    base_payload = {
        "title": "Invalid Lat Villa",
        "price": 5000000.0,
        "property_type": "villa",
        "area_sqft": 1500.0,
        "address": "Test Road",
        "city": "Bengaluru",
        "locality": "Indiranagar",
        "longitude": 77.5,
    }
    # Latitude > 90
    with pytest.raises(ValidationError):
        PropertyCreate(**base_payload, latitude=90.001)

    # Latitude < -90
    with pytest.raises(ValidationError):
        PropertyCreate(**base_payload, latitude=-90.001)


def test_property_create_invalid_longitude():
    base_payload = {
        "title": "Invalid Long Villa",
        "price": 5000000.0,
        "property_type": "villa",
        "area_sqft": 1500.0,
        "address": "Test Road",
        "city": "Bengaluru",
        "locality": "Indiranagar",
        "latitude": 12.97,
    }
    # Longitude > 180
    with pytest.raises(ValidationError):
        PropertyCreate(**base_payload, longitude=180.001)

    # Longitude < -180
    with pytest.raises(ValidationError):
        PropertyCreate(**base_payload, longitude=-180.001)


def test_property_create_negative_price():
    payload = {
        "title": "Negative Price",
        "price": -100.0,
        "property_type": "apartment",
        "area_sqft": 1200.0,
        "address": "Test Road",
        "city": "Bengaluru",
        "locality": "Koramangala",
        "latitude": 12.93,
        "longitude": 77.62,
    }
    with pytest.raises(ValidationError):
        PropertyCreate(**payload)


def test_property_create_zero_or_negative_area():
    payload = {
        "title": "Zero Area Apartment",
        "price": 5000000.0,
        "property_type": "apartment",
        "area_sqft": 0.0,
        "address": "Test Road",
        "city": "Bengaluru",
        "locality": "Koramangala",
        "latitude": 12.93,
        "longitude": 77.62,
    }
    with pytest.raises(ValidationError):
        PropertyCreate(**payload)


def test_property_update_partial_fields():
    update_schema = PropertyUpdate(price=20000000.0, status="sold")
    data = update_schema.model_dump(exclude_unset=True)
    assert data == {"price": 20000000.0, "status": "sold"}
    assert "title" not in data


def test_property_filter_params_defaults_and_limits():
    params = PropertyFilterParams()
    assert params.page == 1
    assert params.page_size == 20
    assert params.sort_by == "newest"

    # page_size > 100 should raise ValidationError
    with pytest.raises(ValidationError):
        PropertyFilterParams(page_size=101)

import pytest

from app.core.exceptions import ValidationException
from app.schemas.geo import PolygonGeoJSON
from app.services.geo_service import GeoService


def test_validate_coordinates_success():
    lat, lng = GeoService.validate_coordinates(12.9716, 77.5946)
    assert lat == 12.9716
    assert lng == 77.5946


def test_validate_coordinates_out_of_bounds():
    with pytest.raises(ValidationException):
        GeoService.validate_coordinates(91.0, 77.5946)

    with pytest.raises(ValidationException):
        GeoService.validate_coordinates(12.9716, 181.0)


def test_validate_radius_success():
    r = GeoService.validate_radius(25.0)
    assert r == 25.0


def test_validate_radius_invalid():
    with pytest.raises(ValidationException):
        GeoService.validate_radius(0.0)

    with pytest.raises(ValidationException):
        GeoService.validate_radius(-10.0)

    with pytest.raises(ValidationException):
        GeoService.validate_radius(250.0)


def test_polygon_to_wkt_or_geojson():
    poly = PolygonGeoJSON(
        type="Polygon",
        coordinates=[
            [
                [77.50, 12.90],
                [77.60, 12.90],
                [77.60, 13.00],
                [77.50, 13.00],
                [77.50, 12.90],
            ]
        ],
    )
    json_str = GeoService.polygon_to_wkt_or_geojson(poly)
    assert '"Polygon"' in json_str
    assert "77.5" in json_str

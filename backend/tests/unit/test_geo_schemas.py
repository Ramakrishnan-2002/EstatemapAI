import pytest
from pydantic import ValidationError

from app.schemas.geo import (
    BoundingBoxSearchParams,
    GeoPoint,
    PolygonGeoJSON,
    PolygonSearchParams,
    RadiusSearchParams,
    ViewportSearchParams,
)


def test_geopoint_valid():
    pt = GeoPoint(latitude=12.9716, longitude=77.5946)
    assert pt.latitude == 12.9716
    assert pt.longitude == 77.5946


def test_geopoint_invalid_latitude():
    with pytest.raises(ValidationError):
        GeoPoint(latitude=95.0, longitude=77.5946)

    with pytest.raises(ValidationError):
        GeoPoint(latitude=-91.0, longitude=77.5946)


def test_geopoint_invalid_longitude():
    with pytest.raises(ValidationError):
        GeoPoint(latitude=12.9716, longitude=185.0)

    with pytest.raises(ValidationError):
        GeoPoint(latitude=12.9716, longitude=-185.0)


def test_geopoint_nan_inf_rejected():
    with pytest.raises(ValidationError):
        GeoPoint(latitude=float("nan"), longitude=77.5946)

    with pytest.raises(ValidationError):
        GeoPoint(latitude=12.9716, longitude=float("inf"))


def test_radius_search_params_valid():
    params = RadiusSearchParams(latitude=12.97, longitude=77.59, radius_km=15.5)
    assert params.radius_km == 15.5
    assert params.limit == 50
    assert params.offset == 0


def test_radius_search_params_invalid_radius():
    # Radius <= 0 must fail
    with pytest.raises(ValidationError):
        RadiusSearchParams(latitude=12.97, longitude=77.59, radius_km=0.0)

    with pytest.raises(ValidationError):
        RadiusSearchParams(latitude=12.97, longitude=77.59, radius_km=-5.0)

    # Radius > 200 must fail
    with pytest.raises(ValidationError):
        RadiusSearchParams(latitude=12.97, longitude=77.59, radius_km=250.0)


def test_bounding_box_params_valid():
    bbox = BoundingBoxSearchParams(
        min_lat=12.8,
        min_lng=77.4,
        max_lat=13.1,
        max_lng=77.8,
    )
    assert bbox.min_lat < bbox.max_lat


def test_bounding_box_params_invalid_min_max_lat():
    with pytest.raises(ValidationError):
        BoundingBoxSearchParams(
            min_lat=13.5,
            min_lng=77.4,
            max_lat=12.5,  # min_lat > max_lat
            max_lng=77.8,
        )


def test_viewport_params_valid():
    vp = ViewportSearchParams(north=13.1, south=12.8, east=77.8, west=77.4)
    assert vp.north == 13.1
    assert vp.south == 12.8


def test_viewport_params_invalid_south_greater_than_north():
    with pytest.raises(ValidationError):
        ViewportSearchParams(north=12.0, south=13.0, east=77.8, west=77.4)


def test_polygon_geojson_valid():
    poly = PolygonGeoJSON(
        type="Polygon",
        coordinates=[
            [
                [77.50, 12.90],
                [77.60, 12.90],
                [77.60, 13.00],
                [77.50, 13.00],
                [77.50, 12.90],  # Closed ring
            ]
        ],
    )
    assert len(poly.coordinates[0]) == 5


def test_polygon_geojson_unclosed_ring_rejected():
    with pytest.raises(ValidationError):
        PolygonGeoJSON(
            type="Polygon",
            coordinates=[
                [
                    [77.50, 12.90],
                    [77.60, 12.90],
                    [77.60, 13.00],
                    [77.50, 13.00],  # NOT closed (does not match 77.50, 12.90)
                ]
            ],
        )


def test_polygon_geojson_less_than_four_coordinates():
    with pytest.raises(ValidationError):
        PolygonGeoJSON(
            type="Polygon",
            coordinates=[
                [
                    [77.50, 12.90],
                    [77.60, 12.90],
                    [77.50, 12.90],
                ]
            ],
        )


def test_polygon_search_params_valid():
    params = PolygonSearchParams(
        polygon=PolygonGeoJSON(
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
        ),
        min_price=1000000,
        limit=25,
    )
    assert params.min_price == 1000000
    assert params.limit == 25

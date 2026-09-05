import pytest
from pydantic import ValidationError

from app.core.exceptions import ValidationException
from app.services.routing.factory import get_routing_provider
from app.services.routing.mock_provider import MockRoutingProvider
from app.services.routing.models import (
    RouteGeometry,
    RoutePoint,
    RouteResult,
    TravelMode,
)
from app.services.routing.osrm_provider import OSRMProvider


def test_travel_mode_enum_values():
    assert TravelMode.DRIVING == "driving"
    assert TravelMode.WALKING == "walking"
    assert TravelMode.CYCLING == "cycling"
    assert TravelMode.TRANSIT == "transit"


def test_route_geometry_valid_geojson():
    geom = RouteGeometry(
        type="LineString",
        coordinates=[[77.5946, 12.9716], [77.6245, 12.9352]],
    )
    assert geom.type == "LineString"
    assert len(geom.coordinates) == 2
    assert geom.coordinates[0] == [77.5946, 12.9716]


def test_route_geometry_rejects_fewer_than_two_points():
    with pytest.raises(ValidationError):
        RouteGeometry(
            type="LineString",
            coordinates=[[77.5946, 12.9716]],
        )


def test_route_point_validation():
    point = RoutePoint(latitude=12.9716, longitude=77.5946)
    assert point.latitude == 12.9716
    assert point.longitude == 77.5946

    with pytest.raises(ValidationError):
        RoutePoint(latitude=95.0, longitude=77.0)

    with pytest.raises(ValidationError):
        RoutePoint(latitude=12.0, longitude=190.0)


@pytest.mark.asyncio
async def test_mock_routing_provider_driving():
    provider = MockRoutingProvider()
    assert provider.provider_name == "mock"
    assert TravelMode.DRIVING in provider.supported_modes

    # MG Road to Koramangala
    res = await provider.get_route(
        origin_lat=12.9716,
        origin_lng=77.5946,
        dest_lat=12.9352,
        dest_lng=77.6245,
        mode=TravelMode.DRIVING,
    )
    assert isinstance(res, RouteResult)
    assert res.mode == TravelMode.DRIVING
    assert res.distance_km > 0.0
    assert res.duration_minutes > 0.0
    assert res.geometry.type == "LineString"
    assert len(res.geometry.coordinates) >= 2
    # Verify RFC 7946 coordinate ordering: [longitude, latitude]
    assert res.geometry.coordinates[0] == [77.5946, 12.9716]
    assert res.geometry.coordinates[-1] == [77.6245, 12.9352]


@pytest.mark.asyncio
async def test_mock_routing_provider_modes_duration_comparison():
    provider = MockRoutingProvider()
    orig_lat, orig_lng = 12.9716, 77.5946
    dest_lat, dest_lng = 12.9352, 77.6245

    res_driving = await provider.get_route(
        orig_lat, orig_lng, dest_lat, dest_lng, TravelMode.DRIVING
    )
    res_cycling = await provider.get_route(
        orig_lat, orig_lng, dest_lat, dest_lng, TravelMode.CYCLING
    )
    res_walking = await provider.get_route(
        orig_lat, orig_lng, dest_lat, dest_lng, TravelMode.WALKING
    )

    # Driving is faster than cycling, which is faster than walking
    assert (
        res_driving.duration_seconds < res_cycling.duration_seconds < res_walking.duration_seconds
    )


@pytest.mark.asyncio
async def test_mock_routing_provider_unsupported_mode():
    provider = MockRoutingProvider()
    with pytest.raises(ValidationException) as exc_info:
        await provider.get_route(12.9716, 77.5946, 12.9352, 77.6245, TravelMode.TRANSIT)
    assert "not supported by mock provider" in str(exc_info.value)


def test_routing_provider_factory():
    mock_prov = get_routing_provider("mock")
    assert isinstance(mock_prov, MockRoutingProvider)

    osrm_prov = get_routing_provider("osrm")
    assert isinstance(osrm_prov, OSRMProvider)

    with pytest.raises(ValidationException):
        get_routing_provider("unknown_engine")


def test_osrm_provider_profile_mapping():
    osrm = OSRMProvider(base_url="http://test-osrm.local")
    assert osrm._mode_to_profile(TravelMode.DRIVING) == "driving"
    assert osrm._mode_to_profile(TravelMode.WALKING) == "foot"
    assert osrm._mode_to_profile(TravelMode.CYCLING) == "bike"

    with pytest.raises(ValidationException):
        osrm._mode_to_profile(TravelMode.TRANSIT)

import pytest
from pydantic import ValidationError

from app.cache.cache_keys import CacheKeys
from app.schemas.commute import (
    BatchCommuteRequest,
    CommuteCompareRequest,
    CommuteDestination,
    CommuteResponse,
)
from app.services.commute_service import CommuteService
from app.services.routing.mock_provider import MockRoutingProvider
from app.services.routing.models import TravelMode


def test_commute_destination_schema():
    dest = CommuteDestination(
        name="Electronic City Phase 1",
        latitude=12.8399,
        longitude=77.6770,
    )
    assert dest.name == "Electronic City Phase 1"
    assert dest.latitude == 12.8399
    assert dest.longitude == 77.6770

    with pytest.raises(ValidationError):
        CommuteDestination(name="", latitude=12.0, longitude=77.0)

    with pytest.raises(ValidationError):
        CommuteDestination(name="Test", latitude=100.0, longitude=77.0)


def test_batch_commute_request_validation():
    # Valid 2 destinations
    req = BatchCommuteRequest(
        destinations=[
            CommuteDestination(name="CBD", latitude=12.9716, longitude=77.5946),
            CommuteDestination(name="Airport", latitude=13.1986, longitude=77.7066),
        ],
        mode=TravelMode.DRIVING,
    )
    assert len(req.destinations) == 2
    assert req.mode == TravelMode.DRIVING

    # Empty destinations rejected
    with pytest.raises(ValidationError):
        BatchCommuteRequest(destinations=[])

    # More than 5 destinations rejected by schema
    with pytest.raises(ValidationError):
        BatchCommuteRequest(
            destinations=[
                CommuteDestination(
                    name=f"Dest {i}", latitude=12.9 + i * 0.01, longitude=77.5 + i * 0.01
                )
                for i in range(6)
            ]
        )


def test_commute_compare_request_validation():
    req = CommuteCompareRequest(
        property_ids=[1, 2, 3],
        destination=CommuteDestination(name="Office", latitude=12.9352, longitude=77.6245),
        mode=TravelMode.CYCLING,
    )
    assert len(req.property_ids) == 3
    assert req.mode == TravelMode.CYCLING

    # Less than 2 properties rejected
    with pytest.raises(ValidationError):
        CommuteCompareRequest(
            property_ids=[1],
            destination=CommuteDestination(name="Office", latitude=12.9352, longitude=77.6245),
        )

    # More than 10 properties rejected
    with pytest.raises(ValidationError):
        CommuteCompareRequest(
            property_ids=list(range(1, 12)),
            destination=CommuteDestination(name="Office", latitude=12.9352, longitude=77.6245),
        )


def test_commute_service_cache_key_generation():
    key = CacheKeys.route(
        provider="mock",
        mode=TravelMode.DRIVING,
        orig_lat=12.971599,
        orig_lng=77.594599,
        dest_lat=12.935201,
        dest_lng=77.624501,
    )
    assert key == "estatemap:route:v1:mock:driving:12.9716,77.5946:12.9352,77.6245"


@pytest.mark.asyncio
async def test_commute_service_direct_route_calculation():
    # Pass MockRoutingProvider directly
    service = CommuteService(session=None, routing_provider=MockRoutingProvider())  # type: ignore[arg-type]

    response = await service.get_direct_commute(
        origin_lat=12.9716,
        origin_lng=77.5946,
        dest_lat=12.9352,
        dest_lng=77.6245,
        dest_name="Koramangala Sony Signal",
        mode=TravelMode.DRIVING,
    )

    assert isinstance(response, CommuteResponse)
    assert response.property_id is None
    assert response.destination.name == "Koramangala Sony Signal"
    assert response.distance_km > 0.0
    assert response.duration_minutes > 0.0
    assert response.mode == TravelMode.DRIVING
    assert response.provider == "mock"
    assert response.geometry.type == "LineString"

from __future__ import annotations

import pytest

from app.utils.location_resolver import (
    KNOWN_LOCATIONS,
    METRO_BOUNDS,
    LocationResolver,
    validate_registry_coordinates,
)


def test_registry_coordinate_bounds():
    """Verify all registry entries satisfy global and supported metro regional bounds."""
    validate_registry_coordinates()
    for key, (lat, lng, label) in KNOWN_LOCATIONS.items():
        assert -90.0 <= lat <= 90.0, f"Invalid latitude for {key}"
        assert -180.0 <= lng <= 180.0, f"Invalid longitude for {key}"
        in_any_metro = any(
            lat_r[0] <= lat <= lat_r[1] and lng_r[0] <= lng <= lng_r[1]
            for _, lat_r, lng_r in METRO_BOUNDS
        )
        assert (
            in_any_metro
        ), f"Coordinates out of supported metro bounds for {key} ({label}): ({lat}, {lng})"


@pytest.mark.parametrize(
    ("query", "expected_name", "expected_lat", "expected_lng"),
    [
        ("Manyata Tech Park", "Manyata Tech Park", 13.0489, 77.6208),
        ("manyata", "Manyata Tech Park", 13.0489, 77.6208),
        ("Manyata Embassy Business Park", "Manyata Tech Park", 13.0489, 77.6208),
        ("RMZ EcoSpace", "RMZ EcoSpace", 12.9260, 77.6840),
        ("ecospace", "RMZ EcoSpace", 12.9260, 77.6840),
        ("Electronic City", "Electronic City", 12.8452, 77.6602),
        ("e-city", "Electronic City Phase 1", 12.8452, 77.6602),
        ("ITPL", "ITPL Whitefield", 12.9863, 77.7308),
        ("Bagmane Tech Park", "Bagmane Tech Park", 12.9784, 77.6575),
        ("Indiranagar", "Indiranagar", 12.9716, 77.6412),
        ("Koramangala", "Koramangala", 12.9352, 77.6245),
        ("HSR Layout", "HSR Layout", 12.9121, 77.6446),
        ("MG Road", "MG Road", 12.9716, 77.5946),
        ("Silk Board", "Silk Board Junction", 12.9175, 77.6227),
        ("Hebbal", "Hebbal", 13.0358, 77.5970),
        ("Marathahalli", "Marathahalli", 12.9591, 77.6974),
        # Chennai test cases
        ("TIDEL Park", "TIDEL Park", 12.9897, 80.2483),
        ("tidel", "TIDEL Park", 12.9897, 80.2483),
        ("OMR", "OMR IT Expressway", 12.8995, 80.2279),
        ("DLF Cybercity", "DLF Cybercity", 13.0183, 80.1706),
        ("Anna Nagar", "Anna Nagar", 13.0850, 80.2100),
        ("Adyar", "Adyar", 13.0012, 80.2565),
        ("T Nagar", "T. Nagar", 13.0418, 80.2341),
        ("Velachery", "Velachery", 12.9759, 80.2212),
    ],
)
def test_resolve_known_landmarks_and_aliases(
    query: str, expected_name: str, expected_lat: float, expected_lng: float
):
    """Verify exact and alias resolution for all major Bengaluru and Chennai tech hubs and neighborhoods."""
    res = LocationResolver.resolve_destination(query)
    assert res is not None, f"Failed to resolve '{query}'"
    assert res.name == expected_name
    assert abs(res.latitude - expected_lat) < 1e-4
    assert abs(res.longitude - expected_lng) < 1e-4


def test_resolve_unknown_destination_returns_none():
    """Verify unknown or unresolvable destination returns None to trigger clarification."""
    assert LocationResolver.resolve_destination("Atlantis") is None
    assert LocationResolver.resolve_destination("Narnia") is None
    assert LocationResolver.resolve_destination("Mordor") is None
    assert LocationResolver.resolve_destination("") is None
    assert LocationResolver.resolve_destination("   ") is None
    assert LocationResolver.resolve_destination(None) is None

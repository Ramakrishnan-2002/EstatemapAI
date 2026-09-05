from app.cache.cache_keys import CacheKeys


def test_cache_keys_coord_normalization():
    """Ensure coordinates are normalized to 4 decimal places (~11m)."""
    assert CacheKeys.normalize_coord(12.9715987) == 12.9716
    assert CacheKeys.normalize_coord(12.9715123) == 12.9715
    assert CacheKeys.normalize_coord(12.0) == 12.0


def test_route_cache_key_deterministic():
    """Verify route cache keys are identical for nearby coordinates within tolerance."""
    key1 = CacheKeys.route("mock", "driving", 12.971598, 77.594563, 12.935241, 77.624478)
    key2 = CacheKeys.route("mock", "driving", 12.971601, 77.594559, 12.935239, 77.624482)
    assert key1 == key2
    assert key1 == "estatemap:route:v1:mock:driving:12.9716,77.5946:12.9352,77.6245"


def test_route_cache_key_mode_sensitivity():
    """Different travel modes must produce different cache keys."""
    key_drive = CacheKeys.route("mock", "driving", 12.97, 77.59, 12.93, 77.62)
    key_transit = CacheKeys.route("mock", "transit", 12.97, 77.59, 12.93, 77.62)
    key_walking = CacheKeys.route("mock", "walking", 12.97, 77.59, 12.93, 77.62)

    assert key_drive != key_transit
    assert key_drive != key_walking
    assert "driving" in key_drive
    assert "transit" in key_transit


def test_poi_location_intelligence_cache_key():
    """Test location intelligence cache key format."""
    key = CacheKeys.poi_intelligence(property_id=42, radius_km=3.0)
    assert key == "estatemap:poi:v1:property:42:radius:3.0"


def test_map_bounds_cache_key():
    """Test map bounds viewport key normalization."""
    key = CacheKeys.map_properties(
        north=13.00003,
        south=12.90001,
        east=77.60004,
        west=77.50002,
        filters={"min_price": 500000},
    )
    assert key.startswith("estatemap:map:v1:properties:13.0:12.9:77.6:77.5:")


def test_ranking_cache_key_hash_consistency():
    """Test ranking cache key hashing and sensitivity to weights and preferences."""
    dest1 = {
        "name": "Office",
        "latitude": 12.97,
        "longitude": 77.59,
        "weight": 1.0,
        "travel_mode": "driving",
    }
    dest2 = {
        "name": "Office",
        "latitude": 12.97,
        "longitude": 77.59,
        "weight": 2.0,
        "travel_mode": "driving",
    }
    weights = {"commute": 0.5, "amenities": 0.3, "lifestyle": 0.2}

    key1 = CacheKeys.ranking({"destination": dest1, "weights": weights, "min_price": 1000})
    key2 = CacheKeys.ranking({"destination": dest1, "weights": weights, "min_price": 1000})
    key3 = CacheKeys.ranking({"destination": dest2, "weights": weights, "min_price": 1000})

    assert key1 == key2
    assert key1.startswith("estatemap:ranking:v1:")
    assert key1 != key3  # Different destination weight must produce different hash

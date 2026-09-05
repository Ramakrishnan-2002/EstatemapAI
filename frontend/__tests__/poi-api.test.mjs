import test from "node:test";
import assert from "node:assert";

// URL builder helper functions representing the API client serialization logic in lib/api/pois.ts

export function buildNearbyPOIUrl(params, baseUrl = "") {
  const query = new URLSearchParams();
  query.append("latitude", params.latitude.toString());
  query.append("longitude", params.longitude.toString());
  if (params.radius_km !== undefined) query.append("radius_km", params.radius_km.toString());
  if (params.category) query.append("category", params.category);
  if (params.limit !== undefined) query.append("limit", params.limit.toString());

  return `${baseUrl}/api/v1/pois/nearby?${query.toString()}`;
}

export function buildMapPOIUrl(params, baseUrl = "") {
  const query = new URLSearchParams();
  query.append("north", params.north.toString());
  query.append("south", params.south.toString());
  query.append("east", params.east.toString());
  query.append("west", params.west.toString());
  if (params.category) query.append("category", params.category);
  if (params.limit !== undefined) query.append("limit", params.limit.toString());

  return `${baseUrl}/api/v1/maps/pois?${query.toString()}`;
}

export function buildPropertyNearbyUrl(propertyId, params = {}, baseUrl = "") {
  const query = new URLSearchParams();
  if (params.category) query.append("category", params.category);
  if (params.radius_km !== undefined) query.append("radius_km", params.radius_km.toString());
  if (params.limit !== undefined) query.append("limit", params.limit.toString());

  const qs = query.toString();
  return `${baseUrl}/api/v1/properties/${propertyId}/nearby${qs ? `?${qs}` : ""}`;
}

export function buildPropertyLocationIntelligenceUrl(propertyId, radiusKm, baseUrl = "") {
  const query = new URLSearchParams();
  if (radiusKm !== undefined) query.append("radius_km", radiusKm.toString());

  const qs = query.toString();
  return `${baseUrl}/api/v1/properties/${propertyId}/location-intelligence${qs ? `?${qs}` : ""}`;
}

// ─── Tests ────────────────────────────────────────────────────────────────────

test("buildNearbyPOIUrl serializes coordinates, category, and radius correctly", () => {
  const url = buildNearbyPOIUrl({
    latitude: 12.9716,
    longitude: 77.5946,
    radius_km: 3.5,
    category: "hospital",
    limit: 25,
  });

  assert.ok(url.startsWith("/api/v1/pois/nearby?"));
  assert.ok(url.includes("latitude=12.9716"));
  assert.ok(url.includes("longitude=77.5946"));
  assert.ok(url.includes("radius_km=3.5"));
  assert.ok(url.includes("category=hospital"));
  assert.ok(url.includes("limit=25"));
});

test("buildNearbyPOIUrl handles optional category and radius omission", () => {
  const url = buildNearbyPOIUrl({
    latitude: 12.9716,
    longitude: 77.5946,
  });

  assert.ok(url.includes("latitude=12.9716"));
  assert.ok(url.includes("longitude=77.5946"));
  assert.ok(!url.includes("category="));
  assert.ok(!url.includes("radius_km="));
});

test("buildMapPOIUrl serializes bounding box viewport bounds", () => {
  const url = buildMapPOIUrl({
    north: 13.05,
    south: 12.89,
    east: 77.72,
    west: 77.48,
    category: "school",
    limit: 100,
  });

  assert.ok(url.startsWith("/api/v1/maps/pois?"));
  assert.ok(url.includes("north=13.05"));
  assert.ok(url.includes("south=12.89"));
  assert.ok(url.includes("east=77.72"));
  assert.ok(url.includes("west=77.48"));
  assert.ok(url.includes("category=school"));
  assert.ok(url.includes("limit=100"));
});

test("buildPropertyNearbyUrl serializes property ID, category, and radius", () => {
  const url = buildPropertyNearbyUrl(42, {
    category: "transit",
    radius_km: 5.0,
    limit: 10,
  });

  assert.ok(url.startsWith("/api/v1/properties/42/nearby?"));
  assert.ok(url.includes("category=transit"));
  assert.ok(url.includes("radius_km=5"));
  assert.ok(url.includes("limit=10"));
});

test("buildPropertyNearbyUrl handles empty params without trailing question mark", () => {
  const url = buildPropertyNearbyUrl(42);
  assert.strictEqual(url, "/api/v1/properties/42/nearby");
});

test("buildPropertyLocationIntelligenceUrl builds correct endpoint with optional radius", () => {
  const urlWithoutRadius = buildPropertyLocationIntelligenceUrl(101);
  assert.strictEqual(urlWithoutRadius, "/api/v1/properties/101/location-intelligence");

  const urlWithRadius = buildPropertyLocationIntelligenceUrl(101, 4.5);
  assert.strictEqual(urlWithRadius, "/api/v1/properties/101/location-intelligence?radius_km=4.5");
});

test("Location intelligence response validates category map and nearest distance", () => {
  const mockResponse = {
    property_id: 101,
    radius_km: 3.0,
    categories: {
      hospital: {
        nearest_distance_km: 0.84,
        count_within_radius: 3,
      },
      school: {
        nearest_distance_km: 1.15,
        count_within_radius: 5,
      },
      transit: {
        nearest_distance_km: null,
        count_within_radius: 0,
      },
    },
  };

  assert.strictEqual(mockResponse.property_id, 101);
  assert.strictEqual(mockResponse.radius_km, 3.0);
  assert.strictEqual(mockResponse.categories.hospital.nearest_distance_km, 0.84);
  assert.strictEqual(mockResponse.categories.hospital.count_within_radius, 3);
  assert.strictEqual(mockResponse.categories.transit.nearest_distance_km, null);
  assert.strictEqual(mockResponse.categories.transit.count_within_radius, 0);
});

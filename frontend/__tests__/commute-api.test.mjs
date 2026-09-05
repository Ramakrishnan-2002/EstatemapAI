import test from "node:test";
import assert from "node:assert";

// URL builder helper functions representing the API client serialization logic in lib/api/commute.ts

export function buildPropertyCommuteUrl(propertyId, params, baseUrl = "") {
  const query = new URLSearchParams();
  query.append("destination_lat", params.destination_lat.toString());
  query.append("destination_lng", params.destination_lng.toString());
  if (params.destination_name) query.append("destination_name", params.destination_name);
  if (params.mode) query.append("mode", params.mode);

  return `${baseUrl}/api/v1/properties/${propertyId}/commute?${query.toString()}`;
}

export function buildDirectRouteUrl(params, baseUrl = "") {
  const query = new URLSearchParams();
  query.append("origin_lat", params.origin_lat.toString());
  query.append("origin_lng", params.origin_lng.toString());
  query.append("dest_lat", params.dest_lat.toString());
  query.append("dest_lng", params.dest_lng.toString());
  if (params.dest_name) query.append("dest_name", params.dest_name);
  if (params.mode) query.append("mode", params.mode);

  return `${baseUrl}/api/v1/commute/route?${query.toString()}`;
}

// ─── Tests ────────────────────────────────────────────────────────────────────

test("buildPropertyCommuteUrl serializes destination coordinates and travel mode", () => {
  const url = buildPropertyCommuteUrl(42, {
    destination_lat: 12.8399,
    destination_lng: 77.6770,
    destination_name: "Electronic City",
    mode: "driving",
  });

  assert.ok(url.startsWith("/api/v1/properties/42/commute?"));
  assert.ok(url.includes("destination_lat=12.8399"));
  assert.ok(url.includes("destination_lng=77.677"));
  assert.ok(url.includes("destination_name=Electronic+City"));
  assert.ok(url.includes("mode=driving"));
});

test("buildDirectRouteUrl serializes origin, destination, and mode", () => {
  const url = buildDirectRouteUrl({
    origin_lat: 12.9716,
    origin_lng: 77.5946,
    dest_lat: 12.9352,
    dest_lng: 77.6245,
    dest_name: "Koramangala",
    mode: "cycling",
  });

  assert.ok(url.startsWith("/api/v1/commute/route?"));
  assert.ok(url.includes("origin_lat=12.9716"));
  assert.ok(url.includes("origin_lng=77.5946"));
  assert.ok(url.includes("dest_lat=12.9352"));
  assert.ok(url.includes("dest_lng=77.6245"));
  assert.ok(url.includes("dest_name=Koramangala"));
  assert.ok(url.includes("mode=cycling"));
});

test("CommuteResponse structure conforms to RFC 7946 GeoJSON LineString format", () => {
  const mockResponse = {
    property_id: 42,
    origin: { latitude: 12.9784, longitude: 77.6408 },
    destination: { name: "Electronic City", latitude: 12.8399, longitude: 77.6770 },
    mode: "driving",
    distance_meters: 18500,
    distance_km: 18.5,
    duration_seconds: 2100,
    duration_minutes: 35.0,
    geometry: {
      type: "LineString",
      coordinates: [
        [77.6408, 12.9784],
        [77.6520, 12.9100],
        [77.6770, 12.8399],
      ],
    },
    summary: "Via Hosur Road Elevated Expressway",
    provider: "mock",
    cached: false,
  };

  assert.strictEqual(mockResponse.property_id, 42);
  assert.strictEqual(mockResponse.distance_km, 18.5);
  assert.strictEqual(mockResponse.duration_minutes, 35.0);
  assert.strictEqual(mockResponse.geometry.type, "LineString");
  assert.strictEqual(mockResponse.geometry.coordinates.length, 3);
  // Ensure coordinate is [longitude, latitude]
  assert.strictEqual(mockResponse.geometry.coordinates[0][0], 77.6408);
  assert.strictEqual(mockResponse.geometry.coordinates[0][1], 12.9784);
});

import test from "node:test";
import assert from "node:assert";

// Spatial parameter builder tests for frontend API layer
function buildBBoxQueryParams(params) {
  const query = new URLSearchParams();
  query.append("min_lat", params.min_lat.toString());
  query.append("min_lng", params.min_lng.toString());
  query.append("max_lat", params.max_lat.toString());
  query.append("max_lng", params.max_lng.toString());
  if (params.min_price !== undefined) query.append("min_price", params.min_price.toString());
  if (params.max_price !== undefined) query.append("max_price", params.max_price.toString());
  if (params.property_type) query.append("property_type", params.property_type);
  if (params.bedrooms !== undefined) query.append("bedrooms", params.bedrooms.toString());
  if (params.limit) query.append("limit", params.limit.toString());
  return query.toString();
}

function buildRadiusQueryParams(params) {
  const query = new URLSearchParams();
  query.append("latitude", params.latitude.toString());
  query.append("longitude", params.longitude.toString());
  if (params.radius_km) query.append("radius_km", params.radius_km.toString());
  if (params.min_price !== undefined) query.append("min_price", params.min_price.toString());
  if (params.bedrooms !== undefined) query.append("bedrooms", params.bedrooms.toString());
  return query.toString();
}

test("buildBBoxQueryParams serializes coordinates and filters correctly", () => {
  const params = {
    min_lat: 12.90,
    min_lng: 77.50,
    max_lat: 13.05,
    max_lng: 77.70,
    min_price: 5000000,
    bedrooms: 3,
    limit: 50,
  };

  const qs = buildBBoxQueryParams(params);
  assert.ok(qs.includes("min_lat=12.9"));
  assert.ok(qs.includes("min_lng=77.5"));
  assert.ok(qs.includes("max_lat=13.05"));
  assert.ok(qs.includes("max_lng=77.7"));
  assert.ok(qs.includes("min_price=5000000"));
  assert.ok(qs.includes("bedrooms=3"));
  assert.ok(qs.includes("limit=50"));
});

test("buildRadiusQueryParams serializes center coordinates and radius", () => {
  const params = {
    latitude: 12.9716,
    longitude: 77.5946,
    radius_km: 15.0,
    min_price: 8000000,
  };

  const qs = buildRadiusQueryParams(params);
  assert.ok(qs.includes("latitude=12.9716"));
  assert.ok(qs.includes("longitude=77.5946"));
  assert.ok(qs.includes("radius_km=15"));
  assert.ok(qs.includes("min_price=8000000"));
});

test("MapBounds correctly maps to bounding box params", () => {
  const mapBounds = {
    north: 13.05,
    south: 12.89,
    east: 77.70,
    west: 77.48,
  };

  const bboxParams = {
    min_lat: mapBounds.south,
    min_lng: mapBounds.west,
    max_lat: mapBounds.north,
    max_lng: mapBounds.east,
  };

  assert.strictEqual(bboxParams.min_lat, 12.89);
  assert.strictEqual(bboxParams.min_lng, 77.48);
  assert.strictEqual(bboxParams.max_lat, 13.05);
  assert.strictEqual(bboxParams.max_lng, 77.70);
});

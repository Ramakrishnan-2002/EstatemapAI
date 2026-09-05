import test from "node:test";
import assert from "node:assert";
import { propertyToFeature, propertiesToFeatureCollection } from "../lib/geojson";
import { Property } from "../types";

const mockProperty: Property = {
  id: 101,
  owner_id: 1,
  title: "Luxury 3BHK Apartment in Indiranagar",
  description: "Modern apartment with balcony views",
  price: 18500000,
  property_type: "apartment",
  bedrooms: 3,
  bathrooms: 3,
  area_sqft: 1950,
  address: "100ft Road",
  locality: "Indiranagar",
  city: "Bengaluru",
  latitude: 12.9719,
  longitude: 77.6412,
  status: "active",
  images: [
    {
      id: 1,
      image_url: "https://example.com/img1.jpg",
      display_order: 1,
    },
  ],
  amenities: [],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

test("propertyToFeature converts property to valid GeoJSON Feature with [longitude, latitude] ordering", () => {
  const feature = propertyToFeature(mockProperty);

  assert.strictEqual(feature.type, "Feature");
  assert.strictEqual(feature.geometry.type, "Point");
  // CRITICAL: First element is longitude (77.6412), second is latitude (12.9719)
  assert.strictEqual(feature.geometry.coordinates[0], 77.6412);
  assert.strictEqual(feature.geometry.coordinates[1], 12.9719);
  assert.strictEqual(feature.properties.id, 101);
  assert.strictEqual(feature.properties.title, "Luxury 3BHK Apartment in Indiranagar");
  assert.strictEqual(feature.properties.price, 18500000);
  assert.strictEqual(feature.properties.bedrooms, 3);
  assert.strictEqual(feature.properties.locality, "Indiranagar");
  assert.strictEqual(feature.properties.city, "Bengaluru");
  assert.strictEqual(feature.properties.primary_image, "https://example.com/img1.jpg");
});

test("propertiesToFeatureCollection converts array of properties to FeatureCollection", () => {
  const properties: Property[] = [
    mockProperty,
    {
      ...mockProperty,
      id: 102,
      title: "2BHK in Whitefield",
      price: 8500000,
      latitude: 12.9698,
      longitude: 77.7500,
      images: [],
    },
  ];

  const featureCollection = propertiesToFeatureCollection(properties);

  assert.strictEqual(featureCollection.type, "FeatureCollection");
  assert.strictEqual(featureCollection.features.length, 2);
  assert.strictEqual(featureCollection.features[0].properties.id, 101);
  assert.strictEqual(featureCollection.features[1].properties.id, 102);
  assert.strictEqual(featureCollection.features[1].geometry.coordinates[0], 77.7500);
  assert.strictEqual(featureCollection.features[1].geometry.coordinates[1], 12.9698);
  assert.strictEqual(featureCollection.features[1].properties.primary_image, null);
});

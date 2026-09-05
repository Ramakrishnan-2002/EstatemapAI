import test from "node:test";
import assert from "node:assert";

// Pure JS conversion logic matching lib/geojson.ts for native node runner
export function propertyToFeature(property) {
  const primaryImage =
    property.images && property.images.length > 0
      ? property.images[0].image_url
      : null;

  return {
    type: "Feature",
    geometry: {
      type: "Point",
      coordinates: [property.longitude, property.latitude],
    },
    properties: {
      id: property.id,
      title: property.title,
      price: property.price,
      property_type: property.property_type,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      area_sqft: property.area_sqft,
      locality: property.locality,
      city: property.city,
      primary_image: primaryImage,
    },
  };
}

export function propertiesToFeatureCollection(properties) {
  return {
    type: "FeatureCollection",
    features: properties.map(propertyToFeature),
  };
}

const mockProperty = {
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
  const properties = [
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

export function poiToFeature(poi) {
  return {
    type: "Feature",
    id: poi.id,
    geometry: {
      type: "Point",
      coordinates: [poi.longitude, poi.latitude],
    },
    properties: {
      id: poi.id,
      name: poi.name,
      category: poi.category,
      subcategory: poi.subcategory || null,
      locality: poi.locality || null,
      city: poi.city,
      is_active: poi.is_active,
    },
  };
}

export function poisToFeatureCollection(pois) {
  return {
    type: "FeatureCollection",
    features: pois.map(poiToFeature),
    total: pois.length,
  };
}

const mockPOI = {
  id: 1,
  name: "Manipal Hospital Old Airport Road",
  category: "hospital",
  subcategory: "private",
  latitude: 12.9592,
  longitude: 77.6456,
  address: "98, HAL Airport Road",
  city: "Bengaluru",
  locality: "Indiranagar",
  is_active: true,
};

test("poiToFeature converts POI to valid GeoJSON Feature with [longitude, latitude] ordering", () => {
  const feature = poiToFeature(mockPOI);

  assert.strictEqual(feature.type, "Feature");
  assert.strictEqual(feature.id, 1);
  assert.strictEqual(feature.geometry.type, "Point");
  // CRITICAL: First element is longitude (77.6456), second is latitude (12.9592)
  assert.strictEqual(feature.geometry.coordinates[0], 77.6456);
  assert.strictEqual(feature.geometry.coordinates[1], 12.9592);
  assert.strictEqual(feature.properties.id, 1);
  assert.strictEqual(feature.properties.name, "Manipal Hospital Old Airport Road");
  assert.strictEqual(feature.properties.category, "hospital");
  assert.strictEqual(feature.properties.subcategory, "private");
  assert.strictEqual(feature.properties.locality, "Indiranagar");
  assert.strictEqual(feature.properties.city, "Bengaluru");
  assert.strictEqual(feature.properties.is_active, true);
});

test("poisToFeatureCollection converts array of POIs to POIGeoJSONFeatureCollection", () => {
  const pois = [
    mockPOI,
    {
      id: 2,
      name: "MG Road Metro Station",
      category: "transit",
      subcategory: "metro",
      latitude: 12.9756,
      longitude: 77.6086,
      city: "Bengaluru",
      locality: "Central",
      is_active: true,
    },
  ];

  const collection = poisToFeatureCollection(pois);

  assert.strictEqual(collection.type, "FeatureCollection");
  assert.strictEqual(collection.total, 2);
  assert.strictEqual(collection.features.length, 2);
  assert.strictEqual(collection.features[0].properties.name, "Manipal Hospital Old Airport Road");
  assert.strictEqual(collection.features[1].properties.name, "MG Road Metro Station");
  assert.strictEqual(collection.features[1].geometry.coordinates[0], 77.6086);
  assert.strictEqual(collection.features[1].geometry.coordinates[1], 12.9756);
});


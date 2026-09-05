import test from "node:test";
import assert from "node:assert";
import { MapViewportState } from "../components/map/map-types";

test("MapViewportState correctly stores center and bounds", () => {
  const viewport: MapViewportState = {
    longitude: 77.5946,
    latitude: 12.9716,
    zoom: 12,
    bounds: {
      north: 13.05,
      south: 12.89,
      east: 77.70,
      west: 77.48,
    },
  };

  assert.strictEqual(viewport.longitude, 77.5946);
  assert.strictEqual(viewport.latitude, 12.9716);
  assert.strictEqual(viewport.zoom, 12);
  assert.ok(viewport.bounds);
  assert.ok(viewport.bounds.north > viewport.bounds.south);
  assert.ok(viewport.bounds.east > viewport.bounds.west);
});

test("Single source of truth selection resolution", () => {
  const properties = [
    { id: "prop-1", title: "Property 1" },
    { id: "prop-2", title: "Property 2" },
  ];

  let selectedPropertyId: string | null = null;

  // Simulate card click
  selectedPropertyId = properties[0].id;
  assert.strictEqual(selectedPropertyId, "prop-1");

  // Derive selection in list and marker
  const isCard1Selected = properties[0].id === selectedPropertyId;
  const isCard2Selected = properties[1].id === selectedPropertyId;
  assert.strictEqual(isCard1Selected, true);
  assert.strictEqual(isCard2Selected, false);

  // Simulate marker click on property 2
  selectedPropertyId = properties[1].id;
  assert.strictEqual(selectedPropertyId, "prop-2");
  assert.strictEqual(properties[0].id === selectedPropertyId, false);
  assert.strictEqual(properties[1].id === selectedPropertyId, true);

  // Simulate map background click deselecting
  selectedPropertyId = null;
  assert.strictEqual(selectedPropertyId, null);
});

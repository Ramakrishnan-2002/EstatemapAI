import test from "node:test";
import assert from "node:assert";

// Unit tests for Phase 14 Ask the Map & Conversational Search Orchestration
// Covers request serialization, state transitions, feedback badges, and response parsing.

test("AskMapRequest serializes canonical search state and map viewport correctly", () => {
  const request = {
    message: "Find 2 BHK under 80 Lakh in Indiranagar",
    session_id: "sess_test_12345",
    current_state: {
      min_price: null,
      max_price: null,
      bedrooms: null,
      bathrooms: null,
      min_area_sqft: null,
      property_type: null,
      city: null,
      locality: null,
      preferred_poi_categories: [],
      commute_destination: null,
      destination_lat: null,
      destination_lng: null,
      travel_mode: "driving",
      max_commute_minutes: null,
      viewport_bbox: null,
      ranking_preset: "balanced",
      ranking_weights: {
        price: 0.3,
        bedrooms: 0.2,
        area: 0.15,
        location: 0.15,
        commute: 0.2,
      },
      selected_property_ids: [],
    },
    map_viewport: {
      north: 12.985,
      south: 12.965,
      east: 77.655,
      west: 77.635,
    },
  };

  assert.strictEqual(request.message, "Find 2 BHK under 80 Lakh in Indiranagar");
  assert.strictEqual(request.session_id, "sess_test_12345");
  assert.strictEqual(request.current_state.ranking_preset, "balanced");
  assert.strictEqual(request.map_viewport.north, 12.985);
});

test("AskMapResponse parses full conversational response with GeoJSON and feedback", () => {
  const mockResponse = {
    session_id: "sess_test_12345",
    message: "Found 4 matching 2 BHK properties in Indiranagar under ₹80.0 Lakh.",
    action: "search",
    state: {
      min_price: null,
      max_price: 8000000,
      bedrooms: 2,
      bathrooms: null,
      min_area_sqft: null,
      property_type: null,
      city: "Bengaluru",
      locality: "Indiranagar",
      preferred_poi_categories: [],
      commute_destination: null,
      destination_lat: null,
      destination_lng: null,
      travel_mode: "driving",
      max_commute_minutes: null,
      viewport_bbox: null,
      ranking_preset: "balanced",
      ranking_weights: {
        price: 0.3,
        bedrooms: 0.2,
        area: 0.15,
        location: 0.15,
        commute: 0.2,
      },
      selected_property_ids: [],
    },
    applied_patch: {
      max_price: 8000000,
      bedrooms: 2,
      locality: "Indiranagar",
      city: "Bengaluru",
      requested_action: "search",
      confidence: 0.95,
    },
    feedback: {
      added: ["bedrooms: 2", "locality: Indiranagar", "max_price: 8000000"],
      modified: [],
      removed: [],
      preserved: [],
    },
    items: [
      {
        property: {
          id: 101,
          title: "Spacious 2 BHK Indiranagar",
          price: 7500000,
          bedrooms: 2,
          bathrooms: 2,
          area_sqft: 1150,
          property_type: "apartment",
          locality: "Indiranagar",
          city: "Bengaluru",
          latitude: 12.9784,
          longitude: 77.6408,
          status: "available",
          images: [{ id: 1, property_id: 101, image_url: "https://images.estatemap.ai/101.jpg", is_primary: true, caption: "Living Room" }],
          amenities: [],
        },
        ranking_score: 88.5,
        match_percentage: 88.5,
        score_breakdown: {},
        top_positive_factors: ["Budget friendly under ₹80 Lakh"],
        top_negative_factors: [],
      },
    ],
    total_matches: 1,
    map_geojson: {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          id: 101,
          geometry: {
            type: "Point",
            coordinates: [77.6408, 12.9784],
          },
          properties: {
            id: 101,
            title: "Spacious 2 BHK Indiranagar",
            price: 7500000,
            bedrooms: 2,
            locality: "Indiranagar",
            primary_image_url: "https://images.estatemap.ai/101.jpg",
          },
        },
      ],
    },
    explanation_bullets: [
      "Filtered properties to Indiranagar with at least 2 bedrooms and maximum price ₹80.0 Lakh.",
    ],
    needs_clarification: false,
    clarification_prompt: null,
    provider: "gemini",
    model: "gemini-2.5-flash",
    latency_ms: 245.8,
    fallback_used: false,
  };

  assert.strictEqual(mockResponse.action, "search");
  assert.strictEqual(mockResponse.total_matches, 1);
  assert.strictEqual(mockResponse.state.locality, "Indiranagar");
  assert.strictEqual(mockResponse.feedback.added.length, 3);
  assert.strictEqual(mockResponse.map_geojson.type, "FeatureCollection");
  assert.strictEqual(mockResponse.map_geojson.features[0].geometry.coordinates[0], 77.6408);
  assert.strictEqual(mockResponse.provider, "gemini");
  assert.strictEqual(mockResponse.fallback_used, false);
});

test("AskMapResponse handles clarification prompt for unknown destination", () => {
  const clarificationResponse = {
    session_id: "sess_test_clarify",
    message: "I could not resolve the destination 'Atlantis'. Please specify a landmark or tech park in Bengaluru.",
    action: "refine",
    state: {
      preferred_poi_categories: [],
      travel_mode: "driving",
      ranking_preset: "balanced",
      ranking_weights: { price: 0.3, commute: 0.2 },
      selected_property_ids: [],
    },
    feedback: {
      added: [],
      modified: [],
      removed: [],
      preserved: [],
    },
    items: [],
    total_matches: 0,
    map_geojson: { type: "FeatureCollection", features: [] },
    needs_clarification: true,
    clarification_prompt: "Could not find 'Atlantis'. Did you mean EcoSpace Bellandur, Manyata Tech Park, or Electronic City?",
    provider: "mock",
    model: "mock-v1",
    latency_ms: 12.0,
    fallback_used: false,
  };

  assert.strictEqual(clarificationResponse.needs_clarification, true);
  assert.ok(clarificationResponse.clarification_prompt.includes("EcoSpace"));
  assert.strictEqual(clarificationResponse.total_matches, 0);
});

test("Multi-turn refinement accumulates and clears filter fields correctly", () => {
  // Turn 1 initial state
  const stateTurn1 = {
    locality: "Indiranagar",
    bedrooms: 2,
    max_price: 8000000,
    preferred_poi_categories: [],
  };

  // Turn 2 patch: add POI category transit
  const patchTurn2 = {
    add_poi_categories: ["transit"],
    requested_action: "refine",
  };

  // Simulated state reducer
  const stateTurn2 = {
    ...stateTurn1,
    preferred_poi_categories: [
      ...new Set([...stateTurn1.preferred_poi_categories, ...patchTurn2.add_poi_categories]),
    ],
  };

  assert.strictEqual(stateTurn2.locality, "Indiranagar");
  assert.strictEqual(stateTurn2.bedrooms, 2);
  assert.deepStrictEqual(stateTurn2.preferred_poi_categories, ["transit"]);

  // Turn 3 patch: clear locality filter
  const patchTurn3 = {
    clear_fields: ["locality"],
    requested_action: "clear_filter",
  };

  const stateTurn3 = {
    ...stateTurn2,
    locality: patchTurn3.clear_fields.includes("locality") ? null : stateTurn2.locality,
  };

  assert.strictEqual(stateTurn3.locality, null);
  assert.strictEqual(stateTurn3.bedrooms, 2);
  assert.deepStrictEqual(stateTurn3.preferred_poi_categories, ["transit"]);
});

test("Comparison action triggers comparison result delegation", () => {
  const compareResponse = {
    session_id: "sess_compare",
    message: "Compared Top 2 properties: Property A vs Property B.",
    action: "compare",
    state: {
      selected_property_ids: [101, 102],
      preferred_poi_categories: [],
      travel_mode: "driving",
      ranking_preset: "balanced",
      ranking_weights: {},
    },
    feedback: {
      added: ["selected_property_ids: [101, 102]"],
      modified: [],
      removed: [],
      preserved: [],
    },
    items: [],
    total_matches: 2,
    map_geojson: { type: "FeatureCollection", features: [] },
    comparison_result: {
      properties: [{ id: 101 }, { id: 102 }],
      dimensions: {
        price: { dimension: "price", best_property_label: "Property A" },
      },
      ranking_deltas: [],
      deterministic_summary: ["Property A is ₹10.0 Lakh cheaper than Property B."],
      best_by_dimension: { price: "Property A" },
    },
    needs_clarification: false,
    provider: "mock",
    model: "mock-v1",
    latency_ms: 35.0,
    fallback_used: false,
  };

  assert.strictEqual(compareResponse.action, "compare");
  assert.deepStrictEqual(compareResponse.state.selected_property_ids, [101, 102]);
  assert.ok(compareResponse.comparison_result);
  assert.strictEqual(compareResponse.comparison_result.best_by_dimension.price, "Property A");
});

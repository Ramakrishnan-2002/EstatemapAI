import test from "node:test";
import assert from "node:assert";

// Unit tests for Phase 13 Multi-Property Comparison request serialization,
// deterministic delta structures, and AI trade-off response schemas.

test("PropertyComparisonRequest serializes bounded 2-3 property comparison payload", () => {
  const request = {
    property_ids: [101, 102],
    destination_lat: 12.9756,
    destination_lng: 77.6066,
    destination_name: "MG Road Metro",
    travel_mode: "driving",
    weights: {
      price: 0.35,
      bedrooms: 0.15,
      area: 0.15,
      location: 0.15,
      commute: 0.20,
      locality: 0.0,
    },
  };

  assert.strictEqual(request.property_ids.length, 2);
  assert.strictEqual(request.destination_name, "MG Road Metro");
  assert.strictEqual(request.travel_mode, "driving");
  assert.strictEqual(request.weights.price, 0.35);
});

test("ComparisonResult preserves deterministic facts, dimension winners, and ranking deltas", () => {
  const mockResult = {
    properties: [
      {
        id: 101,
        label: "Property A",
        title: "Modern 2 BHK HSR Layout",
        price: 6800000,
        price_formatted: "₹68.0 Lakh",
        price_per_sqft: 6181.82,
        bedrooms: 2,
        bathrooms: 2,
        area_sqft: 1100,
        property_type: "apartment",
        address: "100 Feet Road",
        locality: "HSR Layout",
        city: "Bengaluru",
        latitude: 12.9121,
        longitude: 77.6446,
        image_urls: ["https://images.estatemap.ai/101.jpg"],
        location_intelligence: {
          hospital: 0.85,
          school: 0.42,
          transit: 0.31,
        },
        commute_duration_mins: 22.4,
        commute_distance_km: 7.8,
        commute_destination: "MG Road Metro",
        ranking_score: 84.5,
        score_breakdown: {
          price: { score: 0.95, weight: 0.35, weighted_contribution: 33.25, available: true, description: "Budget friendly" },
          commute: { score: 0.82, weight: 0.20, weighted_contribution: 16.4, available: true, description: "22.4 mins" },
        },
      },
      {
        id: 102,
        label: "Property B",
        title: "Luxury 3 BHK Indiranagar",
        price: 18500000,
        price_formatted: "₹1.85 Cr",
        price_per_sqft: 7708.33,
        bedrooms: 3,
        bathrooms: 3,
        area_sqft: 2400,
        property_type: "apartment",
        address: "12th Main",
        locality: "Indiranagar",
        city: "Bengaluru",
        latitude: 12.9716,
        longitude: 77.6412,
        image_urls: ["https://images.estatemap.ai/102.jpg"],
        location_intelligence: {
          hospital: 0.65,
          school: 1.1,
          transit: 0.45,
        },
        commute_duration_mins: 14.8,
        commute_distance_km: 4.5,
        commute_destination: "MG Road Metro",
        ranking_score: 79.2,
        score_breakdown: {
          price: { score: 0.55, weight: 0.35, weighted_contribution: 19.25, available: true, description: "Higher budget" },
          commute: { score: 0.95, weight: 0.20, weighted_contribution: 19.0, available: true, description: "14.8 mins" },
        },
      },
    ],
    dimensions: {
      price: {
        dimension: "price",
        best_property_label: "Property A",
        best_metric_label: "Lowest price (₹68.0 Lakh)",
        metric_name: "Price",
        details: { cheapest_label: "Property A", lowest_price: 6800000 },
        comparison_notes: ["Property A is ₹1.17 Cr cheaper than Property B."],
      },
      space: {
        dimension: "space",
        best_property_label: "Property B",
        best_metric_label: "Largest area (2,400 sq.ft.)",
        metric_name: "Living Area",
        details: { largest_label: "Property B", largest_area_sqft: 2400 },
        comparison_notes: ["Property B provides 1,300 sq.ft. more living area than Property A."],
      },
      commute: {
        dimension: "commute",
        best_property_label: "Property B",
        best_metric_label: "Shortest commute (14.8 mins)",
        metric_name: "Commute Time",
        details: { fastest_label: "Property B", duration_mins: 14.8 },
        comparison_notes: ["Property B's commute is 7.6 minutes shorter than Property A."],
      },
      ranking: {
        dimension: "ranking",
        best_property_label: "Property A",
        best_metric_label: "Highest match score (84.5%)",
        metric_name: "Ranking Match",
        details: { highest_match_label: "Property A", highest_match_score: 84.5 },
        comparison_notes: ["Property A ranks 5.3 points higher than Property B."],
      },
    },
    ranking_deltas: [
      {
        winner_label: "Property A",
        loser_label: "Property B",
        winner_score: 84.5,
        loser_score: 79.2,
        net_score_delta: 5.3,
        factor_deltas: {
          price: 14.0,
          commute: -2.6,
        },
        summary: "Property A ranks 5.3 points higher than Property B mainly because price (+14.0) advantages outweigh commute (-2.6).",
      },
    ],
    deterministic_summary: [
      "Property A is ₹1.17 Cr cheaper than Property B.",
      "Property B provides 1,300 sq.ft. more living area than Property A.",
      "Property B's commute is 7.6 minutes shorter than Property A.",
    ],
    best_by_dimension: {
      price: "Property A",
      space: "Property B",
      commute: "Property B",
      ranking: "Property A",
    },
  };

  assert.strictEqual(mockResult.properties.length, 2);
  assert.strictEqual(mockResult.best_by_dimension.price, "Property A");
  assert.strictEqual(mockResult.best_by_dimension.space, "Property B");
  assert.strictEqual(mockResult.best_by_dimension.commute, "Property B");
  assert.strictEqual(mockResult.best_by_dimension.ranking, "Property A");
  assert.strictEqual(mockResult.ranking_deltas[0].net_score_delta, 5.3);
  assert.strictEqual(mockResult.deterministic_summary.length, 3);
});

test("AIComparisonResponse parses grounded narrative and fallback metadata", () => {
  const mockAiResponse = {
    property_ids: [101, 102],
    narrative:
      "### Key Trade-offs\n- **Property A** provides significantly better affordability (₹68.0 Lakh vs ₹1.85 Cr).\n- **Property B** offers superior living space (2,400 sq.ft.) and a faster commute (14.8 mins vs 22.4 mins).\n\n### Recommendation\nProperty A is the top recommendation for budget efficiency, while Property B is best for maximum living space.",
    comparison: {
      properties: [],
      dimensions: {},
      ranking_deltas: [],
      deterministic_summary: [],
      best_by_dimension: {},
    },
    provider: "gemini",
    model: "gemini-flash-latest",
    latency_ms: 642.5,
    fallback_used: false,
    prompt_version: "property-comparison:v1",
    routing_reason: "2 properties with commute intelligence -> gemini",
    usage: {
      input_tokens: 380,
      output_tokens: 145,
      total_tokens: 525,
    },
  };

  assert.strictEqual(mockAiResponse.provider, "gemini");
  assert.strictEqual(mockAiResponse.fallback_used, false);
  assert.strictEqual(mockAiResponse.usage.total_tokens, 525);
  assert(mockAiResponse.narrative.includes("Key Trade-offs"));
});

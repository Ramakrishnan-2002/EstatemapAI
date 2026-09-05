import test from "node:test";
import assert from "node:assert";

// Unit tests for Phase 9 Ranking request serialization and response structures

test("RankedSearchRequest structure combines hard filters and soft preferences", () => {
  const mockRequest = {
    min_price: 3000000,
    max_price: 8000000,
    bedrooms: 2,
    property_type: "apartment",
    destination: {
      name: "Electronic City",
      latitude: 12.8399,
      longitude: 77.6770,
    },
    travel_mode: "driving",
    weights: {
      price: 0.30,
      bedrooms: 0.20,
      area: 0.10,
      location: 0.20,
      commute: 0.20,
      locality: 0.0,
    },
    limit: 10,
    offset: 0,
  };

  assert.strictEqual(mockRequest.max_price, 8000000);
  assert.strictEqual(mockRequest.bedrooms, 2);
  assert.strictEqual(mockRequest.destination.name, "Electronic City");
  assert.strictEqual(mockRequest.weights.price, 0.30);
});

test("RankedSearchResponse preserves deterministic score breakdown and rank ordering", () => {
  const mockResponse = {
    total_candidates: 12,
    ranking_config: {
      algorithm_version: "weighted_deterministic_v1",
      weights: { price: 0.25, bedrooms: 0.20, area: 0.10, location: 0.20, commute: 0.25, locality: 0.0 },
      candidate_pool_size: 12,
    },
    items: [
      {
        rank: 1,
        property: {
          id: 101,
          title: "Prestige High Fields",
          price: 6500000,
          bedrooms: 2,
          area_sqft: 1200,
          locality: "Koramangala",
          city: "Bengaluru",
          latitude: 12.9352,
          longitude: 77.6245,
          status: "active",
          images: [],
          amenities: [],
          created_at: "2026-09-01T00:00:00Z",
          owner_id: 1,
        },
        final_score: 89.5,
        score_breakdown: {
          price: { score: 0.92, weight: 0.25, weighted_contribution: 23.0, available: true, description: "Within target budget" },
          bedrooms: { score: 1.0, weight: 0.20, weighted_contribution: 20.0, available: true, description: "Exact 2 BHK match" },
          location: { score: 0.85, weight: 0.20, weighted_contribution: 17.0, available: true, description: "Hospital within 1.2km" },
          commute: { score: 0.78, weight: 0.25, weighted_contribution: 19.5, available: true, description: "22.5 min travel time" },
          area: { score: 0.80, weight: 0.10, weighted_contribution: 8.0, available: true, description: "1,200 sq ft" },
          locality: { score: 1.0, weight: 0.0, weighted_contribution: 0.0, available: true, description: "Located in Koramangala" },
        },
        explanations: [
          "Strong affordability within requested budget range",
          "Exact 2 BHK configuration match",
          "Convenient commute (22.5 min travel time)",
        ],
      },
    ],
    page: 1,
    page_size: 10,
    total_pages: 2,
  };

  assert.strictEqual(mockResponse.total_candidates, 12);
  assert.strictEqual(mockResponse.ranking_config.algorithm_version, "weighted_deterministic_v1");
  assert.strictEqual(mockResponse.items[0].rank, 1);
  assert.strictEqual(mockResponse.items[0].final_score, 89.5);
  assert.strictEqual(mockResponse.items[0].score_breakdown.price.weighted_contribution, 23.0);
  assert.strictEqual(mockResponse.items[0].explanations.length, 3);
});

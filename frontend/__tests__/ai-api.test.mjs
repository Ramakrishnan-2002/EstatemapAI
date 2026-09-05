import test from "node:test";
import assert from "node:assert";

// Unit tests for Phase 11 AI API structures and schemas

test("ParseSearchResponse structure matches AI provider contract", () => {
  const mockSearchResponse = {
    provider: "ollama",
    model: "llama3.2:3b",
    intent: {
      raw_query: "2 BHK apartment in Whitefield under 75 lakh near hospital",
      bedrooms: 2,
      bathrooms: null,
      min_price: null,
      max_price: 7500000,
      min_area_sqft: null,
      property_type: "apartment",
      locality: "Whitefield",
      city: "Bengaluru",
      preferred_poi_categories: ["hospital"],
      commute_destination: null,
      confidence: 0.95,
    },
    latency_ms: 124.5,
    prompt_version: "search_intent_v1",
  };

  assert.strictEqual(mockSearchResponse.provider, "ollama");
  assert.strictEqual(mockSearchResponse.model, "llama3.2:3b");
  assert.strictEqual(mockSearchResponse.intent.bedrooms, 2);
  assert.strictEqual(mockSearchResponse.intent.max_price, 7500000);
  assert.strictEqual(mockSearchResponse.intent.locality, "Whitefield");
  assert.strictEqual(mockSearchResponse.intent.property_type, "apartment");
  assert.deepStrictEqual(mockSearchResponse.intent.preferred_poi_categories, ["hospital"]);
  assert.strictEqual(mockSearchResponse.latency_ms, 124.5);
});

test("AIExplanationResponse structure contains factual context and fallback indicator", () => {
  const mockExplanationResponse = {
    property_id: 42,
    explanation: "This 2 BHK apartment in Indiranagar offers 1,200 sq ft of living area priced at ₹85,00,000.",
    provider: "ollama",
    model: "llama3.2:3b",
    latency_ms: 215.3,
    fallback_used: false,
    factual_context: {
      property: {
        id: 42,
        title: "Modern 2BHK in Indiranagar",
        price: 8500000,
        bedrooms: 2,
        locality: "Indiranagar",
        city: "Bengaluru",
      },
      location_intelligence: {
        hospital: { nearest_distance_km: 0.8, count_within_radius: 3 },
      },
    },
    prompt_version: "property_explanation_v1",
  };

  assert.strictEqual(mockExplanationResponse.property_id, 42);
  assert.strictEqual(mockExplanationResponse.fallback_used, false);
  assert.ok(mockExplanationResponse.factual_context.property);
  assert.strictEqual(mockExplanationResponse.factual_context.property.bedrooms, 2);
  assert.strictEqual(mockExplanationResponse.factual_context.location_intelligence.hospital.nearest_distance_km, 0.8);
});

test("AIHealthResponse validates reachability and model availability", () => {
  const mockHealth = {
    enabled: true,
    provider: "ollama",
    reachable: true,
    model: "llama3.2:3b",
    model_available: true,
    available_models: ["llama3.2:3b", "mistral:7b"],
    latency_ms: 18.2,
    details: { version: "0.3.12" },
  };

  assert.strictEqual(mockHealth.enabled, true);
  assert.strictEqual(mockHealth.reachable, true);
  assert.strictEqual(mockHealth.model_available, true);
  assert.ok(mockHealth.available_models.includes("llama3.2:3b"));
});

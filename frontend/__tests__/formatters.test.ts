import { describe, it } from "node:test";
import assert from "node:assert";
import { formatPrice, formatPricePerSqFt } from "../lib/formatters/currency";
import { formatBedrooms, formatBathrooms, formatArea, formatPropertyType } from "../lib/formatters/property";
import { formatDate } from "../lib/formatters/date";

describe("Currency Formatters", () => {
  it("formats crore amounts correctly", () => {
    assert.strictEqual(formatPrice(18500000), "₹1.85 Cr");
    assert.strictEqual(formatPrice(10000000), "₹1 Cr");
    assert.strictEqual(formatPrice(32000000), "₹3.2 Cr");
  });

  it("formats lakh amounts correctly", () => {
    assert.strictEqual(formatPrice(6800000), "₹68 L");
    assert.strictEqual(formatPrice(1450000), "₹14.5 L");
    assert.strictEqual(formatPrice(500000), "₹5 L");
  });

  it("formats small amounts with thousand commas", () => {
    assert.strictEqual(formatPrice(45000), "₹45,000");
  });

  it("calculates price per sq ft correctly", () => {
    assert.strictEqual(formatPricePerSqFt(10000000, 1000), "₹10,000/sq ft");
  });
});

describe("Property Formatters", () => {
  it("formats bedroom counts", () => {
    assert.strictEqual(formatBedrooms(3), "3 BHK");
    assert.strictEqual(formatBedrooms(0), "Studio");
    assert.strictEqual(formatBedrooms(null), "N/A");
  });

  it("formats bathroom counts", () => {
    assert.strictEqual(formatBathrooms(2), "2 Baths");
    assert.strictEqual(formatBathrooms(1), "1 Bath");
    assert.strictEqual(formatBathrooms(null), "N/A");
  });

  it("formats area square footage", () => {
    assert.strictEqual(formatArea(1650), "1,650 sq ft");
  });

  it("formats property type identifiers", () => {
    assert.strictEqual(formatPropertyType("apartment"), "Apartment");
    assert.strictEqual(formatPropertyType("villa"), "Villa");
    assert.strictEqual(formatPropertyType("independent_house"), "Independent House");
  });
});

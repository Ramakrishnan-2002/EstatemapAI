import { describe, it } from "node:test";
import assert from "node:assert";
import { APIError } from "../types";

describe("APIError Class", () => {
  it("creates APIError with default status and code", () => {
    const error = new APIError("Something went wrong");
    assert.strictEqual(error.message, "Something went wrong");
    assert.strictEqual(error.code, "UNKNOWN_ERROR");
    assert.strictEqual(error.statusCode, 500);
    assert.strictEqual(error.name, "APIError");
  });

  it("stores backend error details and requestId", () => {
    const error = new APIError(
      "Property not found",
      "RESOURCE_NOT_FOUND",
      404,
      { resource: "Property", identifier: 123 },
      "req-abc-123"
    );
    assert.strictEqual(error.message, "Property not found");
    assert.strictEqual(error.code, "RESOURCE_NOT_FOUND");
    assert.strictEqual(error.statusCode, 404);
    assert.strictEqual(error.requestId, "req-abc-123");
    assert.deepStrictEqual(error.details, { resource: "Property", identifier: 123 });
  });
});

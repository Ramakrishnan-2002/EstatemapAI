# ADR-008: Unified Error Responses, Exception Hierarchy, and Request Correlation IDs

## Status
Accepted

## Context
Production-grade APIs require predictable, machine-readable error schemas, centralized exception handling that prevents information leakage (stack traces, database credentials), and end-to-end request tracing for observability.

## Decision
1. **Unified Error Schema**: All errors (4xx and 5xx) follow the standardized contract:
   ```json
   {
     "error": {
       "code": "RESOURCE_NOT_FOUND",
       "message": "Human readable summary",
       "details": null,
       "request_id": "uuid-v4"
     }
   }
   ```
2. **Exception Hierarchy**: Domain errors inherit from a base `AppException(code, status_code, message, details)`.
3. **Correlation Middleware**: `RequestIDMiddleware` checks incoming `X-Request-ID` headers or creates a UUIDv4, binds it to Python `contextvars`, annotates structured logs, and injects `X-Request-ID` into response headers.
4. **Information Masking**: Internal database exceptions and unexpected runtime crashes return safe 500 JSON without exposing stack traces or database connection details.

## Consequences
- Clean, consistent error handling for frontend consumers and API clients.
- Every log message and error payload includes a correlation ID for instant log searching.
- Zero credential or stack trace exposure in API responses.

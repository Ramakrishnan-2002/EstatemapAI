# EstateMap AI — Failure Mode Analysis & Resilience Matrix

This document defines all failure modes across the EstateMap AI architecture, detailing user impact, detection mechanisms, current handling strategies, and future production enhancements.

---

## Comprehensive Failure Matrix

| Failure Scenario | Severity | User Impact | Detection Mechanism | Current Handling Strategy | Production Enhancement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL Database Unavailable** | Critical | Cannot search, view property details, or authenticate. | Connection pool timeout / `asyncpg.CannotConnectNowError`. | Returns `HTTP 500 Internal Server Error` with `DATABASE_UNAVAILABLE` error code; transaction rolled back. | Read replicas with automated failover (Patroni / AWS RDS Multi-AZ); circuit breakers. |
| **Redis In-Memory Cache Down** | Medium | Cache misses on commute/POI routes; rate limiting disabled. | `aioredis.ConnectionError` caught in `cache_service.py` / `rate_limit.py`. | **Fail-Open**: Transparently queries PostgreSQL/OSRM directly; logs warning; general requests continue. | Redis Sentinel or Redis Cluster with automatic master-replica failover. |
| **Local Ollama LLM Unreachable** | Low | Slower AI responses during conversational search. | `httpx.ConnectError` in `ollama_provider.py`. | **Failover to Gemini**: Router detects failure within timeout and dispatches to Google Gemini. | Background healthcheck ping; multi-node Ollama inference cluster. |
| **Google Gemini Quota Exceeded (HTTP 429)** | Low | Cloud AI explanations temporarily unavailable. | `google.genai.errors.ClientError` with code 429 in `gemini_provider.py`. | **Failover to Ollama / Fallback**: Dispatches to local Ollama; if offline, uses Deterministic Fallback Provider. | Token bucket pre-throttling; fallback to secondary cloud provider (Anthropic/OpenAI). |
| **OSRM Routing Engine Unavailable** | Medium | Commute times fall back to approximations. | `httpx.TimeoutException` or `httpx.ConnectError` in `routing_service.py`. | **Spherical Fallback**: Uses `ST_DistanceSphere` Euclidean distance / 30 km/h average speed; sets `fallback_used: true`. | High-availability OSRM cluster with multi-region DNS routing. |
| **Invalid / Malformed AI JSON Output** | Low | Conversational search receives non-conforming JSON. | Pydantic `ValidationError` in `AIProviderRouter`. | **Safe Recovery**: Catches schema validation error and invokes deterministic rule-based patch generator. | Constrained decoding / Grammar-based sampling at the LLM engine level. |
| **Coordinates Out of Bounds** | Low | Map or search query outside physical coordinates. | Pydantic validator on `latitude` / `longitude` schemas. | **Validation Rejection**: Returns `HTTP 422 Unprocessable Entity` with exact field error details. | Client-side bounding box sanitization before network dispatch. |
| **Expired or Tampered JWT Token** | Low | User actions rejected. | `jwt.ExpiredSignatureError` or `jwt.InvalidTokenError` in `get_current_user`. | **Authentication Error**: Returns `HTTP 401 Unauthorized` with `AUTHENTICATION_ERROR` code. | Silent refresh token rotation with HTTP-only secure cookies. |
| **Duplicate User Registration** | Low | Attempting to register with an existing email address. | Unique constraint on `users.email` in PostgreSQL. | **Anti-Enumeration Handled**: Catches `IntegrityError` and returns `HTTP 400 Bad Request`. | Rate limit registration endpoints per IP to prevent email harvesting. |
| **Zero Search Results Returned** | None | User sees empty map. | PostGIS query returns empty record set. | **Empty State UX**: Frontend renders `EmptyState` component with suggested filter resets. | Broaden search bounds dynamically / Recommend nearest adjacent localities. |
| **Sliding Window Rate Limit Exceeded** | Low | Spammer / script blocked from overloading API. | Redis `ZCARD` exceeds threshold in `rate_limit.py`. | **Rate Limiting (429)**: Returns `HTTP 429 Too Many Requests` with `Retry-After: 60` response header. | Tiered rate limits based on user reputation and authenticated API keys. |
| **Frontend Network Disconnection** | Medium | User loses connectivity. | `window.navigator.onLine` / `fetch` error in browser. | **Error State UI**: Displays retry banner with cached state preservation. | Progressive Web App (PWA) offline service worker caching. |

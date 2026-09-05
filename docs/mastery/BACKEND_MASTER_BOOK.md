# EstateMap AI — Python Backend Engineering & Systems Master Book
> **Document Status: Authoritative Backend Engineering Textbook & System Design Case Study**
> **Focus: Python, FastAPI, PostgreSQL, PostGIS, Redis Caching, Rate Limiting, Multi-Provider AI & Orchestration**

---

## Table of Contents
1. [Chapter 1: Python & FastAPI Asynchronous Core Architecture](#chapter-1-python--fastapi-asynchronous-core-architecture)
2. [Chapter 2: PostgreSQL & PostGIS Spatial Engineering](#chapter-2-postgresql--postgis-spatial-engineering)
3. [Chapter 3: Deterministic 6-Factor Ranking & MCDA Scoring Engine](#chapter-3-deterministic-6-factor-ranking--mcda-scoring-engine)
4. [Chapter 4: Location Intelligence, Routing & Commute Matrices](#chapter-4-location-intelligence-routing--commute-matrices)
5. [Chapter 5: Multi-Provider AI Architecture & Failover Resilience](#chapter-5-multi-provider-ai-architecture--failover-resilience)
6. [Chapter 6: Redis In-Memory Caching & Sliding Window Rate Limiting](#chapter-6-redis-in-memory-caching--sliding-window-rate-limiting)
7. [Chapter 7: Backend ↔ Frontend API Integration Contract](#chapter-7-backend--frontend-api-integration-contract)

---

## Chapter 1: Python & FastAPI Asynchronous Core Architecture

### 1.1 The ASGI Event Loop Model vs Synchronous WSGI
Traditional Python web frameworks (Django, Flask) operate on the synchronous WSGI standard: one operating system thread per concurrent HTTP request. Under heavy I/O workloads (database queries, Redis calls, LLM API calls), thread pools become saturated, leading to queue buildup and high latency.

FastAPI is built on Starlette and the Asynchronous Server Gateway Interface (ASGI). It utilizes Python's `asyncio` event loop. When an endpoint awaits a non-blocking I/O operation (such as `await session.execute()` with `asyncpg`), the coroutine yields control back to the event loop. The event loop immediately processes other incoming HTTP requests, allowing a single worker process to handle thousands of concurrent requests with minimal memory overhead.

### 1.2 Application Factory & Lifespan Resource Management
EstateMap initializes its FastAPI application using the `asynccontextmanager` Lifespan protocol:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Redis pool, verify DB connectivity, seed data
    await init_redis_pool()
    await verify_db_connectivity()
    await seed_all()
    yield
    # Teardown: Gracefully close pools on SIGTERM
    await close_redis_pool()
    await dispose_db_engine()
```
This guarantees that resources are fully ready before traffic is accepted and active transactions finish cleanly before process termination.

### 1.3 Centralized RFC 7807 Error Handling & Correlation IDs
All error responses adhere strictly to RFC 7807 Problem Details (`type`, `title`, `status`, `detail`, `instance`). A centralized exception handler intercepts all domain exceptions (`AppException`, `ValidationException`, `RateLimitExceededException`), preventing raw database error traces from leaking to clients while ensuring consistent JSON error structures. Every request is tagged with an `X-Request-ID` header propagated across all structured log statements.

---

## Chapter 2: PostgreSQL & PostGIS Spatial Engineering

### 2.1 Coordinate Systems: WGS84 (EPSG:4326) & Spatial Column Types
EstateMap stores geospatial coordinates using the WGS84 standard (EPSG:4326), which models the Earth as an oblate spheroid. Coordinates are represented as `POINT(longitude latitude)`.
* **Geometry vs Geography:** Planar `geometry` columns support fast Cartesian indexing and 2D bounding-box operations. Geodesic `geography` columns compute accurate spherical surface distances in meters. EstateMap stores listings as `Geometry(Point, 4326)` and casts to `Geography` at query time for meter-based distance calculations.

### 2.2 GiST Spatial Indexing (R-Tree Hierarchies)
A standard B-Tree index cannot index 2D coordinates because points cannot be sorted in a single linear order. PostGIS uses Generalized Search Trees (GiST), which implement hierarchical R-Trees:
* Points are enclosed in nested Minimum Bounding Rectangles (MBRs).
* A spatial query tests bounding box intersection first, eliminating entire subtrees in $O(\log N)$ time before performing exact geodesic distance math on candidate rows.

### 2.3 Spatial Search Operators
* **Radius Search (`ST_DWithin`):** Filters listings within a distance threshold:
  ```sql
  WHERE ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography, 5000)
  ```
* **Map Viewport Bounding Box (`ST_MakeEnvelope`):** Queries listings within the visible map window:
  ```sql
  WHERE ST_Within(location, ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326))
  ```

---

## Chapter 3: Deterministic 6-Factor Ranking & MCDA Scoring Engine

### 3.1 Why Deterministic Ranking over Black-Box ML
Real estate discovery requires explainability, reproducibility, and sub-10ms latency. EstateMap implements a Multi-Criteria Decision Analysis (MCDA) mathematical scoring engine that evaluates 6 heterogeneous dimensions:
1. **Price Score ($S_p$):** Min-max linear inverse normalization.
2. **Bedroom Score ($S_b$):** Step-function match penalty based on user requirement.
3. **Area Score ($S_a$):** Linear normalization within budget range.
4. **Locality Score ($S_l$):** Exact match and neighborhood affinity scoring.
5. **Location Proximity Score ($S_{loc}$):** Inverse distance decay from target coordinates.
6. **Commute Duration Score ($S_c$):** Non-linear decay penalty based on travel time.

### 3.2 Dynamic Missing-Factor Weight Redistribution
When a user query does not specify certain optional preferences (e.g. no commute destination provided), static weighting would penalize all listings. EstateMap dynamically renormalizes active weights:
$$W_i' = \frac{W_i}{\sum_{j \in \text{active}} W_j}$$
This ensures the final composite score $\sum (W_i' \cdot S_i)$ always sums to exactly 1.0.

---

## Chapter 4: Location Intelligence, Routing & Commute Matrices

### 4.1 In-Memory Landmark Resolution
Natural language queries often mention tech parks or localities ('near Manyata Tech Park'). EstateMap uses an in-memory `LocationResolver` dictionary of 50+ curated landmarks in Bengaluru and Chennai to resolve exact coordinates in sub-millisecond time with zero external API calls.

### 4.2 OSRM Engine Integration & Haversine Fallback
* **OSRM Integration:** Async HTTP calls query OpenStreetMap Routing Machine (OSRM) for road-network driving durations and polyline geometries.
* **Haversine Fallback:** If OSRM is unreachable or times out (5s deadline), the backend automatically degrades to in-memory spherical Haversine distance with calibrated speed profiles (25 km/h driving, 4 km/h walking), ensuring 100% endpoint availability.

---

## Chapter 5: Multi-Provider AI Architecture & Failover Resilience

### 5.1 Provider Protocol & Dual Adapters
EstateMap defines an abstract `AIProvider` Protocol implemented by two distinct adapters:
1. **Local Ollama Adapter:** Cost-free, local LLM execution for development and privacy-sensitive workloads.
2. **Cloud Gemini Adapter:** Low-latency, scalable managed LLM execution for production workloads.

### 5.2 The Pydantic Validation Firewall
Raw LLM outputs are treated as untrusted user input. Outputs are parsed via regular expressions and validated through strict Pydantic v2 schemas (`AISearchIntent`, `AIExplanationResponse`). Any schema violation triggers immediate failover.

### 5.3 Multi-Tier Failover Circuit
```text
Primary Provider (Ollama / Gemini)
        ↓ (Timeout 5s / Error)
Backup Provider (Gemini / Ollama)
        ↓ (Timeout 5s / Outage)
Algorithmic Factual Fallback Generator (100% Deterministic Grounding)
```

---

## Chapter 6: Redis In-Memory Caching & Sliding Window Rate Limiting

### 6.1 Cache-Aside Pattern & Key Normalization
EstateMap implements Cache-Aside in `CacheService`:
* **Key Design:** `estatemap:v1:map:{min_lat}:{min_lon}:{max_lat}:{max_lon}:{sha256(filters)}`
* **Coordinate Precision:** Coordinates are rounded to 4 decimal places (~11m), collapsing GPS drift into canonical cache buckets and maximizing cache hit ratios.
* **Non-Blocking Invalidation:** Cache purges use `SCAN` with cursor iteration instead of the blocking `KEYS *` command.

### 6.2 Sliding Window Log Rate Limiter via Redis Sorted Sets (ZSET)
To eliminate the 2x burst vulnerability of fixed-window counters, EstateMap implements a millisecond-precision sliding window log using Redis ZSETs:
1. `ZREMRANGEBYSCORE(key, 0, now - window)` — Prunes expired timestamps.
2. `ZCARD(key)` — Counts requests in the current window.
3. If count >= limit: Return HTTP 429 + `Retry-After`.
4. Else: `ZADD(key, now, now)` + `EXPIRE(key, window)` and permit request.
* **Fail-Open Policy:** If Redis is down, `RATE_LIMIT_FAIL_OPEN=True` logs a warning and allows traffic through, prioritizing core application uptime.

---

## Chapter 7: Backend ↔ Frontend API Integration Contract

EstateMap communicates with web clients strictly via versioned REST HTTP endpoints:
* **Authentication:** Bearer token passed in the `Authorization: Bearer <JWT>` header.
* **Map Viewport Data:** `GET /api/v1/properties/map` returns standard GeoJSON `FeatureCollection`.
* **Conversational Search:** `POST /api/v1/search/orchestrated` exchanges `AskMapRequest` and returns updated `ConversationalSearchState` and ranked listings.
* **Rate Limits:** Injected headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After`.
* **Errors:** RFC 7807 standardized Problem Details JSON.

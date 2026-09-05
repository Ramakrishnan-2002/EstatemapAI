# EstateMap AI — Code Rebuild Challenges & Hands-On Curriculum

This document contains 10 progressive, hands-on engineering challenges designed to help you rebuild the entire EstateMap AI system from scratch without AI assistance.

---

## Challenge Level 1: Clean FastAPI CRUD with Async SQLAlchemy
* **Goal**: Build a standalone FastAPI app managing `Property` entities with Pydantic schemas and async database sessions.
* **Requirements**:
  - `POST /api/v1/properties`: Validate title, price, bedrooms, bathrooms.
  - `GET /api/v1/properties/{id}`: Return property or 404 error.
  - Use `async_session_factory` and dependency injection for `get_db()`.
* **Verification**: Run `pytest` with `httpx.AsyncClient`.

---

## Challenge Level 2: PostGIS Point Geometry & Bounding-Box Search
* **Goal**: Add PostGIS geometry to properties and implement spatial bounding-box search.
* **Requirements**:
  - Add `location = Column(Geometry('POINT', srid=4326), nullable=False)`.
  - Create GiST spatial index: `Index('idx_prop_loc_gist', 'location', postgresql_using='gist')`.
  - `POST /api/v1/search/spatial`: Accept `min_lat, max_lat, min_lng, max_lng` and query `location && ST_MakeEnvelope(...)`.
* **Verification**: Insert 10 coordinate points and assert that bounding-box query returns only points within the rectangle.

---

## Challenge Level 3: POI Modeling & Meter-Accurate Radius Search
* **Goal**: Implement Point of Interest (POI) storage and spherical distance calculations.
* **Requirements**:
  - Create `pois` table with `category` and `POINT(4326)` geometry.
  - Query POIs within $R$ meters using `ST_DWithin(location::geography, ST_MakePoint(lng, lat)::geography, R)`.
  - Return sorted by distance: `ST_DistanceSphere(location, ST_MakePoint(lng, lat))`.
* **Verification**: Verify that a POI 500 meters away is returned, but a POI 3000 meters away is excluded when $R=1000$.

---

## Challenge Level 4: Redis Sliding-Window Rate Limiter
* **Goal**: Implement a distributed sliding-window log rate limiter using Redis Sorted Sets.
* **Requirements**:
  - Limit: 5 requests per 60-second sliding window per client IP.
  - Algorithm: `ZREMRANGEBYSCORE key 0 (now - 60)` -> `ZCARD key` -> if count >= 5 raise 429 else `ZADD key now req_id` -> `EXPIRE key 60`.
  - Return `Retry-After: 60` on 429 responses.
* **Verification**: Send 5 rapid requests (HTTP 200), send 6th request (HTTP 429), sleep 60s, send 7th request (HTTP 200).

---

## Challenge Level 5: OSRM Road Graph Routing & Route Caching
* **Goal**: Integrate OSRM HTTP routing with Redis cache-aside.
* **Requirements**:
  - Call OSRM public API or local server for driving routes.
  - Cache results in Redis key `estatemap:commute:v1:{origin}:{dest}:{mode}` with 24-hour TTL.
  - Implement spherical distance fallback if OSRM is unreachable.
* **Verification**: Call route twice; verify second call executes in <2ms with zero network call to OSRM.

---

## Challenge Level 6: Deterministic 6-Factor Mathematical Ranking Engine
* **Goal**: Build a multi-factor property ranking engine with missing-factor weight redistribution.
* **Requirements**:
  - Implement 6 normalized factor equations: Price, Bedrooms, Area, Locality, POIs, Commute.
  - If a factor is missing, redistribute its weight proportionally across available factors.
  - Calculate `final_score` and return sorted list with `score_breakdown`.
* **Verification**: Pass a set of candidate properties and assert deterministic score outputs match mathematical calculations.

---

## Challenge Level 7: Multi-Provider AI Routing with Fallbacks & Deadlines
* **Goal**: Build an AI provider router with Ollama, Gemini, and deterministic fallbacks.
* **Requirements**:
  - Define `AIProvider` Python `Protocol`.
  - Evaluate query complexity to route simple queries to Ollama and complex queries to Gemini.
  - Enforce a 12.0s global request deadline with graceful degradation to fallback rules.
* **Verification**: Mock a Gemini 429 error and verify system automatically falls back to Ollama.

---

## Challenge Level 8: "Ask the Map" Conversational Search State Machine
* **Goal**: Build the conversational state reducer parsing delta patches.
* **Requirements**:
  - Model `ConversationalSearchState` and `SearchStatePatch`.
  - Implement `apply_patch()` supporting `SET`, `CLEAR`, `APPEND`, `REMOVE`, and `RESET` actions.
  - Connect reducer to PostGIS query generator.
* **Verification**: Simulate a 4-turn conversation and assert final state accumulates filters accurately.

---

## Challenge Level 9: Side-by-Side Property Comparison Engine
* **Goal**: Build deterministic property comparison with grounded AI explanations.
* **Requirements**:
  - Compute exact numeric deltas for Price, Living Area, and Commute Duration.
  - Determine dimension winners deterministically in Python.
  - Pass structured facts to LLM to produce a 3-bullet narrative summary.
* **Verification**: Compare Property A (₹80L) and Property B (₹1.2 Cr); verify Property A is identified as Price Winner.

---

## Challenge Level 10: Complete EstateMap Mini-Backend from Scratch
* **Goal**: Assemble all 9 components into a single coherent, production-ready repository.
* **Requirements**:
  - FastAPI modular monolith + PostgreSQL/PostGIS + Redis + Next.js MapLibre frontend.
  - Multi-container `docker-compose.yml` with healthchecks.
  - Complete automated test suite with $>80\%$ code coverage.
* **Verification**: Pass end-to-end integration test creating a listing, searching on the map, ranking by commute, and refining via Ask the Map.

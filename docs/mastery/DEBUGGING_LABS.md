# EstateMap AI — Hands-On Debugging Labs

This document provides 12 realistic debugging scenarios based on real-world backend and geospatial engineering challenges encountered in EstateMap AI. Each lab contains symptoms, diagnostic commands, root causes, fixes, and core engineering lessons.

---

## Lab 1: Spatial Bounding-Box Query Returns Zero Results Despite Properties Existing
* **Symptom**: Querying properties in Chennai returns `[]`, but the database contains 100 Chennai properties.
* **Diagnostic Command**:
  ```sql
  SELECT ST_AsText(location) FROM properties WHERE city = 'Chennai' LIMIT 1;
  -- Output: POINT(12.9228 80.1888)  <-- Notice: Inverted [lat lng] instead of [lng lat]!
  ```
* **Root Cause**: The developer inserted coordinates as `ST_MakePoint(lat, lng)` instead of `ST_MakePoint(lng, lat)`. In PostGIS, the first coordinate is X (longitude) and the second is Y (latitude).
* **Fix**: Ensure all PostGIS geometry constructors use `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)`.
* **Lesson**: Geospatial coordinates follow `[x, y] = [longitude, latitude]` ordering in PostGIS, GeoJSON, and WKT.

---

## Lab 2: Redis Sliding-Window Rate Limiter Blocks All Users Immediately
* **Symptom**: Every request immediately returns `HTTP 429 Too Many Requests`.
* **Diagnostic Command**:
  ```bash
  docker exec estatemap-redis redis-cli ZRANGE "estatemap:ratelimit:ip:127.0.0.1:global" 0 -1 WITHSCORES
  ```
* **Root Cause**: `ZREMRANGEBYSCORE` was called with `(now - window)` where `now` was calculated in milliseconds, but scores were stored in seconds, causing zero timestamps to be pruned.
* **Fix**: Standardize all timestamp operations in `rate_limit.py` to fractional epoch seconds (`time.time()`).
* **Lesson**: Time unit mismatches (milliseconds vs. seconds) in Redis TTLs or sorted set scores cause catastrophic rate-limiting failures.

---

## Lab 3: SQLAlchemy Async Engine Hanging Indefinitely During Tests
* **Symptom**: `pytest` hangs on the first test and never finishes.
* **Diagnostic Command**: Check active PostgreSQL connections via `SELECT count(*) FROM pg_stat_activity;`.
* **Root Cause**: An async test fixture opened an `AsyncSession` without using `NullPool` or closing the connection in a `finally` block, exhausting the connection pool.
* **Fix**: Configure `NullPool` for test database engines and ensure all sessions are managed via `async with session_factory() as session:`.
* **Lesson**: Async tests with concurrency require non-pooled or properly scoped connections to prevent connection starvation.

---

## Lab 4: Local Ollama Intent Parsing Times Out and Blocks Client for 30 Seconds
* **Symptom**: User sends conversational message and UI spins for 30 seconds before failing.
* **Diagnostic Command**: Check `ollama ps` or query `curl http://localhost:11434/api/generate`.
* **Root Cause**: The model was unloaded from VRAM, requiring cold boot disk loading, and no HTTP client timeout was enforced in Python.
* **Fix**: Enforce strict `httpx.Timeout(8.0)` on Ollama HTTP client and implement background keep-alive pings (`keep_alive: "24h"`).
* **Lesson**: External AI service calls must always have aggressive client-side timeouts and global request deadlines.

---

## Lab 5: Property Save State Disappears When Navigating to `/favorites`
* **Symptom**: User clicks "Save" on property detail page, but `/favorites` shows "No saved properties yet".
* **Diagnostic Command**: Inspect browser `localStorage.getItem("estatemap_saved_properties")`.
* **Root Cause**: Component used local `useState(false)` instead of shared `useFavorites()` context, and `FavoritesPage` rendered before hydration was complete without checking `isLoaded`.
* **Fix**: Connect button to `FavoritesContext` and add `isLoaded` hydration check to `FavoritesPage`.
* **Lesson**: In Next.js App Router, client-side persistent storage must guard against premature SSR rendering before hydration completes.

---

## Lab 6: Alembic Migration Fails with "type geometry does not exist"
* **Symptom**: Running `alembic upgrade head` in a clean environment crashes with `UndefinedObjectError`.
* **Diagnostic Command**: Run `\dx` inside `psql` to check installed extensions.
* **Root Cause**: The migration attempted to create a table with `Geometry('POINT', 4326)` before the PostGIS extension was enabled.
* **Fix**: Ensure the very first migration runs `op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")`.
* **Lesson**: Database extensions must be created in migration revision #1 before any spatial column definitions.

---

## Lab 7: AI Comparison Generates Contradictory Price Winners
* **Symptom**: Property A costs ₹80L and Property B costs ₹1.2 Cr, but AI summary claims Property B is more affordable.
* **Diagnostic Command**: Inspect the prompt payload sent to Gemini/Ollama.
* **Root Cause**: Raw property objects were passed to the LLM without pre-computed arithmetic comparison facts.
* **Fix**: Pre-calculate exact numeric deltas and dimension winners in `ComparisonService` before passing facts to the LLM for grounded explanation.
* **Lesson**: Never delegate mathematical calculations or truth determination to probabilistic LLMs.

---

## Lab 8: Bounding-Box Search Inverts Latitude / Longitude in Leaflet vs PostGIS
* **Symptom**: PostGIS returns 422 `VALIDATION_ERROR` when sending MapLibre `activeViewportBounds`.
* **Diagnostic Command**: Inspect API request payload: `{ north: 13.0, south: 12.0, east: 80.0, west: 79.0 }`.
* **Root Cause**: Backend schema expected `{ min_lat, max_lat, min_lng, max_lng }`, where `min_lat = south`, `max_lat = north`, `min_lng = west`, `max_lng = east`.
* **Fix**: Normalize frontend map bounds before network transmission in `frontend/app/search/page.tsx`.
* **Lesson**: Maintain explicit conversion adapters between frontend map coordinate schemas and backend PostGIS bounding box schemas.

---

## Lab 9: Redis Fails and Completely Takes Down Search API
* **Symptom**: When Redis container stops, all search endpoints return 500 errors.
* **Diagnostic Command**: `docker stop estatemap-redis` and test `GET /api/v1/search`.
* **Root Cause**: `CacheService.get()` threw unhandled `ConnectionError`.
* **Fix**: Wrap Redis calls in try/except blocks with fail-open semantics: if Redis fails, log warning and query database/OSRM directly.
* **Lesson**: Caches are performance accelerators, not critical system dependencies; cache failures must fail open.

---

## Lab 10: Missing Commute Destination Penalizes Properties with 0% Score
* **Symptom**: Searching without a commute destination results in top properties scoring only ~60%.
* **Diagnostic Command**: Inspect `score_breakdown` in `RankedPropertyResponse`.
* **Root Cause**: Commute factor was assigned score = 0 and weight = 0.40, dragging down the final score.
* **Fix**: Implement missing-factor weight redistribution in `RankingService`: if a factor is unavailable, redistribute its weight proportionally among available factors.
* **Lesson**: Multi-factor scoring systems must dynamically normalize weights when optional inputs are omitted.

---

## Lab 11: JWT Token Still Valid After User Changes Password
* **Symptom**: User resets password, but old JWT token on another device continues to authenticate successfully.
* **Diagnostic Command**: Decode JWT payload: token only contains `sub`, `user_id`, `role`, `exp`.
* **Root Cause**: Stateless JWTs cannot be revoked without a server-side token blacklist or token version counter.
* **Fix**: Add a `token_version` column to the `users` table, include `v` in the JWT payload, and verify `payload["v"] == user.token_version` in `get_current_user`.
* **Lesson**: Stateless JWTs trade instant revocation for horizontal scalability; critical revocations require versioning or Redis blacklists.

---

## Lab 12: Concurrent Registrations Create Duplicate Users
* **Symptom**: Two simultaneous registration requests with the same email both succeed or trigger race conditions.
* **Diagnostic Command**: Run concurrent `curl` registration requests in parallel.
* **Root Cause**: Code checked `if not user_exists()` before inserting, leaving a time-of-check to time-of-use (TOCTOU) race window.
* **Fix**: Enforce a unique database constraint (`UNIQUE INDEX idx_users_email`) and catch `IntegrityError` to return clean 400 errors.
* **Lesson**: Application-level checks cannot prevent concurrency race conditions; database-level unique constraints are mandatory.

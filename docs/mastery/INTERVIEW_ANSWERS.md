# EstateMap AI — Technical Interview Master Answer Key (3-Tier Depths)

This document provides structured, interview-ready answers for the critical questions in [`INTERVIEW_QUESTIONS.md`](file:///d:/FastAPI/EstateMap/docs/mastery/INTERVIEW_QUESTIONS.md). Every primary topic is answered across **three explicit depth tiers**:
1. **30-Second Elevator Answer**: Concise, crisp summary.
2. **2-Minute Standard Answer**: Detailed technical explanation with files and concepts.
3. **Deep-Dive Follow-Up**: Mathematical formulas, code paths, failure modes, and tradeoffs.

---

## 1. System Design: "Why Modular Monolith Over Microservices?"

### 30-Second Elevator Answer
> "We chose a modular monolith because EstateMap is a synchronized real estate discovery platform with a single development team. A modular monolith gives us ACID relational transactions across properties, amenities, and users with zero inter-service network latency, sub-millisecond in-memory communication, and simple single-container deployments. Microservices would have introduced distributed transaction complexity, network overhead, and heavy DevOps friction without any business justification."

### 2-Minute Standard Answer
> "In evaluating the architecture for EstateMap, we followed Conway's Law and Martin Fowler's MonolithFirst principle.
>
> Our backend is partitioned into clear, decoupled domains (`api/`, `services/`, `repositories/`, `models/`, `ai/`, `cache/`). Communication between domains happens via typed Python service calls rather than gRPC or REST over a network.
>
> This design provides three major engineering advantages:
> 1. **Data Consistency**: PostgreSQL executes atomic transactions across listings, images, and user roles without requiring distributed 2-Phase Commit (2PC) or Saga orchestrators.
> 2. **Performance**: An interactive map query can join properties with spatial bounding boxes and location intelligence in memory in $<20\text{ms}$, avoiding multi-hop network serialization delays.
> 3. **Operational Simplicity**: The entire application runs as a single FastAPI container next to PostgreSQL and Redis.
>
> If a specific module—such as high-volume listing ingestion or background AI batching—develops distinct scaling or independent deployment needs in the future, our strict repository and service boundaries allow clean service extraction."

### Deep-Dive Follow-Up
* **Extraction Criteria**: We would extract a microservice only when: (a) independent deployment cadences are required by separate engineering teams, (b) CPU/memory profiles diverge drastically (e.g. GPU inference workers vs lightweight REST handlers), or (c) failure domains must be strictly isolated.
* **Code Evidence**: Look at `backend/app/main.py` where routers from `backend/app/api/v1/` are mounted into a single FastAPI application instance with shared async database and Redis connection pools.

---

## 2. Geospatial: "How Does PostGIS GiST Indexing Work & Why Do B-Trees Fail?"

### 30-Second Elevator Answer
> "Standard B-Tree indexes only work for 1-dimensional scalar values that can be sorted linearly. Geographic coordinates are 2-dimensional. PostGIS uses Generalized Search Trees (GiST) implementing an R-Tree structure. The GiST index organizes points into a hierarchy of Minimum Bounding Rectangles (MBRs). When a bounding-box query runs, PostGIS evaluates bounding box overlaps and prunes non-intersecting branches in $\mathcal{O}(\log N)$ time, avoiding full table scans."

### 2-Minute Standard Answer
> "In PostgreSQL, storing latitude and longitude as two separate float columns indexed with standard B-Trees is ineffective for spatial queries because a B-Tree can only filter one dimension at a time (e.g. filtering latitude first, which still leaves thousands of rows to scan across longitude).
>
> EstateMap stores coordinates as a single PostGIS `geometry(Point, 4326)` column with a GiST spatial index (`idx_properties_location_gist` in `backend/alembic/versions/001_initial_schema.py`).
>
> Internally, the GiST index builds an R-Tree:
> * Leaf nodes contain actual property points grouped into small bounding boxes.
> * Parent nodes aggregate child boxes into progressively larger bounding boxes up to the root.
>
> When the frontend map executes a viewport search using `location && ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)`, PostGIS evaluates the `&&` intersection operator against the R-Tree root. If a bounding box does not overlap the query envelope, the entire subtree is discarded. This reduces query execution time from $\mathcal{O}(N)$ sequential scans to $\mathcal{O}(\log N)$ index scans, executing in $<15\text{ms}$ over thousands of listings."

### Deep-Dive Follow-Up
* **Coordinate Ordering**: PostGIS adheres strictly to the OGC and GeoJSON standard: `POINT(longitude latitude)` where Longitude = X and Latitude = Y. Inverting to `POINT(lat lng)` causes points to project to Antarctica.
* **Geometry vs. Geography**: `geometry` computes planar math on flat grids. For meter-accurate radius queries, we cast to geography: `ST_DWithin(location::geography, ST_MakePoint(lng, lat)::geography, 2000)` so PostGIS calculates distances along the ellipsoidal curve of the Earth.

---

## 3. Redis & Concurrency: "How Did You Implement Sliding-Window Rate Limiting?"

### 30-Second Elevator Answer
> "We implemented a sliding-window log rate limiter using Redis Sorted Sets (`ZSET`). Every request adds a unique member with the current Unix epoch timestamp as its score. We atomically prune timestamps older than `now - 60s` using `ZREMRANGEBYSCORE`, count the remaining entries with `ZCARD`, and reject the request with HTTP 429 if the count exceeds our threshold. This eliminates the 2x burst vulnerability inherent in fixed-window counters."

### 2-Minute Standard Answer
> "Fixed-window rate limiters count requests within static clock boundaries (e.g. 00:00–00:59). An attacker can send 5 requests at 00:59 and 5 requests at 01:00, effectively pushing 10 requests in 2 seconds while adhering to a '5 req/min' fixed limit.
>
> In `backend/app/core/rate_limit.py`, EstateMap implements a true sliding-window log:
> 1. **Key Structure**: `estatemap:ratelimit:{client_ip_or_user_id}:{endpoint_scope}`.
> 2. **Prune Expired Entries**: `ZREMRANGEBYSCORE key 0 (now - window_seconds)`. This atomically deletes all request timestamps outside the rolling 60-second window.
> 3. **Count Active Requests**: `count = ZCARD key`.
> 4. **Threshold Evaluation**: If `count >= limit`, we return `HTTP 429 Too Many Requests` with header `Retry-After: 60`.
> 5. **Record Current Request**: If within limits, we add the current request: `ZADD key now request_uuid` and set key expiration `EXPIRE key window_seconds`.
>
> This guarantees 100% boundary accuracy at sub-millisecond Redis RAM speed."

### Deep-Dive Follow-Up
* **Fail-Open Policy**: If Redis crashes or disconnects, `rate_limit.py` catches `aioredis.ConnectionError`, logs a warning with the request ID, and fails open for general search traffic to maintain platform availability, while failing closed on auth endpoints.
* **Time Complexity**: $\mathcal{O}(\log M + K)$ where $M$ is the number of requests in the window (typically $\le 60$) and $K$ is the number of pruned expired entries.

---

## 4. Algorithms: "How Does Your Deterministic Ranking Engine Work & Why Not ML?"

### 30-Second Elevator Answer
> "Our ranking engine evaluates listings across 6 mathematical dimensions: Price Compliance, Bedroom Match, Living Area, Locality Match, POI Proximity, and OSRM Commute Duration. Each factor produces a normalized score between 0.0 and 1.0, multiplied by user-selected weights. If an optional factor like commute hub is omitted, its weight is dynamically redistributed proportionally across available factors. We chose deterministic math over ML for 100% audit-proof explainability and zero cold-start delay."

### 2-Minute Standard Answer
> "In real estate discovery, buyers demand to know *why* listing A is recommended over listing B. Furthermore, a new platform starts with zero historical click logs, making Machine Learning ranking models susceptible to severe cold-start failures.
>
> In `backend/app/services/ranking_service.py`, we implemented a 6-factor deterministic scoring engine:
> * **Price Match**: $S_{\text{price}} = \max\left(0, 1 - \frac{|P_{\text{price}} - B_{\text{target}}|}{B_{\text{target}}}\right)$
> * **Bedroom Match**: $S_{\text{bedrooms}} = \max(0, 1 - 0.5 \times |P_{\text{bed}} - B_{\text{target}}|)$
> * **Living Area**: $S_{\text{area}} = \min(1.0, P_{\text{area}} / A_{\text{min}})$
> * **Locality**: $1.0$ if matching locality string, else $0.0$
> * **POI Proximity**: $S_{\text{location}} = M / N$ (available preferred categories / requested categories)
> * **Commute Duration**: $S_{\text{commute}} = \max\left(0, 1 - T_{\text{minutes}} / 60\right)$
>
> The final score is: $\text{FinalScore} = \sum \text{EffectiveWeight}(f) \times \text{Score}(f) \times 100$.
>
> If a user provides no commute destination, the commute factor is unavailable. The engine redistributes its weight proportionally: $\text{EffectiveWeight}(f) = \text{BaseWeight}(f) / \sum_{g \in \text{Available}} \text{BaseWeight}(g)$, ensuring properties are never unfairly penalized with a 0% score."

### Deep-Dive Follow-Up
* **Comparison Fact Ownership**: In `backend/app/services/comparison_service.py`, exact numeric differences ($\Delta \text{Price}, \Delta \text{Area}, \Delta \text{Commute}$) and dimension winners are computed deterministically in Python before passing grounded facts to the LLM for narrative summarization, eliminating AI arithmetic hallucinations.

---

## 5. AI Engineering: "How Does 'Ask the Map' Work & How Do You Prevent Prompt Injection?"

### 30-Second Elevator Answer
> "'Ask the Map' is an explicit state machine orchestrator that parses multi-turn conversational updates into delta patches (`SET`, `CLEAR`, `APPEND`, `RESET`) against a `ConversationalSearchState`. We route queries between local Ollama and Google Gemini using a complexity scorer and enforce strict Pydantic JSON schemas. Prompt injection is defended against by strictly bounding the LLM: it has no SQL access, no tools, and can only emit approved enum actions that are validated before PostGIS queries."

### 2-Minute Standard Answer
> "Passing raw, unbounded chat history into LLMs causes context drift, slow execution latency, and frequent hallucinations.
>
> In `backend/app/services/search_orchestrator.py`, we designed a finite state machine:
> 1. **State Reducer**: The client maintains a canonical `ConversationalSearchState`. Each user message generates a delta `SearchStatePatch`.
> 2. **Patch Application**: The pure function `apply_patch(state, patch)` applies field updates (`SET`), resets (`CLEAR`), or POI set operations (`APPEND`/`REMOVE`).
> 3. **AI Provider Router (`backend/app/ai/router.py`)**:
>    * Evaluates query complexity: simple queries route to local Ollama; complex queries route to Google Gemini 2.5 Flash.
>    * Bounded by a 12.0s global request deadline with automatic cascading failover. If both fail, `DeterministicFallbackProvider` regex rules generate the patch.
> 4. **Defense-in-Depth AI Security**:
>    * The LLM has zero database credentials and cannot execute arbitrary SQL.
>    * Outputs are validated against Pydantic schemas enforcing allowed action enums (`search`, `filter`, `rank`, `compare`, `reset`).
>    * Extracted coordinates are validated against real metropolitan bounds by `LocationResolver` before reaching PostGIS."

### Deep-Dive Follow-Up
* **Compare Top 2 Resolution**: When a user says *"Compare top 2"*, the orchestrator extracts action `compare`, resolves target indices `[1, 2]` to the exact property IDs from the current ranked search list, and redirects the frontend to `/compare?ids=...`.

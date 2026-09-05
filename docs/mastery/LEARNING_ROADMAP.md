# EstateMap AI — Milestone-Based Learning Roadmap
> **Structured Study Progression: Core Mastery Path, Supporting Theory & Production System Design**

This roadmap guides a backend / full-stack engineer through the personal technical mastery of EstateMap AI.

---
## 1. Curriculum Learning Tracks

### Track A: EstateMap Core Mastery Path (68 Stories)
Covers the directly implemented codebase: FastAPI lifespan, async PostgreSQL / PostGIS 3.4 spatial indexing, Redis caching, sliding-window rate limiting, OSRM road-network routing, 6-factor deterministic ranking, multi-provider AI orchestration, Ask the Map conversational state machine, Next.js 14 MapLibre GL frontend, and automated testing.
- **Stories**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18, 19, 20, 22, 23, 24, 25, 26, 27, 14, 15, 16, 17, 32, 33, 35, 36, 37, 38, 62, 63, 64, 40, 41, 46, 47, 48, 49, 52, 53, 54, 55, 57, 58, 61, 65, 66, 67, 68, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 86, 91, 99, 100

### Track B: Supporting Engineering Theory Path (7 Stories)
Teaches general CS, spatial mathematics, and distributed systems algorithms that justify EstateMap design decisions.
- **Stories**: 21, 29, 31, 34, 39, 45, 51 (CRS/WGS84, Haversine math, Road graph theory, MCDA scoring, Redis internals, Rate limiting algorithms, LLM integration patterns).

### Track C: Production Engineering & System Design Extensions (25 Stories)
Explores how EstateMap scales under high throughput and enterprise availability mandates.
- **Stories**: 28, 30, 42, 43, 44, 50, 56, 59, 60, 69, 71, 83, 84, 85, 87, 88, 89, 90, 92, 93, 94, 95, 96, 97, 98

---
## 2. Cumulative Mastery Demonstrations

### Milestone 1: Foundations & API Lifecycle
- 1. Explain ASGI vs WSGI and why async coroutines prevent thread blocking on I/O.
- 2. Trace request lifecycle through `backend/app/main.py` and `middleware.py`.
- 3. Implement a basic CRUD endpoint using Pydantic request/response models.
- 4. Demonstrate exception handling via RFC 7807 problem details.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 2: Database & PostGIS Spatial Indexing
- 1. Explain the difference between `geometry(Point, 4326)` and `geography` on a sphere.
- 2. Write a PostGIS bounding-box (`ST_MakeEnvelope`) and radius (`ST_DWithin`) query from memory.
- 3. Explain how GiST R-Tree indexes prune candidate searches during spatial filtering.
- 4. Run EXPLAIN ANALYZE on a spatial query to prove index scan execution.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 3: Security & Identity
- 1. Explain Argon2id hashing parameters (memory, iterations, parallelism).
- 2. Generate and verify a stateless JWT access token.
- 3. Implement dependency-injected ownership checks preventing IDOR vulnerabilities.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 4: Redis Caching & Rate Limiting
- 1. Implement a cache-aside pattern with TTL and SHA-256 canonical keys.
- 2. Implement a sliding-window rate limiter using Redis Sorted Sets (`ZSET`).
- 3. Explain concurrency and atomicity tradeoffs of pipelines versus server-side Lua scripts.
- 4. Demonstrate fail-open versus fail-closed behavior during Redis downtime.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 5: Routing & Deterministic Ranking
- 1. Explain why PostGIS cannot compute road-network travel times and why OSRM is used.
- 2. Walk through the 6 mathematical factor scoring equations.
- 3. Manually compute missing-factor weight redistribution on a whiteboard.
- 4. Defend why EstateMap uses explainable product heuristics rather than black-box ML models.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 6: Multi-Provider AI Orchestration
- 1. Explain the abstract AIProvider protocol separating Ollama and Gemini.
- 2. Trace query complexity routing heuristics and global request deadline failover.
- 3. Defend the trust boundary: why AI never owns property facts, SQL generation, or ranking.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 7: Conversational Search State Machine
- 1. Trace multi-turn conversational state patches (`SET`, `CLEAR`, `RESET`).
- 2. Explain destination disambiguation and compare-top-two delegation.
- 3. Demonstrate grounded response generation with factual score injection.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 8: Frontend Map & State Sync
- 1. Explain MapLibre GL WebGL vector rendering and GeoJSON conversion.
- 2. Implement bidirectional marker/card hover and selection synchronization.
- 3. Trace dynamic bounding-box calculation and debounced Search This Area workflows.
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 9: DevOps & Automated Testing
- 1. Trace multi-container Docker Compose bridge networking.
- 2. Write an asynchronous pytest integration test using httpx `AsyncClient`.
- 3. Verify test regressions across backend (288 tests) and frontend (33 tests).
- **Pass Condition**: Complete implementation and explanation independently without notes.

### Milestone 10: Whiteboard System Design Defense
- 1. Draw the complete EstateMap architecture on a whiteboard from memory.
- 2. Defend the modular monolith architecture against premature microservices.
- 3. Formulate a requirement-driven scaling roadmap (read replicas, Sentinel, CDC ingestion) with explicit trigger metrics.
- **Pass Condition**: Complete implementation and explanation independently without notes.

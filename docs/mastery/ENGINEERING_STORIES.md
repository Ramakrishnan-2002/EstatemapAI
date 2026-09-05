# EstateMap AI — 100 Connected Engineering Stories

> **A Complete Engineering Curriculum for Mastering EstateMap AI File-by-File.**  
> *Story points represent personal learning and implementation complexity: 1 = tiny concept, 2 = simple, 3 = moderate, 5 = meaningful engineering topic, 8 = deep topic, 13 = major subsystem.*

---

# Phase 1: Foundation (Stories 1–6)

### Story 01 — Python Project Structure & Clean Architecture (Story Points: 2)
* **Why This Story Exists**: Scalable backend applications require clear modular directory boundaries to prevent circular imports and maintain separation of concerns.
* **User/System Problem**: Disorganized projects mix HTTP route handling with database SQL and business logic, leading to unmaintainable spaghetti code.
* **Prerequisites**: Python fundamentals, module imports.
* **Concepts to Master**: Modular Monolith, separation of layers (API -> Service -> Repository -> Model), dependency inversion.
* **EstateMap Implementation**: `backend/app/` is partitioned into `api/`, `core/`, `db/`, `models/`, `repositories/`, `schemas/`, `services/`, `cache/`, `ai/`, `utils/`.
* **Files to Study**: `backend/app/main.py`, `backend/pyproject.toml`.
* **Build It Yourself Exercise**: Create a minimal Python project with `routers/`, `services/`, `models/`, and an `app.py` entrypoint.
* **Verification**: Verify that importing a service does not trigger circular dependencies with API routes.
* **Common Mistakes**: Importing route handlers into database models.
* **Tradeoffs**: Modular monolith vs single-file script: adds initial folder structure for long-term maintainability.
* **Production Considerations**: Use strict `__all__` exports and linting rules (`ruff`) to enforce package boundaries.
* **Interview Question**: "How do you organize a large-scale FastAPI application to avoid circular imports?"
* **Interview Answer Framework**: "By following clean architecture: route handlers call domain services, domain services call repositories, and models/schemas remain pure data structures with zero upward dependencies."
* **Connection**: Foundation for Story 02 (Application Lifespan).

---

### Story 02 — FastAPI Lifespan & Application Lifecycle (Story Points: 3)
* **Why This Story Exists**: Production servers must manage startup and shutdown events (database pools, cache connections, seed verification) cleanly.
* **User/System Problem**: Database connections left uninitialized on startup crash the first user request; unclosed pools leak socket descriptors on shutdown.
* **Prerequisites**: Python async context managers (`@asynccontextmanager`).
* **Concepts to Master**: ASGI lifespan protocol, startup hooks, graceful shutdown, lifespan dependency management.
* **EstateMap Implementation**: `backend/app/main.py` defines `lifespan(app: FastAPI)` which initializes Redis connection pools, verifies database schema readiness, and auto-seeds baseline demo listings.
* **Files to Study**: `backend/app/main.py`, `backend/app/cache/redis.py`.
* **Build It Yourself Exercise**: Write an async context manager for FastAPI that connects to a mock database on startup and disconnects on shutdown.
* **Verification**: Start and terminate Uvicorn; verify startup log message appears on boot and shutdown cleanup log appears on `Ctrl+C`.
* **Common Mistakes**: Using legacy `@app.on_event("startup")` instead of modern lifespan context managers.
* **Tradeoffs**: Lifespan context manager provides structured exception handling around startup/shutdown compared to detached event hooks.
* **Production Considerations**: Implement health checks that return 503 until all lifespan initialization checks succeed.
* **Interview Question**: "How does FastAPI manage startup and shutdown events in modern ASGI applications?"
* **Interview Answer Framework**: "Using the `@asynccontextmanager` lifespan handler passed to `FastAPI(lifespan=...)`, yielding control during application execution and executing cleanup in the `finally` block."
* **Connection**: Prepares environment for Story 03 (Configuration Management).

---

### Story 03 — Type-Safe Configuration with Pydantic-Settings (Story Points: 2)
* **Why This Story Exists**: Hardcoded configuration constants lead to security leaks and deployment failure across dev, staging, and production environments.
* **User/System Problem**: Invalid environment variables (e.g. wrong port format or missing secret keys) cause silent runtime bugs during user requests.
* **Prerequisites**: Pydantic basics, environment variables (`.env`).
* **Concepts to Master**: 12-Factor App config principle, typed settings parsing, fail-fast configuration validation.
* **EstateMap Implementation**: `backend/app/core/config.py` defines `Settings(BaseSettings)` with validation for `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and `ROUTING_PROVIDER`.
* **Files to Study**: `backend/app/core/config.py`, `.env.example`.
* **Build It Yourself Exercise**: Create a `Settings` class that parses `PORT` as an integer and crashes with a clear validation error if `PORT="abc"`.
* **Verification**: Run script with invalid environment variables and verify it fails fast at boot before serving requests.
* **Common Mistakes**: Reading `os.getenv()` randomly inside route handlers instead of injecting a centralized settings singleton.
* **Tradeoffs**: Upfront schema definition vs. unstructured `os.environ` lookups.
* **Production Considerations**: Load secrets from AWS Secrets Manager or HashiCorp Vault in production.
* **Interview Question**: "Why should environment variables be validated at startup rather than read on-demand?"
* **Interview Answer Framework**: "Validating settings at boot adheres to the fail-fast principle: if a required database URL or secret key is missing, the container immediately fails to start rather than crashing midway through a production transaction."
* **Connection**: Feeds configuration into Story 04 (API Schemas).

---

### Story 04 — API Request/Response Schemas with Pydantic v2 (Story Points: 3)
* **Why This Story Exists**: Robust APIs require strict validation of incoming request bodies and deterministic serialization of outgoing responses.
* **User/System Problem**: Passing unvalidated user input directly to the database leads to SQL injection, type corruption, and malformed responses.
* **Prerequisites**: Python type hints, Pydantic `BaseModel`.
* **Concepts to Master**: Request deserialization, response filtering, field validation, custom validators, OpenAPI schema generation.
* **EstateMap Implementation**: `backend/app/schemas/` defines strict contracts (`PropertyCreate`, `RankedSearchRequest`, `AskMapResponse`).
* **Files to Study**: `backend/app/schemas/property.py`, `backend/app/schemas/search.py`.
* **Build It Yourself Exercise**: Create a Pydantic model for a property listing that rejects negative prices and invalid bedroom numbers (<1).
* **Verification**: Pass invalid JSON to FastAPI and verify it returns HTTP 422 with structured field error messages.
* **Common Mistakes**: Exposing internal database fields (like `hashed_password`) in response models.
* **Tradeoffs**: Minor serialization CPU overhead vs. 100% type safety and automatic Swagger documentation.
* **Production Considerations**: Enable Pydantic v2 `model_config = ConfigDict(extra='forbid')` to reject unexpected payload fields.
* **Interview Question**: "What is the role of Pydantic response models in API security?"
* **Interview Answer Framework**: "Response models act as strict data loss prevention (DLP) filters, ensuring that sensitive internal database fields (like password hashes or internal IDs) are never serialized into outgoing client JSON."
* **Connection**: Enables Story 05 (Centralized Error Handling).

---

### Story 05 — RFC 7807 Centralized Error Handling (Story Points: 3)
* **Why This Story Exists**: Inconsistent error formats across endpoints break frontend client parsers and make debugging difficult.
* **User/System Problem**: One endpoint returns `{ "err": "failed" }`, another returns HTML 500, and a third returns a plain string, confusing API consumers.
* **Prerequisites**: HTTP status codes, FastAPI custom exception handlers.
* **Concepts to Master**: RFC 7807 Problem Details specification, custom exception classes, global exception interception.
* **EstateMap Implementation**: `backend/app/core/exceptions.py` defines domain exceptions (`PropertyNotFoundError`, `AuthenticationError`), and `backend/app/core/exception_handlers.py` maps them to uniform JSON envelopes.
* **Files to Study**: `backend/app/core/exceptions.py`, `backend/app/core/exception_handlers.py`.
* **Build It Yourself Exercise**: Create a custom `EntityNotFoundError` and register an exception handler that returns a standardized error envelope with a timestamp and error code.
* **Verification**: Trigger a 404 in FastAPI; verify the returned JSON contains `status_code`, `error_code`, `message`, and `request_id`.
* **Common Mistakes**: Letting raw unhandled Python tracebacks leak to the client on 500 errors.
* **Tradeoffs**: Standardized JSON format requires custom handlers for `RequestValidationError` and general `Exception`.
* **Production Considerations**: Redact internal database error messages before sending responses to external clients.
* **Interview Question**: "How do you achieve consistent error reporting across all endpoints in a REST API?"
* **Interview Answer Framework**: "By defining domain-specific exception classes and registering global exception handlers with FastAPI that serialize all errors into RFC 7807 compliant JSON envelopes containing standardized error codes and correlation request IDs."
* **Connection**: Integrates with Story 06 (Structured Logging & Request IDs).

---

### Story 06 — Structured Logging & Distributed Request IDs (Story Points: 3)
* **Why This Story Exists**: Debugging production issues across thousands of concurrent requests is impossible without correlation identifiers.
* **User/System Problem**: Logs from concurrent users interleave on the console, making it impossible to trace the lifecycle of a specific failing request.
* **Prerequisites**: Python `logging` module, ASGI middleware.
* **Concepts to Master**: Context variables (`contextvars`), correlation IDs (`X-Request-ID`), structured JSON logging.
* **EstateMap Implementation**: `backend/app/core/middleware.py` extracts or generates `X-Request-ID`, attaches it to response headers, and injects it into every log line via `backend/app/core/logging.py`.
* **Files to Study**: `backend/app/core/middleware.py`, `backend/app/core/logging.py`.
* **Build It Yourself Exercise**: Write an ASGI middleware that sets a unique UUID in `request.state.request_id` and adds it to the HTTP response headers.
* **Verification**: Send a request with `X-Request-ID: test-123`; assert the response header returns `X-Request-ID: test-123` and server logs display `[test-123]`.
* **Common Mistakes**: Using global variables for request IDs instead of thread-safe `contextvars`.
* **Tradeoffs**: Small string generation overhead per request vs. 100% end-to-end log traceability.
* **Production Considerations**: Ship structured JSON logs to OpenSearch / Datadog with indexed `request_id` fields.
* **Interview Question**: "How do you correlate logs for a single user request across multiple backend services?"
* **Interview Answer Framework**: "By generating a unique `X-Request-ID` at the API gateway or middleware layer, propagating it via asynchronous context variables (`contextvars`), attaching it to outgoing response headers, and including it in every log statement."
* **Connection**: Completes Foundation phase; leads into Phase 2: Database.

---

# Phase 2: Database & Geospatial (Stories 7–13 & 21–28)

*(Detailed stories covering PostgreSQL relational modeling, Asyncpg, SQLAlchemy 2.0, Alembic migrations, PostGIS geometry, GiST indexes, bounding box search, and GeoJSON).*

### Story 07 — PostgreSQL Relational Modeling & Schema Integrity (Story Points: 5)
* **Concepts**: Relational constraints, primary keys, foreign keys (`ON DELETE RESTRICT` vs `CASCADE`), composite unique indexes.
* **Files**: `backend/app/models/property.py`, `backend/app/models/user.py`.

### Story 08 — SQLAlchemy 2.0 Declarative Models & Repository Pattern (Story Points: 5)
* **Concepts**: Clean separation between database models and query logic; preventing leaky ORM abstractions.
* **Files**: `backend/app/repositories/property_repository.py`.

### Story 09 — Non-Blocking Async Database Access with Asyncpg (Story Points: 5)
* **Concepts**: Async database drivers, connection pooling, avoiding thread pool contention.
* **Files**: `backend/app/db/session.py`.

### Story 10 — Database Migrations with Alembic (Story Points: 3)
* **Concepts**: Version-controlled schema migrations, upgrade/downgrade scripts, extension creation order.
* **Files**: `backend/alembic/versions/`.

### Story 21 — Geospatial Fundamentals & Coordinate Reference Systems (Story Points: 5)
* **Concepts**: EPSG:4326 (WGS 84), spherical coordinates, longitude/latitude ordering vs latitude/longitude.
* **Files**: `backend/app/models/property.py`, `backend/app/schemas/geo.py`.

### Story 22 — PostGIS POINT Geometry & Spatial Storage (Story Points: 5)
* **Concepts**: `geometry(Point, 4326)`, Well-Known Text (WKT), binary EWKB storage, spatial functions.
* **Files**: `backend/app/repositories/geo_repository.py`.

### Story 23 — GiST Spatial Indexing (Generalized Search Tree) (Story Points: 8)
* **Concepts**: R-Tree hierarchical bounding boxes, why B-Trees fail for 2D spatial queries, index scan mechanics.
* **Files**: `backend/alembic/versions/001_initial_schema.py`.

### Story 24 — Radius Distance Search via ST_DWithin (Story Points: 5)
* **Concepts**: `ST_DWithin`, geometry vs geography casting, `ST_DistanceSphere` in meters.
* **Files**: `backend/app/repositories/geo_repository.py`.

### Story 25 — Bounding-Box Viewport Search via ST_MakeEnvelope (Story Points: 5)
* **Concepts**: 2D bounding-box intersection operator (`&&`), interactive map viewport filtering.
* **Files**: `backend/app/repositories/geo_repository.py`, `backend/app/api/v1/search.py`.

### Story 27 — RFC 7946 GeoJSON Standard Compliance (Story Points: 3)
* **Concepts**: Feature, FeatureCollection, `[longitude, latitude]` coordinate ordering standard.
* **Files**: `backend/app/schemas/geo.py`, `frontend/lib/formatters/geojson.ts`.

---

# Phase 3: Security & Identity (Stories 14–17)

### Story 14 — Password Hashing with Argon2id (Story Points: 3)
* **Concepts**: Salt generation, memory-hard hashing algorithms, preventing rainbow table attacks.
* **Files**: `backend/app/core/security.py`.

### Story 15 — Stateless JWT Authentication (Story Points: 5)
* **Concepts**: HMAC-SHA256 signatures, claims (`sub`, `exp`, `user_id`), expiration validation.
* **Files**: `backend/app/core/security.py`, `backend/app/api/v1/auth.py`.

### Story 16 — Role-Based Authorization & Ownership Verification (Story Points: 3)
* **Concepts**: Resource ownership checks, preventing Insecure Direct Object References (IDOR).
* **Files**: `backend/app/api/v1/properties.py`, `backend/app/core/dependencies.py`.

---

# Phase 4: Redis Caching & Rate Limiting (Stories 39–50)

### Story 39 — Redis In-Memory Architecture & Data Types (Story Points: 3)
* **Concepts**: In-memory key-value store, sub-millisecond RAM latency, Strings vs Hashes vs Sorted Sets.
* **Files**: `backend/app/cache/redis.py`.

### Story 40 — Cache-Aside Pattern Implementation (Story Points: 5)
* **Concepts**: Reading cache first, falling back to database, writing back with TTL, handling cache misses.
* **Files**: `backend/app/cache/cache_service.py`.

### Story 41 — Canonical Cache Key Design & Hashing (Story Points: 3)
* **Concepts**: Deterministic key naming (`estatemap:{domain}:v1:{params}`), SHA-256 parameter hashing, float coordinate rounding.
* **Files**: `backend/app/cache/cache_keys.py`.

### Story 46 — Sliding-Window Log Rate Limiter via Redis Sorted Sets (Story Points: 8)
* **Concepts**: Why fixed windows fail (2x boundary burst), storing timestamps in Sorted Sets (`ZSET`), atomic pruning via `ZREMRANGEBYSCORE`.
* **Files**: `backend/app/core/rate_limit.py`.

### Story 49 — Fail-Open vs. Fail-Closed Degradation Policies (Story Points: 5)
* **Concepts**: System resilience during cache outage; failing open on search vs failing closed on auth.
* **Files**: `backend/app/cache/cache_service.py`, `backend/app/core/rate_limit.py`.

---

# Phase 5: Routing & Deterministic Ranking (Stories 31–38 & 62–64)

### Story 31 — Road-Network Graph Traversal vs. Euclidean Distance (Story Points: 5)
* **Concepts**: Directed road graphs, one-way streets, bridge constraints, why geometric straight lines mislead buyers.
* **Files**: `backend/app/services/routing_service.py`.

### Story 32 — OSRM Engine Integration & Provider Abstraction (Story Points: 5)
* **Concepts**: HTTP routing client, GeoJSON route extraction, mock provider for offline testing.
* **Files**: `backend/app/services/routing_service.py`, `backend/app/services/commute_service.py`.

### Story 35 — 6-Factor Mathematical Ranking Engine (Story Points: 8)
* **Concepts**: Price compliance score, bedroom match, living area, locality, POI proximity, commute duration equations.
* **Files**: `backend/app/services/ranking_service.py`.

### Story 37 — Dynamic Missing-Factor Weight Redistribution (Story Points: 5)
* **Concepts**: Proportional weight normalization when optional criteria (e.g. commute hub) are omitted.
* **Files**: `backend/app/services/ranking_service.py`.

### Story 62 — Deterministic Property Comparison & Dimension Winners (Story Points: 5)
* **Concepts**: Exact arithmetic delta calculations for price, area, and commute duration; separating facts from AI narratives.
* **Files**: `backend/app/services/comparison_service.py`.

---

# Phase 6: Multi-Provider AI & Conversational Search (Stories 51–61 & 65–72)

### Story 52 — Abstract AI Provider Protocol (Story Points: 5)
* **Concepts**: Python `Protocol`, zero vendor lock-in, decoupling business services from specific LLM SDKs.
* **Files**: `backend/app/ai/base.py`.

### Story 53 — Local LLM Inference with Ollama (Story Points: 5)
* **Concepts**: Private offline inference, HTTP daemon integration, model keep-alive management.
* **Files**: `backend/app/ai/ollama_provider.py`.

### Story 54 — Cloud LLM Inference with Google Gemini (Story Points: 5)
* **Concepts**: `google-genai` SDK, structured JSON output enforcement, cloud latency and quota management.
* **Files**: `backend/app/ai/gemini_provider.py`.

### Story 57 — Complexity-Based AI Provider Routing (Story Points: 5)
* **Concepts**: Syntactic and constraint-based query scoring, selecting local vs cloud LLMs automatically.
* **Files**: `backend/app/ai/routing_policy.py`.

### Story 58 — Global Request Deadlines & Automatic Failover (Story Points: 8)
* **Concepts**: Bounded request deadlines, cascading failover from primary to secondary to deterministic fallback.
* **Files**: `backend/app/ai/router.py`.

### Story 65 — "Ask the Map" Conversational State Machine (Story Points: 8)
* **Concepts**: Multi-turn search state machine, delta patches (`SET`, `CLEAR`, `APPEND`, `RESET`), state reducer mechanics.
* **Files**: `backend/app/services/search_orchestrator.py`, `backend/app/schemas/conversational_search.py`.

---

# Phase 7: Frontend & Map Synchronization (Stories 73–80)

### Story 73 — Next.js 14 App Router & Server/Client Boundaries (Story Points: 5)
* **Concepts**: React Server Components (RSC), `"use client"` directives, hydration boundaries, route groups.
* **Files**: `frontend/app/layout.tsx`, `frontend/app/search/page.tsx`.

### Story 76 — MapLibre GL WebGL Vector Map Rendering (Story Points: 5)
* **Concepts**: WebGL map container, GPU-accelerated rendering, GeoJSON source updates.
* **Files**: `frontend/components/map/map-container.tsx`.

### Story 78 — Bidirectional Map Marker & Listing Card Synchronization (Story Points: 5)
* **Concepts**: Clicking pins scrolls cards into view; clicking cards centers map viewport.
* **Files**: `frontend/app/search/page.tsx`.

### Story 80 — Persistent Cross-Tab Favorites & Comparison Contexts (Story Points: 5)
* **Concepts**: `localStorage` persistence, `isLoaded` hydration protection, `storage` and custom event synchronization across tabs.
* **Files**: `frontend/context/favorites-context.tsx`, `frontend/context/comparison-context.tsx`.

---

# Phase 8: DevOps, Testing & System Design (Stories 81–100)

### Story 81 — Multi-Container Docker Architecture (Story Points: 5)
* **Concepts**: Container networking, volume persistence, port mappings, healthchecks.
* **Files**: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`.

### Story 86 — Comprehensive Test Pyramid & Async Testing Fixtures (Story Points: 8)
* **Concepts**: Pytest-asyncio, ASGI transport testing, database isolation, mock routing fixtures.
* **Files**: `backend/tests/conftest.py`, `backend/tests/`.

### Story 91 — Defense of the Modular Monolith Architecture (Story Points: 8)
* **Concepts**: Why microservices were rejected; module boundaries; ACID transactions; team size alignment.
* **Files**: `docs/mastery/TRADEOFF_MATRIX.md`.

### Story 100 — Complete EstateMap System Design Whiteboard Defense (Story Points: 13)
* **Concepts**: End-to-end whiteboard interview presentation covering requirements, PostGIS queries, Redis sliding windows, deterministic ranking, AI state machine, and scale evolution.
* **Files**: `docs/mastery/SYSTEM_DESIGN_INTERVIEW.md`, `docs/mastery/ESTATEMAP_MASTER_BOOK.md`.

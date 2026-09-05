# EstateMap AI — Architectural Design

## 1. Modular Monolith Architecture
EstateMap AI is designed as a **Modular Monolith**. Rather than introducing distributed microservices with network boundaries, distributed transactions, and deployment complexities, EstateMap organizes business concerns into strictly bounded internal modules.

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (React)                 │
│              mapcn + MapLibre GL + TanStack Query           │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON / GeoJSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Monolith                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     RequestIDMiddleware & Unified Exception Handlers   │ │
│  └───────────────────────────┬────────────────────────────┘ │
│                              ▼                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                            API Router Layer                            │ │
│  └───────┬──────────────┬──────────────┬──────────────┬───────────┬───────┘ │
│          │              │              │              │           │         │
│          ▼              ▼              ▼              ▼           ▼         │
│     Auth Service   Search Service  GeoService    POI Service  AI Router     │
│          │              │              │              │           │         │
│          ▼              ▼              ▼              ▼           ├── Ollama│
│     User Repo     Property Repo   Ranking Svc      POI Repo       └── Gemini│
│          │              │              │              │                     │
│          └──────────────┴──────────────┴──────┬───────┴─────────────────────┘
│                                               │                            │
│                                               ▼                            │
│                                        Redis Cache                         │
└───────────────────────────────────────────────┬────────────────────────────┘
                                                │ asyncpg / GeoAlchemy2
                                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL 16 + PostGIS 3.4                         │
│            GiST Spatial Indexes, Relational Tables, Triggers                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Layer Responsibilities
- **API Routers (`app/api/v1/`)**: Request validation, route definition, HTTP status mapping, dependency injection (`auth`, `users`, `properties`, `commute`, `search`, `maps`, `pois`, `favorites`, `ai`).
- **Service Layer (`app/services/`)**: Business workflows, spatial calculation orchestration (`GeoService`), POI intelligence orchestration (`POIService`), road network commute intelligence (`CommuteService`), 2-stage bounded deterministic ranking (`RankingService`), deterministic multi-property comparison (`ComparisonService`), permission validation.
- **Ranking Engine (`app/utils/ranking.py`, `app/services/ranking_service.py`)**: 2-stage bounded scoring pipeline (`MAX_RANKING_CANDIDATES = 50`), clamped $[0.0, 1.0]$ modular scoring functions (price, BHK, area, locality, POIs, commute), dynamic missing factor weight redistribution, deterministic tie-breaking, and rule-based factual explanations.
- **Comparison Engine (`app/services/comparison_service.py`, `app/schemas/comparison.py`)**: Deterministic 2–3 property comparison pipeline. Computes pairwise price deltas, per-sqft price, area differences, POI distance deltas, commute travel times, and ranking factor contribution margins ($\Delta C_f$) with 0% LLM arithmetic.
- **Routing Engine (`app/services/routing/`)**: Pluggable road network routing abstraction (`RoutingProvider` protocol, `MockRoutingProvider`, `OSRMProvider`) generating RFC 7946 LineString geometries.
- **Repository Layer (`app/repositories/`)**: Async SQL queries, PostGIS function calls (`ST_DWithin`, `ST_Distance`, `ST_MakeEnvelope`, `ST_Within`), data transformations (`PropertyRepository`, `POIRepository`, `UserRepository`).
- **AI Subsystem (`app/ai/`)**: Multi-provider AI abstraction (`AIProvider`, `GeminiProvider`, `OllamaProvider`, `MockAIProvider`, `AIRoutingPolicy`) with deterministic complexity-based auto-routing, failover loop prevention, token usage tracking (`AIUsageMetadata`), hosted context privacy scrubbing, and rule-based fallback. Parses natural language search queries into validated Pydantic models (`ParsedSearchIntent`), explains individual property matches, and generates grounded comparative narratives (`explain_comparison`).
- **Cache Layer (`app/cache/`)**: Short-lived route caching, ranking candidate caching, comparison caching (`CacheKeys.comparison`), and property caching with explicit TTLs (600s / 300s) and graceful degradation on Redis downtime.




## 3. Database Lifecycle & Transaction Strategy
- **Session Management**: Handled via FastAPI dependency `get_db()` yielding an `AsyncSession`.
- **Transaction Boundaries**:
  - Read operations execute within the active read transaction.
  - Write operations commit explicitly in the Service layer after business logic invariants are satisfied.
  - If an exception occurs, the `get_db()` context manager automatically issues a `rollback()` before closing the session.
- **Connection Pool**:
  - `AsyncAdaptedQueuePool` for production (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=3600`).
  - `NullPool` for automated testing (`ENVIRONMENT=test`) to eliminate event loop affinity conflicts.

## 4. Authentication & Authorization Model
- **Authentication Flow**:
  1. Client sends credentials to `POST /api/v1/auth/login`.
  2. `AuthService` verifies credentials against the stored Argon2/bcrypt hash.
  3. `create_access_token` issues a signed JWT with subject (`user_id`), expiration (`exp`), and type (`access`).
  4. Client attaches `Authorization: Bearer <token>` on protected endpoints.
  5. `get_current_active_user` dependency validates signature/expiration, looks up user in PostgreSQL, and verifies active status.
- **Authorization Enforcement**:
  - Service-level ownership checks via `AuthService.ensure_ownership(resource_owner_id, current_user_id)` raising `FORBIDDEN` (403).

# EstateMap AI — Project Context & System Specification

## 1. Project Purpose & Overview
**EstateMap AI** is a location-first real estate discovery platform built using FastAPI, PostgreSQL/PostGIS, Redis, Google Gemini, local Ollama (`llama3.2:3b`), Next.js, and **mapcn** (backed by MapLibre GL). 

Unlike conventional property listing platforms that treat a map as a secondary decorative widget alongside static cards, EstateMap AI treats the **map as the primary product feature and discovery engine**. The map actively drives search, viewport-based filtering, draw-area polygon queries, location intelligence, commute routing, and geographic price distribution.

---

## 2. Core Architectural Principles
1. **The LLM Interprets Intent; The Backend Validates & Executes Business Logic**:
   - AI extracts structured search parameters from user natural language queries.
   - Pydantic models validate and normalize the intent.
   - PostGIS executes spatial queries against indexed geometries.
   - The PostgreSQL database remains the single source of truth for factual data (prices, coordinates, availability, permissions).
   - The AI **never** generates raw SQL, never directly accesses PostgreSQL, and never invents factual property attributes.
2. **Modular Monolith**:
   - Clean layer separation (`API` -> `Services` -> `Repositories` -> `Database/PostGIS`).
   - Easily understood and maintained without distributed-system overhead.
3. **Mapcn as Non-Negotiable Map Component System**:
   - Uses [mapcn](https://www.mapcn.dev/) for React map components, markers, popups, and layers.
   - Underpinned by MapLibre GL for high-performance vector rendering.
4. **Deterministic Ranking Engine**:
   - Multi-factor scoring (affordability, commute, amenities, preferences) calculated deterministically by backend services.
   - AI provides natural language explanations based strictly on calculated ranking facts.

---

## 3. Directory Structure
```
EstateMap/
├── backend/
│   ├── alembic/                     # Async database migrations
│   │   ├── env.py                   # Async Alembic runtime configuration
│   │   └── versions/                # Migration scripts (0001_initial_postgis, 0002_create_users_table, etc.)
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint, lifespan, middlewares, handlers
│   │   ├── api/v1/                  # Endpoints (auth, users, properties, search, maps, favorites, recommendations, ai, health)
│   │   ├── core/                    # Settings, security (Argon2/bcrypt/JWT), logging, context, middleware, exceptions, exception_handlers, dependencies
│   │   ├── db/                      # Async SQLAlchemy session engine, DeclarativeBase, session lifecycle, DB health
│   │   ├── models/                  # SQLAlchemy ORM models (User, Property, PropertyImage, Amenity, Favorite, View)
│   │   ├── schemas/                 # Pydantic v2 validation models (Auth, User, ErrorResponse)
│   │   ├── repositories/            # Data access layer (UserRepository, PropertyRepository, FavoriteRepository)
│   │   ├── services/                # Business & spatial logic (AuthService, GeoService, SearchService, RankingService)
│   │   ├── ai/                      # AI provider abstraction (GeminiProvider, OllamaProvider, AIRouter, prompt templates)
│   │   ├── cache/                   # Redis connection, Redis health check & cache key definitions
│   │   └── utils/                   # Haversine distance, pagination models
│   ├── tests/                       # Pytest unit & integration test suites
│   │   ├── unit/                    # Health, exceptions, middleware, security tests
│   │   ├── integration/             # PostgreSQL + PostGIS, Redis, and Auth/User integration tests
│   │   └── conftest.py              # Pytest async fixtures (client, db_session, redis_conn)
│   ├── alembic.ini                  # Alembic configuration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                         # Next.js App Router (/search, /properties/[id], /favorites, /dashboard)
│   ├── components/                  # UI, navigation, map, filters, cards, commute, amenities
│   ├── features/                    # Feature-specific controllers and hooks
│   ├── lib/                         # API clients, map utilities, formatters, validation
│   ├── types/                       # TypeScript interfaces
│   ├── config/                      # Environment & map configurations
│   ├── Dockerfile
│   └── package.json
├── docs/                            # Comprehensive architectural and interview documentation
│   ├── ARCHITECTURE.md
│   ├── SYSTEM_DESIGN.md
│   ├── DATABASE_DESIGN.md
│   ├── MAP_ARCHITECTURE.md
│   ├── AI_ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── ADR/                         # Architecture Decision Records (ADR-001 to ADR-009)
├── docker-compose.yml               # Multi-service local development stack
├── .env.example                     # Environment configuration blueprint
└── README.md
```

---

## 4. Technology Stack
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), GeoAlchemy2, asyncpg, Redis, PyJWT, Argon2/bcrypt, structlog, pytest.
- **Database**: PostgreSQL 16 + PostGIS 3.4 (`postgis/postgis:16-3.4`).
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui design patterns, TanStack Query, mapcn, MapLibre GL.
- **AI Stack**: AIProvider abstraction with Google Gemini (`gemini-1.5-flash`) and local Ollama (`llama3.2:3b`).
- **DevOps**: Docker, Docker Compose with health checks and isolated network bridges.

---

## 5. API Contracts (Overview)
- `/health` — Overall diagnostic health (status, database PostGIS version, Redis latency).
- `/health/live` — Process liveness probe.
- `/health/ready` — Dependency readiness probe (PostgreSQL + PostGIS verification).
- `POST /api/v1/auth/register` — User registration with email normalization & Argon2 password hashing.
- `POST /api/v1/auth/login` — User authentication returning JWT Bearer token and safe UserResponse.
- `GET /api/v1/users/me` — Authenticated caller's profile retrieval.
- `/api/v1/properties` — Property CRUD and multi-criteria query endpoints (Phase 3).
- `/api/v1/search` — Structured search with filters, radius, and sorting.
- `/api/v1/maps/viewport` — PostGIS viewport bounding box query returning GeoJSON FeatureCollection.
- `/api/v1/maps/polygon` — PostGIS polygon search for user-drawn areas.
- `/api/v1/ai/parse-intent` — Natural-language query parsing into `ParsedSearchIntent`.
- `/api/v1/ai/explain` — Factual explanation generation for property match.
- `/api/v1/ai/compare` — Side-by-side factual comparison explanation.

---

## 6. Implementation Status & Roadmap
- **Phase 0 (Completed)**: Architecture Scaffolding, Directory Structure, Docker Compose, Redis/PostGIS configs, and comprehensive System Documentation.
- **Phase 1 (Completed)**: FastAPI application core, Async SQLAlchemy engine, PostGIS extension via Alembic migration, unified error responses, request correlation ID middleware, database & Redis health checks, and full unit/integration test suite.
- **Phase 2 (Completed)**: User Authentication & JWT (Registration, Login, Argon2/bcrypt password hashing, Current User dependency `get_current_active_user`, Ownership authorization foundation, `/api/v1/users/me`, and integration test suite).
- **Phase 3 (Completed)**: Property Management & Repository layer (Property spatial model with `Geometry(POINT, 4326)`, GiST index, check constraints, PropertyImage, Amenity M:N relationship, Alembic migration `0003_create_properties`, PropertyRepository with safe sorting/filtering/pagination, PropertyService with ownership enforcement, CRUD REST endpoints `/api/v1/properties`, and 47 passing unit/integration tests).
- **Phase 4 (Completed)**: Next.js Frontend Foundation & Design System (Tailwind CSS tokens, Dark/Light modes, typography, canonical TypeScript models matching backend, centralized `apiClient` with error envelope unwrapping, UI primitives, Feedback states, PropertyCard/Grid components, SearchBar/FilterBar, MapContainer placeholder boundary, and full pages for `/`, `/search`, `/properties/[id]`, `/login`, `/register`, `/favorites`, `/dashboard`).
- **Phase 5 (Completed)**: Official mapcn Installation + Interactive Map Integration (`components/ui/map.tsx` registry component, MapLibre tiled basemap, custom price pill markers `PropertyMarker`, rich popup cards `PropertyPopup`, GeoJSON transformation `[lng, lat]` in `lib/geojson.ts`, bidirectional List ↔ Map selection synchronization, split-view discovery on `/search`, detail map on `/properties/[id]`, zero backend changes, passing unit tests & Next.js production build).
- **Phase 6 (Completed)**: PostGIS Geospatial Search (Dedicated `GeoService`, `PropertyRepository` spatial query methods `ST_DWithin`, `ST_MakeEnvelope`, `ST_Within`, `ST_GeomFromGeoJSON`, endpoints `/api/v1/search/radius`, `/api/v1/search/bbox`, `/api/v1/search/polygon`, `/api/v1/maps/properties`, `/api/v1/maps/radius`, Pydantic v2 spatial validation, RFC 7946 GeoJSON serializers, frontend "Search this area" interactive UX, 74 backend tests & 8 frontend unit tests passing).
- **Phase 7 (Completed)**: Location Intelligence & Points of Interest (POICategory StrEnum, PointOfInterest ORM model with PostGIS Point SRID 4326 and GiST index `idx_pois_location_gist`, Alembic migration `0004_create_pois`, POIRepository & POIService, endpoints `/api/v1/pois/nearby`, `/api/v1/maps/pois`, `/api/v1/properties/{id}/nearby`, `/api/v1/properties/{id}/location-intelligence`, deterministic seed data in `seed_pois.py`, frontend POIMarker & POIPopup, POIFilter layer widget on `/search`, LocationIntelligence component on `/properties/[id]`, 130 backend tests & 17 frontend tests passing).
- **Phase 8 (Completed)**: Commute & Travel Intelligence (Pluggable `RoutingProvider` protocol with `MockRoutingProvider` and `OSRMProvider`, `CommuteService` with normalized Redis route caching and graceful degradation, endpoints `/api/v1/properties/{id}/commute`, `/api/v1/properties/{id}/commute/batch`, `/api/v1/commute/compare`, `/api/v1/commute/route`, RFC 7946 GeoJSON LineString path geometry, frontend `CommutePanel` and mapcn `MapRoute` route drawing on detail map, 154 backend tests & 20 frontend unit tests passing, ADR-012).
- **Phase 9 (Completed)**: Deterministic Property Ranking & Explainable Recommendations (Modular $[0.0, 1.0]$ clamped scoring algorithms in `utils/ranking.py`, 2-stage bounded candidate pipeline with `MAX_RANKING_CANDIDATES = 50`, dynamic missing-factor weight redistribution policy, deterministic tie-breaking `(-final_score, price, id)`, rule-based template explanations, `RankingService`, endpoints `/api/v1/search/ranked` and `/api/v1/recommendations/ranked`, frontend `RankedPropertyCard`, `RankingPreferences`, FilterBar/SearchPage integration, 170 backend tests & 22 frontend unit tests passing, ADR-013).
- **Phase 10 (Completed)**: Production Performance Layer: Redis Caching, Invalidation, Sliding-Window Rate Limiting & Observability (Centralized `CacheService`, deterministic versioned key namespace `CacheKeys` with coordinate normalization, non-blocking `scan_iter` + `unlink` pattern invalidation, sliding-window rate limiter via Redis `ZSET`, fail-open search degradation, fail-closed auth security, cold vs warm benchmark speedup >16x, 186 backend tests & 22 frontend tests passing, ADR-014, `CACHING_AND_PERFORMANCE.md`).
- **Phase 11 (Completed)**: Local Ollama Integration, AI Provider Abstraction & Safe AI Assistance (Asynchronous `AIProvider` protocol, `OllamaProvider` with `llama3.2:3b` JSON mode and keep-alive, `MockAIProvider`, `AIRouter`, `AIService` with bounded context assembly and deterministic fallback, `IndianPriceParser` for Lakhs/Crores, endpoints `/api/v1/ai/health`, `/api/v1/ai/parse-search`, `/api/v1/ai/properties/{id}/explain`, sliding-window rate limiting on AI operations, frontend `NaturalLanguageSearch` & `AIPropertyExplanation` components, 208 backend tests & 25 frontend tests passing, ADR-015, `AI_PROVIDER_ARCHITECTURE.md`).
- **Phase 12 (Completed)**: Gemini Provider Integration, Multi-Provider AI Routing, Fallback Strategy & Cost/Latency Controls (`GeminiProvider` via `google-genai` SDK with JSON schema mode and token usage tracking, deterministic `AIRoutingPolicy` with complexity heuristics, multi-provider failover orchestration with loop-prevention, multi-provider health check `/api/v1/ai/health`, `AIUsageMetadata` observability, 226 backend tests & 25 frontend unit tests passing, ADR-016, `MULTI_PROVIDER_AI.md`).
- **Phase 13 (Completed)**: Grounded AI Multi-Property Comparison & Explainable Recommendation Narratives (Dedicated deterministic `ComparisonService` computing pairwise price differences, area deltas, price/sqft, POI distance deltas, commute travel times, and mathematical ranking contribution margins $\Delta C_f$ without LLM arithmetic; strict 2–3 property bounds; hosted provider privacy allowlist excluding database IDs and PII; prompt template `property_comparison_v1.txt`; multi-provider comparison routing; endpoints `POST /api/v1/properties/compare` and `POST /api/v1/ai/properties/compare`; frontend `ComparisonTable`, `RankingDiffCard`, `AIComparisonSummary`, `ComparisonBar`, and `/compare` page with MapLibre A/B/C synchronization; 245 backend tests & 28 frontend unit tests passing, ADR-017, `PROPERTY_COMPARISON_ARCHITECTURE.md`).
- **Phase 14 (Completed)**: Ask the Map — Conversational Search Orchestration & Multi-Turn Query Refinement (Patch-based state transition reducer with SET, CLEAR, APPEND, REMOVE, RESET_SEARCH semantics; deterministic `LocationResolver` mapping landmarks and tech parks to verified Bengaluru coordinates with bounded validation; clarification flow for unrecognized locations; action routing for `SEARCH`, `REFINE`, `CLEAR_FILTER`, `RESET_SEARCH`, `RANK`, `COMPARE`, `EXPLAIN`; typed numeric `commute_duration_minutes` hard filtering; unified `ConversationalSearchState` bridging manual UI controls, map viewport, and AI turns; endpoint `POST /api/v1/ai/ask-map`; frontend `AskTheMapBar` with suggestion quick pills, patch feedback badges, clarification alert banner, and telemetry; 280 backend tests & 33 frontend unit tests passing, ADR-018, `ASK_THE_MAP_ARCHITECTURE.md`).
- **Phase 15**: Final End-to-End Production Hardening & System Verification.


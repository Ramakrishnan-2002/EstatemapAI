# -*- coding: utf-8 -*-
# Metadata for all 100 EstateMap AI Engineering Stories

STORIES_META = [
    # Phase 1: Foundation (1-6)
    (1, "Python Project Structure & Clean Architecture", 2, 1, [], [2, 3, 4], ["backend/app/main.py", "backend/pyproject.toml", "backend/app/core/config.py"]),
    (2, "FastAPI Lifespan & Application Lifecycle", 3, 1, [1], [3, 6, 9, 39], ["backend/app/main.py", "backend/app/cache/redis.py", "backend/app/db/session.py"]),
    (3, "Type-Safe Configuration with Pydantic-Settings", 2, 1, [1], [2, 4, 7, 14, 39, 52], ["backend/app/core/config.py", ".env.example"]),
    (4, "API Request/Response Schemas with Pydantic v2", 3, 1, [1, 3], [5, 18, 19, 27, 34, 55], ["backend/app/schemas/property.py", "backend/app/schemas/search.py", "backend/app/schemas/auth.py"]),
    (5, "RFC 7807 Centralized Error Handling", 3, 1, [1, 4], [6, 14, 18, 58], ["backend/app/core/exceptions.py", "backend/app/core/exception_handlers.py"]),
    (6, "Structured Logging & Distributed Request IDs", 3, 1, [1, 5], [13, 46, 58, 89], ["backend/app/core/middleware.py", "backend/app/core/logging.py"]),

    # Phase 2: Database & Geospatial Engineering (7-13 & 18-28)
    (7, "PostgreSQL Relational Modeling & Schema Integrity", 5, 2, [1, 3], [8, 9, 10, 11, 21], ["backend/app/models/property.py", "backend/app/models/user.py", "backend/app/models/poi.py"]),
    (8, "SQLAlchemy 2.0 Declarative Models & Repository Pattern", 5, 2, [7], [9, 18, 19, 20], ["backend/app/models/base.py", "backend/app/repositories/property_repo.py", "backend/app/repositories/user_repo.py"]),
    (9, "Non-Blocking Async Database Access with Asyncpg", 5, 2, [2, 7, 8], [13, 18, 86], ["backend/app/db/session.py", "backend/app/repositories/base_repo.py"]),
    (10, "Database Migrations with Alembic", 3, 2, [7, 8], [11, 12, 81], ["backend/alembic/env.py", "backend/alembic/versions/", "backend/alembic.ini"]),
    (11, "Soft Deletion & Audit Fields Pattern", 3, 2, [7, 8, 10], [18, 19], ["backend/app/models/base.py", "backend/app/repositories/property_repo.py"]),
    (12, "Database Seeding & Deterministic Test Fixtures", 3, 2, [7, 8, 10], [18, 86], ["backend/app/db/seed.py", "backend/app/db/seed_chennai.py", "backend/tests/conftest.py"]),
    (13, "Connection Pooling & Pool Exhaustion Prevention", 5, 2, [2, 6, 9], [86, 92], ["backend/app/db/session.py", "backend/app/core/config.py"]),
    (18, "Property CRUD Domain Service & Validation Logic", 5, 2, [4, 5, 8, 9, 11], [19, 20, 34, 62], ["backend/app/services/property_service.py", "backend/app/api/v1/endpoints/properties.py"]),
    (19, "Advanced Multi-Facet Property Filtering", 5, 2, [4, 8, 18], [20, 25, 34, 75], ["backend/app/repositories/property_repo.py", "backend/app/schemas/search.py"]),
    (20, "Deterministic Pagination & Cursor vs Offset", 5, 2, [8, 18, 19], [75, 95], ["backend/app/schemas/common.py", "backend/app/repositories/property_repo.py"]),
    (21, "Geospatial Fundamentals & Coordinate Reference Systems (WGS84 vs Projected)", 5, 2, [7], [22, 23, 24, 29], ["backend/app/models/property.py", "backend/app/models/poi.py"]),
    (22, "PostGIS POINT Geometry & Spatial Column Storage", 5, 2, [7, 21], [23, 24, 25], ["backend/app/models/property.py", "backend/app/models/poi.py", "backend/app/db/session.py"]),
    (23, "GiST Spatial Indexing (Generalized Search Tree)", 8, 2, [21, 22], [24, 25, 28, 92], ["backend/alembic/versions/", "backend/app/models/property.py"]),
    (24, "Radius Distance Search via ST_DWithin on Spheroids", 5, 2, [21, 22, 23], [26, 28, 35], ["backend/app/services/spatial_service.py", "backend/app/repositories/property_repo.py"]),
    (25, "Bounding-Box Viewport Search via ST_MakeEnvelope", 5, 2, [21, 22, 23], [28, 76, 77], ["backend/app/services/spatial_service.py", "backend/app/api/v1/endpoints/spatial.py"]),
    (26, "Points of Interest (POI) Location Intelligence & Category Queries", 5, 2, [22, 24], [35, 38], ["backend/app/models/poi.py", "backend/app/services/poi_service.py", "backend/app/repositories/poi_repo.py"]),
    (27, "RFC 7946 GeoJSON Standard Compliance & Serializers", 3, 2, [4, 22], [76, 78], ["backend/app/schemas/spatial.py", "backend/app/services/spatial_service.py"]),
    (28, "Geospatial Query Optimization & Spatial EXPLAIN ANALYZE", 8, 2, [23, 24, 25], [89, 92], ["backend/app/services/spatial_service.py", "backend/app/db/session.py"]),

    # Phase 3: Security, Identity & Authentication (14-17)
    (14, "Password Hashing with Argon2id & Cryptographic Salting", 3, 3, [3, 5, 7], [15, 16], ["backend/app/core/security.py", "backend/app/services/auth_service.py"]),
    (15, "Stateless JWT Authentication & Cryptographic Signature Verification", 5, 3, [3, 14], [16, 48, 80], ["backend/app/core/security.py", "backend/app/api/v1/endpoints/auth.py"]),
    (16, "Role-Based Authorization & Ownership Verification", 3, 3, [14, 15], [18, 98], ["backend/app/api/deps.py", "backend/app/models/user.py", "backend/app/services/property_service.py"]),
    (17, "Security Headers, CORS Policy & Defense-in-Depth", 3, 3, [1, 15], [81, 98], ["backend/app/main.py", "backend/app/core/middleware.py"]),

    # Phase 4: Location, Routing & Commute Intelligence (29-33)
    (29, "Haversine Great-Circle Distance vs Geodesic Mathematics", 3, 4, [21], [30, 31, 35], ["backend/app/utils/geo.py", "backend/app/services/commute_service.py"]),
    (30, "Location Extraction & Nominatim Geocoding Integration", 5, 4, [21, 29], [31, 69], ["backend/app/services/geocoding_service.py", "backend/app/api/v1/endpoints/search.py"]),
    (31, "Road-Network Graph Traversal vs Euclidean Spatial Distance", 5, 4, [21, 29], [32, 33, 35], ["backend/app/services/commute_service.py", "backend/app/services/osrm_client.py"]),
    (32, "OSRM Routing Engine Integration & Table Matrix API", 5, 4, [31], [33, 44], ["backend/app/services/osrm_client.py", "backend/app/services/commute_service.py"]),
    (33, "Multi-Modal Commute Matrix & Fallback Strategies", 5, 4, [31, 32], [35, 44], ["backend/app/services/commute_service.py", "backend/app/schemas/search.py"]),

    # Phase 5: Deterministic Scoring & Comparison Engine (34-38 & 62-64)
    (34, "Multi-Criteria Decision Analysis & Scoring Normalization", 5, 5, [4, 18], [35, 36, 62], ["backend/app/services/ranking_service.py", "backend/app/schemas/search.py"]),
    (35, "6-Factor Mathematical Ranking Engine", 8, 5, [24, 26, 29, 31, 33, 34], [36, 37, 38, 62], ["backend/app/services/ranking_service.py", "backend/app/api/v1/endpoints/search.py"]),
    (36, "Weight Vector Validation & Preference Calibration", 3, 5, [34, 35], [37, 75], ["backend/app/schemas/search.py", "backend/app/services/ranking_service.py"]),
    (37, "Dynamic Missing-Factor Weight Redistribution", 5, 5, [35, 36], [38, 62], ["backend/app/services/ranking_service.py"]),
    (38, "Ranking Score Explainability & Score Breakdown Generation", 5, 5, [26, 35, 37], [64, 70, 78], ["backend/app/schemas/search.py", "backend/app/services/ranking_service.py"]),
    (62, "Deterministic Property Comparison Engine & Dimension Winners", 5, 5, [18, 34, 35], [63, 64, 79], ["backend/app/services/comparison_service.py", "backend/app/api/v1/endpoints/comparison.py"]),
    (63, "Quantitative Feature Comparison & Metric Diff Calculation", 3, 5, [62], [64, 79], ["backend/app/services/comparison_service.py", "backend/app/schemas/comparison.py"]),
    (64, "Grounded Comparison Summary Generation", 5, 5, [38, 62, 63], [70, 79], ["backend/app/services/comparison_service.py", "backend/app/ai/gemini_provider.py"]),

    # Phase 6: In-Memory Acceleration & Rate Limiting (39-50)
    (39, "Redis In-Memory Architecture & In-Memory Data Structures", 3, 6, [2, 3], [40, 41, 46], ["backend/app/cache/redis.py", "backend/app/cache/service.py"]),
    (40, "Cache-Aside (Lazy Loading) Pattern Implementation", 5, 6, [39], [41, 42, 43, 44], ["backend/app/cache/service.py", "backend/app/services/property_service.py"]),
    (41, "Canonical Cache Key Design & Cryptographic Hashing", 3, 6, [39, 40], [42, 44], ["backend/app/cache/service.py", "backend/app/utils/hashing.py"]),
    (42, "Cache Invalidation Strategies & Event-Driven Cache Eviction", 5, 6, [40, 41], [43, 93], ["backend/app/cache/service.py", "backend/app/services/property_service.py"]),
    (43, "Cache Stampede Mitigation & Mutex Locking / TTL Jitter", 5, 6, [40, 41, 42], [93], ["backend/app/cache/service.py"]),
    (44, "Geospatial Route Caching with Invariant Coordinate Rounding", 5, 6, [32, 33, 40, 41], [93], ["backend/app/services/commute_service.py", "backend/app/cache/service.py"]),
    (45, "Token Bucket vs Leaky Bucket vs Sliding Window Rate Limiting", 5, 6, [39], [46, 47, 48], ["backend/app/cache/rate_limiter.py"]),
    (46, "Sliding-Window Log Rate Limiter via Redis Sorted Sets (ZSET)", 8, 6, [6, 39, 45], [47, 48, 49], ["backend/app/cache/rate_limiter.py", "backend/app/core/middleware.py"]),
    (47, "Rate Limit Headers (RFC 6585 & IETF Draft Standards)", 3, 6, [46], [48, 49], ["backend/app/core/middleware.py", "backend/app/cache/rate_limiter.py"]),
    (48, "Multi-Tiered Rate Limiting by Endpoint & Auth Identity", 5, 6, [15, 46, 47], [49, 94], ["backend/app/core/middleware.py", "backend/app/core/config.py"]),
    (49, "Fail-Open vs Fail-Closed Degradation Policies", 5, 6, [46, 47, 48], [50, 94], ["backend/app/cache/rate_limiter.py", "backend/app/core/middleware.py"]),
    (50, "Distributed Redis Connection Management & Sentinel High Availability", 5, 6, [2, 39, 49], [93, 97], ["backend/app/cache/redis.py", "backend/app/core/config.py"]),

    # Phase 7: Multi-Provider AI Architecture & Conversational State Machine (51-61 & 65-72)
    (51, "LLM Integration Patterns: RAG vs Function Calling vs State Machines", 5, 7, [4], [52, 55, 65], ["backend/app/ai/protocol.py", "backend/app/ai/state_reducer.py"]),
    (52, "Abstract AI Provider Protocol & Decoupled Architecture", 5, 7, [3, 51], [53, 54, 57], ["backend/app/ai/protocol.py", "backend/app/ai/router.py"]),
    (53, "Local LLM Inference with Ollama (Llama 3 / Mistral)", 5, 7, [52], [57, 58], ["backend/app/ai/ollama_provider.py", "backend/app/ai/protocol.py"]),
    (54, "Cloud LLM Inference with Google Gemini 1.5 Pro / Flash", 5, 7, [52], [57, 58], ["backend/app/ai/gemini_provider.py", "backend/app/ai/protocol.py"]),
    (55, "Structured JSON Schema Enforcement & LLM Output Validation", 5, 7, [4, 51, 52], [56, 59, 66], ["backend/app/schemas/ai.py", "backend/app/ai/gemini_provider.py", "backend/app/ai/ollama_provider.py"]),
    (56, "Prompt Engineering for Real Estate Query Disambiguation", 5, 7, [55], [57, 65, 69], ["backend/app/ai/prompts.py", "backend/app/ai/state_reducer.py"]),
    (57, "Complexity-Based AI Provider Routing Strategy", 5, 7, [52, 53, 54, 56], [58, 60, 94], ["backend/app/ai/router.py", "backend/app/services/search_service.py"]),
    (58, "Global Request Deadlines & Automatic AI Provider Failover", 8, 7, [5, 6, 53, 54, 57], [61, 94], ["backend/app/ai/router.py", "backend/app/ai/gemini_provider.py", "backend/app/ai/ollama_provider.py"]),
    (59, "AI Guardrails, Prompt Injection Defense & Schema Whitelisting", 5, 7, [55, 56], [66, 70, 98], ["backend/app/ai/guardrails.py", "backend/app/ai/state_reducer.py"]),
    (60, "Token Usage Tracking, Cost Estimation & Latency Metrics", 3, 7, [57, 58], [90, 94], ["backend/app/ai/tracker.py", "backend/app/ai/router.py"]),
    (61, "Deterministic Fallback Parser (Zero-LLM Mode)", 5, 7, [58], [65, 66], ["backend/app/ai/fallback_parser.py", "backend/app/services/search_service.py"]),
    (65, "\"Ask the Map\" Conversational Search Architecture", 8, 7, [51, 56, 57, 61], [66, 67, 68, 75], ["backend/app/api/v1/endpoints/search.py", "backend/app/services/search_service.py", "frontend/src/components/AskMapDrawer.tsx"]),
    (66, "Multi-Turn Conversation State Reducer & Delta Patches", 8, 7, [55, 59, 61, 65], [67, 68, 71], ["backend/app/ai/state_reducer.py", "backend/app/schemas/search.py"]),
    (67, "Implicit vs Explicit Filter Modification in Conversational Dialogue", 5, 7, [65, 66], [68, 69], ["backend/app/ai/state_reducer.py", "backend/app/ai/prompts.py"]),
    (68, "Conversational Filter History & Undo/Reset State Management", 5, 7, [66, 67], [71, 75], ["backend/app/ai/state_reducer.py", "backend/app/schemas/search.py"]),
    (69, "Conversational Spatial Intent Disambiguation", 5, 7, [30, 56, 65, 67], [70, 77], ["backend/app/ai/state_reducer.py", "backend/app/services/geocoding_service.py"]),
    (70, "Grounded AI Response Generation & Hallucination Prevention", 5, 7, [38, 59, 64, 65], [72, 75], ["backend/app/ai/response_generator.py", "backend/app/services/search_service.py"]),
    (71, "Conversation Session Persistence & Storage in Redis / Postgres", 5, 7, [39, 66, 68], [72, 96], ["backend/app/cache/session_store.py", "backend/app/repositories/session_repo.py"]),
    (72, "End-to-End Conversational Search Integration Testing", 5, 7, [65, 66, 70, 71], [86, 88], ["backend/tests/integration/test_conversational_search.py", "backend/tests/fixtures/conversations.py"]),

    # Phase 8: Frontend Engineering & Map Visualization (73-80)
    (73, "Next.js 14 App Router & Server/Client Boundary Architecture", 5, 8, [4], [74, 75, 76], ["frontend/src/app/page.tsx", "frontend/src/app/layout.tsx", "frontend/src/app/search/page.tsx"]),
    (74, "Responsive Real Estate Discovery UI with Tailwind CSS", 3, 8, [73], [75, 78, 79], ["frontend/src/app/globals.css", "frontend/tailwind.config.js", "frontend/src/components/PropertyCard.tsx"]),
    (75, "Interactive Property Search & Dynamic Filter Sidebar", 5, 8, [19, 36, 73, 74], [77, 78], ["frontend/src/components/FilterSidebar.tsx", "frontend/src/app/search/page.tsx"]),
    (76, "MapLibre GL WebGL Vector Map Rendering & Tile Management", 5, 8, [25, 27, 73], [77, 78], ["frontend/src/components/MapComponent.tsx", "frontend/src/components/MapLibreWrapper.tsx"]),
    (77, "Dynamic Viewport Bounding-Box Calculation & Debounced Pan/Zoom", 5, 8, [25, 69, 75, 76], [78, 96], ["frontend/src/components/MapComponent.tsx", "frontend/src/hooks/useDebounce.ts"]),
    (78, "Bidirectional Map Marker & Listing Card Synchronized Highlighting", 5, 8, [27, 38, 74, 76, 77], [79, 80], ["frontend/src/components/MapComponent.tsx", "frontend/src/components/PropertyCard.tsx", "frontend/src/app/search/page.tsx"]),
    (79, "Interactive Property Comparison Drawer & Visual Differencing", 5, 8, [62, 63, 64, 74, 78], [80], ["frontend/src/components/ComparisonDrawer.tsx", "frontend/src/app/compare/page.tsx"]),
    (80, "Persistent Cross-Tab Favorites & Comparison Contexts", 5, 8, [15, 78, 79], [88], ["frontend/src/context/FavoritesContext.tsx", "frontend/src/context/ComparisonContext.tsx"]),

    # Phase 9: Reliability, Performance & DevOps Engineering (81-90)
    (81, "Multi-Container Docker Architecture & Networking", 5, 9, [10, 17], [82, 83, 84], ["docker-compose.yml", "backend/Dockerfile", "frontend/Dockerfile"]),
    (82, "Docker Compose Health Checks & Service Dependency Orchestration", 3, 9, [81], [83, 85], ["docker-compose.yml"]),
    (83, "Multi-Stage Dockerfile Optimization & Minimal Distroless Containers", 5, 9, [81, 82], [84, 85], ["backend/Dockerfile", "frontend/Dockerfile", ".dockerignore"]),
    (84, "Non-Root Security Policies & Container Hardening", 3, 9, [81, 83], [85, 98], ["backend/Dockerfile", "frontend/Dockerfile", "docker-compose.yml"]),
    (85, "Continuous Integration Pipeline with GitHub Actions", 5, 9, [82, 83, 84], [86, 88], [".github/workflows/ci.yml"]),
    (86, "Comprehensive Test Pyramid & Async Testing Fixtures", 8, 9, [9, 12, 72, 85], [87, 88], ["backend/tests/conftest.py", "backend/pytest.ini", "backend/tests/unit/", "backend/tests/integration/"]),
    (87, "Integration Testing with Testcontainers & Isolated Postgres/Redis", 5, 9, [86], [88, 92], ["backend/tests/integration/test_spatial_db.py", "backend/tests/integration/test_redis_cache.py"]),
    (88, "Frontend End-to-End Testing with Playwright & Mock Service Worker", 5, 9, [80, 85, 86], [96], ["frontend/tests/", "frontend/playwright.config.ts"]),
    (89, "Application Performance Monitoring & OpenTelemetry Tracing", 5, 9, [6, 28], [90, 96], ["backend/app/core/telemetry.py", "backend/app/core/middleware.py"]),
    (90, "Prometheus Metrics & Grafana Dashboard Observability", 5, 9, [60, 89], [96], ["backend/app/core/metrics.py", "docker-compose.yml"]),

    # Phase 10: Architecture Defense & System Design (91-100)
    (91, "Defense of the Modular Monolith Architecture", 8, 10, [1, 81], [92, 93, 99, 100], ["backend/app/main.py", "docs/architecture/ADR_001_MODULAR_MONOLITH.md"]),
    (92, "Database Scaling: Read Replicas, Connection Pooling & Sharding", 8, 10, [13, 23, 28, 87], [93, 95, 97, 100], ["backend/app/db/session.py", "docs/architecture/DATABASE_SCALING.md"]),
    (93, "Caching Architecture at Scale: Distributed Redis Cluster & Invalidation", 8, 10, [42, 43, 44, 50], [95, 96, 97, 100], ["backend/app/cache/service.py", "docs/architecture/CACHING_STRATEGY.md"]),
    (94, "AI Gateway Architecture: Rate Limiting, Cost Optimization & Model Routing", 8, 10, [48, 49, 57, 58, 60], [96, 100], ["backend/app/ai/router.py", "docs/architecture/AI_GATEWAY.md"]),
    (95, "High-Throughput Ingestion Pipeline for Real Estate Listings", 8, 10, [20, 92, 93], [96, 97, 100], ["backend/app/services/ingestion_service.py", "docs/architecture/INGESTION_PIPELINE.md"]),
    (96, "Real-Time Viewport Sync at 100k Concurrent Users", 8, 10, [71, 77, 88, 89, 90], [97, 100], ["backend/app/services/spatial_service.py", "docs/architecture/VIEWPORT_SYNC.md"]),
    (97, "Disaster Recovery, Multi-Region Availability & Data Replication", 8, 10, [50, 92, 93, 95], [98, 100], ["docs/architecture/DISASTER_RECOVERY.md"]),
    (98, "Security Architecture: Zero-Trust, Secret Rotation & Data Protection", 8, 10, [16, 17, 59, 84], [99, 100], ["backend/app/core/security.py", "docs/architecture/SECURITY_ARCHITECTURE.md"]),
    (99, "Engineering Tradeoff Audit: 10 Decisions We Defend and 5 We Would Change", 8, 10, [91, 98], [100], ["docs/mastery/TRADEOFF_MATRIX.md", "docs/mastery/ADR_MASTER_INDEX.md"]),
    (100, "Complete EstateMap System Design Whiteboard Defense", 13, 10, [91, 92, 93, 94, 95, 96, 97, 98, 99], [], ["docs/mastery/ESTATEMAP_MASTER_BOOK.md", "docs/mastery/SYSTEM_DESIGN_INTERVIEW.md"])
]

PHASE_TITLES = {
    1: "Phase 1: Foundation (Stories 1-6)",
    2: "Phase 2: Database Modeling & Geospatial Engineering (Stories 7-13 & 18-28)",
    3: "Phase 3: Security, Identity & Authentication (Stories 14-17)",
    4: "Phase 4: Location, Routing & Commute Intelligence (Stories 29-33)",
    5: "Phase 5: Deterministic Scoring & Ranking Engine (Stories 34-38 & 62-64)",
    6: "Phase 6: In-Memory Acceleration & Rate Limiting (Stories 39-50)",
    7: "Phase 7: Multi-Provider AI Architecture & Conversational State Machine (Stories 51-61 & 65-72)",
    8: "Phase 8: Frontend Engineering & Map Visualization (Stories 73-80)",
    9: "Phase 9: Reliability, Performance & DevOps Engineering (Stories 81-90)",
    10: "Phase 10: Architecture Defense & System Design (Stories 91-100)"
}

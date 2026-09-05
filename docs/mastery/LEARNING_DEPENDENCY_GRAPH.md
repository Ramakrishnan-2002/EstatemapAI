# EstateMap AI — Concept & Learning Dependency Graph

This document visualizes the prerequisite relationships, unlock chains, and learning paths across all 100 engineering stories in EstateMap AI.

---
## 1. Technical Dependency Flow

`mermaid
graph TD
    HTTP[HTTP Protocol & REST] --> ASGI[ASGI Specification & Uvicorn]
    ASGI --> FastAPI[FastAPI Framework]
    FastAPI --> Pydantic[Pydantic v2 Validation]
    FastAPI --> Middleware[RequestID & RateLimit Middleware]
    FastAPI --> DepInj[Dependency Injection]

    SQL[Relational SQL & ACID] --> Postgres[PostgreSQL 16 Engine]
    Postgres --> PostGIS[PostGIS 3.4 Extension]
    PostGIS --> GiST[GiST Spatial Indexing]
    GiST --> BBoxSearch[Bounding-Box Viewport Search]
    GiST --> RadiusSearch[POI Radius Search]

    DepInj --> SQLAlchemy[SQLAlchemy 2.0 Async ORM]
    SQLAlchemy --> Asyncpg[Asyncpg Database Driver]
    Asyncpg --> Repositories[Repository Pattern]

    Repositories --> DomainCRUD[Property CRUD & Filters]
    BBoxSearch --> SpatialAPI[Spatial Search API]
    RadiusSearch --> LocationIntel[POI Location Intelligence]

    RoadGraph[Road Network Graph Theory] --> OSRM[OSRM Routing Engine]
    OSRM --> CommuteService[Commute Calculation Service]

    DomainCRUD --> RankingEngine[Deterministic 6-Factor Ranking]
    LocationIntel --> RankingEngine
    CommuteService --> RankingEngine

    RedisBasics[Redis In-Memory Key-Value] --> CacheAside[Cache-Aside Route Storage]
    RedisBasics --> ZSET[Redis Sorted Sets]
    ZSET --> SlidingWindow[Sliding-Window Rate Limiter]

    LLMFundamentals[LLM Structured Generation] --> AIProtocol[AIProvider Protocol]
    AIProtocol --> Ollama[Local Ollama Provider]
    AIProtocol --> Gemini[Cloud Gemini Provider]
    Ollama --> AIRouter[AI Provider Router & Failover]
    Gemini --> AIRouter
    AIRouter --> ConversationalState[Ask the Map State Reducer]

    RankingEngine --> ComparisonEngine[Side-by-Side Comparison]
    ComparisonEngine --> AIExplanation[Grounded AI Summary]

    React[React 18 & Next.js 14] --> MapLibre[MapLibre GL WebGL]
    MapLibre --> MapSync[Bidirectional Map/List Sync]
    ConversationalState --> FrontendAskMap[Ask The Map UI]
    FrontendAskMap --> DiscoveryExperience[Complete EstateMap Discovery Platform]
`

---

## 2. 100-Story Prerequisite & Unlock Table

| Story # | Title | Points | Phase | Depends On | Unlocks |
|---|---|---|---|---|---|
| **Story 01** | Python Project Structure & Clean Architecture | 2 SP | Phase 1 | None | Story 02, Story 03, Story 04 |
| **Story 02** | FastAPI Lifespan & Application Lifecycle | 3 SP | Phase 1 | Story 01 | Story 03, Story 06, Story 09, Story 39 |
| **Story 03** | Type-Safe Configuration with Pydantic-Settings | 2 SP | Phase 1 | Story 01 | Story 02, Story 04, Story 07, Story 14, Story 39, Story 52 |
| **Story 04** | API Request/Response Schemas with Pydantic v2 | 3 SP | Phase 1 | Story 01, Story 03 | Story 05, Story 18, Story 19, Story 27, Story 34, Story 55 |
| **Story 05** | RFC 7807 Centralized Error Handling | 3 SP | Phase 1 | Story 01, Story 04 | Story 06, Story 14, Story 18, Story 58 |
| **Story 06** | Structured Logging & Distributed Request IDs | 3 SP | Phase 1 | Story 01, Story 05 | Story 13, Story 46, Story 58, Story 89 |
| **Story 07** | PostgreSQL Relational Modeling & Schema Integrity | 5 SP | Phase 2 | Story 01, Story 03 | Story 08, Story 09, Story 10, Story 11, Story 21 |
| **Story 08** | SQLAlchemy 2.0 Declarative Models & Repository Pattern | 5 SP | Phase 2 | Story 07 | Story 09, Story 18, Story 19, Story 20 |
| **Story 09** | Non-Blocking Async Database Access with Asyncpg | 5 SP | Phase 2 | Story 02, Story 07, Story 08 | Story 13, Story 18, Story 86 |
| **Story 10** | Database Migrations with Alembic | 3 SP | Phase 2 | Story 07, Story 08 | Story 11, Story 12, Story 81 |
| **Story 11** | Soft Deletion & Audit Fields Pattern | 3 SP | Phase 2 | Story 07, Story 08, Story 10 | Story 18, Story 19 |
| **Story 12** | Database Seeding & Deterministic Test Fixtures | 3 SP | Phase 2 | Story 07, Story 08, Story 10 | Story 18, Story 86 |
| **Story 13** | Connection Pooling & Pool Exhaustion Prevention | 5 SP | Phase 2 | Story 02, Story 06, Story 09 | Story 86, Story 92 |
| **Story 18** | Property CRUD Domain Service & Validation Logic | 5 SP | Phase 2 | Story 04, Story 05, Story 08, Story 09, Story 11 | Story 19, Story 20, Story 34, Story 62 |
| **Story 19** | Advanced Multi-Facet Property Filtering | 5 SP | Phase 2 | Story 04, Story 08, Story 18 | Story 20, Story 25, Story 34, Story 75 |
| **Story 20** | Deterministic Pagination & Cursor vs Offset | 5 SP | Phase 2 | Story 08, Story 18, Story 19 | Story 75, Story 95 |
| **Story 21** | Geospatial Fundamentals & Coordinate Reference Systems (WGS84 vs Projected) | 5 SP | Phase 2 | Story 07 | Story 22, Story 23, Story 24, Story 29 |
| **Story 22** | PostGIS POINT Geometry & Spatial Column Storage | 5 SP | Phase 2 | Story 07, Story 21 | Story 23, Story 24, Story 25 |
| **Story 23** | GiST Spatial Indexing (Generalized Search Tree) | 8 SP | Phase 2 | Story 21, Story 22 | Story 24, Story 25, Story 28, Story 92 |
| **Story 24** | Radius Distance Search via ST_DWithin on Spheroids | 5 SP | Phase 2 | Story 21, Story 22, Story 23 | Story 26, Story 28, Story 35 |
| **Story 25** | Bounding-Box Viewport Search via ST_MakeEnvelope | 5 SP | Phase 2 | Story 21, Story 22, Story 23 | Story 28, Story 76, Story 77 |
| **Story 26** | Points of Interest (POI) Location Intelligence & Category Queries | 5 SP | Phase 2 | Story 22, Story 24 | Story 35, Story 38 |
| **Story 27** | RFC 7946 GeoJSON Standard Compliance & Serializers | 3 SP | Phase 2 | Story 04, Story 22 | Story 76, Story 78 |
| **Story 28** | Geospatial Query Optimization & Spatial EXPLAIN ANALYZE | 8 SP | Phase 2 | Story 23, Story 24, Story 25 | Story 89, Story 92 |
| **Story 14** | Password Hashing with Argon2id & Cryptographic Salting | 3 SP | Phase 3 | Story 03, Story 05, Story 07 | Story 15, Story 16 |
| **Story 15** | Stateless JWT Authentication & Cryptographic Signature Verification | 5 SP | Phase 3 | Story 03, Story 14 | Story 16, Story 48, Story 80 |
| **Story 16** | Role-Based Authorization & Ownership Verification | 3 SP | Phase 3 | Story 14, Story 15 | Story 18, Story 98 |
| **Story 17** | Security Headers, CORS Policy & Defense-in-Depth | 3 SP | Phase 3 | Story 01, Story 15 | Story 81, Story 98 |
| **Story 29** | Haversine Great-Circle Distance vs Geodesic Mathematics | 3 SP | Phase 4 | Story 21 | Story 30, Story 31, Story 35 |
| **Story 30** | Location Extraction & Nominatim Geocoding Integration | 5 SP | Phase 4 | Story 21, Story 29 | Story 31, Story 69 |
| **Story 31** | Road-Network Graph Traversal vs Euclidean Spatial Distance | 5 SP | Phase 4 | Story 21, Story 29 | Story 32, Story 33, Story 35 |
| **Story 32** | OSRM Routing Engine Integration & Table Matrix API | 5 SP | Phase 4 | Story 31 | Story 33, Story 44 |
| **Story 33** | Multi-Modal Commute Matrix & Fallback Strategies | 5 SP | Phase 4 | Story 31, Story 32 | Story 35, Story 44 |
| **Story 34** | Multi-Criteria Decision Analysis & Scoring Normalization | 5 SP | Phase 5 | Story 04, Story 18 | Story 35, Story 36, Story 62 |
| **Story 35** | 6-Factor Mathematical Ranking Engine | 8 SP | Phase 5 | Story 24, Story 26, Story 29, Story 31, Story 33, Story 34 | Story 36, Story 37, Story 38, Story 62 |
| **Story 36** | Weight Vector Validation & Preference Calibration | 3 SP | Phase 5 | Story 34, Story 35 | Story 37, Story 75 |
| **Story 37** | Dynamic Missing-Factor Weight Redistribution | 5 SP | Phase 5 | Story 35, Story 36 | Story 38, Story 62 |
| **Story 38** | Ranking Score Explainability & Score Breakdown Generation | 5 SP | Phase 5 | Story 26, Story 35, Story 37 | Story 64, Story 70, Story 78 |
| **Story 62** | Deterministic Property Comparison Engine & Dimension Winners | 5 SP | Phase 5 | Story 18, Story 34, Story 35 | Story 63, Story 64, Story 79 |
| **Story 63** | Quantitative Feature Comparison & Metric Diff Calculation | 3 SP | Phase 5 | Story 62 | Story 64, Story 79 |
| **Story 64** | Grounded Comparison Summary Generation | 5 SP | Phase 5 | Story 38, Story 62, Story 63 | Story 70, Story 79 |
| **Story 39** | Redis In-Memory Architecture & In-Memory Data Structures | 3 SP | Phase 6 | Story 02, Story 03 | Story 40, Story 41, Story 46 |
| **Story 40** | Cache-Aside (Lazy Loading) Pattern Implementation | 5 SP | Phase 6 | Story 39 | Story 41, Story 42, Story 43, Story 44 |
| **Story 41** | Canonical Cache Key Design & Cryptographic Hashing | 3 SP | Phase 6 | Story 39, Story 40 | Story 42, Story 44 |
| **Story 42** | Cache Invalidation Strategies & Event-Driven Cache Eviction | 5 SP | Phase 6 | Story 40, Story 41 | Story 43, Story 93 |
| **Story 43** | Cache Stampede Mitigation & Mutex Locking / TTL Jitter | 5 SP | Phase 6 | Story 40, Story 41, Story 42 | Story 93 |
| **Story 44** | Geospatial Route Caching with Invariant Coordinate Rounding | 5 SP | Phase 6 | Story 32, Story 33, Story 40, Story 41 | Story 93 |
| **Story 45** | Token Bucket vs Leaky Bucket vs Sliding Window Rate Limiting | 5 SP | Phase 6 | Story 39 | Story 46, Story 47, Story 48 |
| **Story 46** | Sliding-Window Log Rate Limiter via Redis Sorted Sets (ZSET) | 8 SP | Phase 6 | Story 06, Story 39, Story 45 | Story 47, Story 48, Story 49 |
| **Story 47** | Rate Limit Headers (RFC 6585 & IETF Draft Standards) | 3 SP | Phase 6 | Story 46 | Story 48, Story 49 |
| **Story 48** | Multi-Tiered Rate Limiting by Endpoint & Auth Identity | 5 SP | Phase 6 | Story 15, Story 46, Story 47 | Story 49, Story 94 |
| **Story 49** | Fail-Open vs Fail-Closed Degradation Policies | 5 SP | Phase 6 | Story 46, Story 47, Story 48 | Story 50, Story 94 |
| **Story 50** | Distributed Redis Connection Management & Sentinel High Availability | 5 SP | Phase 6 | Story 02, Story 39, Story 49 | Story 93, Story 97 |
| **Story 51** | LLM Integration Patterns: RAG vs Function Calling vs State Machines | 5 SP | Phase 7 | Story 04 | Story 52, Story 55, Story 65 |
| **Story 52** | Abstract AI Provider Protocol & Decoupled Architecture | 5 SP | Phase 7 | Story 03, Story 51 | Story 53, Story 54, Story 57 |
| **Story 53** | Local LLM Inference with Ollama (Llama 3 / Mistral) | 5 SP | Phase 7 | Story 52 | Story 57, Story 58 |
| **Story 54** | Cloud LLM Inference with Google Gemini 1.5 Pro / Flash | 5 SP | Phase 7 | Story 52 | Story 57, Story 58 |
| **Story 55** | Structured JSON Schema Enforcement & LLM Output Validation | 5 SP | Phase 7 | Story 04, Story 51, Story 52 | Story 56, Story 59, Story 66 |
| **Story 56** | Prompt Engineering for Real Estate Query Disambiguation | 5 SP | Phase 7 | Story 55 | Story 57, Story 65, Story 69 |
| **Story 57** | Complexity-Based AI Provider Routing Strategy | 5 SP | Phase 7 | Story 52, Story 53, Story 54, Story 56 | Story 58, Story 60, Story 94 |
| **Story 58** | Global Request Deadlines & Automatic AI Provider Failover | 8 SP | Phase 7 | Story 05, Story 06, Story 53, Story 54, Story 57 | Story 61, Story 94 |
| **Story 59** | AI Guardrails, Prompt Injection Defense & Schema Whitelisting | 5 SP | Phase 7 | Story 55, Story 56 | Story 66, Story 70, Story 98 |
| **Story 60** | Token Usage Tracking, Cost Estimation & Latency Metrics | 3 SP | Phase 7 | Story 57, Story 58 | Story 90, Story 94 |
| **Story 61** | Deterministic Fallback Parser (Zero-LLM Mode) | 5 SP | Phase 7 | Story 58 | Story 65, Story 66 |
| **Story 65** | "Ask the Map" Conversational Search Architecture | 8 SP | Phase 7 | Story 51, Story 56, Story 57, Story 61 | Story 66, Story 67, Story 68, Story 75 |
| **Story 66** | Multi-Turn Conversation State Reducer & Delta Patches | 8 SP | Phase 7 | Story 55, Story 59, Story 61, Story 65 | Story 67, Story 68, Story 71 |
| **Story 67** | Implicit vs Explicit Filter Modification in Conversational Dialogue | 5 SP | Phase 7 | Story 65, Story 66 | Story 68, Story 69 |
| **Story 68** | Conversational Filter History & Undo/Reset State Management | 5 SP | Phase 7 | Story 66, Story 67 | Story 71, Story 75 |
| **Story 69** | Conversational Spatial Intent Disambiguation | 5 SP | Phase 7 | Story 30, Story 56, Story 65, Story 67 | Story 70, Story 77 |
| **Story 70** | Grounded AI Response Generation & Hallucination Prevention | 5 SP | Phase 7 | Story 38, Story 59, Story 64, Story 65 | Story 72, Story 75 |
| **Story 71** | Conversation Session Persistence & Storage in Redis / Postgres | 5 SP | Phase 7 | Story 39, Story 66, Story 68 | Story 72, Story 96 |
| **Story 72** | End-to-End Conversational Search Integration Testing | 5 SP | Phase 7 | Story 65, Story 66, Story 70, Story 71 | Story 86, Story 88 |
| **Story 73** | Next.js 14 App Router & Server/Client Boundary Architecture | 5 SP | Phase 8 | Story 04 | Story 74, Story 75, Story 76 |
| **Story 74** | Responsive Real Estate Discovery UI with Tailwind CSS | 3 SP | Phase 8 | Story 73 | Story 75, Story 78, Story 79 |
| **Story 75** | Interactive Property Search & Dynamic Filter Sidebar | 5 SP | Phase 8 | Story 19, Story 36, Story 73, Story 74 | Story 77, Story 78 |
| **Story 76** | MapLibre GL WebGL Vector Map Rendering & Tile Management | 5 SP | Phase 8 | Story 25, Story 27, Story 73 | Story 77, Story 78 |
| **Story 77** | Dynamic Viewport Bounding-Box Calculation & Debounced Pan/Zoom | 5 SP | Phase 8 | Story 25, Story 69, Story 75, Story 76 | Story 78, Story 96 |
| **Story 78** | Bidirectional Map Marker & Listing Card Synchronized Highlighting | 5 SP | Phase 8 | Story 27, Story 38, Story 74, Story 76, Story 77 | Story 79, Story 80 |
| **Story 79** | Interactive Property Comparison Drawer & Visual Differencing | 5 SP | Phase 8 | Story 62, Story 63, Story 64, Story 74, Story 78 | Story 80 |
| **Story 80** | Persistent Cross-Tab Favorites & Comparison Contexts | 5 SP | Phase 8 | Story 15, Story 78, Story 79 | Story 88 |
| **Story 81** | Multi-Container Docker Architecture & Networking | 5 SP | Phase 9 | Story 10, Story 17 | Story 82, Story 83, Story 84 |
| **Story 82** | Docker Compose Health Checks & Service Dependency Orchestration | 3 SP | Phase 9 | Story 81 | Story 83, Story 85 |
| **Story 83** | Multi-Stage Dockerfile Optimization & Minimal Distroless Containers | 5 SP | Phase 9 | Story 81, Story 82 | Story 84, Story 85 |
| **Story 84** | Non-Root Security Policies & Container Hardening | 3 SP | Phase 9 | Story 81, Story 83 | Story 85, Story 98 |
| **Story 85** | Continuous Integration Pipeline with GitHub Actions | 5 SP | Phase 9 | Story 82, Story 83, Story 84 | Story 86, Story 88 |
| **Story 86** | Comprehensive Test Pyramid & Async Testing Fixtures | 8 SP | Phase 9 | Story 09, Story 12, Story 72, Story 85 | Story 87, Story 88 |
| **Story 87** | Integration Testing with Testcontainers & Isolated Postgres/Redis | 5 SP | Phase 9 | Story 86 | Story 88, Story 92 |
| **Story 88** | Frontend End-to-End Testing with Playwright & Mock Service Worker | 5 SP | Phase 9 | Story 80, Story 85, Story 86 | Story 96 |
| **Story 89** | Application Performance Monitoring & OpenTelemetry Tracing | 5 SP | Phase 9 | Story 06, Story 28 | Story 90, Story 96 |
| **Story 90** | Prometheus Metrics & Grafana Dashboard Observability | 5 SP | Phase 9 | Story 60, Story 89 | Story 96 |
| **Story 91** | Defense of the Modular Monolith Architecture | 8 SP | Phase 10 | Story 01, Story 81 | Story 92, Story 93, Story 99, Story 100 |
| **Story 92** | Database Scaling: Read Replicas, Connection Pooling & Sharding | 8 SP | Phase 10 | Story 13, Story 23, Story 28, Story 87 | Story 93, Story 95, Story 97, Story 100 |
| **Story 93** | Caching Architecture at Scale: Distributed Redis Cluster & Invalidation | 8 SP | Phase 10 | Story 42, Story 43, Story 44, Story 50 | Story 95, Story 96, Story 97, Story 100 |
| **Story 94** | AI Gateway Architecture: Rate Limiting, Cost Optimization & Model Routing | 8 SP | Phase 10 | Story 48, Story 49, Story 57, Story 58, Story 60 | Story 96, Story 100 |
| **Story 95** | High-Throughput Ingestion Pipeline for Real Estate Listings | 8 SP | Phase 10 | Story 20, Story 92, Story 93 | Story 96, Story 97, Story 100 |
| **Story 96** | Real-Time Viewport Sync at 100k Concurrent Users | 8 SP | Phase 10 | Story 71, Story 77, Story 88, Story 89, Story 90 | Story 97, Story 100 |
| **Story 97** | Disaster Recovery, Multi-Region Availability & Data Replication | 8 SP | Phase 10 | Story 50, Story 92, Story 93, Story 95 | Story 98, Story 100 |
| **Story 98** | Security Architecture: Zero-Trust, Secret Rotation & Data Protection | 8 SP | Phase 10 | Story 16, Story 17, Story 59, Story 84 | Story 99, Story 100 |
| **Story 99** | Engineering Tradeoff Audit: 10 Decisions We Defend and 5 We Would Change | 8 SP | Phase 10 | Story 91, Story 98 | Story 100 |
| **Story 100** | Complete EstateMap System Design Whiteboard Defense | 13 SP | Phase 10 | Story 91, Story 92, Story 93, Story 94, Story 95, Story 96, Story 97, Story 98, Story 99 | None |
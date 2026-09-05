# EstateMap AI — Concept & Learning Dependency Graph

This document visualizes the prerequisite relationships between all technical concepts in the EstateMap AI platform.

---

## 1. Technical Dependency Flow

```mermaid
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
```

---

## 2. Learning Progression Clusters

1. **Cluster 1: Foundations**: Python 3.12, FastAPI, ASGI, Pydantic, Middleware, Error Handling.
2. **Cluster 2: Persistence & Spatial**: PostgreSQL, PostGIS, GiST, Spatial SQL (`ST_MakeEnvelope`, `ST_DWithin`), GeoJSON.
3. **Cluster 3: In-Memory Acceleration**: Redis, Cache-Aside, Key Canonicalization, Sliding-Window ZSET Rate Limiting.
4. **Cluster 4: Routing & Ranking**: OSRM road graphs, Commute matrix, 6-factor deterministic scoring, Missing-factor redistribution.
5. **Cluster 5: AI Orchestration**: Protocol abstraction, Ollama, Gemini, Query complexity routing, Deadlines, State machine delta patches.
6. **Cluster 6: Frontend & Map Sync**: Next.js App Router, MapLibre GL, WebGL viewport bounding box, Persistent Contexts.

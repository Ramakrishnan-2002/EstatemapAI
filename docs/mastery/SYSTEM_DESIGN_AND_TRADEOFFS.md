# EstateMap AI — System Design, Tradeoffs & Architectural Decisions
> **Document Status: Authoritative Tradeoff Analysis, Failure Modes, and ADR Index**

# Part 1: Engineering Tradeoff Matrix (15 Core Architectural Decisions)

# EstateMap AI — Architectural Tradeoff Matrix

This document provides in-depth technical comparisons of major architectural decisions, evaluating alternatives, pros, cons, and the exact reasons EstateMap AI adopted its specific approach.

---

## 1. Modular Monolith vs. Microservices

| Architecture | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Modular Monolith (Chosen)** | • Single codebase, single deployment unit.<br>• ACID database transactions across domains.<br>• Zero network latency between modules.<br>• Simplified debugging and testing.<br>• Low operational complexity (1 container per tier). | • Shared CPU/memory resources.<br>• Scaling is coarse-grained (entire app scales together).<br>• Requires strict internal module discipline to prevent spaghetti code. | **Right-sized architecture**: For a team of 1–10 engineers and 100k DAU, microservices introduce distributed transaction complexity, network latency, and gRPC overhead with zero business benefit. |
| **Microservices (Rejected)** | • Independent deployments per domain (Auth, Search, AI).<br>• Independent technology stacks and autoscaling.<br>• Fine-grained failure isolation. | • Requires distributed transactions (Saga / 2PC).<br>• High network latency on inter-service calls.<br>• Complex CI/CD, Kubernetes, and service mesh overhead.<br>• Massive debugging and distributed tracing friction. | **Premature Optimization**: Unjustified complexity for the current problem space. Clear domain boundaries inside the monolith allow clean future service extraction if necessary. |

---

## 2. PostGIS in PostgreSQL vs. External Spatial Search Engine (Elasticsearch)

| Architecture | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **PostGIS in PostgreSQL (Chosen)** | • Single source of truth (zero data synchronization delay).<br>• Native relational JOINs with property amenities, prices, and owners.<br>• ACID transactional updates.<br>• Full spatial SQL predicate library (`ST_DWithin`, `ST_MakeEnvelope`, `ST_DistanceSphere`). | • Spatial calculations consume database CPU.<br>• Advanced full-text fuzzy linguistic search is simpler in dedicated search engines. | **Zero Data Replication**: Eliminates dual-write anomalies, change-data-capture (CDC) pipelines, and Debezium/Kafka sync infrastructure. PostGIS handles millions of points easily on standard hardware. |
| **Elasticsearch / OpenSearch (Rejected)** | • Fast distributed full-text fuzzy search.<br>• Highly scalable horizontal document sharding. | • Eventual consistency (indexing lag).<br>• Requires complex CDC sync pipeline (Debezium/Kafka).<br>• Heavy JVM memory footprint.<br>• Weaker spatial relational join capabilities. | **Excessive Operational Burden**: Adding Elasticsearch creates data drift risks without offering superior bounding-box performance over PostGIS GiST indexing for real estate listing volumes. |

---

## 3. Deterministic Heuristic Ranking vs. Machine Learning (ML) Ranking

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Deterministic Heuristics (Chosen)** | • 100% explainable and audit-proof.<br>• Zero cold start problem (works instantly without historical logs).<br>• Real-time parameter tuning (user controls weights).<br>• Sub-millisecond arithmetic computation.<br>• Fully reproducible across test suites. | • Cannot automatically discover hidden non-linear user preference patterns.<br>• Requires manual mathematical formula design. | **Transparency & Cold Start**: Real estate buyers demand to know *why* a property is ranked #1. With zero historical click logs, ML models cannot be trained safely. |
| **Machine Learning / Learning-to-Rank (Rejected)** | • Automatically learns complex multi-feature interactions.<br>• Continuously optimizes for click-through rate (CTR) or conversion. | • Black-box scoring (impossible to explain clearly to users).<br>• Severe cold start failure without massive interaction datasets.<br>• Susceptible to popularity bias and data drift.<br>• Expensive training and model serving infrastructure. | **Premature & Unexplainable**: ML ranking is appropriate only after accumulating millions of interaction events. Deterministic math provides the reliable baseline required today. |

---

## 4. OSRM Self-Hosted vs. Commercial Routing APIs (Google Maps Distance Matrix)

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **OSRM Self-Hosted Engine (Chosen)** | • Zero per-query API costs.<br>• Sub-5ms road route calculation on local road graph.<br>• High throughput (thousands of matrix routes/sec).<br>• Complete data sovereignty. | • Requires hosting and maintaining road network graph data files (.osm.pbf).<br>• Live real-time traffic congestion data is not included in base OSM. | **Cost & Throughput Control**: Calculating commute times for 50 properties across 4 travel modes would cost \$1.00+ *per search query* on Google Maps ($5.00/1000 requests), making the product financially non-viable at scale. |
| **Google Maps / Mapbox APIs (Rejected)** | • Live real-time traffic congestion modeling.<br>• Global zero-setup cloud endpoint. | • Exorbitant per-request API costs.<br>• Strict rate limits and network latency bottlenecks.<br>• Vendor lock-in. | **Unsustainable Cost**: For high-volume ranking matrices, commercial APIs impose extreme financial and rate-limiting penalties. |

---

## 5. Explicit State Machine vs. Autonomous Agent (LangGraph / AutoGPT)

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Explicit State Machine (Chosen)** | • 100% deterministic state transitions (`SET`, `CLEAR`, `APPEND`, `RESET`).<br>• State is fully inspectable, serializable, and debuggable.<br>• Bounded execution latency (<1.5s).<br>• Impossible for LLM to enter infinite loops or hallucinate non-existent database mutations. | • Requires predefined state schema (`ConversationalSearchState`). | **Safety & Determinism**: Real estate search requires strict adherence to spatial bounds and filter constraints. Autonomous agents suffer from hallucinations, non-deterministic loops, and unmanageable latency. |
| **Autonomous Multi-Agent / LangGraph (Rejected)** | • Free-form autonomous multi-step reasoning.<br>• Dynamic tool invocation graphs. | • Unbounded latency (10–45s per user message).<br>• High hallucination and infinite loop risks.<br>• Massive token costs.<br>• Flaky test verification. | **Unacceptable Latency & Flakiness**: A search interface must respond in <1.5 seconds. Multi-agent loops are completely unsuited for synchronous conversational search. |


---

# Part 2: Technology Necessity Matrix (Why Each Component Is Essential)

# EstateMap AI — Technology Necessity Matrix

This document provides a defensible explanation for every primary technology used in EstateMap AI. It details why each technology is necessary, what explicit problem it solves, what breaks if it is removed, what alternatives were evaluated, and the engineering tradeoffs accepted.

---

| Technology | Why It Is Needed | Problem It Solves | What Breaks Without It | Evaluated Alternatives | Accepted Tradeoff |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | High-performance asynchronous API framework. | Non-blocking ASGI I/O for concurrent database, Redis, and AI network calls. | Code becomes synchronous and threads block on I/O; no automatic OpenAPI generation. | Flask, Django REST Framework, Express.js. | Smaller legacy plugin ecosystem than Django, but vastly superior async concurrency. |
| **PostgreSQL 16** | Relational data persistence with ACID guarantees. | Reliable relational storage for users, properties, amenities, reviews, and foreign key integrity. | No persistent storage; impossible to maintain foreign key consistency or transaction rollbacks. | MySQL, MongoDB, SQLite. | Requires structured schema migrations (Alembic) compared to schemaless NoSQL. |
| **PostGIS 3.4** | Spatial indexing and 2D geometric computation in the DB. | Enables sub-50ms bounding-box viewport queries (`ST_MakeEnvelope`) and radial distance filtering (`ST_DWithin`). | Spatial queries require full-table memory scans in Python, causing $\mathcal{O}(N)$ compute/bandwidth lag. | Elasticsearch Geo queries, SpatiaLite, in-memory R-Tree. | Adds C-library database extension dependency, but eliminates separate search engine synchronization. |
| **Redis 7** | Sub-millisecond in-memory caching and sliding-window state. | Caches expensive OSRM road routes and executes atomic sliding-window rate limiting via Sorted Sets. | OSRM routing server gets flooded with duplicate requests; rate limiting becomes per-process or inaccurate. | Memcached, in-memory Python `dict`, Hazelcast. | Requires separate memory store, but provides atomic primitives (ZSET, TTL) essential for sliding window. |
| **SQLAlchemy 2.0 (Async)** | Typed async Object-Relational Mapping (ORM). | Maps relational tables to Python models with connection pooling and async transaction lifecycles. | Developers must write raw SQL strings and manually manage database connection lifecycles. | Tortoise ORM, Peewee, raw asyncpg queries. | Minor ORM abstraction overhead, but prevents SQL injection and ensures compile-time type safety. |
| **Pydantic v2** | Rust-accelerated schema validation and serialization. | Strictly validates incoming request payloads and serializes responses according to strict API contracts. | Unvalidated, malformed data reaches database; no automated RFC 7807 error emission. | Marshmallow, attrs, standard dataclasses. | Strict typing requires explicit schemas, but guarantees zero schema drift across frontend and backend. |
| **OSRM Engine** | Open-source road network graph traversal. | Computes realistic driving, cycling, and walking durations across real street networks with turn-by-turn geometry. | Commute times fall back to straight-line Euclidean distance, ignoring rivers, one-ways, and barriers. | Google Maps Distance Matrix, Mapbox Directions, Valhalla. | Requires road network graph data, but eliminates exorbitant commercial API fees ($5.00/1000 queries). |
| **Google Gemini 2.5** | Fast hosted cloud LLM inference. | Generates grounded natural language property explanations and conversational intent parsing. | Conversational search requires local GPU hardware or falls back to rigid regex pattern matching. | OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet. | Requires internet connectivity and API quota, mitigated by automatic fallback to local Ollama. |
| **Ollama (Local LLM)** | Offline, privacy-preserving local LLM runner. | Enables zero-cost offline intent parsing and local development without cloud API credentials. | System becomes completely non-functional for AI tasks when internet is disconnected. | Local vLLM, llama.cpp, TGI. | Requires local CPU/GPU memory, but provides 100% offline self-containment. |
| **MapLibre GL JS** | WebGL-accelerated interactive vector map rendering. | Renders 60fps interactive vector maps, GeoJSON property markers, and road-network LineString overlays. | Map rendering becomes sluggish or impossible; no WebGL hardware acceleration. | Leaflet.js, Google Maps JS SDK, Mapbox GL JS. | Slightly steeper learning curve than Leaflet, but delivers GPU-accelerated rendering and zero license fees. |
| **TanStack Query** | Declarative asynchronous client state management. | Manages frontend caching, background refetching, and request deduplication. | Boilerplate `useEffect`/`useState` required for every component; duplicate network calls occur. | SWR, Redux Toolkit Query, manual fetch wrappers. | Adds small frontend bundle weight, but eliminates race conditions and inconsistent UI loading states. |
| **Docker Compose** | Multi-container environment orchestration. | Spins up PostgreSQL+PostGIS, Redis, FastAPI Backend, and Next.js Frontend with single command. | Developer must manually install and configure 4 separate daemons across different host operating systems. | Kubernetes (K8s), manual local installation. | Container resource overhead, but guarantees 100% deterministic environment parity across machines. |


---

# Part 3: Failure Modes, System Impact & Resiliency Mitigations

# EstateMap AI — Failure Mode Analysis & Resilience Matrix

This document defines all failure modes across the EstateMap AI architecture, detailing user impact, detection mechanisms, current handling strategies, and future production enhancements.

---

## Comprehensive Failure Matrix

| Failure Scenario | Severity | User Impact | Detection Mechanism | Current Handling Strategy | Production Enhancement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL Database Unavailable** | Critical | Cannot search, view property details, or authenticate. | Connection pool timeout / `asyncpg.CannotConnectNowError`. | Returns `HTTP 500 Internal Server Error` with `DATABASE_UNAVAILABLE` error code; transaction rolled back. | Read replicas with automated failover (Patroni / AWS RDS Multi-AZ); circuit breakers. |
| **Redis In-Memory Cache Down** | Medium | Cache misses on commute/POI routes; rate limiting disabled. | `aioredis.ConnectionError` caught in `cache_service.py` / `rate_limit.py`. | **Fail-Open**: Transparently queries PostgreSQL/OSRM directly; logs warning; general requests continue. | Redis Sentinel or Redis Cluster with automatic master-replica failover. |
| **Local Ollama LLM Unreachable** | Low | Slower AI responses during conversational search. | `httpx.ConnectError` in `ollama_provider.py`. | **Failover to Gemini**: Router detects failure within timeout and dispatches to Google Gemini. | Background healthcheck ping; multi-node Ollama inference cluster. |
| **Google Gemini Quota Exceeded (HTTP 429)** | Low | Cloud AI explanations temporarily unavailable. | `google.genai.errors.ClientError` with code 429 in `gemini_provider.py`. | **Failover to Ollama / Fallback**: Dispatches to local Ollama; if offline, uses Deterministic Fallback Provider. | Token bucket pre-throttling; fallback to secondary cloud provider (Anthropic/OpenAI). |
| **OSRM Routing Engine Unavailable** | Medium | Commute times fall back to approximations. | `httpx.TimeoutException` or `httpx.ConnectError` in `routing_service.py`. | **Spherical Fallback**: Uses `ST_DistanceSphere` Euclidean distance / 30 km/h average speed; sets `fallback_used: true`. | High-availability OSRM cluster with multi-region DNS routing. |
| **Invalid / Malformed AI JSON Output** | Low | Conversational search receives non-conforming JSON. | Pydantic `ValidationError` in `AIProviderRouter`. | **Safe Recovery**: Catches schema validation error and invokes deterministic rule-based patch generator. | Constrained decoding / Grammar-based sampling at the LLM engine level. |
| **Coordinates Out of Bounds** | Low | Map or search query outside physical coordinates. | Pydantic validator on `latitude` / `longitude` schemas. | **Validation Rejection**: Returns `HTTP 422 Unprocessable Entity` with exact field error details. | Client-side bounding box sanitization before network dispatch. |
| **Expired or Tampered JWT Token** | Low | User actions rejected. | `jwt.ExpiredSignatureError` or `jwt.InvalidTokenError` in `get_current_user`. | **Authentication Error**: Returns `HTTP 401 Unauthorized` with `AUTHENTICATION_ERROR` code. | Silent refresh token rotation with HTTP-only secure cookies. |
| **Duplicate User Registration** | Low | Attempting to register with an existing email address. | Unique constraint on `users.email` in PostgreSQL. | **Anti-Enumeration Handled**: Catches `IntegrityError` and returns `HTTP 400 Bad Request`. | Rate limit registration endpoints per IP to prevent email harvesting. |
| **Zero Search Results Returned** | None | User sees empty map. | PostGIS query returns empty record set. | **Empty State UX**: Frontend renders `EmptyState` component with suggested filter resets. | Broaden search bounds dynamically / Recommend nearest adjacent localities. |
| **Sliding Window Rate Limit Exceeded** | Low | Spammer / script blocked from overloading API. | Redis `ZCARD` exceeds threshold in `rate_limit.py`. | **Rate Limiting (429)**: Returns `HTTP 429 Too Many Requests` with `Retry-After: 60` response header. | Tiered rate limits based on user reputation and authenticated API keys. |
| **Frontend Network Disconnection** | Medium | User loses connectivity. | `window.navigator.onLine` / `fetch` error in browser. | **Error State UI**: Displays retry banner with cached state preservation. | Progressive Web App (PWA) offline service worker caching. |


---

# Part 4: Performance Benchmarks & Service Level Objectives (SLOs)

# EstateMap AI — Performance, Scalability & Capacity Planning

This document provides a rigorous technical breakdown of system performance. All metrics are explicitly partitioned into **MEASURED**, **LOCAL OBSERVED**, **THEORETICAL**, and **HYPOTHETICAL** categories.

---

## 1. Measured & Observed Metrics

### Local Test Suite Performance (MEASURED)
* **Backend Pytest Suite**: 288 tests completed in **50.67 seconds** on Docker container environment (Linux x86_64, Python 3.12, asyncpg, PostgreSQL 16 + PostGIS, Redis 7).
* **Frontend Node Test Suite**: 33 tests completed in **202.75 ms** using Node.js native test runner.
* **TypeScript Compilation**: 0 errors across all Next.js App Router pages and components.

### Local HTTP Endpoint Latency (LOCAL OBSERVED)
* **Static / Basic Routes (`GET /`, `GET /dashboard`, `GET /favorites`)**: ~75ms – 150ms in Next.js development server.
* **PostGIS Bounding-Box Spatial Search (`POST /api/v1/search/spatial`)**: ~12ms – 25ms database query time on 104 seeded listings.
* **Sliding-Window Rate Limiter Execution (`Redis ZSET`)**: ~0.8ms – 1.8ms per request.
* **Google Gemini AI Parsing Latency**: ~650ms – 1400ms per conversational turn.
* **Local Ollama Inference (Llama 3.2 on local CPU/GPU)**: ~1800ms – 4200ms per turn.

---

## 2. Theoretical Algorithmic Complexities

| Subsystem / Operation | Theoretical Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| **PostGIS GiST Spatial Indexing** | $\mathcal{O}(\log N)$ average query time | $\mathcal{O}(N)$ R-Tree disk space | Hierarchical bounding-box tree pruning non-intersecting geometries without full table scans. |
| **Sliding-Window Log (Redis ZSET)** | $\mathcal{O}(\log M + K)$ per request | $\mathcal{O}(M)$ per rate-limited identity | $M$ = requests in window (e.g. 5–60), $K$ = expired entries removed by `ZREMRANGEBYSCORE`. |
| **Deterministic Ranking Math** | $\mathcal{O}(P \times F)$ where $P$ = properties, $F = 6$ | $\mathcal{O}(P)$ output memory | Single-pass arithmetic evaluation over candidate properties (sub-millisecond for $P \le 500$). |
| **Conversational State Patch Reducer** | $\mathcal{O}(K)$ where $K$ = keys modified | $\mathcal{O}(1)$ state memory | Dict lookup and field overwrite on immutable Pydantic model. |
| **OSRM Route Lookup (Cached)** | $\mathcal{O}(1)$ Redis key lookup | $\mathcal{O}(1)$ payload size | Instantaneous memory hash lookup on canonical coordinate key. |

---

## 3. Hypothetical Capacity-Planning Exercise

> [!NOTE]
> **IMPORTANT**: The following numbers represent a **HYPOTHETICAL CAPACITY-PLANNING EXERCISE** designed for system-design interviews. They do not represent measured production benchmarks.

### Target Assumptions
* **Daily Active Users (DAU)**: 100,000 users.
* **Searches per User per Day**: 10 searches on average.
* **Total Daily Searches**: $100{,}000 \times 10 = 1{,}000{,}000\text{ searches/day}$.
* **Active Window**: 12 peak hours ($43{,}200\text{ seconds}$).

### QPS & Workload Calculations

#### 1. Average & Peak Query Per Second (QPS)
$$\text{Average QPS} = \frac{1{,}000{,}000\text{ requests}}{43{,}200\text{ seconds}} \approx 23.15\text{ QPS}$$
$$\text{Peak QPS (Assumed 3x Burst Factor)} = 23.15 \times 3 \approx 70\text{ QPS}$$

#### 2. Database Workload & Read Replica Sizing
* Assume 70 QPS at peak with 60% spatial searches hitting PostGIS (42 QPS PostGIS queries).
* With GiST indexed queries executing in ~15ms, a single PostgreSQL 16 primary instance with 4 vCPUs and 16 GB RAM can handle ~250 QPS.
* **Conclusion**: A single primary database + 1 read replica easily satisfies 100k DAU without sharding.

#### 3. Redis In-Memory Footprint Estimation
* **Rate Limiter Keys**: 100,000 active users $\times$ 5 requests $\times 128\text{ bytes} \approx 64\text{ MB}$.
* **Commute Route Cache**: 50,000 unique routes $\times 2\text{ KB} \approx 100\text{ MB}$.
* **POI Intelligence Cache**: 10,000 unique properties/radii $\times 4\text{ KB} \approx 40\text{ MB}$.
* **Total Redis Memory**: $\approx 204\text{ MB}$.
* **Conclusion**: A standard 2 GB Redis instance operates at $<15\%$ memory utilization with substantial headroom.

#### 4. AI Inference Capacity Planning
* Assume 10% of users engage in "Ask the Map" conversational search (10,000 conversational turns/day).
* Average token usage: 150 prompt tokens + 100 completion tokens = 250 tokens/turn.
* **Total Daily Tokens**: $10{,}000 \times 250 = 2{,}500{,}000\text{ tokens/day}$.
* With Gemini 2.5 Flash pricing / free tier limits, operating cost is negligible (<$1.00/day).


---

# Part 5: Production Scaling Evolution (10k → 1M Concurrent Users)

# EstateMap AI — Production Evolution Roadmap

This document outlines the architectural roadmap for transitioning EstateMap AI from a single-node modular monolith portfolio project to a distributed, multi-region production platform handling millions of daily active users.

---

## 1. Clear Architecture Separation: Current vs. Future

```
CURRENT (Single-Node Modular Monolith)
- Docker Compose Network
- Single PostgreSQL 16 + PostGIS Primary
- Single Redis 7 In-Memory Instance
- Self-Hosted OSRM HTTP Engine
- In-Process Python Asynchronous Worker Pool
- Local Ollama / Google Gemini AI Router

                    │
                    ▼  (Evolution to Enterprise Scale)

FUTURE (Distributed High-Availability Cloud Deployment)
- Kubernetes (EKS / GKE) Auto-Scaling Worker Pods
- AWS Aurora PostgreSQL Multi-AZ (1 Writer + 3 Read Replicas)
- AWS ElastiCache Redis Cluster (3 Shards + Multi-AZ Failover)
- Distributed Multi-Zone OSRM Routing Fleet
- Apache Kafka Event Bus (Listing Ingestion & Analytics Pipeline)
- OpenSearch Cluster (Fuzzy Linguistic Search & Document Retrieval)
- Cloudflare Enterprise WAF + Anycast CDN
```

---

## 2. Phase-by-Phase Production Evolution

### Stage 1: High Availability & Database Read Replicas (100k -> 500k DAU)
1. **Database Tier**: Migrate to AWS Aurora PostgreSQL Multi-AZ with PostGIS. Configure 1 Writer instance and 2 Reader replicas. Use PgBouncer connection pooling to handle thousands of concurrent client connections.
2. **Cache Tier**: Upgrade to AWS ElastiCache for Redis Cluster with automatic multi-AZ failover and data encryption at rest.
3. **Application Tier**: Containerize backend into AWS ECS Fargate or Kubernetes with Horizontal Pod Autoscalers (HPA) scaling on CPU/Memory and request queue depth.

### Stage 2: Asynchronous Event Pipelines & Ingestion (500k -> 2M DAU)
1. **Apache Kafka Event Bus**:
   * Topic `property.listings.created`: Triggers asynchronous image optimization, CDN distribution, and spatial indexing.
   * Topic `user.search.analytics`: Streams user search queries to clickhouse/BigQuery for analytics without blocking the search API.
2. **Object Storage & CDN**: Store listing images on Amazon S3 / Cloudflare R2 with automatic WebP transformation and Cloudflare CDN caching.

### Stage 3: Dedicated Full-Text & Fuzzy Linguistic Search (2M -> 10M DAU)
1. **OpenSearch / Elasticsearch Cluster**: Integrate OpenSearch via Change Data Capture (Debezium + Kafka Connect) from PostgreSQL. Use OpenSearch for fuzzy phonetic and typo-tolerant search ("Indra Ngr" -> "Indiranagar"), while keeping PostGIS for authoritative spatial polygon and bounding-box queries.
2. **Learning-to-Rank (LTR) Machine Learning**: Train an XGBoost / LambdaMART ranking model on accumulated user interaction logs (clicks, dwell time, favorites, contact owner inquiries), using deterministic ranking scores as a primary feature.


---

# Part 6: Architecture Decision Record (ADR) Master Index

# EstateMap AI — Architecture Decision Record (ADR) Master Index

This document provides a verified index and validity audit of all 18 Architecture Decision Records (ADRs) in the EstateMap AI codebase (`docs/ADR/`).

---

| ADR ID | Decision Title | Problem Addressed | Chosen Option | Rejected Alternatives | Accepted Tradeoff | Current Code Validity | Key Source Files |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ADR-001** | Modular Monolithic Architecture | Architecture pattern for real estate discovery backend. | Modular Monolith inside FastAPI. | Microservices, Serverless Lambdas. | Coarse-grained scaling vs. zero network overhead. | **Active & Valid** | `backend/app/main.py`, `backend/app/api/v1/` |
| **ADR-002** | PostGIS for Spatial Persistence & Indexing | Geospatial data storage and 2D query execution. | PostgreSQL + PostGIS with GiST indexing. | Elasticsearch Geo, MongoDB 2dsphere, App-side math. | Database CPU spatial workload vs. single source of truth. | **Active & Valid** | `backend/app/models/property.py`, `backend/app/repositories/geo_repository.py` |
| **ADR-003** | MapLibre GL JS & mapcn Mapping Stack | Interactive map rendering in Next.js frontend. | MapLibre GL JS with mapcn components. | Google Maps JS SDK, Leaflet.js, Mapbox GL. | WebGL setup complexity vs. 60fps GPU acceleration and zero licensing costs. | **Active & Valid** | `frontend/components/map/map-container.tsx`, `frontend/components/ui/map.tsx` |
| **ADR-004** | Redis for Caching & Rate Limiting | In-memory caching and distributed rate limiting. | Redis 7 with Asyncio client (`redis-py`). | Memcached, In-memory Python `dict`, KeyDB. | Separate memory infrastructure vs. sub-millisecond atomic ZSETs. | **Active & Valid** | `backend/app/cache/redis.py`, `backend/app/core/rate_limit.py` |
| **ADR-005** | Abstract AI Provider Protocol | LLM integration interface and provider independence. | Typed `AIProvider` Protocol (`base.py`). | LangChain, LangGraph, direct hardcoded Gemini calls. | Interface maintenance vs. zero vendor lock-in. | **Active & Valid** | `backend/app/ai/base.py`, `backend/app/ai/router.py` |
| **ADR-006** | Dual LLM Strategy (Ollama + Gemini) | Balance local privacy with cloud speed. | Ollama (Local) + Google Gemini (Cloud) with automatic failover. | Cloud-only (OpenAI), Local-only (Ollama). | Maintaining dual provider drivers vs. offline resilience. | **Active & Valid** | `backend/app/ai/ollama_provider.py`, `backend/app/ai/gemini_provider.py` |
| **ADR-007** | GeoJSON RFC 7946 Standard Compliance | Spatial serialization format between backend and frontend. | RFC 7946 GeoJSON FeatureCollections with `[lng, lat]` coordinates. | Custom coordinate dictionaries `{latitude, longitude}`. | GeoJSON wrapper verbosity vs. native MapLibre source ingestion. | **Active & Valid** | `backend/app/schemas/geo.py`, `frontend/lib/formatters/geojson.ts` |
| **ADR-008** | RFC 7807 Structured Errors & Request IDs | Error reporting and distributed request tracing. | Centralized RFC 7807 JSON handlers + `X-Request-ID` middleware. | Default FastAPI error formats, unstructured strings. | Explicit error schema maintenance vs. deterministic client error handling. | **Active & Valid** | `backend/app/core/exception_handlers.py`, `backend/app/core/middleware.py` |
| **ADR-009** | JWT Stateless Authentication & Ownership RBAC | User authentication and listing mutation authorization. | HMAC-SHA256 JWT tokens + Argon2id password hashing. | Stateful session cookies, OAuth2 external IdPs. | Token revocation complexity vs. horizontally scalable stateless auth. | **Active & Valid** | `backend/app/core/security.py`, `backend/app/core/dependencies.py` |
| **ADR-010** | PostGIS Bounding-Box & Viewport Search | Fast spatial filtering for interactive map pans. | PostGIS `&&` operator with `ST_MakeEnvelope` and GiST index. | Application-side coordinate filtering, polygon geo-hashing. | PostGIS index disk footprint vs. sub-20ms bounding box execution. | **Active & Valid** | `backend/app/repositories/geo_repository.py`, `backend/app/api/v1/search.py` |
| **ADR-011** | POI Category Aggregation & Location Intelligence | Surrounding urban amenities calculation. | PostGIS `ST_DWithin` grouped by categorical dimensions with Redis cache. | Live Google Places API calls, on-the-fly web scraping. | Fixed POI database maintenance vs. instantaneous zero-cost queries. | **Active & Valid** | `backend/app/services/poi_service.py`, `backend/app/api/v1/pois.py` |
| **ADR-012** | OSRM Road-Network Routing & Commute Policy | Commute duration calculation across travel modes. | OSRM HTTP Engine with Redis route caching. | Google Distance Matrix API, Straight-line Euclidean distance. | Road graph file management vs. zero per-query API fees. | **Active & Valid** | `backend/app/services/routing_service.py`, `backend/app/services/commute_service.py` |
| **ADR-013** | Deterministic Multi-Factor Ranking Engine | Property recommendation and sorting algorithm. | 6-dimension mathematical scoring formula with weight redistribution. | Machine Learning (LambdaMART), Random Forests. | Manual formula tuning vs. 100% explainability and zero cold-start delay. | **Active & Valid** | `backend/app/services/ranking_service.py`, `backend/app/api/v1/recommendations.py` |
| **ADR-014** | Sliding-Window Rate Limiter via Redis Sorted Sets | API protection against abusive request bursts. | Redis Sorted Sets (`ZSET`) sliding-window algorithm. | Fixed-window counter, Leaky bucket algorithm. | Small memory overhead per active IP vs. 100% accurate boundary protection. | **Active & Valid** | `backend/app/core/rate_limit.py` |
| **ADR-015** | Local Ollama Provider Implementation | Private offline LLM inference. | Native `httpx` async client to local Ollama daemon. | LangChain Ollama wrapper. | Managing local daemon process vs. direct control over timeouts and keep-alive. | **Active & Valid** | `backend/app/ai/ollama_provider.py` |
| **ADR-016** | Google Gemini Provider & Provider Routing Policy | Cloud LLM integration with complexity-based routing. | Official `google-genai` SDK + rule-based query complexity scorer. | Direct unstructured prompt calls, LiteLLM proxy. | Cloud API quota management vs. structured schema guarantees and high accuracy. | **Active & Valid** | `backend/app/ai/gemini_provider.py`, `backend/app/ai/routing_policy.py` |
| **ADR-017** | Deterministic Comparison & Grounded AI Explanations | Side-by-side property comparison architecture. | `ComparisonService` computes exact mathematical deltas; AI provides grounded narrative. | Full LLM-based comparison generation. | Strict Pydantic contract maintenance vs. 100% mathematical accuracy. | **Active & Valid** | `backend/app/services/comparison_service.py`, `backend/app/api/v1/ai.py` |
| **ADR-018** | Conversational Search State & Delta Patch Orchestration | Multi-turn conversational map refinement ("Ask the Map"). | Explicit `ConversationalSearchState` + delta `SearchStatePatch` reducer. | Full chat history re-prompting, LangGraph multi-agent loops. | Predefined state schema vs. zero hallucination, sub-1.5s latency, and testability. | **Active & Valid** | `backend/app/services/search_orchestrator.py`, `backend/app/utils/location_resolver.py` |


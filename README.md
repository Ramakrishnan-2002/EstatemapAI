# EstateMap AI 🗺️ 🏡
> **Location-first real estate discovery platform powered by FastAPI, PostGIS, Multi-Provider AI, Redis, and MapLibre GL.**

---

## 🚀 Overview
**EstateMap AI** is a location-first real estate discovery platform that replaces traditional keyword filters with spatial intelligence. In EstateMap AI, **the map is the primary product feature**, actively driving property exploration, viewport-based filtering, commute calculations, and multi-turn conversational search.

### Core Capabilities
1. **PostGIS Spatial Search Engine**: Viewport bounding-box filtering (`ST_MakeEnvelope`, GiST indexing) and geodesic radius searches (`ST_DWithin` on cast geography).
2. **Location Intelligence & POI Aggregation**: In-memory landmark resolution for metropolitan hubs (Bengaluru & Chennai) and surrounding points of interest (schools, hospitals, transit, tech parks).
3. **Commute & Travel Intelligence**: Real road-network driving, walking, and cycling durations via OSRM engine with spherical Haversine fallback.
4. **Deterministic 6-Factor Ranking Engine**: Multi-Criteria Decision Analysis (MCDA) mathematical scoring normalizing price, bedrooms, area, locality, POI proximity, and commute duration with dynamic missing-factor weight redistribution.
5. **Multi-Provider AI Orchestration**: "Ask the Map" conversational search powered by an abstract AI provider supporting local Ollama (`llama3.2:3b`) and cloud Google Gemini with structured Pydantic output validation and offline algorithmic fallbacks.
6. **Distributed Caching & Rate Limiting**: Redis cache-aside caching, non-blocking SCAN key invalidation, and sliding-window rate limiting via Redis Sorted Sets (`ZSET`) with graceful fail-open behavior.

---

## 🏗️ Architecture Overview
EstateMap AI employs a clean **Modular Monolith** architecture:

```
┌────────────────────────────────────────────────────────┐
│              Next.js 14 Web Application                │
│             (MapLibre GL Vector Engine)                │
└──────────────────────────┬─────────────────────────────┘
                           │ Asynchronous JSON / GeoJSON
                           ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend (ASGI)                 │
│  ├── Auth & JWT Security (Argon2id + PyJWT)            │
│  ├── Properties & Spatial Filters (PostGIS GiST)       │
│  ├── Commute & Routing Service (OSRM + Haversine)      │
│  ├── 6-Factor MCDA Ranking & Comparison Engine         │
│  ├── Search Orchestrator ("Ask the Map" State Reducer) │
│  ├── Redis Caching & Sliding-Window Rate Limiter       │
│  └── Multi-Provider AI Router (Ollama + Gemini)        │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────────┐ ┌───────────────────────┐
│ PostgreSQL 16 + PostGIS 3.4  │ │        Redis 7        │
│ (Relational Data + GiST MBR) │ │ (Cache-Aside + ZSET)  │
└──────────────────────────────┘ └───────────────────────┘
```

---

## 🛠️ Technology Stack
- **Backend**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), GeoAlchemy2, asyncpg, Redis (`redis.asyncio`), PyJWT, Argon2, httpx, structlog, pytest.
- **Geospatial Database**: PostgreSQL 16 with PostGIS 3.4 (`postgis/postgis:16-3.4`), GiST Spatial Indexing.
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, TanStack Query, MapLibre GL JS.
- **AI Engine**: Abstracted `AIProvider` base class with local Ollama (`llama3.2:3b`) and Google Gemini (`gemini-1.5-flash`), dynamic router, sequential failover, and Pydantic validation firewalls.
- **Infrastructure**: Docker & Docker Compose with native health probes.

---

## ⚡ Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Start Full Development Stack
```bash
docker compose up --build -d
```

### 3. Verify Health & Interactive Docs
- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Ask the Map Conversational Search**: [http://localhost:3000/search](http://localhost:3000/search)
- **Property Comparison View**: [http://localhost:3000/compare](http://localhost:3000/compare)

---

## 🧪 Testing & Verification

### Run Backend Regression Suite (288 Tests)
```bash
docker compose exec backend pytest
```

### Run Integration Tests Only (PostGIS, Redis, Auth, AI)
```bash
docker compose exec backend pytest tests/integration -v
```

### Run Unit Tests Only
```bash
docker compose exec backend pytest tests/unit -v
```

---

## 📚 Master Documentation & Backend Study System

Deep technical documentation, architecture deep dives, and system design case studies are organized under [`docs/`](docs/):

```text
README.md (Repository Overview)
    │
    ├── Architecture & Schema
    │     → docs/mastery/ARCHITECTURE.md
    │
    ├── Backend Systems Textbook
    │     → docs/mastery/BACKEND_MASTER_BOOK.md
    │
    ├── 48 Backend Engineering Stories
    │     → docs/mastery/BACKEND_ENGINEERING_STORIES.md
    │
    ├── System Design & Tradeoffs
    │     → docs/mastery/SYSTEM_DESIGN.md
    │
    ├── Architecture Decision Records (ADRs)
    │     → docs/ADRs/README.md
    │
    └── Backend Mastery Curriculum Portal
          → docs/mastery/README.md
```

| Document | Purpose |
| :--- | :--- |
| [`docs/mastery/README.md`](docs/mastery/README.md) | **Master Curriculum Portal**: 15-module backend progression, 3-pass study method. |
| [`docs/mastery/ARCHITECTURE.md`](docs/mastery/ARCHITECTURE.md) | **Backend Architecture**: Modular monolith layout, container topology, database schema, Mermaid diagrams. |
| [`docs/mastery/BACKEND_MASTER_BOOK.md`](docs/mastery/BACKEND_MASTER_BOOK.md) | **Systems Textbook**: FastAPI lifecycle, PostGIS spatial indexing, 6-Factor ranking math, Redis caching, AI failover. |
| [`docs/mastery/BACKEND_ENGINEERING_STORIES.md`](docs/mastery/BACKEND_ENGINEERING_STORIES.md) | **48 Engineering Stories**: 11-section format with topic-specific build snippets and failure modes. |
| [`docs/mastery/SYSTEM_DESIGN.md`](docs/mastery/SYSTEM_DESIGN.md) | **System Design Case Study**: 15 core architectural tradeoffs, technology necessity, evolutionary scaling ($10\text{k} \to 1\text{M}$ users). |
| [`docs/mastery/INTERVIEW_PREP.md`](docs/mastery/INTERVIEW_PREP.md) | **Interview Defense Guide**: Verbal pitches, Top 25 STAR Q&As, 10 Whiteboard blueprints, Mock interview transcript. |
| [`docs/mastery/ACTIVE_RECALL.md`](docs/mastery/ACTIVE_RECALL.md) | **Active Recall & Labs**: 50 active recall drills with answer keys, 8 debugging labs, 5 rebuild challenges. |
| [`docs/mastery/BACKEND_ROADMAP.md`](docs/mastery/BACKEND_ROADMAP.md) | **Study Roadmap**: 10 Cumulative Mastery Demonstrations (CMDs), 4-week structured schedule. |
| [`docs/mastery/BACKEND_DEPENDENCY_GRAPH.md`](docs/mastery/BACKEND_DEPENDENCY_GRAPH.md) | **Dependency Graph**: Visual Mermaid DAG mapping prerequisite relationships across all 48 stories. |
| [`docs/ADRs/README.md`](docs/ADRs/README.md) | **ADR Index**: 18 Architecture Decision Records documenting foundational technical choices. |

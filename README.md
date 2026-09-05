# EstateMap AI 🗺️ 🏡
> **Location-first real estate discovery powered by FastAPI, PostGIS, AI and mapcn.**

---

## 🚀 Overview
**EstateMap AI** is a location-first real estate discovery platform built using **FastAPI**, **PostgreSQL + PostGIS**, **Redis**, **Google Gemini**, **Ollama**, **Next.js**, and **mapcn** (backed by MapLibre GL). 

In EstateMap AI, **the map is the primary product feature**. The map actively drives property exploration, viewport-based filtering, draw-area polygon searches, commute calculations, and location intelligence.

---

## 🏗️ Architecture
EstateMap AI employs a clean **Modular Monolith** architecture:

```
Next.js (mapcn + MapLibre)
         │
         ▼
FastAPI Backend (Async)
   ├── Auth & Users
   ├── Properties & Search
   ├── GeoService (PostGIS Spatial Queries)
   ├── POI & Location Intelligence
   ├── Commute & Travel Intelligence (OSRM)
   ├── Ranking Engine (Deterministic Multi-factor)
   ├── Comparison Service (Pairwise Facts & Delta Math)
   ├── Search Orchestrator (Ask the Map Conversational Engine)
   ├── Redis Cache Layer (Sliding Rate Limiter)
   └── AI Router (Ollama llama3.2:3b / Gemini API)
         │
         ▼
PostgreSQL 16 + PostGIS 3.4 (GiST Spatial Indexes)
```

---

## 🛠️ Technology Stack
- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), GeoAlchemy2, asyncpg, Redis, PyJWT, Argon2, structlog, pytest.
- **Geospatial & Database**: PostgreSQL 16, PostGIS 3.4 (`postgis/postgis:16-3.4`), GiST Spatial Indexing.
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui patterns, TanStack Query, mapcn, MapLibre GL.
- **AI Engine**: Abstracted AIProvider with local Ollama (`llama3.2:3b`) and Google Gemini (`gemini-1.5-flash`), deterministic auto-routing, failover budget, Ask the Map multi-turn query refinement, and grounded fact extraction.
- **Infrastructure**: Docker & Docker Compose with native health checks.

---

## ⚡ Quickstart

### 1. Copy Environment Variables
```bash
cp .env.example .env
```

### 2. Start PostgreSQL/PostGIS and Redis
```bash
docker compose up -d postgres-postgis redis
```

### 3. Run Full Development Stack
```bash
docker compose up --build
```

- **Interactive API Docs (Swagger UI)**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **API Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- **Frontend Application**: [http://localhost:3000](http://localhost:3000)
- **Ask the Map Search View**: [http://localhost:3000/search](http://localhost:3000/search)
- **Property Comparison View**: [http://localhost:3000/compare](http://localhost:3000/compare)

---

## 🧪 Testing

### Backend Unit & Integration Tests
```bash
cd backend
pytest
```

### Frontend Unit Tests
```bash
cd frontend
npm run test:unit
```

---

## 📚 Documentation
Comprehensive design documents and Architecture Decision Records (ADRs) are available in `/docs`:
- [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/SYSTEM_DESIGN.md`](docs/SYSTEM_DESIGN.md)
- [`docs/DATABASE_DESIGN.md`](docs/DATABASE_DESIGN.md)
- [`docs/MAP_ARCHITECTURE.md`](docs/MAP_ARCHITECTURE.md)
- [`docs/AI_PROVIDER_ARCHITECTURE.md`](docs/AI_PROVIDER_ARCHITECTURE.md)
- [`docs/PROPERTY_COMPARISON_ARCHITECTURE.md`](docs/PROPERTY_COMPARISON_ARCHITECTURE.md)
- [`docs/ASK_THE_MAP_ARCHITECTURE.md`](docs/ASK_THE_MAP_ARCHITECTURE.md)
- [`docs/CACHING_AND_PERFORMANCE.md`](docs/CACHING_AND_PERFORMANCE.md)
- [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
- [`docs/ADR/`](docs/ADR/) (ADR-001 through ADR-018)

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

## 📚 Documentation & Technical Mastery Curriculum
Comprehensive engineering documentation, system design deep dives, and interview defense resources are available in [`docs/mastery/`](docs/mastery/):
- 📘 [**EstateMap Master Book**](docs/mastery/ESTATEMAP_MASTER_BOOK.md): The definitive 32-chapter technical textbook for this codebase.
- 🎓 [**100 Connected Engineering Stories**](docs/mastery/ENGINEERING_STORIES.md): Step-by-step curriculum with build-it-yourself exercises.
- 🏛️ [**System Design Interview Guide**](docs/mastery/SYSTEM_DESIGN_INTERVIEW.md): Complete 45-minute whiteboard defense guide.
- 🎯 [**250+ Active Recall Questions**](docs/mastery/ACTIVE_RECALL.md) & [**Answer Key**](docs/mastery/ACTIVE_RECALL_ANSWERS.md).
- 💬 [**200+ Interview Questions & Answers**](docs/mastery/INTERVIEW_QUESTIONS.md) with 3-tier depths ([**Answers**](docs/mastery/INTERVIEW_ANSWERS.md)).
- 🗺️ [**Know Your Codebase Map**](docs/mastery/KNOW_YOUR_CODE.md) & [**End-to-End Request Traces**](docs/mastery/REQUEST_TRACES.md).
- ⚖️ [**Tradeoff Matrix**](docs/mastery/TRADEOFF_MATRIX.md) & [**Technology Necessity Matrix**](docs/mastery/TECHNOLOGY_NECESSITY_MATRIX.md).
- ⚠️ [**Failure Modes & Resilience Matrix**](docs/mastery/FAILURE_MODES.md) & [**Interview Red Flags**](docs/mastery/INTERVIEW_RED_FLAGS.md).
- 📑 [**ADR Master Index**](docs/mastery/ADR_MASTER_INDEX.md) (Auditing all 18 Architecture Decision Records).
- 🧭 [**Master Curriculum Navigation**](docs/mastery/README.md).

Additional legacy design specifications remain preserved in [`docs/`](docs/).

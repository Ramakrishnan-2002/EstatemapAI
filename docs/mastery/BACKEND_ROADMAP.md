# EstateMap AI — Backend Learning Roadmap & Verification Guide
> **Structured Study Progression for Python Backend Engineers & System Designers**

## 1. The 15-Module Backend Progression Path
```text
Python & FastAPI Foundations (Stories 01-04)
        ↓
REST API Design & Validation (Stories 05-07)
        ↓
PostgreSQL & SQLAlchemy 2.0 Async (Stories 08-12)
        ↓
Authentication & Security (Stories 13-15)
        ↓
PostGIS Spatial Search Engine (Stories 16-21)
        ↓
Location Intelligence & Routing (Stories 22-24)
        ↓
Deterministic Ranking & Business Logic (Stories 25-28)
        ↓
Redis In-Memory Caching (Stories 29-31)
        ↓
Rate Limiting & Distributed Resilience (Stories 32-34)
        ↓
Multi-Provider AI Architecture (Stories 35-38)
        ↓
Ask-the-Map Conversational Orchestrator (Stories 39-41)
        ↓
Backend ↔ Frontend API Integration Contract (Story 42)
        ↓
Backend Testing & Debugging (Stories 43-44)
        ↓
Docker for Backend Developers (Story 45)
        ↓
EstateMap System Design & Architectural Defense (Stories 46-48)
```

---

## 2. The 10 Cumulative Mastery Demonstrations (CMDs)

| CMD | Milestone | Core Focus | Verification Command |
| :---: | :--- | :--- | :--- |
| **CMD 01** | Modular Monolith & Lifespan | FastAPI, Lifespan, Logging | `docker compose exec backend pytest tests/unit/test_health.py` |
| **CMD 02** | Asyncpg Relational Database | SQLAlchemy 2.0, Asyncpg, Alembic | `docker compose exec backend pytest tests/integration/test_database.py` |
| **CMD 03** | PostGIS Geodesic Spatial Search | GiST Index, ST_DWithin, ST_MakeEnvelope | `docker compose exec backend pytest tests/integration/test_spatial_search.py` |
| **CMD 04** | Stateless JWT Authentication | Argon2id, JWT, FastAPI Depends | `docker compose exec backend pytest tests/integration/test_auth.py` |
| **CMD 05** | Commute Routing & Matrix | OSRM Engine, Haversine Fallback | `docker compose exec backend pytest tests/integration/test_commute.py` |
| **CMD 06** | 6-Factor Deterministic Ranking | MCDA, Weight Redistribution | `docker compose exec backend pytest tests/integration/test_ranking.py` |
| **CMD 07** | Redis Caching & Invalidation | Cache-Aside, SHA-256 Key Hashing | `docker compose exec backend pytest tests/unit/test_cache_service.py` |
| **CMD 08** | Pipelined Sliding Window Rate Limiter | Redis ZSET, Pipelined Eval | `docker compose exec backend pytest tests/integration/test_rate_limiting.py` |
| **CMD 09** | Multi-Provider AI & Orchestration | Ollama + Gemini, State Reducer | `docker compose exec backend pytest tests/integration/test_ai_endpoints.py` |
| **CMD 10** | End-to-End Backend Verification | Complete 288-Test Regression Suite | `docker compose exec backend pytest` |

---

## 3. 4-Week Structured Study Plan
- **Week 1: Foundations, Database & Spatial Indexing** (Modules 1–5: Stories 01–21)
- **Week 2: Location, Routing, Ranking & Caching** (Modules 6–8: Stories 22–31)
- **Week 3: Rate Limiting, Multi-Provider AI & Conversational Search** (Modules 9–11: Stories 32–41)
- **Week 4: API Contracts, Testing, Docker & System Design Whiteboarding** (Modules 12–15: Stories 42–48)

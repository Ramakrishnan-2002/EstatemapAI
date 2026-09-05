# EstateMap AI — Milestone-Based Learning Roadmap

This document outlines the step-by-step learning progression to master EstateMap AI for backend engineering and system design interviews.

---

## Milestone 1: Foundations & API Lifecycle (Level: Beginner)
* **Goal**: Understand how an HTTP request enters FastAPI, passes through middleware, executes async dependency injection, and returns a validated Pydantic response.
* **Key Tasks**:
  - Trace request lifecycle through `backend/app/main.py` and `backend/app/core/middleware.py`.
  - Explain ASGI vs WSGI and why async coroutines prevent thread blocking on I/O.
  - Implement a basic CRUD endpoint using Pydantic request/response models.
* **Success Criteria**: Can explain the role of `lifespan`, `get_db()`, and `X-Request-ID` without notes.

---

## Milestone 2: Relational Data & Spatial Indexing (Level: Intermediate)
* **Goal**: Master PostgreSQL relational schemas, PostGIS geometry types, and spatial indexing.
* **Key Tasks**:
  - Study `backend/app/models/property.py` and `backend/app/repositories/geo_repository.py`.
  - Explain why `geometry(Point, 4326)` stores coordinates as `[lng, lat]` and how GiST R-Tree indexing accelerates bounding-box queries (`&& ST_MakeEnvelope`).
  - Explain the difference between `geometry` planar math and `geography` spherical math in `ST_DWithin`.
* **Success Criteria**: Can write a raw PostGIS bounding-box and radius SQL query on a whiteboard from memory.

---

## Milestone 3: In-Memory Caching & Rate Limiting (Level: Advanced)
* **Goal**: Master Redis caching patterns and sliding-window rate limiting algorithms.
* **Key Tasks**:
  - Study `backend/app/cache/cache_service.py` and `backend/app/core/rate_limit.py`.
  - Trace the exact Redis Sorted Set (`ZSET`) commands used in the sliding-window log limiter (`ZREMRANGEBYSCORE`, `ZCARD`, `ZADD`, `EXPIRE`).
  - Explain why sliding windows prevent the 2x burst vulnerability of fixed-window counters.
  - Explain fail-open vs. fail-closed semantics during Redis outages.
* **Success Criteria**: Can implement an atomic sliding-window rate limiter in Python with Redis from scratch.

---

## Milestone 4: Commute Routing & Deterministic Ranking (Level: Advanced)
* **Goal**: Master road-network graph calculations and mathematical multi-factor scoring.
* **Key Tasks**:
  - Study `backend/app/services/routing_service.py` and `backend/app/services/ranking_service.py`.
  - Explain why PostGIS cannot calculate road-network driving times and why OSRM is used.
  - Walk through all 6 mathematical factor scoring equations.
  - Explain dynamic missing-factor weight redistribution when optional inputs (like commute hub) are omitted.
* **Success Criteria**: Given sample property coordinates and user preferences, can manually compute the final ranking score step-by-step on a whiteboard.

---

## Milestone 5: Multi-Provider AI & Conversational Search (Level: Master)
* **Goal**: Master resilient LLM provider orchestration and state machine thinking.
* **Key Tasks**:
  - Study `backend/app/ai/router.py`, `backend/app/ai/routing_policy.py`, and `backend/app/services/search_orchestrator.py`.
  - Explain why AI is non-authoritative and how prompt injection is defended against.
  - Trace multi-turn conversational delta patches (`SET`, `CLEAR`, `APPEND`, `REMOVE`, `RESET`) in `apply_patch()`.
  - Explain global request deadlines and graceful failover from Gemini -> Ollama -> Deterministic Fallback.
* **Success Criteria**: Can explain how "Ask the Map" refines searches without suffering from LLM hallucination or unbounded execution latency.

---

## Milestone 6: System Design Interview Ready (Level: Staff / Senior)
* **Goal**: Whiteboard the entire EstateMap AI system architecture, defend all design tradeoffs, and answer deep-dive failure mode and scaling questions.
* **Success Criteria**: Can execute a 45-minute mock system design interview following [`SYSTEM_DESIGN_INTERVIEW.md`](file:///d:/FastAPI/EstateMap/docs/mastery/SYSTEM_DESIGN_INTERVIEW.md) flawlessly.

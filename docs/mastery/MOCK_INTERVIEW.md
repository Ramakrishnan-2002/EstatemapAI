# EstateMap AI — Senior Backend & System Design Mock Interview

This document simulates an interactive technical interview where the interviewer progressively drills deeper into architectural choices, failure modes, algorithms, and concurrency.

---

## Round 1: High-Level Architecture & Persistence

**Interviewer**: *"I see EstateMap AI is a real estate discovery platform. Walk me through the high-level architecture."*  
**Candidate**: *"EstateMap AI is built as an asynchronous modular monolith on FastAPI, backed by PostgreSQL 16 with PostGIS 3.4 for spatial indexing, Redis 7 for in-memory route caching and sliding-window rate limiting, and an abstract AI multi-provider router supporting local Ollama and Google Gemini. The frontend is built on Next.js 14 App Router using MapLibre GL for WebGL-accelerated 60fps vector map rendering."*

**Interviewer**: *"Why did you use PostGIS instead of just storing latitude and longitude as floats in PostgreSQL and calculating distances in Python?"*  
**Candidate**: *"Calculating distance in Python requires pulling thousands of listing coordinates across the network into memory, resulting in $\mathcal{O}(N)$ CPU time and network transfer. PostGIS stores coordinates as `geometry(Point, 4326)` with an R-Tree GiST spatial index. PostGIS evaluates bounding box intersections (`&& ST_MakeEnvelope`) and spherical radius filters directly inside the database C-kernel in $\mathcal{O}(\log N)$ time, returning only the matched subset to the application in $<15\text{ms}$."*

**Interviewer**: *"What coordinate order does PostGIS expect, and what happens if you invert them?"*  
**Candidate**: *"PostGIS and GeoJSON strictly adhere to `POINT(longitude latitude)`—X then Y. If you invert them to `POINT(lat lng)`, coordinates project to Antarctica or the Indian Ocean, causing spatial queries to return zero results."*

---

## Round 2: In-Memory Caching & Rate Limiting

**Interviewer**: *"Why did you introduce Redis into this architecture?"*  
**Candidate**: *"Redis serves two distinct roles: (1) Cache-aside for expensive OSRM road-network route calculations and POI location intelligence aggregations, and (2) An atomic sliding-window rate limiter to protect our API from automated scrapers and brute-force attacks."*

**Interviewer**: *"Why not use a simple fixed-window counter in Redis? It's much simpler."*  
**Candidate**: *"Fixed-window counters suffer from a severe 2x boundary burst vulnerability. If your limit is 5 requests per minute, a client can send 5 requests at 00:59 and 5 requests at 01:00. Both are permitted by fixed windows, but the server just received 10 requests in 2 seconds. Our sliding-window log uses Redis Sorted Sets (`ZSET`), storing timestamps as scores. We atomically prune timestamps older than `now - 60s` via `ZREMRANGEBYSCORE`, count remaining items with `ZCARD`, and reject the 6th request, guaranteeing 100% boundary accuracy."*

**Interviewer**: *"What happens if the Redis container crashes in production? Does the entire platform go down?"*  
**Candidate**: *"No. We implemented a fail-open degradation policy in `backend/app/cache/cache_service.py` and `backend/app/core/rate_limit.py`. If Redis throws a connection error, the backend catches it, logs a warning with the request ID, and queries PostgreSQL and OSRM directly. For rate limiting, search endpoints fail open to maintain platform availability, while sensitive auth routes fail closed."*

---

## Round 3: Algorithms & AI Multi-Provider Router

**Interviewer**: *"Why did you use deterministic mathematical equations for property ranking instead of a machine learning model?"*  
**Candidate**: *"Two reasons: (1) Explainability: Real estate buyers need clear reasons why listing A outranks listing B (e.g., 'Ranked higher due to 12-min commute vs 28-min commute'). (2) Cold-Start: A new platform has zero historical user click logs. ML ranking models cannot be trained without interaction datasets. Our 6-factor deterministic model calculates normalized scores across Price, Bedrooms, Living Area, Locality, POI proximity, and OSRM Commute, with dynamic weight redistribution when optional criteria like commute destinations are omitted."*

**Interviewer**: *"Tell me about 'Ask the Map'. How do you prevent the LLM from hallucinating non-existent properties or altering database records?"*  
**Candidate**: *"The AI is intentionally non-authoritative. It has zero direct database credentials, no SQL execution privileges, and no shell access. It operates as an intent extractor within a state machine. When a user says '3 BHK in Adyar under 1.5 Cr', the LLM emits a Pydantic-validated `SearchStatePatch`. Our deterministic state reducer `apply_patch()` updates the canonical `ConversationalSearchState`, and the application executes a standard PostGIS query with the updated parameters."*

**Interviewer**: *"What if Google Gemini's API is down or throttles you with HTTP 429?"*  
**Candidate**: *"Our `AIProviderRouter` enforces a 12-second global request deadline. If Gemini fails or hits quota, the router immediately fails over to local Ollama. If Ollama is also offline, our `DeterministicFallbackProvider` uses rule-based regex parsing to generate a valid patch, ensuring zero user-facing 500 errors."*

**Interviewer**: *"Excellent. That demonstrates complete end-to-end technical mastery of your system."*

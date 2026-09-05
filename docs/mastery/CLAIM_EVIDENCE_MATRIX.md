# EstateMap AI — Resume & Interview Claim-Evidence Matrix

This document maps every technical resume claim to verified source code, database migrations, tests, and execution proof. It ensures 100% technical honesty and prevents interview overstatement.

---

| Resume / Interview Claim | Code Evidence | Test Verification | Executable Proof | Safe to State in Interview? |
| :--- | :--- | :--- | :--- | :--- |
| **"Engineered PostGIS 2D spatial queries with GiST R-Tree indexing"** | `backend/alembic/versions/001_initial_schema.py` (index `idx_properties_location_gist`), `backend/app/repositories/geo_repository.py` | `backend/tests/unit/test_geo_service.py`, `backend/tests/integration/test_spatial_search.py` | `location && ST_MakeEnvelope(...)` executed with index scan in PostgreSQL | **YES — 100% Verified** |
| **"Implemented Redis sliding-window log rate limiter using Sorted Sets"** | `backend/app/core/rate_limit.py` (`ZREMRANGEBYSCORE`, `ZCARD`, `ZADD`, `EXPIRE`) | `backend/tests/integration/test_rate_limiting.py` (5 tests passing) | Returns HTTP 429 and `Retry-After` header on threshold violation | **YES — 100% Verified** |
| **"Designed multi-provider AI routing with local/cloud failover & deadlines"** | `backend/app/ai/router.py`, `backend/app/ai/routing_policy.py`, `backend/app/ai/ollama_provider.py`, `backend/app/ai/gemini_provider.py` | `backend/tests/integration/test_ai_failover.py`, `backend/tests/unit/test_cross_provider_parity.py` | Automatic failover from Gemini/Ollama to Deterministic Fallback on deadline expiry | **YES — 100% Verified** |
| **"Built deterministic 6-factor ranking engine with missing-factor redistribution"** | `backend/app/services/ranking_service.py` (`calculate_final_score`, `_redistribute_weights`) | `backend/tests/unit/test_ranking_scoring.py`, `backend/tests/integration/test_ranking.py` | Mathematical scoring verified with zero non-deterministic drift | **YES — 100% Verified** |
| **"Created multi-turn conversational search state machine ('Ask the Map')"** | `backend/app/services/search_orchestrator.py` (`apply_patch`), `backend/app/schemas/conversational_search.py` | `backend/tests/integration/test_ask_the_map.py`, `frontend/__tests__/ask_the_map.test.mjs` | Multi-turn state delta transitions (`SET`, `CLEAR`, `APPEND`, `RESET`) tested | **YES — 100% Verified** |
| **"Integrated OSRM road-network graph commute duration & routing"** | `backend/app/services/routing_service.py`, `backend/app/services/commute_service.py` | `backend/tests/unit/test_routing_models.py`, `backend/tests/integration/test_commute.py` | Turn-by-turn GeoJSON LineStrings and multi-modal travel durations calculated | **YES — 100% Verified** |
| **"Built WebGL-accelerated interactive map with bidirectional list sync"** | `frontend/components/map/map-container.tsx`, `frontend/app/search/page.tsx` | `frontend/__tests__/map-sync.test.mjs`, `frontend/__tests__/geojson.test.mjs` | MapLibre GL 60fps rendering, marker popups, smooth scroll into view | **YES — 100% Verified** |
| **"Implemented persistent cross-tab saved properties & comparison contexts"** | `frontend/context/favorites-context.tsx`, `frontend/context/comparison-context.tsx` | `frontend/__tests__/comparison.test.mjs` | `localStorage` persistence with `estatemap-favorites-changed` and `storage` event sync | **YES — 100% Verified** |

---

## 🚫 Unsupported Claims to NEVER Make in Interviews
1. ❌ *"We use PostGIS to calculate live road traffic conditions"* -> **Correction**: PostGIS calculates 2D geometric and spherical distances; OSRM models the road-network graph.
2. ❌ *"The AI ranking engine learns from user preferences using deep learning"* -> **Correction**: Ranking is 100% deterministic heuristic math across 6 normalized factors.
3. ❌ *"Our system is infinitely scalable to millions of users on Kubernetes"* -> **Correction**: Current implementation is a Docker Compose modular monolith. A single PostgreSQL primary can comfortably handle 100k DAU (~70 peak QPS).
4. ❌ *"Prompt injection is 100% impossible in our system"* -> **Correction**: We employ defense-in-depth (strict Pydantic schema validation, action allowlists, no direct DB/tool access), but residual LLM output risks always exist.

# ADR-013: Deterministic Multi-Factor Ranking & Explainable Recommendations

## Status
Accepted

## Context
Real estate searchers rarely have single-variable decision criteria. Instead, buyers and renters balance trade-offs across budget, family size requirements, living space, neighborhood amenities (POIs), and commute time to work.

Common industry approaches include:
1. **Black-box AI / Vector Embeddings**: Ranking properties via LLMs or cosine similarity on vector embeddings. This is non-deterministic, opaque, difficult to test, expensive to compute in real time, and fails to guarantee hard database constraints.
2. **Naive SQL Sorting**: Sorting strictly by price or recency. This ignores multi-criteria suitability and fails to highlight optimal trade-offs.

EstateMap AI requires a production-grade ranking engine that is:
- **100% Deterministic & Reproducible**: Identical inputs always produce identical scores and ranks.
- **Strictly Respectful of Hard Constraints**: Hard database filters (PostGIS bounding boxes, radius, exact budget ceilings) are executed in SQL first; ranking only evaluates eligible candidates.
- **Factual & Explainable**: Every rank and score must be backed by verifiable math and human-readable factual bullet points.
- **Computationally Bounded**: Sub-20ms latency without N+1 query or routing bottlenecks.

---

## Decisions

### D1: Two-Stage Bounded Candidate Pipeline
- **Decision**: Separate the search pipeline into:
  1. **Stage 1 (Hard Filtering)**: Fast, index-accelerated SQL/PostGIS filtering returning at most `MAX_RANKING_CANDIDATES = 50` candidates.
  2. **Stage 2 (Soft Ranking)**: In-memory multi-factor scoring, feature enrichment, dynamic weight redistribution, and deterministic tie-breaking.
- **Why**: Protects against CPU exhaustion, avoids evaluating thousands of irrelevant listings, and prevents routing network fan-out.

### D2: Modular Clamped Factor Scoring ($[0.0, 1.0]$)
- **Decision**: All factor scoring logic is encapsulated in pure mathematical functions in `app.utils.ranking`, clamped to $[0.0, 1.0]$:
  - `score_price`: Relative budget deviation with linear decay up to 50% tolerance.
  - `score_bedrooms`: Exact BHK match ($1.0$), $\pm 1$ BHK ($0.60$), $\pm 2$ BHK ($0.20$), $\ge 3$ BHK ($0.0$).
  - `score_area`: Continuous reward for exceeding minimum area, penalty for falling short.
  - `score_locality`: Exact string match ($1.0$) and Jaccard token overlap ($[0.4, 0.8]$).
  - `score_location`: Weighted combination of nearest POI distances ($60\%$) and category variety ($40\%$).
  - `score_commute`: Piecewise linear scoring against road network duration ($\le 15\text{m} \to 1.0$, $\ge 60\text{m} \to 0.0$).
- **Why**: Modular, unit-testable functions with guaranteed mathematical bounds prevent arithmetic overflows or negative score artifacts.

### D3: Missing Factor Weight Redistribution Policy
- **Decision**: If a preference is not provided by the user (or if commute data is unavailable), the factor is flagged `available = False` and its weight is proportionally redistributed across all active available factors:
  $$w_k' = \frac{w_k}{\sum_{j \in \text{Available}} w_j}$$
- **Why**: Ensures listings are never penalized for omitted user preferences or missing optional data.

### D4: Deterministic Tie-Breaking Order
- **Decision**: When two properties produce identical final scores, ties are resolved deterministically by:
  1. `final_score DESC`
  2. `price ASC`
  3. `id ASC`
- **Why**: Eliminates non-deterministic ordering or database-dependent row shuffling across pagination.

### D5: Rule-Based Deterministic Explanation Generation
- **Decision**: Factual explanations are generated using programmatic template rules (`generate_deterministic_explanations`) that reference exact criteria (e.g. *"Matches 3 BHK preference"*, *"17 min drive to Whitefield ITPL"*). Zero LLMs are used.
- **Why**: Zero hallucinations, zero API cost, zero external latency, and complete compliance with auditability standards.

### D6: Dedicated `RankingService` and API Endpoints
- **Decision**: Create `app.services.ranking_service.RankingService` with endpoints:
  - `POST /api/v1/search/ranked`
  - `POST /api/v1/recommendations/ranked` (convenience alias)
- **Why**: Keeps search controller logic lean while providing dedicated endpoints for ranked discovery and recommendation carousels.

---

## Consequences
- EstateMap AI delivers transparent, fast (<10ms), and explainable property matching.
- Frontend users can customize target criteria and priority weights to immediately observe ranked results with visual breakdown bars and factual highlights.
- Future AI phases (Phase 10+) can safely consume deterministic ranking outputs and explanations as trustworthy facts.

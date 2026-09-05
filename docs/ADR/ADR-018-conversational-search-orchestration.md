# ADR-018: Conversational Search Orchestration & Multi-Turn Query Refinement

## Status
Accepted

## Context
In Phase 11, EstateMap introduced natural language search parsing to translate a single text query into structured `PropertySearchIntent` parameters. In Phase 13, deterministic multi-property comparison and grounded narratives were implemented.

However, real-world map exploration is inherently multi-turn and iterative:
1. A user starts with broad criteria: *"Find apartments in Indiranagar under 80 Lakh"*.
2. The user refines criteria based on visual map feedback: *"Add nearby transit and hospitals"*.
3. The user alters commute preferences: *"Must be within 20 mins of EcoSpace"*.
4. The user requests comparison: *"Compare the top 2 results"*.
5. The user clears specific filters: *"Remove the price constraint"*.

We needed an architecture that supports seamless multi-turn conversational exploration without compromising system determinism, data privacy, or backend security.

## Decision
We chose a **Patch-Based Deterministic Search Orchestration Architecture**:

1. **Strict Separation of Concerns ("LLM Interprets, Backend Decides, DB Owns Facts")**:
   - The LLM is restricted to a structured JSON-only extractor emitting a validated `SearchStatePatch`.
   - The LLM cannot generate SQL, execute code, call external tools autonomously, or hallucinate coordinates.
2. **Canonical Search State & State Transition Reducer**:
   - Both manual UI controls (filter bars, range sliders, POI toggles, ranking presets) and conversational inputs share the single canonical `ConversationalSearchState`.
   - Patch application uses deterministic semantics: explicit `SET`, `APPEND`, `REMOVE`, `CLEAR`, and `RESET_SEARCH`.
   - Preserved filters are explicitly tracked and returned to the UI as feedback badges.
3. **Deterministic Location Resolution (`LocationResolver`)**:
   - Geographic coordinates are resolved on the backend using an exact/alias landmark database for Bengaluru.
   - Ambiguous or unrecognized destinations trigger a graceful clarification prompt rather than coordinate guessing.
4. **Action Delegation**:
   - Actions (`SEARCH`, `REFINE`, `CLEAR_FILTER`, `RESET_SEARCH`, `RANK`, `COMPARE`, `EXPLAIN`) are mapped directly to EstateMap's existing tested services (`SearchOrchestrator`, `ComparisonService`, `RankingService`, `CommuteService`, `GeoService`).
5. **Security & Privacy Boundary**:
   - Structured privacy allowlists prevent PII or database internals from being sent to external LLMs.
   - Global time budgets (`AI_TOTAL_TIMEOUT_SECONDS = 35.0s`) and multi-provider fallbacks ensure zero-downtime resilience.

## Consequences

### Positive
- **Deterministic & Verifiable**: All property filtering, ranking, distance, and commute metrics are computed in Python/PostGIS, preventing model-generated metric inaccuracies.
- **Bi-directional UI Synchronization**: Users can freely interleave typing conversational prompts and clicking manual filter buttons with seamless state convergence.
- **Fast & Scalable**: Eliminates heavy autonomous agent loops and vector database overhead.
- **Authoritative Location Grounding**: Every commute destination is mapped to verified coordinates in the curated location registry or safely flagged for clarification.

### Negative
- New landmarks and tech parks must be registered in the `LocationResolver` database or resolved via geocoding providers.

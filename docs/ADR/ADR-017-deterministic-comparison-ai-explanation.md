# ADR-017: Deterministic Multi-Property Comparison with Grounded AI Explanation

## Status
Accepted

## Context
In property discovery, users frequently compare 2 to 3 candidate properties across competing trade-off dimensions (e.g. price vs. living space vs. commute time vs. neighborhood amenities). 

Modern LLMs, when prompted with raw property descriptions to "compare and recommend", suffer from critical production failure modes:
1. **Arithmetic & Unit Hallucinations**: LLMs miscalculate price differences (e.g., subtracting Lakhs from Crores), compute incorrect price per square foot values, and hallucinate commute time advantages.
2. **Subjective & Unbounded Recommendations**: LLMs declare arbitrary "winners" based on unverified premises, predict future capital appreciation, or infer school ratings without data backing.
3. **Availability & Latency Coupling**: If comparison relies solely on an LLM, downstream comparisons fail whenever the LLM is slow, rate-limited, or offline.
4. **Data Privacy Leakage**: Sending database IDs, user IDs, owner info, or internal metadata to third-party hosted LLMs violates privacy boundaries.

EstateMap requires an enterprise-grade comparison architecture where:
- All factual differences, mathematical metrics, and ranking factor contribution margins are computed deterministically by PostgreSQL/PostGIS and Python.
- AI is strictly constrained to *explaining* precomputed facts in natural language, never *computing* facts.
- The comparison system functions completely when AI is offline.

## Decision
1. **Dedicated Deterministic Domain Service (`ComparisonService`)**:
   - Implemented `backend/app/services/comparison_service.py` to calculate exact pairwise price differences, area deltas, price/sqft, POI distance differences, and commute deltas in Python. Zero LLM arithmetic is permitted.
   - Reuses existing `PropertyRepository`, `POIService`, `CommuteService`, and Phase 9 `RankingService`.
   - Computes mathematical ranking contribution margins ($\Delta C_f$) between properties to explain *why* one listing ranked higher without LLM guesswork.
   - Generates precomputed deterministic summary statements (e.g., `"Property A is ₹1.17 Cr cheaper than Property B."`).

2. **Dual-Endpoint Architecture**:
   - `POST /api/v1/properties/compare`: Returns authoritative, deterministic `ComparisonResult` with zero LLM dependency.
   - `POST /api/v1/ai/properties/compare`: Runs `ComparisonService`, sanitizes context, and invokes `AIService.explain_comparison` for natural language trade-off synthesis, falling back to precomputed summary statements if AI is unavailable.

3. **Strict Bounded Limits & Input Validation**:
   - Constrained to 2 to 3 properties ($2 \le N \le 3$). Requests with $<2$, $>3$, or duplicate IDs are rejected with HTTP 422.

4. **Privacy Allowlisting for Hosted Providers**:
   - Context sent to hosted AI providers strictly replaces database IDs with generic labels (`"Property A"`, `"Property B"`, `"Property C"`), excluding all owner IDs, user IDs, emails, password hashes, and database primary keys.

5. **Multi-Provider AI Routing & Bounded Time Budget**:
   - Extended `AIProvider` protocol with `explain_comparison`.
   - `AIRoutingPolicy.profile_comparison_context` routes 2 standard properties to Ollama and 3 properties / rich commute contexts to Gemini Flash.
   - Governed by `AI_TOTAL_TIMEOUT_SECONDS` (35.0s) deadline budget and single-attempt failover.

## Alternatives Considered

1. **LLM Computes All Comparisons (Full AI Dependency)**:
   - *Description*: Send raw property listings to the LLM and ask it to compute price differences, identify the best commute, and recommend the best property.
   - *Reason for Rejection*: Unacceptable arithmetic failure rates on INR denominations (Lakhs vs Crores), inability to perform geometric routing, arbitrary subjective scoring, high latency, and complete feature failure when the LLM is unavailable.

2. **Deterministic Comparison Only (Zero AI)**:
   - *Description*: Provide only the structured data table and rule-based bullet points.
   - *Reason for Rejection*: While robust, users lose the benefit of synthesized natural-language narratives that highlight nuanced trade-offs across multiple competing dimensions.

3. **Hybrid Architecture: Deterministic Calculation + Grounded AI Explanation (Accepted)**:
   - *Description*: Python and PostGIS compute 100% of facts, deltas, and ranking margins. The LLM is used solely to generate a readable summary from the verified facts, with instant fallback to deterministic rules if AI fails.

## Consequences

### Positive
- **Reproducible Arithmetic**: All numeric differences, per-sqft metrics, and rankings are calculated deterministically in Python before AI prompt generation.
- **Resilience**: If AI providers fail or are disabled, property comparison remains fully usable via `deterministic_summary` and structured matrix facts.
- **Privacy Compliance**: No internal IDs, owner identifiers, coordinates, or PII ever leave the backend to hosted AI providers.
- **Transparent Rankings**: Factor contribution deltas ($\Delta C_f = C_f(A) - C_f(B)$) explain ranking differences mathematically.

### Trade-offs & Limitations
- Comparing 3 properties with commute evaluation requires up to 3 routing calculations (mitigated by Redis route caching).
- Context allowlisting requires strict schema maintenance between backend models and AI context builders.
- While factual context is verified, generated natural-language text remains non-authoritative.

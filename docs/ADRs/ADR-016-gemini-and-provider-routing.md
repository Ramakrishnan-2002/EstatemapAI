# ADR-016: Multi-Provider AI Architecture with Deterministic Routing and Fallback

## Status
Accepted

## Context
In Phase 11, EstateMap AI introduced local AI capabilities via Ollama (`llama3.2:3b`) for structured search intent parsing and grounded property explanations. While local inference guarantees privacy and zero per-token cloud costs, local models can exhibit latency variance on constrained host hardware and lower precision on complex, multi-constraint queries (e.g., matching multiple amenities, budget constraints, and commute targets simultaneously).

EstateMap requires an enterprise-grade AI architecture capable of:
1. Routing complex or high-nuance queries to high-capability hosted models (Google Gemini 1.5/2.0 Flash) while reserving local Ollama inference for standard or offline workloads.
2. Protecting the core principle: **"LLM interprets. Backend decides. Database owns facts."**
3. Ensuring high search availability via single-attempt multi-provider failover and deterministic rule-based fallback.
4. Providing real-time observability over model latency, provider selection, fallback status, and token usage.

## Decision
1. **Extend `AIProvider` Abstraction**: Implement [`GeminiProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/gemini_provider.py) behind the existing abstract [`AIProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/base.py) interface using Google's official `google-genai` client library with JSON schema mode.
2. **Deterministic Auto-Routing Engine**: Introduce [`AIRoutingPolicy`](file:///d:/FastAPI/EstateMap/backend/app/ai/routing_policy.py) and [`AIRequestProfile`](file:///d:/FastAPI/EstateMap/backend/app/ai/routing_policy.py) to classify request complexity deterministically based on grouped core filters (+1), multiple POIs (+2), commute destinations (+2), comparisons (+2), and text length (+2). The LLM never decides its own routing path.
3. **Resilient Failover Orchestration**: Update [`AIRouter`](file:///d:/FastAPI/EstateMap/backend/app/ai/router.py) and [`AIService`](file:///d:/FastAPI/EstateMap/backend/app/services/ai_service.py) with loop-prevention (each provider attempted at most once per request), bounded timeouts (`AI_TOTAL_TIMEOUT_SECONDS`), and deterministic regex fallback if all providers fail.
4. **Token Usage & Health Observability**: Equip all AI schemas and endpoints (`GET /api/v1/ai/health`, `POST /api/v1/ai/parse-search`, `POST /api/v1/ai/properties/{id}/explain`) with multi-provider health telemetry and `AIUsageMetadata` tracking input/output tokens.

## Consequences

### Positive
- **High Availability & Zero Single-Point-of-Failure**: If Gemini experiences quota limits or network outages, requests fail over to Ollama. If both fail, rule-based heuristics serve the search intent.
- **Cost & Latency Optimization**: Simple queries remain local and free; complex queries leverage Gemini Flash's high accuracy and sub-second reasoning.
- **Zero Vendor Lock-in**: Application services remain decoupled from provider SDKs; new models or providers (e.g., Anthropic, OpenAI) can be added simply by implementing `AIProvider`.
- **Preserved System Invariants**: AI output remains strictly structured, Pydantic-validated, and completely isolated from database execution.

### Negative / Trade-offs
- Requires managing API credentials (`GEMINI_API_KEY`) for hosted environments.
- Small latency overhead (< 1ms) incurred for deterministic routing evaluation and circuit orchestration.

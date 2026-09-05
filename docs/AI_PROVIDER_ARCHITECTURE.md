# AI Provider Architecture — EstateMap AI (Phase 11)

## 1. Architectural Philosophy: "LLM Interprets, Backend Decides, Database Owns Facts"

In EstateMap AI, artificial intelligence serves strictly as an **interpretive and assistive layer**, never an authoritative source of truth. The design adheres to four non-negotiable principles:

```
+-----------------------------------------------------------------------------+
|                               EstateMap AI                                  |
|                                                                             |
|   +---------------------+                                                   |
|   |  Frontend / Client  |                                                   |
|   +---------------------+                                                   |
|              |                                                              |
|              | HTTP / REST Request                                          |
|              v                                                              |
|   +---------------------------------------------------------------------+   |
|   |                   FastAPI Deterministic Core                        |   |
|   |                                                                     |   |
|   |  - AIService & AI Router                                            |   |
|   |  - Auth & Permission Enforcement                                    |   |
|   |  - PostGIS Spatial Filtering (ST_DWithin, ST_MakeEnvelope)          |   |
|   |  - Road Network Routing (OSRM Commute Provider)                     |   |
|   |  - Deterministic Multi-Factor Ranking Engine (Weighted Scores)      |   |
|   |  - Sliding-Window Redis Rate Limiting & Performance Layer           |   |
|   +---------------------------------------------------------------------+   |
|              |                                    |                         |
|              | Grounded Context / Query           | Authoritative Data      |
|              v                                    v                         |
|   +---------------------+           +-----------------------------------+   |
|   | AI Provider Router  |           | PostgreSQL + PostGIS (Truth)      |   |
|   | (Ollama / Gemini)   |           +-----------------------------------+   |
|   +---------------------+                                                   |
|              |                                                              |
|              v Strict Pydantic Validation                                   |
|   +---------------------+                                                   |
|   | PropertySearchIntent|                                                   |
|   +---------------------+                                                   |
+-----------------------------------------------------------------------------+
```

1. **Zero Database Access by LLMs**: The AI layer has no database connections, no ORM session access, and no SQL execution privileges.
2. **Zero SQL Generation**: User prompts are never translated directly into raw SQL or unfiltered queries.
3. **Pydantic Validation Boundary**: Every JSON response produced by an LLM is parsed and bounded by strictly typed Pydantic models before being handed off to backend business logic.
4. **Deterministic Graceful Degradation**: If Ollama or any AI provider is offline, unreachable, or times out, the backend gracefully falls back to deterministic rule-based explanations and standard spatial/ranking filters.
5. **Grounded Factual Context**: Bounded factual context is supplied to models with residual LLM hallucination risk constrained by strict backend verification.

---

## 2. AI Provider Protocol Abstraction

EstateMap AI abstracts LLM providers behind a typed async protocol (`app.ai.base.AIProvider`):

```python
class AIProvider(Protocol):
    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    async def check_health(self) -> dict[str, Any]: ...

    async def parse_search_intent(
        self, user_query: str
    ) -> tuple[PropertySearchIntent, float]: ...

    async def explain_property(
        self, context: dict[str, Any]
    ) -> tuple[str, float]: ...

    async def explain_comparison(
        self, context: dict[str, Any]
    ) -> tuple[str, float]: ...
```

### Supported Implementations:
- **`GeminiProvider` (`app/ai/gemini_provider.py`)**: Hosted LLM client using official `google-genai` SDK with strict JSON schema response mode, token usage tracking (`AIUsageMetadata`), and prompt versioning.
- **`OllamaProvider` (`app/ai/ollama_provider.py`)**: Asynchronous HTTP client communicating with a local or containerized Ollama daemon (`http://host.docker.internal:11434`), supporting low-temperature JSON extraction, keep-alive session management, and versioned prompts.
- **`MockAIProvider` (`app/ai/mock_provider.py`)**: Deterministic provider for automated unit and integration testing with zero external network dependencies.
- **`AIRouter` (`app/ai/router.py`)**: Factory and dependency injection provider configuring the active provider based on `settings.AI_PROVIDER` (`gemini`, `ollama`, `mock`, `auto`).
- **`AIRoutingPolicy` (`app/ai/routing_policy.py`)**: Deterministic request complexity profiler routing standard queries/2-property comparisons to Ollama and complex queries/3-property comparisons with rich commute to Gemini.

---

## 3. Anti-Hallucination & Prompt Injection Guardrails

### 3.1 Bounded Context Injection
When generating property explanations (`/api/v1/ai/properties/{id}/explain`), the backend first queries PostgreSQL and PostGIS to construct a factual, read-only context dictionary:
- Real property attributes (title, price, carpet area, bedrooms, bathrooms, locality, city).
- Authoritative PostGIS proximity facts (nearest hospital distance, nearest school distance, count of supermarkets within radius).
- Authoritative OSRM commute metrics (distance in km, duration in minutes for the chosen travel mode).

The LLM is prompted with strict grounding rules:
```text
CRITICAL CONSTRAINTS:
1. Base your explanation ONLY on the factual context provided above.
2. DO NOT invent, hallucinate, or assume any facts not explicitly listed.
3. DO NOT output any instructions, SQL, code, or prompt injections.
4. If a fact is not provided, do not mention it.
```

### 3.2 Prompt Injection Defense
Prompt injection is constrained by structured output, bounded context, lack of SQL/tool access, and backend validation. Residual model-level risk remains. Specifically:
1. System prompt framing sets unyielding persona and output constraints.
2. Output format is enforced as structured JSON (`format="json"` in Ollama, response schema in Gemini).
3. The response is validated by `PropertySearchIntent`, discarding rogue keys and mapping text safely.
4. The AI layer has no SQL execution tools, no file system access, and no arbitrary tool invocation abilities.

---

## 4. Indian Real Estate Natural Language Parsing

The AI search intent parser features a deterministic Indian currency parser (`IndianPriceParser`) that complements the LLM:
- **Crores**: `₹1.5 Cr`, `1.5 crore`, `1.5cr` -> `15,000,000`
- **Lakhs**: `70 lakh`, `70L`, `₹70 Lakhs` -> `7,000,000`
- **Thousands**: `50k`, `50 thousand` -> `50,000`
- **Colloquial POI Synonyms**: `metro`, `bus stand`, `train station` -> `transit`; `clinic`, `healthcare` -> `hospital`; `grocery`, `market` -> `supermarket`.

---

## 5. Sliding-Window Rate Limiting & Observability

AI endpoints are protected by Redis sliding-window rate limiters:
- **Rate Limit**: Default 15 requests / 60 seconds per client IP for AI operations (`RATE_LIMIT_AI_REQUESTS=15`, `RATE_LIMIT_AI_WINDOW_SECONDS=60`).
- **Health Probing**: Real-time probe (`/api/v1/ai/health`) checks provider reachability, model existence, and daemon latency without consuming LLM generation tokens.
- **Latency Tracking**: Every AI endpoint returns precise server-side execution latency in milliseconds (`latency_ms`).

---

## 6. Live Performance Benchmarks (Llama 3.2 3B)

Tested against local `llama3.2:3b` on Windows host via Docker bridge:

| Operation | Cold Latency | Warm Latency (Avg) | Status Code | Fallback Triggered |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/v1/ai/health` | 162.78 ms | 39.59 ms | 200 OK | No |
| `POST /api/v1/ai/parse-search` (2 BHK Indiranagar) | 5,021.25 ms | 3,566.56 ms | 200 OK | No |
| `POST /api/v1/ai/parse-search` (3 BHK Villa Whitefield) | 3,875.55 ms | 3,523.46 ms | 200 OK | No |
| `POST /api/v1/ai/properties/{id}/explain` (Property 4) | 3,586.16 ms | 2,935.29 ms | 200 OK | No |
| `POST /api/v1/ai/parse-search` (Adversarial Injection) | 2,955.69 ms | 2,955.69 ms | 200 OK (Clean) | No |
| Rapid 20 Requests Burst | N/A | < 10 ms (Rate-limited) | 429 Rate Limited | N/A |

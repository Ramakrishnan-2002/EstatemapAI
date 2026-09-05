# Multi-Provider AI Architecture & Routing

EstateMap AI implements a multi-provider AI architecture designed to balance **accuracy, speed, cost, and privacy** while upholding the core system invariants:

> **LLM interprets. Backend decides. Database owns facts.**

---

## 1. Provider Interface & Abstraction

All AI interactions occur behind the abstract base class [`AIProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/base.py), isolating the FastAPI application layer from concrete provider SDKs or API implementations:

```
                      +-------------------+
                      |   FastAPI Layer   |
                      +---------+---------+
                                |
                                v
                      +-------------------+
                      |     AIService     |
                      +----+---------+----+
                           |         |
                  +--------+         +--------+
                  v                           v
        +-------------------+       +-------------------+
        |  AIRoutingPolicy  |       |     AIRouter      |
        +-------------------+       +---------+---------+
                                              |
                   +--------------------------+--------------------------+
                   |                          |                          |
                   v                          v                          v
        +--------------------+      +--------------------+     +--------------------+
        |   OllamaProvider   |      |   GeminiProvider   |     |    MockProvider    |
        |   (Local / Fast)   |      |  (Hosted / Accur)  |     |   (Deterministic)  |
        +--------------------+      +--------------------+     +--------------------+
```

### Supported Concrete Providers

| Provider | Implementation Class | Engine / SDK | Primary Use Case | Network Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Ollama** | [`OllamaProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/ollama_provider.py) | `httpx` + Ollama REST API (`llama3.2:3b`) | Standard queries, local-only offline workloads, zero per-token cost | Local host network only |
| **Gemini** | [`GeminiProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/gemini_provider.py) | `google-genai` SDK (`genai.Client`) | Complex queries, nuanced multi-criteria search, long explanations | External HTTPS to Google APIs |
| **Mock** | [`MockAIProvider`](file:///d:/FastAPI/EstateMap/backend/app/ai/base.py) | Pure Python regex & heuristics | Unit testing, CI environments, fallback when all LLMs disabled | In-process, 0ms latency |

---

## 2. Deterministic Routing Policy

EstateMap AI avoids arbitrary or non-deterministic provider routing. The LLM **never** decides its own provider or routing path.

The [`AIRoutingPolicy`](file:///d:/FastAPI/EstateMap/backend/app/ai/routing_policy.py) evaluates a request profile against deterministic criteria:

### Complexity Scoring Heuristics

1. **Structured Search Intent (`search_intent`)**:
   - **Core Property Filters**: Grouped criteria (bedrooms, bathrooms, price bounds, area, property types, localities, cities) contribute **+1 base point total**.
   - **Multiple POI Categories**: Specifying 2 or more distinct POI categories contributes **+2 points**.
   - **Commute Intent**: Specifying a workplace or commute destination contributes **+2 points**.
   - **Comparison Intent**: Multi-entity or comparison phrases contribute **+2 points**.
   - **Query Length**: Long queries (>100 chars) contribute **+2 points**.
   - **Rule**: If `complexity_score >= AI_ROUTING_COMPLEXITY_THRESHOLD` (default: 3), the request is classified as **complex** and routed to **Gemini**. Standard queries (`complexity_score < 3`) route to **Ollama** for low-latency local execution.

2. **Property Explanation (`property_explanation`)**:
   - Explanation requests synthesize property attributes, commute times, and nearest POIs.
   - Grounded context synthesis defaults to **Gemini** with fallback to **Ollama**.

3. **Adversarial / Empty Queries**:
   - Minimal or unparseable queries score 0 constraints and route to **Ollama** locally, avoiding external API consumption on malformed inputs.

---

## 3. Failover Orchestration & Circuit Rules

Failover is managed in [`AIService`](file:///d:/FastAPI/EstateMap/backend/app/services/ai_service.py) with the following resilience invariants:

1. **Loop Prevention**: Each provider in the failover chain is attempted **at most once**. A provider never repeats in the same request lifecycle.
2. **Total Time Budgeting**: All operations are bounded by `AI_TOTAL_TIMEOUT_SECONDS` (default: 35.0s) and individual provider timeouts (`GEMINI_TIMEOUT_SECONDS`: 20.0s, `OLLAMA_TIMEOUT_SECONDS`: 20.0s).
3. **Graceful Fallback**:
   - If the primary provider times out, fails health checks, encounters 429 rate limits, or throws unparseable JSON, the router immediately attempts the secondary provider.
   - If **all** AI providers fail or are disabled, the system executes deterministic regex-based fallback extraction, ensuring core search and discovery remain functional even in complete provider outages.

---

## 4. Token Usage & Telemetry

Every AI response tracks token consumption and latency via [`AIUsageMetadata`](file:///d:/FastAPI/EstateMap/backend/app/schemas/ai.py):

```json
{
  "provider": "gemini",
  "model": "gemini-flash-latest",
  "fallback_used": false,
  "routing_reason": "Auto-routed to GEMINI (complex search_intent with score 7 >= threshold 3; fallback: OLLAMA)",
  "usage": {
    "input_tokens": 596,
    "output_tokens": 134,
    "total_tokens": 730
  }
}
```

### Telemetry & Latency Comparison

| Metric | Ollama (`llama3.2:3b`) | Gemini (`gemini-flash-latest`) | Mock Provider |
| :--- | :--- | :--- | :--- |
| **Health Probe Latency** | ~15 ms | ~185 ms | < 1 ms |
| **Simple Search Latency** | ~2,100 ms | ~4,500 ms | < 5 ms |
| **Complex Search Latency** | ~10,600 ms | ~2,690 ms | < 10 ms |
| **Token Usage Tracking** | Supported | Supported (`google-genai` usage) | Simulated |
| **Network Boundary** | Local host network only | Google APIs HTTPS | In-process |
| **Structured Output Reliability** | Medium (Schema guided) | High (Native JSON Mode) | Deterministic |

---

## 5. Security & Privacy Boundaries

To prevent unauthorized data leakage or prompt injection risks:

1. **No Database Access**: Neither Ollama nor Gemini have database credentials, connection pools, or SQL generation permissions.
2. **Strict Schema Filtering**: Prompts only receive public property facts and POI distances. No user PII, hashed passwords, or private listing notes are ever passed to AI providers.
3. **Pydantic Validation Barrier**: LLM outputs are treated as untrusted user input and strictly validated through Pydantic v2 schemas before being used in database queries.

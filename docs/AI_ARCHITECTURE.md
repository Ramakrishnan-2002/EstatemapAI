# EstateMap AI — AI Architecture & Provider Orchestration

## 1. Core AI Principles & Guardrails
- **The LLM is an Interpreter, NOT the Source of Truth**:
  - The LLM extracts parameters (`bedrooms`, `price_max`, `locality`, `nearby_amenities`).
  - The LLM **never** generates executable SQL queries.
  - The LLM **never** connects directly to PostgreSQL.
  - All factual data (availability, coordinates, pricing, distances) is computed deterministically in Python/PostGIS.
- **Strict Pydantic Validation**:
  - Every LLM response is strictly parsed and validated against typed schemas (`ParsedSearchIntent`).
  - Malformed or out-of-schema responses trigger graceful fallback or clarification.

## 2. Provider Abstraction
```
                    ┌─────────────────────────┐
                    │       AIRouter          │
                    │  (Strategy & Fallback)  │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     ┌────────────────────────┐      ┌────────────────────────┐
     │     OllamaProvider     │      │     GeminiProvider     │
     │     (llama3.2:3b)      │      │   (gemini-1.5-flash)   │
     │  - Fast, Local, Free   │      │  - Complex Inferences  │
     │  - Search Intent       │      │  - Rich Comparisons    │
     └────────────────────────┘      └────────────────────────┘
```

## 3. Provider Routing & Fallback Matrix
| Mode | Primary Provider | Secondary / Fallback | Behavior on Total Failure |
| :--- | :--- | :--- | :--- |
| `auto` | Ollama (local) | Gemini API | Standard structured filter UI |
| `ollama` | Ollama | None | Standard structured filter UI |
| `gemini` | Gemini | None | Standard structured filter UI |

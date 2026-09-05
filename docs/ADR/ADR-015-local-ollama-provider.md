# ADR-015: Local Ollama Provider Abstraction and Deterministic AI Assistance

## Status
Accepted (Phase 11)

## Context
EstateMap AI requires natural language search intent parsing and conversational property explanations to enhance property discovery. However, integrating Large Language Models presents significant architectural risks:
1. **Hallucination Risk**: LLMs may invent property details, non-existent metro stations, or false pricing.
2. **Security & Data Authority**: Allowing LLMs to write or execute SQL queries or make authorization decisions creates severe security vulnerabilities.
3. **Availability & Resilience**: External AI APIs or local LLM daemons may experience outages, network timeouts, or high latency.
4. **Vendor Lock-In**: Tightly coupling business logic to a single model provider limits operational flexibility.

## Decision
1. **Provider Abstraction Protocol**: Implement an asynchronous `AIProvider` protocol with unified interfaces for health probing, search intent parsing, and property explanations.
2. **Local Ollama Integration**: Use local `OllamaProvider` with lightweight `llama3.2:3b` running via HTTP JSON mode (`format="json"`, `temperature=0.0` for search intent, `temperature=0.2` for explanations).
3. **LLM Interprets, Backend Decides, Database Owns Facts**:
   - Zero direct database access or SQL generation by the AI layer.
   - All spatial, pricing, and commute facts are fetched deterministically by FastAPI and PostgreSQL/PostGIS before bounded context assembly.
   - Pydantic v2 schemas (`PropertySearchIntent`, `AIExplanationResponse`) strictly validate all structured LLM outputs.
4. **Deterministic Rule-Based Fallback**: If Ollama is offline, unreachable, or times out (>30s), the service automatically generates deterministic explanations based on database records without throwing 500 errors to the user.
5. **Redis Sliding-Window Rate Limiting**: Limit AI requests (15 requests/min per IP) to prevent local GPU/CPU exhaustion.

## Consequences
### Positive
- **Guaranteed Factuality**: Explanations only reference verified database and routing facts.
- **Zero SQL Injection Risk**: Queries are validated as Pydantic models and executed via existing SQLAlchemy repositories.
- **High Resilience**: The platform remains fully functional for property search, filtering, and detail views even when Ollama is offline.
- **Cost & Privacy**: Zero cloud API fees; user queries remain entirely local.

### Negative / Tradeoffs
- Local LLM inference on consumer hardware incurs ~2.5s to ~4.5s latency per request.
- Requires local Ollama daemon and model weights (~2.0 GB for `llama3.2:3b`).

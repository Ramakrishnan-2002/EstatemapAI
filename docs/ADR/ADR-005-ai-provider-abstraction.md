# ADR-005: AI Provider Abstraction Layer

## Status
Accepted

## Context
Directly embedding provider-specific LLM SDK calls across routes or services causes tight coupling and vendor lock-in.

## Decision
Create an abstract `AIProvider` base class in `app/ai/base.py` and route all AI operations through `AIRouter`. Providers like `GeminiProvider` and `OllamaProvider` implement this interface.

## Consequences
- Single point of change for model upgrades or new providers.
- Testable with mock providers during automated unit test runs.

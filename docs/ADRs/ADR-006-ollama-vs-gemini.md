# ADR-006: Local Ollama (llama3.2:3b) with Google Gemini Hybrid Routing

## Status
Accepted

## Context
Running all intent parsing via external APIs introduces network latency, token costs, and external dependency risks.

## Decision
Support local Ollama (`llama3.2:3b`) for fast search intent extraction and property summaries, while utilizing Google Gemini for complex explanations or as an automatic cloud fallback.

## Consequences
- Fast, offline-capable intent parsing during local development.
- Robust reliability through automated cloud fallback.

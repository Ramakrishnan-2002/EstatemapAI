# ADR-001: Modular Monolith vs Microservices Architecture

## Status
Accepted

## Context
EstateMap AI requires a structured, maintainable, and high-performance backend capable of complex geospatial queries, caching, AI routing, and authentication.

## Decision
We choose a **Modular Monolith** architecture for FastAPI rather than premature microservices.
Modules (`auth`, `properties`, `search`, `geo`, `ai`, `cache`) maintain strict internal boundaries and repository patterns, communicating via clean Python interfaces within a single deployable process.

## Alternatives Considered
- **Microservices**: Decomposing search, auth, properties, and AI into separate services communicating over gRPC/HTTP/Kafka. Rejected due to premature complexity, distributed transaction overhead, and debugging latency.
- **Traditional Monolith**: Unstructured monolithic codebase with shared global models and overlapping queries. Rejected due to poor maintainability.

## Consequences
- Single runtime deployment and straightforward local setup.
- Direct database transactions without two-phase commit or eventual consistency synchronization issues.
- Clear module boundaries allow extracting individual microservices in the future if specific scaling bottlenecks emerge.

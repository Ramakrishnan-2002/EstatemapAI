# EstateMap AI — Project Pitch & Technical Elevator Speeches

This document provides four structured verbal pitch templates for presenting EstateMap AI across different interview contexts: 30-second elevator pitch, 2-minute project overview, 5-minute architectural pitch, and 10-minute deep-dive technical walkthrough.

---

## 1. 30-Second Elevator Pitch
> "EstateMap AI is a location-first real estate discovery platform that replaces traditional keyword filters with true geospatial intelligence. Built as a FastAPI modular monolith with PostgreSQL and PostGIS, it combines sub-50ms R-Tree bounding-box search, OSRM road-network commute calculations, and a deterministic 6-factor ranking engine. We also built 'Ask the Map', a multi-turn conversational search orchestrator that uses local and cloud LLMs to parse natural language updates into a verified state machine with offline fallback."

---

## 2. 2-Minute Project Overview
> "Most real estate portals treat location as a simple text match on neighborhood names. EstateMap AI treats spatial coordinates and commute times as core engineering primitives.
>
> On the backend, we use PostgreSQL 16 with PostGIS 3.4. Instead of scanning tables in memory, our bounding-box and radius queries execute directly against PostGIS GiST spatial indexes.
>
> For travel times, we integrated OSRM to compute real road-network driving, transit, and walking times across the street graph, caching routes in Redis with canonical coordinate keys.
>
> For property recommendations, we designed a deterministic mathematical ranking engine across 6 dimensions—price, bedrooms, living area, locality, POI proximity, and commute duration—with explicit missing-factor weight redistribution.
>
> Finally, we built a resilient AI multi-provider router supporting both local Ollama and Google Gemini. The AI is intentionally non-authoritative: it parses natural language into structured delta patches for our state machine, but never queries the database or invents facts directly. The entire system is covered by 288 backend tests and 33 frontend tests."

---

## 3. 5-Minute Architectural Pitch
> "When designing EstateMap AI, our goal was to build a production-grade, highly performant real estate platform while maintaining a strict modular monolithic architecture.
>
> **1. Geospatial Persistence Layer**:
> We store coordinates using PostGIS `geometry(Point, 4326)`. Spatial queries leverage 2D R-Tree GiST indexes. When a user pans the map, the frontend extracts the bounding box, and PostGIS evaluates `ST_MakeEnvelope` in under 20ms. Surrounding amenities use `ST_DWithin` with geography casting for meter-accurate spherical distance.
>
> **2. In-Memory Performance & Protection**:
> We use Redis 7 for two distinct purposes:
> * *Cache-Aside*: Caches OSRM route calculations and location intelligence aggregations with deterministic SHA-256 and canonical coordinate keys.
> * *Sliding-Window Rate Limiting*: Implements a sliding-window log using Redis Sorted Sets (`ZSET`). By recording request timestamps as scores and pruning expired records atomically via `ZREMRANGEBYSCORE`, we eliminate the 2x burst boundary vulnerabilities of fixed-window counters.
>
> **3. Deterministic Domain Engines**:
> Rather than relying on black-box machine learning or hallucinating LLMs, both our Ranking and Comparison engines are 100% deterministic mathematical services. The ranking service scores properties across normalized weights, and the comparison service computes exact arithmetic deltas before passing grounded facts to the AI for narrative summarization.
>
> **4. Resilient Conversational Orchestration ('Ask the Map')**:
> For conversational exploration, we treat user interactions as state transitions. An incoming prompt like *'3 BHK under 1.5 Cr in Adyar near hospitals'* is evaluated by an AI routing policy that scores complexity, selects Ollama or Gemini, enforces strict Pydantic JSON schemas, and returns a delta patch (`SET`, `CLEAR`, `APPEND`, `RESET`). If both cloud and local LLMs timeout or fail, a deterministic rule-based engine takes over.
>
> The frontend is built with Next.js 14 App Router, MapLibre GL for WebGL-accelerated 60fps rendering, and TanStack Query for cache management."

---

## 4. 10-Minute Deep-Dive Technical Walkthrough
*(Refer to [`ESTATEMAP_MASTER_BOOK.md`](file:///d:/FastAPI/EstateMap/docs/mastery/ESTATEMAP_MASTER_BOOK.md) for chapter-by-chapter code citations and diagrams).*

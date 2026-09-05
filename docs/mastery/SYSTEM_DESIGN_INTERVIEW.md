# EstateMap AI — Complete System Design Interview Guide

This document presents EstateMap AI structured as an end-to-end Senior Backend / System Design Interview presentation. It strictly distinguishes **IMPLEMENTED ARCHITECTURE** from **HYPOTHETICAL PRODUCTION EVOLUTION**.

---

## 1. Problem Statement & Requirements Clarification

### Functional Requirements
1. **Interactive Spatial Search**: Search listings within a dynamic viewport bounding box on an interactive map.
2. **Road-Network Commute Discovery**: Rank and filter properties by realistic travel times to key employment hubs across driving, transit, cycling, and walking.
3. **Location Intelligence**: Group and aggregate nearby amenities (schools, hospitals, transit, tech parks).
4. **Deterministic Multi-Factor Ranking**: Score listings mathematically across 6 dimensions with explainable weights.
5. **Conversational Exploration**: Refine map queries conversationally using multi-turn natural language updates.
6. **Side-by-Side Comparison**: Compare 2–3 properties with exact mathematical deltas and grounded AI summaries.

### Non-Functional Requirements
1. **Low Latency**: Spatial queries $<50\text{ms}$; cached commute queries $<10\text{ms}$; AI turns $<1.5\text{s}$.
2. **High Availability**: Core search and property details operational even during AI provider outages.
3. **Data Integrity**: ACID guarantees on user listings, images, and favorites; zero spatial coordinate drift.
4. **Rate Limiting & Security**: Protection against automated scraping and brute-force attacks via sliding-window limits.

---

## 2. High-Level Architecture

```
                  ┌─────────────────────────────────────┐
                  │          Client Tier (Next.js)      │
                  │   MapLibre WebGL + mapcn + React    │
                  └──────────────────┬──────────────────┘
                                     │ HTTPS
                  ┌──────────────────▼──────────────────┐
                  │         Application Gateway         │
                  │  FastAPI Modular Monolith (Port 8000)│
                  │  - RequestID & RateLimit Middleware │
                  │  - Centralized Exception Handlers   │
                  └───────┬──────────┬──────────┬───────┘
                          │          │          │
        ┌─────────────────▼┐   ┌─────▼───────┐  │
        │ PostGIS Spatial  │   │ Redis 7     │  │
        │ Database (5432)  │   │ In-Memory   │  │
        │ - R-Tree GiST    │   │ Cache (6379)│  │
        │ - POINT(lng lat) │   │ - ZSET Limit│  │
        │ - ACID Relational│   │ - TTL Cache │  │
        └──────────────────┘   └─────────────┘  │
                                                │
                      ┌─────────────────────────▼──────┐
                      │    AI Multi-Provider Tier      │
                      │  - Google Gemini 2.5 (Cloud)   │
                      │  - Ollama Llama 3.2 (Local)    │
                      │  - Deterministic Rule Engine   │
                      │  - OSRM Road Graph Routing     │
                      └────────────────────────────────┘
```

---

## 3. Deep-Dive Design Decisions

### A. Why PostGIS Over Application-Side Geometry Math?
* **Application Math**: Requires pulling thousands of rows into Python memory to compute Euclidean distance, resulting in $\mathcal{O}(N)$ network transfer, Python GIL overhead, and high latency.
* **PostGIS GiST Index**: Uses hierarchical R-Trees to discard non-intersecting coordinate boxes in $\mathcal{O}(\log N)$ time directly inside the database C-engine before transmitting any rows.

### B. Why Redis Sorted Sets for Rate Limiting?
* **Fixed-Window Counter**: Suffers from 2x traffic bursts at window boundaries (e.g. 5 requests at 00:59 + 5 requests at 01:00 = 10 requests in 2 seconds).
* **Sliding-Window Log (`ZSET`)**: Stores timestamps as sorted set scores. Pruning timestamps older than `now - 60s` via `ZREMRANGEBYSCORE` provides mathematical 100% boundary accuracy.

### C. Why Heuristic Ranking Over Machine Learning?
* **Cold Start & Zero Log Dependency**: ML ranking models require millions of logged user clicks and conversions.
* **Explainability**: Real estate transactions demand auditable reasons for ranking order. Heuristic equations allow users to directly control factor weights.

### D. Why Explicit State Machine Over Autonomous Agents?
* **Deterministic Bounded Latency**: A state reducer executes in $<1\text{ms}$ after LLM extraction. Autonomous multi-agent loops introduce 15–45s latency, hallucination risks, and unmanageable test flakiness.

---

## 4. Scaling & Production Evolution (Hypothetical Architecture)

When scaling from 100k DAU to 10M DAU:

```
[Global Cloudflare Anycast CDN / WAF]
           │
[AWS ALB Layer 7 Load Balancer]
           │
┌──────────▼────────────────────────────────────────────────────────┐
│             FastAPI Backend Auto-Scaling Group (EKS / ECS)        │
│   Worker 1   Worker 2   Worker 3 ... Worker N                     │
└──────────┬──────────────────────┬───────────────────────┬─────────┘
           │                      │                       │
┌──────────▼────────────┐  ┌──────▼─────────────┐  ┌──────▼─────────┐
│ AWS Aurora PostgreSQL │  │ AWS ElastiCache    │  │ Self-Hosted    │
│ Multi-AZ PostGIS      │  │ Redis Cluster      │  │ OSRM Cluster   │
│ - 1 Writer Primary    │  │ - 3 Shards         │  │ - Multi-Zone   │
│ - 3 Reader Replicas   │  │ - Read Replicas    │  │   Auto-scaled  │
└───────────────────────┘  └────────────────────┘  └────────────────┘
```

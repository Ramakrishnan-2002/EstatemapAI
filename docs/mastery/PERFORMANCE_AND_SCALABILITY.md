# EstateMap AI — Performance, Scalability & Capacity Planning

This document provides a rigorous technical breakdown of system performance. All metrics are explicitly partitioned into **MEASURED**, **LOCAL OBSERVED**, **THEORETICAL**, and **HYPOTHETICAL** categories.

---

## 1. Measured & Observed Metrics

### Local Test Suite Performance (MEASURED)
* **Backend Pytest Suite**: 288 tests completed in **50.67 seconds** on Docker container environment (Linux x86_64, Python 3.12, asyncpg, PostgreSQL 16 + PostGIS, Redis 7).
* **Frontend Node Test Suite**: 33 tests completed in **202.75 ms** using Node.js native test runner.
* **TypeScript Compilation**: 0 errors across all Next.js App Router pages and components.

### Local HTTP Endpoint Latency (LOCAL OBSERVED)
* **Static / Basic Routes (`GET /`, `GET /dashboard`, `GET /favorites`)**: ~75ms – 150ms in Next.js development server.
* **PostGIS Bounding-Box Spatial Search (`POST /api/v1/search/spatial`)**: ~12ms – 25ms database query time on 104 seeded listings.
* **Sliding-Window Rate Limiter Execution (`Redis ZSET`)**: ~0.8ms – 1.8ms per request.
* **Google Gemini AI Parsing Latency**: ~650ms – 1400ms per conversational turn.
* **Local Ollama Inference (Llama 3.2 on local CPU/GPU)**: ~1800ms – 4200ms per turn.

---

## 2. Theoretical Algorithmic Complexities

| Subsystem / Operation | Theoretical Time Complexity | Space Complexity | Description |
| :--- | :--- | :--- | :--- |
| **PostGIS GiST Spatial Indexing** | $\mathcal{O}(\log N)$ average query time | $\mathcal{O}(N)$ R-Tree disk space | Hierarchical bounding-box tree pruning non-intersecting geometries without full table scans. |
| **Sliding-Window Log (Redis ZSET)** | $\mathcal{O}(\log M + K)$ per request | $\mathcal{O}(M)$ per rate-limited identity | $M$ = requests in window (e.g. 5–60), $K$ = expired entries removed by `ZREMRANGEBYSCORE`. |
| **Deterministic Ranking Math** | $\mathcal{O}(P \times F)$ where $P$ = properties, $F = 6$ | $\mathcal{O}(P)$ output memory | Single-pass arithmetic evaluation over candidate properties (sub-millisecond for $P \le 500$). |
| **Conversational State Patch Reducer** | $\mathcal{O}(K)$ where $K$ = keys modified | $\mathcal{O}(1)$ state memory | Dict lookup and field overwrite on immutable Pydantic model. |
| **OSRM Route Lookup (Cached)** | $\mathcal{O}(1)$ Redis key lookup | $\mathcal{O}(1)$ payload size | Instantaneous memory hash lookup on canonical coordinate key. |

---

## 3. Hypothetical Capacity-Planning Exercise

> [!NOTE]
> **IMPORTANT**: The following numbers represent a **HYPOTHETICAL CAPACITY-PLANNING EXERCISE** designed for system-design interviews. They do not represent measured production benchmarks.

### Target Assumptions
* **Daily Active Users (DAU)**: 100,000 users.
* **Searches per User per Day**: 10 searches on average.
* **Total Daily Searches**: $100{,}000 \times 10 = 1{,}000{,}000\text{ searches/day}$.
* **Active Window**: 12 peak hours ($43{,}200\text{ seconds}$).

### QPS & Workload Calculations

#### 1. Average & Peak Query Per Second (QPS)
$$\text{Average QPS} = \frac{1{,}000{,}000\text{ requests}}{43{,}200\text{ seconds}} \approx 23.15\text{ QPS}$$
$$\text{Peak QPS (Assumed 3x Burst Factor)} = 23.15 \times 3 \approx 70\text{ QPS}$$

#### 2. Database Workload & Read Replica Sizing
* Assume 70 QPS at peak with 60% spatial searches hitting PostGIS (42 QPS PostGIS queries).
* With GiST indexed queries executing in ~15ms, a single PostgreSQL 16 primary instance with 4 vCPUs and 16 GB RAM can handle ~250 QPS.
* **Conclusion**: A single primary database + 1 read replica easily satisfies 100k DAU without sharding.

#### 3. Redis In-Memory Footprint Estimation
* **Rate Limiter Keys**: 100,000 active users $\times$ 5 requests $\times 128\text{ bytes} \approx 64\text{ MB}$.
* **Commute Route Cache**: 50,000 unique routes $\times 2\text{ KB} \approx 100\text{ MB}$.
* **POI Intelligence Cache**: 10,000 unique properties/radii $\times 4\text{ KB} \approx 40\text{ MB}$.
* **Total Redis Memory**: $\approx 204\text{ MB}$.
* **Conclusion**: A standard 2 GB Redis instance operates at $<15\%$ memory utilization with substantial headroom.

#### 4. AI Inference Capacity Planning
* Assume 10% of users engage in "Ask the Map" conversational search (10,000 conversational turns/day).
* Average token usage: 150 prompt tokens + 100 completion tokens = 250 tokens/turn.
* **Total Daily Tokens**: $10{,}000 \times 250 = 2{,}500{,}000\text{ tokens/day}$.
* With Gemini 2.5 Flash pricing / free tier limits, operating cost is negligible (<$1.00/day).

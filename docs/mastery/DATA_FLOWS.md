# EstateMap AI — Architectural Data Flows

This document visualizes the complete architectural data flows across the EstateMap AI platform using Mermaid diagrams.

---

## 1. Authentication & Security Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Client Browser
    participant API as FastAPI Auth Router
    participant Sec as Security Engine (Argon2 / JWT)
    participant DB as PostgreSQL (users table)
    participant Redis as Redis (Sliding Window ZSET)

    User->>API: POST /api/v1/auth/login (email, password)
    API->>Redis: Check Rate Limit (IP identity)
    Redis-->>API: Rate Limit OK (Count < 5)
    API->>DB: SELECT * FROM users WHERE email = :email
    DB-->>API: Return User Entity (with hashed_password)
    API->>Sec: verify_password(plain_pw, hashed_pw)
    Sec-->>API: Password Valid (True)
    API->>Sec: create_access_token(sub, user_id, role)
    Sec-->>API: Return Signed JWT (HS256)
    API-->>User: HTTP 200 OK (access_token, token_type)
```

---

## 2. PostGIS Spatial Bounding-Box Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Map UI (MapLibre)
    participant SearchAPI as FastAPI Spatial Search Route
    participant GeoRepo as PostGIS GeoRepository
    participant DB as PostgreSQL + PostGIS (GiST Index)

    User->>SearchAPI: POST /api/v1/search/spatial (min_lat, max_lat, min_lng, max_lng)
    SearchAPI->>GeoRepo: search_by_bbox(bounds)
    GeoRepo->>DB: SELECT *, ST_AsGeoJSON(location) FROM properties WHERE location && ST_MakeEnvelope(...)
    Note over DB: Evaluates R-Tree GiST Index on geometry(Point, 4326)
    DB-->>GeoRepo: Return Matched Property Rows + GeoJSON
    GeoRepo-->>SearchAPI: List[Property]
    SearchAPI-->>User: HTTP 200 OK (PropertyListResponse + GeoJSON Features)
```

---

## 3. Road-Network Commute & Caching Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Commute Panel
    participant CommuteAPI as FastAPI Commute Route
    participant Cache as Redis In-Memory Cache
    participant OSRM as OSRM Road Graph Engine
    participant DB as PostGIS (Fallback)

    User->>CommuteAPI: POST /api/v1/commute/route (origin, dest, mode)
    CommuteAPI->>Cache: GET estatemap:commute:v1:origin_dest:mode
    alt Cache Hit
        Cache-->>CommuteAPI: Return Cached Route JSON
    else Cache Miss
        CommuteAPI->>OSRM: HTTP GET /route/v1/{mode}/{lng1},{lat1};{lng2},{lat2}
        alt OSRM Success
            OSRM-->>CommuteAPI: Return Road Duration (s), Distance (m), GeoJSON LineString
            CommuteAPI->>Cache: SETEX key 86400 (Route JSON)
        else OSRM Timeout / Error
            CommuteAPI->>DB: Compute ST_DistanceSphere() Euclidean fallback
            DB-->>CommuteAPI: Return Spherical Distance / Average Speed
        end
    end
    CommuteAPI-->>User: HTTP 200 OK (CommuteResponse + GeoJSON Route)
```

---

## 4. Multi-Provider AI Failover Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Ask The Map Bar
    participant AIRouter as AI Provider Router
    participant Policy as Routing Policy (Complexity Scorer)
    participant Gemini as Google Gemini 2.5 (Cloud)
    participant Ollama as Ollama Llama 3.2 (Local)
    participant Fallback as Deterministic Fallback Engine

    User->>AIRouter: POST /api/v1/ai/ask-map (query, state)
    AIRouter->>Policy: evaluate_query_complexity(query)
    alt Complex Query (Score >= 3)
        Policy-->>AIRouter: Primary = Gemini, Secondary = Ollama
        AIRouter->>Gemini: Generate Structured Patch (Deadline: 8s)
        alt Gemini Success
            Gemini-->>AIRouter: Valid SearchStatePatch JSON
        else Gemini 429 Quota / Network Timeout
            AIRouter->>Ollama: Failover to Ollama (Remaining Deadline)
            alt Ollama Success
                Ollama-->>AIRouter: Valid SearchStatePatch JSON
            else Ollama Offline / Timeout
                AIRouter->>Fallback: Deterministic Rule-Based Fallback
                Fallback-->>AIRouter: Safe Guaranteed Fallback Patch
            end
        end
    else Simple Query (Score < 3)
        Policy-->>AIRouter: Primary = Ollama, Secondary = Gemini
        AIRouter->>Ollama: Generate Structured Patch
        alt Ollama Error
            AIRouter->>Gemini: Failover to Gemini
            Gemini-->>AIRouter: Valid SearchStatePatch JSON
        end
    end
    AIRouter-->>User: HTTP 200 OK (AskMapResponse)
```

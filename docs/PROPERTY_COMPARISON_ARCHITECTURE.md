# EstateMap AI — Property Comparison Architecture (Phase 13)

## 1. Executive Summary & Architectural Invariant

EstateMap AI implements a **grounded, multi-property comparison and explainable recommendation narrative engine** built on a strict architectural boundary:

$$\boxed{\text{Backend Computes Facts}} \quad \longrightarrow \quad \boxed{\text{LLM Explains Facts}}$$

```text
LLM interprets.
Backend decides.
Database owns facts.
```

The AI layer **never** performs arithmetic, **never** derives price per sq.ft., **never** calculates commute differences, **never** alters deterministic ranking orders, and **never** accesses PostgreSQL directly.

---

## 2. End-to-End System Topology

```text
                                 Client (Next.js 14 App Router)
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
         POST /api/v1/properties/compare               POST /api/v1/ai/properties/compare
         (Deterministic Facts Only)                    (Grounded Trade-off Narrative)
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                                   ComparisonService (Domain)
                                               │
            ┌──────────────────────────────────┼──────────────────────────────────┐
            ▼                                  ▼                                  ▼
   PropertyRepository                     POIService                        CommuteService
  (PostgreSQL/PostGIS)                (GiST Spatial Queries)             (OSRM / Road Networks)
            │                                  │                                  │
            └──────────────────────────────────┼──────────────────────────────────┘
                                               ▼
                                         RankingService
                                  (Phase 9 Deterministic Engine)
                                               │
                                               ▼
                                    ComparisonResult (Facts)
                                               │
                                 ┌─────────────┴─────────────┐
                                 ▼                           ▼
                     Direct Client Response              AIService
                                                             │
                                                             ▼
                                                      AIRoutingPolicy
                                                   ┌─────────┴─────────┐
                                                   ▼                   ▼
                                             OllamaProvider      GeminiProvider
                                              (Local Fast)      (Hosted Complex)
                                                   │                   │
                                                   └─────────┬─────────┘
                                                             ▼
                                                    AIComparisonResponse
                                                 (Grounded Narrative + Facts)
```

---

### 3.1 Supported Ranking Factors (Phase 9 Authoritative Vocabulary)
EstateMap strictly uses the six authoritative Phase 9 ranking factors:
1. `price`: Affordability and budget alignment score ($s_{\text{price}} \in [0.0, 1.0]$).
2. `bedrooms`: BHK match score ($s_{\text{bedrooms}} \in [0.0, 1.0]$).
3. `area`: Carpet/living area match score ($s_{\text{area}} \in [0.0, 1.0]$).
4. `locality`: Preferred neighborhood/locality match score ($s_{\text{locality}} \in [0.0, 1.0]$).
5. `location`: POI proximity location intelligence score ($s_{\text{location}} \in [0.0, 1.0]$).
6. `commute`: Road-network travel time convenience score ($s_{\text{commute}} \in [0.0, 1.0]$).

### 3.2 Effective Factor Weights & Missing-Factor Redistribution
When a factor is unavailable for a specific property (e.g., commute destination not provided or POI data missing), its weight is redistributed proportionally among available active factors for that property:

$$w_{f, P}^{\text{eff}} = \begin{cases} \frac{w_f}{\sum_{k \in \text{Available}(P)} w_k} & \text{if factor } f \text{ is available for property } P \\ 0.0 & \text{otherwise} \end{cases}$$

### 3.3 Authoritative Ranking Contribution Delta Formula
Because missing-factor redistribution can result in different effective weights between compared properties, ranking contribution margins are calculated using the general formula:

$$C_f(P) = w_{f, P}^{\text{eff}} \cdot s_f(P) \cdot 100$$

$$\Delta C_f(P_A, P_B) = C_f(P_A) - C_f(P_B) = \left(w_{f, P_A}^{\text{eff}} \cdot s_f(P_A) - w_{f, P_B}^{\text{eff}} \cdot s_f(P_B)\right) \cdot 100$$

Where $\Delta C_f > 0$ indicates factor $f$ contributed positively to Property A's score relative to Property B.

### 3.4 Dimension Metrics Summary Table

| Dimension | Calculation Method | Handling for Missing Data |
| :--- | :--- | :--- |
| **Price Difference** | $\|P_A.\text{price} - P_B.\text{price}\|$ in INR (formatted as Lakhs/Crores) | Required field; always available |
| **Price per sq.ft.** | $\text{price} / \text{area\_sqft}$ (if $\text{area\_sqft} > 0$) | Returns `null` if area is missing; zero division prevented |
| **Living Area Delta** | $\|P_A.\text{area} - P_B.\text{area}\|$ in sq.ft. | Omitted from space ranking if either area is null |
| **POI Distance Delta** | PostGIS `ST_DistanceSphere` nearest distance difference | If category absent for a property, delta marked unavailable |
| **Commute Difference** | $\|P_A.\text{duration} - P_B.\text{duration}\|$ in minutes | If unrouted, marked unavailable; never declares arbitrary winner |
| **Ranking Match Score** | Multi-factor weighted sum (0–100%) with weight redistribution | Factor weights renormalized across active factors only |
| **Ranking Contribution Margin** | $\Delta C_f = C_f(P_A) - C_f(P_B)$ | Explains exact driver points (+25.0 price vs -10.4 location) |

---

## 4. Privacy & Hosted AI Context Allowlist

Before invoking hosted models (e.g. Gemini), the backend sanitizes the comparison payload into an anonymous allowlisted structure.

### Strict Allowlist
- Bounded labels: `"Property A"`, `"Property B"`, `"Property C"`
- Public attributes: `title`, `property_type`, `price_inr`, `price_per_sqft`, `bedrooms`, `bathrooms`, `area_sqft`, `locality`, `city`
- Proximity facts: POI nearest distances in km
- Commute facts: destination label, travel mode, duration in minutes, distance in km
- Ranking breakdown: match score %, factor score contributions
- Precomputed statements: e.g. `"Property A is ₹1.17 Cr cheaper than Property B."`

### Explicitly Excluded (Zero Leakage)
- Database primary keys (`id`, `property_id`)
- User / Owner identifiers (`owner_id`, `user_id`)
- User contact info / PII (`email`, `phone`, `full_name`)
- Security credentials (`hashed_password`, `jwt`, `api_key`)
- Internal routing / database metadata

---

## 5. Multi-Provider AI Routing & Bounded Failover

Comparisons are profiled dynamically by `AIRoutingPolicy`:

$$\text{Profile}(\text{Context}) \longrightarrow \begin{cases} \text{ollama} & \text{if } N_{\text{props}} = 2 \text{ and standard complexity} \\ \text{gemini} & \text{if } N_{\text{props}} = 3 \text{ or rich commute/POI context} \end{cases}$$

- **Global Deadline Budget**: Enforced via `AI_TOTAL_TIMEOUT_SECONDS` (35.0s). Primary consumes time budget; fallback only receives remaining budget.
- **Single-Attempt Failover**: If primary fails or times out, fallback is attempted at most once.
- **Deterministic Rule Summary**: If both providers fail or `AI_ENABLED=false`, the endpoint returns HTTP 200 with precomputed statements in `deterministic_summary` and `fallback_used: true`.

---

## 6. Data Source & Ingestion Extensions

### Current Implementation
The current EstateMap portfolio uses **authoritative, verified demo seed datasets** stored in PostgreSQL 16 + PostGIS 3.4. No live scraping or third-party portal integrations (MagicBricks/99acres) are implied.

### Production Ingestion Architecture (Future Extension)
```text
Partner Feeds (RESO Web API / MLS)
Admin Listing API
Bulk CSV/GeoJSON Imports
         │
         ▼
Ingestion & Validation Pipeline (Pydantic v2 + Shapely)
         │
         ▼
Geocoding & Spatial Normalization (PostGIS ST_SetSRID)
         │
         ▼
Authoritative PostgreSQL Database
```

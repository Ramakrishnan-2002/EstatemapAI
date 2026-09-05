# EstateMap AI — Python Backend & System Design Mastery Curriculum
> **Curriculum Status: FROZEN & TAILORED STRICTLY FOR PYTHON BACKEND & SYSTEM DESIGN**
> **Canonical Document Library: 9 Focused Documents | 100% Code Truth**

Welcome to the EstateMap AI Backend Engineering Curriculum. This curriculum is designed to help you become strong in **Python backend development, database engineering (PostgreSQL + PostGIS), distributed caching & rate limiting (Redis), and system design** by deeply understanding, building, and explaining the EstateMap backend.

---

## 1. My Exact Learning Target
```text
Python
  ↓
FastAPI
  ↓
REST API Engineering
  ↓
Pydantic v2
  ↓
Async Python (asyncio / asyncpg)
  ↓
SQLAlchemy 2.0
  ↓
PostgreSQL
  ↓
PostGIS (WGS84, GiST, ST_DWithin, ST_MakeEnvelope)
  ↓
Authentication & Authorization (Argon2id, JWT, RBAC)
  ↓
Redis (In-Memory Data Structures)
  ↓
Caching (Cache-Aside, SHA-256 Hashing, SCAN Invalidation)
  ↓
Rate Limiting (Sliding Window Log via Redis ZSET)
  ↓
Routing / External APIs (Async Httpx, OSRM, Haversine)
  ↓
Deterministic Ranking (MCDA 6-Factor Normalization)
  ↓
AI Provider Integration (Ollama Local, Gemini Cloud, Pydantic Firewall)
  ↓
Conversational Backend Orchestration (Stateless State Reducer)
  ↓
Backend Testing Fundamentals (Pytest, Fixtures, Mocking)
  ↓
Docker Fundamentals (Docker Compose, Healthchecks)
  ↓
System Design (Tradeoffs, Bottlenecks, Scaling 10k → 1M users)
```

---

## 2. How to Study This Repository (The 3-Pass Backend Study System)

### Pass 1: UNDERSTAND (Mental Models & System Architecture)
*Goal: Understand how the backend works, why each decision was made, and how data flows through the system.*
1. Read [`ARCHITECTURE.md`](ARCHITECTURE.md) to understand the backend modular monolith layout, Docker Compose topology, and database schema.
2. Read [`BACKEND_MASTER_BOOK.md`](BACKEND_MASTER_BOOK.md) for deep textbook chapters on FastAPI request lifecycles, PostGIS spatial indexing, 6-Factor ranking math, Redis caching, and multi-provider AI failover.
3. Read [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md) to internalize the 15 architectural tradeoffs, technology necessity, failure mode mitigations, and scaling roadmaps.

### Pass 2: BUILD (Hand-Rebuild & Active Recall)
*Goal: Gain hands-on muscle memory by coding the core mechanisms from scratch without AI assistance.*
1. Follow the **48 Backend Engineering Stories** in [`BACKEND_ENGINEERING_STORIES.md`](BACKEND_ENGINEERING_STORIES.md).
2. Execute the **10 Cumulative Mastery Demonstrations (CMDs)** in [`BACKEND_ROADMAP.md`](BACKEND_ROADMAP.md).
3. Practice the 8 Live Backend Debugging Labs and 5 Rebuild Challenges in [`ACTIVE_RECALL.md`](ACTIVE_RECALL.md).

### Pass 3: INTERVIEW (Pitch, Defend & Whiteboard)
*Goal: Flawlessly communicate your technical expertise in senior backend and system design interviews.*
1. Rehearse the 30-second and 2-minute elevator pitches in [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md).
2. Master the Top 25 Backend/System Design STAR-format answers in [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md).
3. Practice sketching the 10 Whiteboard Challenge Blueprints.
4. Review the 12 Red Flags to avoid during interviews.
5. Study the complete Senior Backend Mock Interview transcript.

---

## 3. What to Study vs What to Ignore

| Category | What to Study (ESSENTIAL & IMPORTANT) | What to Ignore (REMOVED FROM CURRICULUM) |
| :--- | :--- | :--- |
| **Backend & Spatial** | FastAPI, Pydantic v2, SQLAlchemy 2.0, Asyncpg, PostGIS `Geometry(Point, 4326)`, GiST indexes, `ST_DWithin`, `ST_MakeEnvelope`, GeoJSON serializers. | Next.js internals, React components, Tailwind CSS, MapLibre rendering. |
| **Caching & Limiting** | Redis Cache-Aside, SHA-256 key hashing, SCAN invalidation, Redis ZSET sliding-window rate limiter, Fail-open policy. | Redis Cluster sharding, Raft consensus, complex multi-region replication. |
| **AI Orchestration** | Provider Abstract Interface, Ollama (local) + Gemini (cloud), Pydantic validation firewall, SearchOrchestrator stateless state reducer. | Token streaming, LLM fine-tuning, autonomous agent frameworks. |
| **DevOps & Testing** | Dockerfile, Docker Compose local orchestration, Pytest async fixtures, dependency overrides, integration test suites. | Kubernetes, Helm, CI/CD GitHub Actions matrices, Playwright browser tests, Testcontainers, Prometheus/OpenTelemetry agents. |

---

## 4. The 9 Canonical Documents Library

| # | Document | Role & Purpose | Recommended Focus |
| :-: | :--- | :--- | :--- |
| 1 | [`README.md`](README.md) | **Single Entry Point**, Backend Learning Path, Study Order. | All Learners |
| 2 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Authoritative backend architecture, container topology, database schema, services, and Mermaid diagrams. | Architecture & SDE Study |
| 3 | [`BACKEND_MASTER_BOOK.md`](BACKEND_MASTER_BOOK.md) | In-depth backend engineering textbook (FastAPI, PostGIS, Ranking, Routing, AI, Caching, Rate Limiting, API Contract). | Deep Technical Study |
| 4 | [`BACKEND_ENGINEERING_STORIES.md`](BACKEND_ENGINEERING_STORIES.md) | 48 deep backend engineering stories organized into 15 modules with 11-section high-signal format. | Hands-On Implementation |
| 5 | [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md) | Requirement-driven system design case study, 15 core architectural tradeoffs, technology necessity, failure modes, scaling evolution. | System Design Prep |
| 6 | [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) | Senior Backend & System Design interview guide (Pitches, Top 25 STAR Q&As, 10 Whiteboard challenge blueprints, Mock interview). | Interview Practice |
| 7 | [`ACTIVE_RECALL.md`](ACTIVE_RECALL.md) | 50 Backend active recall drills with hidden answer keys, 8 topic-specific live debugging labs, and 5 rebuild challenges. | Self-Assessment |
| 8 | [`BACKEND_ROADMAP.md`](BACKEND_ROADMAP.md) | 15-module progression path, 10 Cumulative Mastery Demonstrations (CMDs), and 4-week study plan. | Study Planning |
| 9 | [`BACKEND_DEPENDENCY_GRAPH.md`](BACKEND_DEPENDENCY_GRAPH.md) | Visual Mermaid DAG of prerequisite dependencies across all 48 backend stories. | Prerequisites Mapping |

---

## 5. Implementation & Verification Status
- **Total Backend Stories:** 48
- **Essential Backend Stories:** 37
- **Important Backend Stories:** 11
- **Automated Regression Status:** 288/288 Backend Pytest Passed | 100% Executable Code Truth

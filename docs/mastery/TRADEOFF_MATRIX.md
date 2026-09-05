# EstateMap AI — Architectural Tradeoff Matrix

This document provides in-depth technical comparisons of major architectural decisions, evaluating alternatives, pros, cons, and the exact reasons EstateMap AI adopted its specific approach.

---

## 1. Modular Monolith vs. Microservices

| Architecture | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Modular Monolith (Chosen)** | • Single codebase, single deployment unit.<br>• ACID database transactions across domains.<br>• Zero network latency between modules.<br>• Simplified debugging and testing.<br>• Low operational complexity (1 container per tier). | • Shared CPU/memory resources.<br>• Scaling is coarse-grained (entire app scales together).<br>• Requires strict internal module discipline to prevent spaghetti code. | **Right-sized architecture**: For a team of 1–10 engineers and 100k DAU, microservices introduce distributed transaction complexity, network latency, and gRPC overhead with zero business benefit. |
| **Microservices (Rejected)** | • Independent deployments per domain (Auth, Search, AI).<br>• Independent technology stacks and autoscaling.<br>• Fine-grained failure isolation. | • Requires distributed transactions (Saga / 2PC).<br>• High network latency on inter-service calls.<br>• Complex CI/CD, Kubernetes, and service mesh overhead.<br>• Massive debugging and distributed tracing friction. | **Premature Optimization**: Unjustified complexity for the current problem space. Clear domain boundaries inside the monolith allow clean future service extraction if necessary. |

---

## 2. PostGIS in PostgreSQL vs. External Spatial Search Engine (Elasticsearch)

| Architecture | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **PostGIS in PostgreSQL (Chosen)** | • Single source of truth (zero data synchronization delay).<br>• Native relational JOINs with property amenities, prices, and owners.<br>• ACID transactional updates.<br>• Full spatial SQL predicate library (`ST_DWithin`, `ST_MakeEnvelope`, `ST_DistanceSphere`). | • Spatial calculations consume database CPU.<br>• Advanced full-text fuzzy linguistic search is simpler in dedicated search engines. | **Zero Data Replication**: Eliminates dual-write anomalies, change-data-capture (CDC) pipelines, and Debezium/Kafka sync infrastructure. PostGIS handles millions of points easily on standard hardware. |
| **Elasticsearch / OpenSearch (Rejected)** | • Fast distributed full-text fuzzy search.<br>• Highly scalable horizontal document sharding. | • Eventual consistency (indexing lag).<br>• Requires complex CDC sync pipeline (Debezium/Kafka).<br>• Heavy JVM memory footprint.<br>• Weaker spatial relational join capabilities. | **Excessive Operational Burden**: Adding Elasticsearch creates data drift risks without offering superior bounding-box performance over PostGIS GiST indexing for real estate listing volumes. |

---

## 3. Deterministic Heuristic Ranking vs. Machine Learning (ML) Ranking

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Deterministic Heuristics (Chosen)** | • 100% explainable and audit-proof.<br>• Zero cold start problem (works instantly without historical logs).<br>• Real-time parameter tuning (user controls weights).<br>• Sub-millisecond arithmetic computation.<br>• Fully reproducible across test suites. | • Cannot automatically discover hidden non-linear user preference patterns.<br>• Requires manual mathematical formula design. | **Transparency & Cold Start**: Real estate buyers demand to know *why* a property is ranked #1. With zero historical click logs, ML models cannot be trained safely. |
| **Machine Learning / Learning-to-Rank (Rejected)** | • Automatically learns complex multi-feature interactions.<br>• Continuously optimizes for click-through rate (CTR) or conversion. | • Black-box scoring (impossible to explain clearly to users).<br>• Severe cold start failure without massive interaction datasets.<br>• Susceptible to popularity bias and data drift.<br>• Expensive training and model serving infrastructure. | **Premature & Unexplainable**: ML ranking is appropriate only after accumulating millions of interaction events. Deterministic math provides the reliable baseline required today. |

---

## 4. OSRM Self-Hosted vs. Commercial Routing APIs (Google Maps Distance Matrix)

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **OSRM Self-Hosted Engine (Chosen)** | • Zero per-query API costs.<br>• Sub-5ms road route calculation on local road graph.<br>• High throughput (thousands of matrix routes/sec).<br>• Complete data sovereignty. | • Requires hosting and maintaining road network graph data files (.osm.pbf).<br>• Live real-time traffic congestion data is not included in base OSM. | **Cost & Throughput Control**: Calculating commute times for 50 properties across 4 travel modes would cost \$1.00+ *per search query* on Google Maps ($5.00/1000 requests), making the product financially non-viable at scale. |
| **Google Maps / Mapbox APIs (Rejected)** | • Live real-time traffic congestion modeling.<br>• Global zero-setup cloud endpoint. | • Exorbitant per-request API costs.<br>• Strict rate limits and network latency bottlenecks.<br>• Vendor lock-in. | **Unsustainable Cost**: For high-volume ranking matrices, commercial APIs impose extreme financial and rate-limiting penalties. |

---

## 5. Explicit State Machine vs. Autonomous Agent (LangGraph / AutoGPT)

| Approach | Pros | Cons | Why EstateMap Chose This |
| :--- | :--- | :--- | :--- |
| **Explicit State Machine (Chosen)** | • 100% deterministic state transitions (`SET`, `CLEAR`, `APPEND`, `RESET`).<br>• State is fully inspectable, serializable, and debuggable.<br>• Bounded execution latency (<1.5s).<br>• Impossible for LLM to enter infinite loops or hallucinate non-existent database mutations. | • Requires predefined state schema (`ConversationalSearchState`). | **Safety & Determinism**: Real estate search requires strict adherence to spatial bounds and filter constraints. Autonomous agents suffer from hallucinations, non-deterministic loops, and unmanageable latency. |
| **Autonomous Multi-Agent / LangGraph (Rejected)** | • Free-form autonomous multi-step reasoning.<br>• Dynamic tool invocation graphs. | • Unbounded latency (10–45s per user message).<br>• High hallucination and infinite loop risks.<br>• Massive token costs.<br>• Flaky test verification. | **Unacceptable Latency & Flakiness**: A search interface must respond in <1.5 seconds. Multi-agent loops are completely unsuited for synchronous conversational search. |

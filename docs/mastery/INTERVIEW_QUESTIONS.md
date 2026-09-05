# EstateMap AI — Comprehensive Technical Interview Question Bank (200+ Questions)

This question bank contains over 200 real-world senior backend, system design, and geospatial engineering interview questions tailored directly to the EstateMap AI codebase. Complete answers at three depths (30-Second Elevator, 2-Minute Standard, and Deep-Dive Follow-up) are provided in [`INTERVIEW_ANSWERS.md`](file:///d:/FastAPI/EstateMap/docs/mastery/INTERVIEW_ANSWERS.md).

---

## 1. System Design & High-Level Architecture
1. Walk me through the high-level architecture of EstateMap AI.
2. Why did you choose a Modular Monolith instead of Microservices?
3. Under what scale conditions or organizational constraints would you split this into microservices?
4. How do you ensure modular boundaries are maintained within a monolithic codebase?
5. How would you design this system to scale from 100k DAU to 10 million DAU?
6. What is the single biggest bottleneck in this architecture under 100x traffic?
7. How does the system achieve high availability when external dependencies (like LLMs or OSRM) experience outages?
8. Explain the data flow for an interactive map bounding-box search from click to render.
9. How would you add a notifications system when a property matching user criteria is listed?
10. Why did you not use Kafka or RabbitMQ in the current implementation?
11. How would you design listing ingestion from multiple external MLS feeds?
12. Where would you place a Content Delivery Network (CDN) and what would it cache?
13. How do you prevent data drift between your relational database and cache?
14. How would you design multi-region database replication for this platform?
15. What are the tradeoffs between eventual consistency and strong consistency in real estate discovery?

---

## 2. FastAPI, Async Python & Concurrency
16. How does FastAPI's async execution model work under the hood?
17. What is the difference between ASGI and WSGI?
18. Explain how the Python `asyncio` event loop handles non-blocking I/O.
19. What happens if CPU-bound calculation or blocking synchronous code runs inside an async FastAPI route?
20. How would you offload heavy CPU-bound ranking calculations without blocking the event loop?
21. How does FastAPI's dependency injection system manage database connection lifecycles?
22. What is the purpose of using `yield` inside dependency functions like `get_db()`?
23. How do you implement request-scoped correlation IDs across async task chains?
24. How does Pydantic v2 achieve sub-millisecond data validation?
25. Explain the RFC 7807 problem details specification and how you implemented centralized error handling.
26. What is the difference between `asyncio.gather()` and `asyncio.create_task()`?
27. How do you prevent connection pool exhaustion in async SQLAlchemy?
28. What is `contextvars` and why can't global variables be used in async Python?
29. How do you implement custom ASGI middleware in FastAPI?
30. Explain how FastAPI handles route matching and parameter parsing.

---

## 3. PostgreSQL, PostGIS & Database Engineering
31. How does PostGIS store geographic coordinates in PostgreSQL?
32. What is SRID 4326 (WGS 84) and why is it the standard for GPS coordinates?
33. Explain the internal working of a PostGIS GiST (Generalized Search Tree) spatial index.
34. Why do standard B-Tree indexes fail for 2D spatial queries?
35. What is the difference between PostGIS `geometry` and `geography` types?
36. How does the `ST_MakeEnvelope` function work in bounding-box viewport searches?
37. Explain the PostGIS `&&` 2D bounding-box intersection operator.
38. How does `ST_DWithin` perform spherical distance filtering in meters?
39. What is the difference between `ST_Distance` and `ST_DistanceSphere`?
40. Why must coordinates strictly follow `POINT(longitude latitude)` ordering in PostGIS?
41. How did you structure relational foreign keys between users, properties, and amenities?
42. What is the difference between `ON DELETE CASCADE` and `ON DELETE RESTRICT`?
43. How do you detect and prevent N+1 query problems in SQLAlchemy async relationships?
44. How does Alembic track and apply database migrations safely?
45. What are the four ACID properties and how does PostgreSQL guarantee them?
46. What is PostgreSQL's default transaction isolation level and what anomalies does it prevent?
47. How would you shard a PostGIS database if listing volume grew to 100 million properties?
48. What is the difference between an R-Tree index and a Quadtree / Geohash index?
49. How do you optimize slow spatial queries using `EXPLAIN ANALYZE`?
50. Why is `DECIMAL` / `Numeric` preferred over `FLOAT` for storing property prices?

---

## 4. Redis In-Memory Caching & Sliding-Window Rate Limiting
51. What is the Cache-Aside pattern and how did you implement it in EstateMap?
52. How did you design your Redis cache keys to ensure deterministic cache hits?
53. Why are floating-point coordinates rounded to 4 decimal places in cache keys?
54. What TTL strategy did you choose for commute routes, POIs, and ranking results?
55. Explain Cache Stampede, Cache Penetration, and Cache Avalanche, and your mitigations.
56. What happens if Redis crashes? Explain your fail-open degradation strategy.
57. Why did you choose a Sliding-Window Log rate limiter over a Fixed-Window counter?
58. Explain the mathematical 2x boundary burst vulnerability in fixed-window rate limiters.
59. Walk me through the exact Redis Sorted Set (`ZSET`) commands in your rate limiter.
60. What is stored as the member and what is stored as the score in the rate limit `ZSET`?
61. How does your rate limiter identify unauthenticated versus authenticated users?
62. What HTTP status code and header are returned when a rate limit is exceeded?
63. Why is running `KEYS *` dangerous in production Redis, and what should be used instead?
64. How does `aioredis` manage asynchronous connection pools?
65. What is the memory footprint of storing rate limit logs for 100,000 active users in Redis?

---

## 5. Commute, Routing & Location Intelligence
66. Why can't PostGIS calculate realistic driving times to employment hubs?
67. What is OSRM (Open Source Routing Machine) and how does it model road networks?
68. How does EstateMap abstract routing engines via the `RoutingProvider` protocol?
69. What travel modes does your commute service support?
70. How does the system handle an OSRM server timeout or network failure?
71. What is the spherical distance fallback formula used when OSRM is offline?
72. How do you compute a 1-to-N commute matrix efficiently for 50 candidate properties?
73. Why is route geometry serialized as an RFC 7946 GeoJSON LineString?
74. How does `LocationIntelligenceService` aggregate surrounding amenities?
75. What urban POI categories are tracked in the database?
76. How do you calculate the nearest POI and distance for each category in a single query?
77. Why are property amenities and geographic POIs modeled as separate domain entities?
78. How does the frontend render the active commute route polyline on MapLibre?
79. How is hard commute duration filtering (`max_commute_minutes`) enforced?
80. What are the memory and latency tradeoffs of pre-computing vs on-demand routing?

---

## 6. Deterministic Multi-Factor Ranking & Comparison
81. What are the 6 dimensions in your deterministic ranking algorithm?
82. Walk me through the mathematical formula for the Price Match score.
83. Walk me through the mathematical formula for the Bedroom Match score.
84. Walk me through the mathematical formula for the Living Area score.
85. Walk me through the mathematical formula for the Locality Match score.
86. Walk me through the mathematical formula for the POI Proximity score.
87. Walk me through the mathematical formula for the Commute Duration score.
88. What happens when a user does not specify a commute destination?
89. Explain dynamic missing-factor weight redistribution mathematically.
90. How do you compute the individual percentage contribution of each factor?
91. How are ranking ties broken deterministically?
92. Why did you choose deterministic heuristic equations over Machine Learning ranking?
93. What is the cold-start problem in machine learning recommendation engines?
94. How does `ComparisonService` compute side-by-side property comparison deltas?
95. How are dimension winners (Price, Area, Commute) determined mathematically?
96. What is the maximum number of properties that can be compared simultaneously and why?
97. What is the role of AI in property comparison?
98. Why is the AI strictly prohibited from computing mathematical deltas or winners?
99. Where is comparison state persisted on the frontend?
100. How does the frontend handle navigating to `/compare?ids=103,107`?

---

## 7. AI Multi-Provider Architecture, Safety & "Ask the Map"
101. How is the `AIProvider` protocol structured in `backend/app/ai/base.py`?
102. What LLM models are supported across local and cloud environments?
103. How does `AIProviderRouter` decide whether to route a query to Gemini or Ollama?
104. What heuristics does your query complexity scorer evaluate?
105. What is the global request deadline and how is it divided across providers?
106. What happens if both Google Gemini and Ollama fail or timeout?
107. How does `DeterministicFallbackProvider` generate structured search patches?
108. How do you enforce strict JSON schema output from Google Gemini?
109. What is prompt injection and how could an attacker exploit a real estate search bar?
110. Explain your defense-in-depth security model against prompt injection.
111. Does the LLM have direct access to execute SQL queries or shell commands?
112. How does the system validate extracted geographic coordinates against hallucination?
113. What is "Ask the Map" and why is it modeled as a finite state machine?
114. Explain the difference between `ConversationalSearchState` and `SearchStatePatch`.
115. How does the `apply_patch()` state reducer handle `SET`, `CLEAR`, `APPEND`, and `RESET`?
116. Trace a 3-turn search refinement conversation through state transitions S0 -> S1 -> S2 -> S3.
117. How does "Ask the Map" resolve queries like "Compare top 2" to specific property IDs?
118. What is `LocationResolver` and how does it handle unknown or ambiguous landmark names?
119. How does the frontend display AI patch feedback badges (+ Added, ✏️ Modified, ✕ Cleared)?
120. Why does EstateMap not use autonomous multi-agent frameworks like LangGraph?

---

## 8. Frontend Architecture & MapLibre WebGL Integration
121. How is the Next.js 14 App Router organized in this project?
122. What is the difference between React Server Components (RSC) and Client Components?
123. Why is the search page marked with `"use client"`?
124. What library manages asynchronous client state and caching in the frontend?
125. Why did you choose MapLibre GL JS over Leaflet or Google Maps JS SDK?
126. How does MapLibre render vector map tiles using WebGL hardware acceleration?
127. Explain how bidirectional selection synchronization works between listing cards and map markers.
128. How does clicking a map pin scroll the corresponding card into view smoothly?
129. How does the "Search this area" button transition state when the user pans the map?
130. How does `FavoritesProvider` persist saved properties in `localStorage`?
131. How does `FavoritesProvider` prevent hydration mismatch errors during Next.js SSR?
132. How does `FavoritesProvider` synchronize saved properties across multiple open browser tabs?
133. What custom window event is dispatched when a property is saved or removed?
134. How does the Header navigation bar display the live count of saved properties?
135. What utility is used to merge conditional Tailwind CSS class names?
136. How is responsive layout handled between mobile and desktop on the search page?
137. How are loading skeletons implemented in `PropertyGrid`?
138. How does `PropertyDetailPage` handle invalid or non-numeric property IDs?
139. How do you convert backend property entities into RFC 7946 GeoJSON in TypeScript?
140. How does the frontend handle API client errors gracefully?

---

## 9. Security, Authentication & Cryptography
141. Explain the anatomy of a JSON Web Token (JWT) using HMAC-SHA256 (HS256).
142. Why is JWT stateless and what are the tradeoffs compared to server-side session cookies?
143. How do you verify a JWT signature in FastAPI dependency injection?
144. What claims are included in EstateMap's JWT payload (`sub`, `user_id`, `role`, `exp`)?
145. Why did you choose Argon2id over MD5 or SHA-256 for password hashing?
146. How does salt generation prevent rainbow table attacks?
147. What is Insecure Direct Object Reference (IDOR) and how does your API prevent it?
148. How do you enforce resource ownership checks on property mutations (`PUT /properties/{id}`)?
149. How do you prevent user enumeration attacks during registration and password reset?
150. How do you handle JWT revocation if a user changes their password?

---

## 10. DevOps, Testing, Reliability & Observability
151. Walk me through the multi-container Docker Compose architecture.
152. How does container networking allow `estatemap-backend` to reach Postgres and Redis?
153. What is `host.docker.internal` and how does the backend container reach host Ollama?
154. How do healthchecks in `docker-compose.yml` ensure proper container startup order?
155. What is the structure of your testing pyramid (Unit, Spatial, Contract, Integration)?
156. How do you test async FastAPI endpoints using `httpx.AsyncClient`?
157. How do you isolate database state between integration tests?
158. How do you mock external network dependencies (OSRM, Gemini) in pytest?
159. What linter and code formatter do you use, and why is Ruff faster than Flake8/Black?
160. What is structured logging and why are logs formatted with correlation IDs?
161. What metrics would you monitor in production (QPS, p95 latency, error rates, cache hit ratio)?
162. How would you configure Prometheus and Grafana for backend observability?
163. How does the system handle database connection drops during an active transaction?
164. What happens if Redis runs out of memory (OOM)?
165. How do you seed 104 verified properties and 29 POIs idempotently on startup?
166. Explain the difference between fail-open and fail-closed degradation policies.
167. How do you ensure environment variables are never committed to version control?
168. How do you verify that PostGIS spatial queries use GiST indexes rather than Seq Scans?
169. What are the key production considerations before deploying this system to AWS?
170. How would you whiteboard EstateMap AI from scratch in a 45-minute system design interview?

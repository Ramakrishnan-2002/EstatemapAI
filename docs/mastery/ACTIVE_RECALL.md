# EstateMap AI — Active Recall Question Bank (250+ Questions)

> **Instructions**: Use this question bank for active self-testing. Questions range from basic syntax and code navigation to deep system design, edge cases, and failure modes.  
> *Complete answers are provided in [`ACTIVE_RECALL_ANSWERS.md`](file:///d:/FastAPI/EstateMap/docs/mastery/ACTIVE_RECALL_ANSWERS.md).*

---

## Category 1: Architecture & System Overview (Q1–Q25)
1. What architectural style does EstateMap AI use, and why was it chosen over microservices?
2. What are the 5 primary capabilities of the platform?
3. Where is the main FastAPI entrypoint defined in the repository?
4. What role does Docker Compose play in the development and runtime environment?
5. Why is the AI provider designated as "non-authoritative" in this system?
6. Which port does the FastAPI backend run on by default in Docker?
7. Which port does the Next.js frontend run on?
8. What database engine and spatial extension are used?
9. Why does EstateMap AI use Redis in addition to PostgreSQL?
10. How does the frontend communicate with the backend?
11. What is the standard coordinate ordering convention in PostGIS and GeoJSON?
12. What happens if a client passes coordinates in `[lat, lng]` order to PostGIS?
13. Why does the system not use an external vector database (like Pinecone or Milvus)?
14. Why is Elasticsearch / OpenSearch currently omitted from the architecture?
15. Under what specific business conditions would Apache Kafka become justified?
16. How does EstateMap handle database migrations across development and production?
17. What is the primary routing provider used for road-network travel times?
18. What local LLM runner is supported alongside Google Gemini?
19. What protocol decouples the backend services from specific LLM SDK implementations?
20. What is the purpose of the `X-Request-ID` header?
21. What RFC standard governs error response formats in EstateMap?
22. What RFC standard governs GeoJSON spatial payloads?
23. Where are application settings and environment variables parsed and validated?
24. How many total tests currently exist in the backend test suite?
25. What is the role of `MapLibre GL JS` in the frontend?

---

## Category 2: FastAPI & Async Python (Q26–Q55)
26. What is the difference between ASGI and WSGI?
27. Why does FastAPI use ASGI servers like Uvicorn?
28. What is the Python Event Loop and how does it handle non-blocking I/O?
29. What happens to the Python event loop if a developer calls synchronous `time.sleep(5)` inside an async route?
30. How does FastAPI's dependency injection (`Depends`) manage database connection lifecycles?
31. Where is the `get_db()` dependency implemented in the codebase?
32. What does the `yield` statement in `get_db()` accomplish?
33. Why is `await session.rollback()` placed in the exception block of `get_db()`?
34. What is the difference between `asyncpg` and standard `psycopg2`?
35. How does Pydantic v2 achieve significantly faster validation speeds compared to v1?
36. What is the purpose of `pydantic-settings` in `backend/app/core/config.py`?
37. How does FastAPI automatically generate OpenAPI (Swagger) documentation?
38. Where are custom exception handlers registered in FastAPI?
39. What is the lifespan context manager (`@asynccontextmanager`) in `backend/app/main.py`?
40. How does middleware intercept incoming requests before route handlers execute?
41. What is `contextvars` and why is it used for request ID tracking in async Python?
42. How do you return a custom header (like `X-Request-ID`) from an ASGI middleware?
43. What is the difference between HTTP 400, 401, 403, 404, 422, and 429 status codes?
44. How does Pydantic validate that a latitude value is between -90 and 90?
45. Why should database models never be returned directly from route handlers?
46. What does `model_config = ConfigDict(from_attributes=True)` do in Pydantic?
47. How does FastAPI handle background tasks?
48. What is the purpose of `NullPool` in test database configurations?
49. How do you mock an async service dependency in Pytest?
50. What is `httpx.ASGITransport` and how does it accelerate integration tests?
51. How does FastAPI handle path parameters vs query parameters vs request bodies?
52. What happens when a request payload fails Pydantic schema validation?
53. How do you write an async generator in Python?
54. What is the difference between `asyncio.gather()` and sequential `await` calls?
55. How do you set connection pool limits in `create_async_engine()`?

---

## Category 3: PostgreSQL & PostGIS (Q56–Q90)
56. What does SRID 4326 represent?
57. What is the difference between PostGIS `geometry` and `geography` types?
58. Why does EstateMap store coordinates as `geometry(Point, 4326)`?
59. How do you convert a PostGIS geometry to meters when calculating spherical distance?
60. What is the PostGIS bounding-box intersection operator (`&&`)?
61. What does the PostGIS function `ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)` do?
62. What is a GiST (Generalized Search Tree) index and how does it work internally?
63. Why does a standard B-Tree index fail for 2D geographic coordinate searches?
64. What is the PostGIS function `ST_DWithin` and what arguments does it accept?
65. What is the difference between `ST_Distance` and `ST_DistanceSphere`?
66. How does `ST_AsGeoJSON(location)` serialize geometry data?
67. Where is the spatial query for bounding-box search implemented in the backend?
68. What relational table stores property records in PostgreSQL?
69. What is the foreign key relationship between `properties` and `users`?
70. Why is `ON DELETE RESTRICT` used on the `properties.owner_id` foreign key?
71. Why is `ON DELETE CASCADE` used on the `property_images.property_id` foreign key?
72. How is the many-to-many relationship between `properties` and `amenities` modeled?
73. What is the composite primary key of the `property_amenities` table?
74. How does Alembic track the current database migration revision?
75. Where are Alembic migration scripts stored in the repository?
76. Why must `CREATE EXTENSION IF NOT EXISTS postgis;` run in the very first migration?
77. What is an N+1 query problem in SQLAlchemy and how does `selectinload` prevent it?
78. How do you write a PostGIS point constructor in SQLAlchemy using GeoAlchemy2?
79. What is the difference between `ST_SetSRID` and `ST_Transform`?
80. How does PostGIS evaluate an R-Tree index scan vs a sequential table scan?
81. What EXPLAIN command do you use in PostgreSQL to verify index usage?
82. What does `Index('idx_properties_location_gist', 'location', postgresql_using='gist')` do?
83. How are property prices stored in PostgreSQL to prevent floating-point rounding errors?
84. What is a database transaction and what does ACID stand for?
85. What is the default transaction isolation level in PostgreSQL?
86. How does optimistic concurrency control differ from pessimistic locking?
87. What happens if an async SQLAlchemy session fails to commit due to a constraint violation?
88. How does `seed_all.py` restore database records without creating duplicate rows?
89. How many properties and POIs are seeded in the default development database?
90. What Indian cities are currently supported in the seeded dataset?

---

## Category 4: Redis Caching & Rate Limiting (Q91–Q120)
91. What is Redis and why is it categorized as an in-memory data store?
92. What is the Cache-Aside (Lazy Loading) caching pattern?
93. What is the TTL (Time-to-Live) strategy used for commute routes in EstateMap?
94. What is the TTL used for POI location intelligence in EstateMap?
95. What is the TTL used for ranked search results in EstateMap?
96. How are Redis cache keys formatted for commute routes in `cache_keys.py`?
97. Why are floating-point coordinates rounded (e.g. `:.4f`) in cache key generation?
98. What is a Cache Stampede and how does TTL jitter mitigate it?
99. What is Cache Penetration and how does caching null/empty results prevent it?
100. What is Cache Avalanche and how do staggered expirations mitigate it?
101. What happens to search queries in EstateMap if the Redis container stops running?
102. What does "Fail-Open" mean in the context of caching and rate limiting?
103. What is the difference between a Fixed-Window counter and a Sliding-Window log rate limiter?
104. Why can a Fixed-Window rate limiter allow up to 2x the configured limit at window boundaries?
105. What Redis data structure does EstateMap use to implement sliding-window rate limiting?
106. What is a Redis Sorted Set (`ZSET`) and what are members and scores?
107. In EstateMap's rate limiter, what value is stored as the score in the Redis Sorted Set?
108. What Redis command prunes expired timestamps from the sliding window?
109. What Redis command counts the remaining requests in the sliding window?
110. What Redis command adds the current request timestamp to the set?
111. What HTTP status code is returned when a client exceeds the rate limit?
112. What HTTP header tells the client how many seconds to wait after a 429 response?
113. How does the rate limiter determine client identity for unauthenticated users?
114. How does the rate limiter determine client identity for authenticated users?
115. Why should `KEYS` never be run in production Redis, and what command should be used instead?
116. What is the memory footprint of storing 1,000 sliding-window rate limit entries in Redis?
117. What is the difference between Redis `EXPIRE` and `PEXPIRE`?
118. How does `aioredis` manage connection pooling in async Python?
119. What is the difference between `UNLINK` and `DEL` in Redis?
120. How does Redis achieve sub-millisecond read and write latency?

---

## Category 5: Routing & Commute Intelligence (Q121–Q145)
121. What is OSRM and what does the acronym stand for?
122. Why does EstateMap not use PostGIS straight-line distance to calculate commute times?
123. What travel modes are supported by EstateMap's routing system?
124. What is the `RoutingProvider` protocol in `backend/app/services/routing_service.py`?
125. What is the role of `MockRoutingProvider` in the test suite?
126. What OSRM HTTP endpoint calculates a route between two coordinate pairs?
127. What fields does OSRM return in its route response payload?
128. What happens if OSRM times out or is unreachable?
129. How does `CommuteService` estimate travel time during an OSRM fallback?
130. What is a 1-to-N commute matrix calculation?
131. Why is route geometry serialized as an RFC 7946 GeoJSON `LineString`?
132. What coordinate ordering does OSRM URL pathing expect (`{lng},{lat}` or `{lat},{lng}`)?
133. Where are major verified employment hubs defined for Chennai and Bengaluru?
134. Name three verified employment hubs in Chennai included in the platform presets.
135. Name three verified employment hubs in Bengaluru included in the platform presets.
136. What is the default travel mode if none is specified by the user?
137. How does `CommutePanel` in the frontend render the commute route on MapLibre?
138. What color is used to display the active commute route LineString on the map?
139. How is a hard commute duration constraint (e.g. `max_commute_minutes=25`) enforced during search?
140. What is the maximum sensible driving radius in minutes before filtering out distant properties?
141. Why is routing separated from property CRUD in the service layer?
142. How does the backend prevent OSRM from being called multiple times for the same property and hub?
143. What is the time complexity of looking up a cached commute route in Redis?
144. How does OSRM model one-way streets and turn restrictions?
145. What file format does OSRM use for road-network graph data (`.osm.pbf`)?

---

## Category 6: Deterministic Ranking & Comparison (Q146–Q175)
146. What are the 6 factors evaluated by the deterministic ranking engine?
147. What is the mathematical formula for the Price Score ($S_{\text{price}}$)?
148. What is the mathematical formula for the Bedroom Score ($S_{\text{bedrooms}}$)?
149. What is the mathematical formula for the Area Score ($S_{\text{area}}$)?
150. What is the mathematical formula for the Locality Score ($S_{\text{locality}}$)?
151. What is the mathematical formula for the POI Location Score ($S_{\text{location}}$)?
152. What is the mathematical formula for the Commute Score ($S_{\text{commute}}$)?
153. What is the maximum possible score for any individual factor before weighting?
154. What is the default weight distribution for the "Balanced" preset?
155. What is the default weight distribution for the "Commute First" preset?
156. What is the default weight distribution for the "Budget First" preset?
157. What happens when a user specifies no commute destination during a ranked search?
158. How does dynamic missing-factor weight redistribution work mathematically?
159. What is the formula for calculating factor contribution in percentage points?
160. How are ties broken when two properties receive the exact same final score?
161. Why is the ranking engine 100% deterministic rather than machine-learning based?
162. What is the cold-start problem in machine learning recommendation systems?
163. What is the time complexity of ranking $P$ properties across 6 factors?
164. What service computes side-by-side property comparison deltas?
165. What arithmetic metrics are compared in `ComparisonService`?
166. How does `ComparisonService` determine the "Price Winner" between two listings?
167. How does `ComparisonService` determine the "Living Area Winner"?
168. How does `ComparisonService` determine the "Commute Winner"?
169. What is the maximum number of properties that can be compared simultaneously?
170. Where is comparison state persisted on the frontend?
171. What is the role of AI in the property comparison workflow?
172. Why is the AI not allowed to compute arithmetic deltas or determine dimension winners?
173. What component renders the comparison bar drawer at the bottom of the frontend?
174. How does the frontend handle navigating to `/compare?ids=103,107`?
175. What happens if a user tries to compare 4 properties simultaneously?

---

## Category 7: AI Multi-Provider Architecture & Safety (Q176–Q210)
176. What is the `AIProvider` Python protocol in `backend/app/ai/base.py`?
177. What three providers implement the `AIProvider` protocol in EstateMap?
178. What local LLM models are supported via Ollama?
179. What cloud model is used via Google Gemini?
180. How does `evaluate_query_complexity()` determine whether to route a query to Gemini or Ollama?
181. What complexity score threshold routes a query to the cloud model?
182. What is the global request deadline for AI operations in `AIProviderRouter`?
183. If the primary provider consumes 7 seconds before failing, how much time is allocated to the secondary provider?
184. What happens if both cloud and local AI providers fail or timeout?
185. What is the `DeterministicFallbackProvider` and how does it generate responses?
186. How is structured JSON output enforced when querying Google Gemini?
187. What Pydantic model defines the output contract for conversational search intent?
188. What is prompt injection and how could an attacker attempt it in real estate search?
189. Why is prompt injection in EstateMap strictly bounded in blast radius?
190. Does the LLM have direct access to execute SQL queries or shell commands?
191. Does the LLM have access to database credentials or internal API tokens?
192. What are the allowed action enum values in `SearchStatePatch`?
193. How does the system validate extracted geographic coordinates against hallucination?
194. What is the role of `LocationResolver` in `backend/app/utils/location_resolver.py`?
195. How does `LocationResolver` handle unknown landmark names?
196. What is a clarification prompt in "Ask the Map"?
197. How does the frontend render clarification suggestions when an unknown hub is mentioned?
198. What telemetry metadata is returned in `AskMapResponse` (`latency_ms`, `provider`, `model`, `fallback_used`)?
199. Why does EstateMap not use LangChain or LangGraph?
200. What is the latency advantage of Google Gemini 2.5 Flash over local CPU Ollama inference?
201. What is the privacy advantage of Ollama over Google Gemini?
202. How does Docker networking allow `estatemap-backend` to reach Ollama on the host machine?
203. What is `host.docker.internal` in Docker desktop?
204. What is the keep-alive parameter in Ollama and why is it important for latency?
205. How are prompt versions tracked in the codebase?
206. What is the difference between temperature 0.0 and temperature 0.7 in LLM generation?
207. Why does EstateMap use low temperature ($\le 0.1$) for intent parsing?
208. How does the AI property explanation endpoint ensure explanations are factually grounded?
209. What happens if Gemini returns an HTTP 429 quota exceeded error?
210. How does the test suite verify AI failover without incurring real cloud API costs?

---

## Category 8: Conversational Search & State Machine (Q211–Q230)
211. What is the "Ask the Map" feature?
212. Why is Ask the Map modeled as an explicit state machine rather than passing chat history?
213. What fields are contained in `ConversationalSearchState`?
214. What fields are contained in `SearchStatePatch`?
215. What does the `SET` operation do in `apply_patch()`?
216. What does the `CLEAR` operation do in `apply_patch()`?
217. What does the `APPEND` operation do for POI categories?
218. What does the `REMOVE` operation do for POI categories?
219. What does the `RESET` operation do in `apply_patch()`?
220. Trace state transition: Start at S0 (Empty) -> User says "3 BHK under 1 Cr in Koramangala". What is S1?
221. Trace state transition: From S1 -> User says "Near hospitals and parks". What is S2?
222. Trace state transition: From S2 -> User says "Remove price limit". What is S3?
223. Trace state transition: From S3 -> User says "Compare top 2". What action is emitted?
224. How does `SearchOrchestrator` map "Compare top 2" to specific property IDs?
225. How does the frontend synchronize manual filter changes with conversational search state?
226. How does the frontend display the patch feedback badges (+ Added, ✏️ Modified, ✕ Cleared)?
227. What happens if a user submits an empty message in `AskTheMapBar`?
228. Where is `SearchOrchestrator` implemented in the backend?
229. How does `SearchOrchestrator` execute post-filtering against PostGIS after applying a patch?
230. Why is multi-turn state reduction testable with standard unit tests?

---

## Category 9: Frontend & UI State Architecture (Q231–Q250)
231. What version of Next.js is used in the frontend?
232. What is the difference between React Server Components (RSC) and Client Components (`"use client"`)?
233. Why is `frontend/app/search/page.tsx` marked with `"use client"`?
234. What React library manages asynchronous server state and caching in the frontend?
235. What is MapLibre GL JS and why is it preferred over Leaflet for vector maps?
236. How does the frontend convert property listings to GeoJSON?
237. How does clicking a listing card highlight and center the map marker?
238. How does clicking a map pin scroll the corresponding listing card into view?
239. What event in MapLibre detects when the user finishes panning or zooming the map?
240. How does the "Search this area" button transition between hidden and visible states?
241. Where is the persistent comparison state stored in the browser?
242. Where is the persistent saved properties (favorites) state stored in the browser?
243. How does `FavoritesProvider` prevent hydration mismatch errors during Next.js SSR?
244. How does `FavoritesProvider` synchronize saved properties across multiple open browser tabs?
245. What custom window event is dispatched when a property is saved or removed?
246. How does the Header navigation bar display the live count of saved properties?
247. What component renders property card loading states before data arrives?
248. What utility combines Tailwind CSS class names conditionally?
249. How is responsive layout handled on the search page between desktop and mobile screens?
250. How does `PropertyDetailPage` handle invalid property IDs (e.g. `/properties/abc`)?

---

## Category 10: DevOps, Quality & Failure Modes (Q251–Q260)
251. How do you run the complete backend test suite inside Docker?
252. How do you run the frontend unit test suite?
253. How do you run the frontend TypeScript type check?
254. What linter and code formatter is configured for the backend?
255. What command checks code formatting with Ruff?
256. What happens if PostgreSQL crashes during a multi-statement database transaction?
257. What happens if Redis runs out of memory (OOM)?
258. What happens if a user attempts to register an account with an email that already exists?
259. What happens if an expired JWT token is passed in the `Authorization: Bearer <token>` header?
260. What single command starts the entire multi-container EstateMap system from scratch?

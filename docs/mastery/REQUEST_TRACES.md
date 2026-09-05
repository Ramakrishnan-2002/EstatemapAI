# EstateMap AI — End-to-End Request Traces

This document traces critical user workflows step-by-step through the entire technical stack: Frontend -> HTTP Network -> FastAPI Router -> Middleware -> Dependency Injection -> Domain Service -> PostGIS / Redis / OSRM / LLM Provider -> Response Serialization.

---

## 1. User Authentication (Login) Trace

```
1. Frontend User Input: User enters email="user@example.com", password="SecurePassword123" on /login
2. Frontend Network: POST http://localhost:8000/api/v1/auth/login with JSON body
3. FastAPI Middleware:
   - RequestIDMiddleware generates X-Request-ID (e.g. "req_login_91a4")
   - RateLimitMiddleware checks Redis sliding window for key "estatemap:ratelimit:ip:{client_ip}:auth_login"
4. Route Handler: backend/app/api/v1/auth.py -> login(credentials: LoginRequest, db: AsyncSession)
5. Dependency Injection: get_db() yields active AsyncSession from async_session_factory()
6. Authentication Service: backend/app/services/auth_service.py -> authenticate_user()
   - Queries user by email: SELECT * FROM users WHERE email = 'user@example.com'
   - Verifies password hash using backend/app/core/security.py -> verify_password() via Argon2id
7. JWT Generation: backend/app/core/security.py -> create_access_token(data={"sub": user.email, "user_id": user.id})
   - Encodes HMAC-SHA256 signature with SECRET_KEY, exp = now + 1440 minutes
8. Response Serialization: Returns TokenResponse { access_token: "eyJ...", token_type: "bearer" }
9. Frontend Client: Stores token in localStorage and updates global authentication context.
```

---

## 2. Interactive Map Viewport Spatial Search Trace

```
1. Frontend Action: User pans/zooms map; MapLibre fires 'moveend' event.
2. Viewport Calculation: frontend/components/map/map-container.tsx extracts bounds { north: 13.08, south: 12.98, east: 80.28, west: 80.18 }.
3. User Click: User clicks "Search this area" floating button on /search.
4. Frontend Network: POST http://localhost:8000/api/v1/search/spatial
   - Request Body: { min_lat: 12.98, max_lat: 13.08, min_lng: 80.18, max_lng: 80.28, page: 1, page_size: 20 }
5. FastAPI Pipeline:
   - RequestIDMiddleware assigns X-Request-ID: "req_spatial_882b"
   - RateLimitMiddleware verifies sliding window limit.
   - Pydantic validates BoundingBoxSearchParams (checks latitude/longitude bounds).
6. Service & Repository Layer:
   - backend/app/services/geo_service.py -> search_properties_bbox()
   - backend/app/repositories/geo_repository.py executes PostGIS SQL:
     SELECT properties.*, ST_AsGeoJSON(properties.location) AS geojson
     FROM properties
     WHERE properties.location && ST_MakeEnvelope(80.18, 12.98, 80.28, 13.08, 4326)
       AND properties.status = 'active'
     ORDER BY properties.created_at DESC LIMIT 20;
7. PostGIS Kernel Execution: Evaluates spatial GiST index on properties.location using R-Tree bounding boxes.
8. Response Serialization: Maps database entities to PropertyListResponse with RFC 7946 GeoJSON features.
9. Frontend State Update: Next.js search page receives 20 properties, updates PropertyGrid, and updates MapLibre GeoJSON source markers.
```

---

## 3. Deterministic Ranked Search with Commute Route Trace

```
1. Frontend Action: User selects "Commute First" preset, chooses destination "TIDEL Park (OMR)", travel_mode="driving".
2. Frontend Network: POST http://localhost:8000/api/v1/recommendations/ranked
   - Body: {
       "filters": { "city": "Chennai", "bedrooms": 3 },
       "preferences": {
         "destination": { "name": "TIDEL Park", "latitude": 12.9897, "longitude": 80.2483 },
         "travel_mode": "driving",
         "weights": { "price": 0.15, "bedrooms": 0.15, "area": 0.10, "locality": 0.10, "location": 0.10, "commute": 0.40 }
       }
     }
3. FastAPI Pipeline: Validates RankedSearchRequest schema.
4. Ranking Service Execution: backend/app/services/ranking_service.py -> search_and_rank()
   - Step A: Filter candidate properties from PostGIS matching hard filters (city='Chennai', bedrooms=3).
   - Step B: For each candidate property (e.g. Property #103 at Lat 12.9228, Lng 80.1888):
     - Check Redis cache for commute key: `estatemap:commute:v1:p103:d12.9897_80.2483:mdriving`
     - Cache Miss: Call CommuteService -> OSRMProvider HTTP call:
       GET http://router.project-osrm.org/route/v1/driving/80.1888,12.9228;80.2483,12.9897?overview=full&geometries=geojson
     - OSRM returns: duration = 1320s (22.0 mins), distance = 14200m.
     - Store route in Redis with TTL = 86400s (24h).
   - Step C: Calculate 6 mathematical factor scores:
     - Price Score = 0.92
     - Bedrooms Score = 1.00
     - Area Score = 0.88
     - Locality Score = 0.00
     - POI Location Score = 0.80
     - Commute Score = max(0, 1 - 22.0/60) = 0.633
   - Step D: Multiply by normalized weights and sum: FinalScore = 81.42%.
5. Response: Returns RankedPropertyResponse sorted descending by final_score with exact score_breakdown.
6. Frontend Render: RankedPropertyCard displays #1 Match badge, 81.4% score pill, and expandable factor bars.
```

---

## 4. "Ask the Map" Conversational Search Trace

```
1. Frontend User Input: User types: "3 BHK under 1.5 Cr in Adyar near hospitals" in AskTheMapBar.
2. Frontend Network: POST http://localhost:8000/api/v1/ai/ask-map
   - Body: {
       "message": "3 BHK under 1.5 Cr in Adyar near hospitals",
       "session_id": "sess_9123",
       "current_state": { "city": "Chennai", "min_price": null, "max_price": null, "bedrooms": null, "preferred_poi_categories": [] }
     }
3. Orchestrator Entry: backend/app/services/search_orchestrator.py -> process_conversational_turn()
4. AI Provider Router:
   - Query complexity evaluated: Length=46, constraints=3 -> Routed to Google Gemini 2.5 Flash.
   - Dispatches structured prompt with JSON Schema enforcing SearchStatePatch.
5. LLM Structured Output:
   {
     "action": "search",
     "set_fields": { "bedrooms": 3, "max_price": 15000000, "locality": "Adyar" },
     "clear_fields": [],
     "add_poi_categories": ["hospital"],
     "remove_poi_categories": [],
     "reset_all": false,
     "assistant_message": "Filtering to 3 BHK properties in Adyar under ₹1.5 Cr with nearby hospitals.",
     "explanation_bullets": ["Set maximum price to ₹1.50 Cr", "Set bedrooms to 3", "Filtered locality to Adyar", "Added hospital access requirement"]
   }
6. State Reducer: apply_patch() updates current state -> new state: { bedrooms: 3, max_price: 15000000, locality: "Adyar", preferred_poi_categories: ["hospital"] }.
7. Direct Query Execution: Orchestrator executes PostGIS spatial/filter search with new state, returning matched properties.
8. Response Serialization: Returns AskMapResponse containing new canonical state, GeoJSON properties, and telemetry (latency=740ms, provider="gemini-2.5-flash").
9. Frontend UI Update: Map updates pins, search sidebar filters update to match new state, and AI feedback card shows exact patch badges (+ Added: hospital, ✏️ Modified: max_price).
```

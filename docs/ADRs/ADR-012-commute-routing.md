# ADR-012: Commute & Road Network Travel Intelligence Domain

## Status
Accepted

## Context
EstateMap AI requires road network travel intelligence to answer practical buyer/renter questions such as: *"How long does it take to drive from this property to my workplace during normal hours?"* and *"Which of these 3 shortlisted apartments has the shortest commute to Kempegowda International Airport?"*

Geographic proximity (Phase 7 PostGIS geodesic straight-line distance) cannot capture road topology, urban grid detours, natural barriers, traffic corridors, or travel mode variations (driving vs cycling vs walking). However, proprietary external routing APIs (Google Directions, Mapbox Directions) introduce latency, high financial cost, external rate limits, and failure modes if tightly coupled to core queries.

## Decisions

### D1: Pluggable Routing Provider Abstraction
- **Decision**: Define a formal `RoutingProvider` protocol (`app.services.routing.protocol.RoutingProvider`) with an abstract `get_route(origin_lat, origin_lng, dest_lat, dest_lng, mode)` interface and dynamic factory resolution (`get_routing_provider()`).
- **Why**: Allows seamless switching between a deterministic offline mock provider (`MockRoutingProvider`), self-hosted/public OSRM (`OSRMProvider`), OpenRouteService, or commercial routing engines without modifying service logic or API contracts.
- **Alternatives Considered**: Direct hardcoded calls to external APIs within routes. Rejected due to tight coupling and testing fragility.

### D2: Architectural Boundary: PostGIS Geodesic vs Road Network Routing
- **Decision**: Clearly partition geographic responsibilities:
  - **PostGIS (SRID 4326/Geography)**: Spatial indexing, radius containment, bounding boxes, polygon filtering, and spatial nearest-neighbor search.
  - **Routing Provider**: Road network distances (meters), travel durations (seconds), multi-modal routing profiles, and GeoJSON LineString route geometries.
- **Why**: Preserves PostGIS as the geographic source of truth for spatial queries while offloading pathfinding and graph traversal to specialized routing engines.

### D3: Strict RFC 7946 GeoJSON LineString Coordinate Ordering
- **Decision**: All route path geometries are serialized as GeoJSON `LineString` with strictly ordered `[longitude, latitude]` coordinate pairs.
- **Why**: Full adherence to RFC 7946 and seamless zero-conversion ingestion by mapcn and MapLibre GL `MapRoute` vector layers.
- **Alternatives Considered**: Returning encoded polylines (Google/OSRM polyline5/6 format). Rejected in favor of open, human-readable GeoJSON for transparency and client simplicity.

### D4: Ephemeral Route Caching in Redis with Graceful Degradation
- **Decision**: Cache computed routes in Redis with a 600-second (10-minute) TTL using normalized coordinate keys (`route:{provider}:{mode}:{round(lat1,4)},{round(lng1,4)}:{round(lat2,4)},{round(lng2,4)}`). If Redis is unavailable or fails, log the warning and execute the provider directly without failing user requests.
- **Why**: Drastically reduces external routing engine calls for popular destinations (e.g. tech parks, airports, metro stations) while ensuring high availability during cache outages.

### D5: Authoritative Database Coordinate Extraction
- **Decision**: For all property commute endpoints (`GET /properties/{id}/commute`, `POST /properties/{id}/commute/batch`), origin coordinates are extracted strictly from `Property.location` in the database. The client cannot supply or forge property coordinates.
- **Why**: Ensures spatial truth and prevents spoofing or mismatched location calculations.

### D6: Rate Limiting & Bound Payload Safeguards
- **Decision**: Impose strict validation limits on batch and comparison operations:
  - Batch commute: maximum 5 destinations per request (`MAX_COMMUTE_DESTINATIONS = 5`).
  - Property comparison: minimum 2, maximum 10 properties (`MAX_COMMUTE_COMPARE_PROPERTIES = 10`).
- **Why**: Prevents unbounded route fan-out, excessive connection starvation, and routing provider rate limiting.

### D7: Zero Stored Route Metrics in Property Tables
- **Decision**: Commute metrics (distance, duration, route geometry) are computed dynamically and never stored as columns on the `properties` table.
- **Why**: Commute targets are user-specific and travel conditions change. Storing fixed travel times to arbitrary places on a real estate listing introduces stale data and redundant schema bloat.

### D8: Deterministic Mock Engine for Offline Testing & CI/CD
- **Decision**: Implement `MockRoutingProvider` using Haversine calculation, mode-specific detour coefficients (1.30x driving, 1.20x cycling, 1.15x walking), realistic urban velocities, and multi-segment waypoint generation.
- **Why**: Guarantees fast, reproducible test execution in CI/CD without network dependencies or API keys.

### D9: Frontend mapcn `MapRoute` Integration & Reactive Viewport Fitting
- **Decision**: Integrate official mapcn `<MapRoute>` component directly into `EstateMap`, with reactive bounding box fitting (`map.fitBounds`) whenever a route is selected in `CommutePanel`.
- **Why**: Delivers an immediate visual representation of the driving/walking route on the property detail map.

## Consequences
- EstateMap AI gains practical, network-aware commute intelligence with sub-50ms cached response times.
- Subsequent ranking and recommendation phases can consume verified travel times to evaluate commute feasibility for buyers and tenants.

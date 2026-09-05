# ADR-010: PostGIS Geospatial Search (Radius, Bounding Box, Viewport & Polygon)

## Status
Accepted

## Context
EstateMap AI is a location-first discovery platform. In traditional web applications, map widgets often fetch large batches of properties into the browser and perform geographic filtering in JavaScript loops. This creates serious scalability bottlenecks, client memory bloat, high latency over mobile connections, and inaccurate distance calculations when planar approximations are used across large geographic areas.

## Decision
We chose to execute all spatial filtering inside PostgreSQL using PostGIS with GiST indexing:
1. **Radius Queries**: Implemented with `ST_DWithin` on `geography` type, ensuring accurate geodesic meter calculations over the Earth's spheroid without planar distortion, while returning exact `distance_km`.
2. **Bounding Box & Viewport Queries**: Implemented with `ST_MakeEnvelope` and `ST_Within` in SRID 4326, with split-hemisphere handling for antimeridian-crossing spans.
3. **Polygon Queries**: Implemented with `ST_Within` / `ST_GeomFromGeoJSON` for arbitrary GeoJSON polygon boundaries.
4. **Data Transport**: Responses are serialized into standard RFC 7946 `GeoJSONFeatureCollection` objects with `[longitude, latitude]` coordinates and typed property metadata.
5. **Search Trigger UX**: Implemented an explicit "Search this area" button when panning/zooming, preventing thrashing API requests on every intermediate movement frame.

## Alternatives Considered
1. **Client-Side Filtering (JavaScript)**:
   - *Rejected*: Scales poorly beyond a few hundred listings, leaks unpaginated data, and risks inaccurate distance calculations.
2. **MongoDB Geospatial**:
   - *Rejected*: Would require running a separate database engine, breaking the unified transactional relational model and ACID consistency with user listings.
3. **In-Memory Haversine Filtering in Python**:
   - *Rejected*: Bypasses database GiST indexes, requiring full table scans into application memory.

## Tradeoffs
- **Pros**:
  - Leverages database-native spatial indexing (`GiST`) for sub-millisecond query execution.
  - Keeps geographic truth strictly within PostgreSQL.
  - Zero raw SQL injection vulnerability via parameterized SQLAlchemy expressions.
- **Cons**:
  - Requires developers to understand PostGIS spatial predicates and geography vs geometry casting.

## Consequences
- All spatial endpoints are centralized in `/api/v1/search` and `/api/v1/maps`.
- Result limits are strictly capped at 200 items per request to guarantee high-performance query execution.

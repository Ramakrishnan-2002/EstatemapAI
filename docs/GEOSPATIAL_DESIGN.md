# EstateMap AI — PostGIS Geospatial Design & Spatial Query Architecture

## 1. Executive Summary & Core Principles
In EstateMap AI, the **PostgreSQL + PostGIS database is the single source of geographic truth**.
The frontend map does NOT download the full property dataset into JavaScript to filter client-side. Instead, user map interactions (pan, zoom, radius, viewport, polygon) are validated server-side by FastAPI and executed directly against PostGIS spatial indexes.

```
Frontend (MapLibre / mapcn)
         │ [north, south, east, west] / [latitude, longitude, radius]
         ▼
FastAPI API Gateway & Pydantic Validation (geo.py)
         │ Validated Spatial Parameters
         ▼
Geo Service (geo_service.py) & Property Service
         │ Coordinate normalization & conversion helpers
         ▼
Property Repository (property_repository.py)
         │ ST_DWithin / ST_MakeEnvelope / ST_Within
         ▼
PostgreSQL / PostGIS (GiST Index: idx_properties_location_gist)
         │ Filtered Spatial Tuples
         ▼
GeoJSON Serializer (RFC 7946 FeatureCollection)
         │ [longitude, latitude] Ordering
         ▼
Frontend Interactive Map (EstateMap / PropertyMarkers)
```

---

## 2. Canonical Spatial Storage & Coordinate Conventions

### 2.1 Database Column Definition
All property locations are stored as canonical PostGIS points in **WGS84 (EPSG:4326)**:
```sql
location GEOMETRY(Point, 4326) NOT NULL
```
- Indexed with a **GiST Spatial Index**: `idx_properties_location_gist`.
- Coordinate storage convention: `Point(longitude, latitude)` (`Point(x, y)`).

### 2.2 GeoJSON RFC 7946 Compliance
The GeoJSON specification strictly requires coordinates to be ordered as:
$$\text{coordinates} = [\text{longitude}, \text{latitude}]$$
- **Longitude** (X / East-West): `[-180.0, +180.0]`
- **Latitude** (Y / North-South): `[-90.0, +90.0]`

---

## 3. Spatial Query Mechanisms

### 3.1 Geodesic Radius Search (`/api/v1/search/radius`)
- **Query Operator**: `ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography, radius_meters)`
- **Distance Computation**: `ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(lng, lat), 4326)::geography) / 1000.0` as `distance_km`.
- **Rationale**: Casting to `geography` performs great-circle distance calculations on the WGS84 spheroid (in meters) without planar distortion, while utilizing the underlying GiST spatial index.

### 3.2 Bounding Box Search (`/api/v1/search/bbox`)
- **Query Operator**: `ST_Within(location, ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326))`
- **Antimeridian Handling**: If `min_lng > max_lng` (crosses the 180° meridian), the query is safely split into an `OR` condition spanning both hemispheres:
  ```sql
  ST_Within(location, ST_MakeEnvelope(min_lng, min_lat, 180.0, max_lat, 4326))
  OR
  ST_Within(location, ST_MakeEnvelope(-180.0, min_lat, max_lng, max_lat, 4326))
  ```

### 3.3 Map Viewport Search (`/api/v1/maps/properties`)
- Directly converts `north`, `south`, `east`, `west` bounds into an envelope query returning an RFC 7946 `GeoJSONFeatureCollection`.

### 3.4 Polygon Search (`/api/v1/search/polygon` & `/api/v1/maps/polygon`)
- **Query Operator**: `ST_Within(location, ST_SetSRID(ST_GeomFromGeoJSON(polygon_json), 4326))`
- **Validation**: Ensures exterior ring is closed (first point == last point), contains at least 4 positions, and adheres to WGS84 coordinate boundaries.

### 3.5 Point of Interest (POI) Proximity & Location Intelligence (Phase 7)
- **Nearby POIs (`/api/v1/pois/nearby` & `/api/v1/properties/{id}/nearby`)**:
  - `ST_DWithin(poi.location::geography, target_point::geography, radius_meters)` with geodesic meters.
  - Calculated distance: `ST_Distance(poi.location::geography, target_point::geography) / 1000.0 AS distance_km`.
  - Filtered by `is_active = true` and optional `category = :category`.
  - For property-relative queries, the origin coordinates are pulled securely from `Property.location` to prevent client coordinate tampering.
- **Location Intelligence Summary (`/api/v1/properties/{id}/location-intelligence`)**:
  - Deterministic per-category nearest distance (`ORDER BY distance_km ASC LIMIT 1`) and count within radius (`COUNT(*) WHERE ST_DWithin`).
  - No N+1 query loop across properties — single property analysis executed across indexed categories in < 15ms.

---

## 4. Query Composability & Result Limits
Spatial queries compose seamlessly with business filters:
- Price boundaries (`min_price`, `max_price`)
- Property attributes (`property_type`, `bedrooms`, `bathrooms`, `status`)
- Sorting options (`distance_asc`, `distance_desc`, `price_asc`, `newest`)
- Safe result limits: default 50–100, maximum capped at 200 (500 for POI viewport) to prevent denial-of-service memory pressure.

---

## 5. Performance & Scalability Evolution

```
Phase 6-7 (Completed)
PostGIS + GiST Indexes (Properties & POIs) + GeoJSON FeatureCollections + Deterministic Location Intelligence

Phase 8-9 (Near Term)
Commute Isochrones & Routing + Multi-factor Deterministic Ranking Engine

Phase 10-12 (Production Scale)
PostGIS Read Replicas + Redis Viewport Caching + Cursor Pagination + AI Factual Explanation Layer

Very Large Map Datasets (Enterprise)
Vector Tiles (MVT / ST_AsMVT) + Dedicated Tile CDN
```


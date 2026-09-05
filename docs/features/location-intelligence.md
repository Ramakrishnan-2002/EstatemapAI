# Feature Guide: Location Intelligence & Points of Interest (POI)

## 1. Overview
Location Intelligence in EstateMap AI provides a deterministic, geographic factual assessment of property proximity to critical urban amenities (hospitals, schools, transit stops, supermarkets, parks, pharmacies, and banks). 

Rather than relying on AI hallucinations, scraped estimates, or static proximity tags, every metric is computed dynamically against PostGIS geometries using spatial algorithms.

---

## 2. Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                         │
│  - MapContainer & EstateMap (POIMarker & POIPopup)          │
│  - POIFilter (Controlled Category Checkboxes)               │
│  - LocationIntelligence Component (Detail View Card)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP /api/v1/... (JSON/GeoJSON)
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Routers                          │
│  - GET /api/v1/pois/nearby                                  │
│  - GET /api/v1/maps/pois                                    │
│  - GET /api/v1/properties/{id}/nearby                       │
│  - GET /api/v1/properties/{id}/location-intelligence        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Pydantic Validation & Orchestration
┌──────────────────────────────▼──────────────────────────────┐
│             POIService & GeoService                         │
│  - Coordinate & Radius Validation                           │
│  - Authoritative Coordinate Extraction from Property Model  │
│  - RFC 7946 GeoJSON Serialization                           │
└──────────────────────────────┬──────────────────────────────┘
                               │ Async SQLAlchemy
┌──────────────────────────────▼──────────────────────────────┐
│                    POIRepository                            │
│  - ST_DWithin(poi_geog, origin_geog, radius_m)              │
│  - ST_Distance(poi_geog, origin_geog) / 1000.0              │
│  - ST_MakeEnvelope + ST_Within (Bounding Box)               │
└──────────────────────────────┬──────────────────────────────┘
                               │ PostGIS GiST Index
┌──────────────────────────────▼──────────────────────────────┐
│          PostgreSQL 16 + PostGIS 3.4 (`pois` Table)         │
│  - Geometry(POINT, 4326) with idx_pois_location_gist        │
│  - ix_pois_category_active, ix_pois_name, etc.              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema

### Table: `pois`
| Column | Type | Constraints / Indexes | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY, AUTOINCREMENT` | Unique identifier |
| `name` | `VARCHAR(255)` | `NOT NULL, INDEX` | Name of the POI |
| `category` | `VARCHAR(50)` | `NOT NULL, INDEX, CHECK IN enum` | Controlled category |
| `subcategory`| `VARCHAR(100)` | `NULLABLE` | Sub-classification (e.g. `private`, `metro`) |
| `location` | `GEOMETRY(POINT, 4326)` | `NOT NULL, GiST INDEX` | PostGIS WGS84 point |
| `address` | `VARCHAR(500)` | `NULLABLE` | Street address |
| `city` | `VARCHAR(100)` | `NOT NULL, INDEX` | City name |
| `locality` | `VARCHAR(100)` | `NULLABLE, INDEX` | Suburb / neighborhood |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE, INDEX` | Active status |
| `created_at` | `TIMESTAMPTZ` | `DEFAULT NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | `NULLABLE` | Last update timestamp |

### Indexes:
- `idx_pois_location_gist`: PostGIS GiST spatial index on `location`.
- `ix_pois_category_active`: Composite B-tree index on `(category, is_active)`.
- `ix_pois_name`, `ix_pois_city`, `ix_pois_locality`, `ix_pois_category`, `ix_pois_is_active`.

---

## 4. API Endpoints

### 1. Nearby POI Search
- **Endpoint**: `GET /api/v1/pois/nearby`
- **Query Parameters**:
  - `latitude` (`float`, -90 to 90)
  - `longitude` (`float`, -180 to 180)
  - `radius_km` (`float`, max 50, default 3.0)
  - `category` (`POICategory`, optional)
  - `limit` (`int`, 1-200, default 50)
- **Response**: `NearbyPOIsResponse` (`items` with `poi` and `distance_km`).

### 2. Viewport Map POIs (GeoJSON)
- **Endpoint**: `GET /api/v1/maps/pois`
- **Query Parameters**:
  - `north`, `south`, `east`, `west` (`float`)
  - `category` (`POICategory`, optional)
  - `limit` (`int`, 1-500, default 200)
- **Response**: `POIGeoJSONFeatureCollection` (RFC 7946 GeoJSON).

### 3. Property Nearby POIs
- **Endpoint**: `GET /api/v1/properties/{property_id}/nearby`
- **Query Parameters**:
  - `category` (`POICategory`, optional)
  - `radius_km` (`float`, default 5.0)
  - `limit` (`int`, default 20)
- **Response**: `NearbyPOIsResponse`. Coordinates are pulled from the stored property geometry.

### 4. Property Location Intelligence
- **Endpoint**: `GET /api/v1/properties/{property_id}/location-intelligence`
- **Query Parameters**:
  - `radius_km` (`float`, default 3.0)
- **Response**:
  ```json
  {
    "property_id": 1,
    "radius_km": 3.0,
    "categories": {
      "hospital": { "nearest_distance_km": 0.85, "count_within_radius": 3 },
      "school": { "nearest_distance_km": 0.42, "count_within_radius": 6 },
      "transit": { "nearest_distance_km": 0.21, "count_within_radius": 2 },
      "supermarket": { "nearest_distance_km": 0.65, "count_within_radius": 4 },
      "park": { "nearest_distance_km": 1.10, "count_within_radius": 1 },
      "pharmacy": { "nearest_distance_km": 0.35, "count_within_radius": 5 },
      "bank": { "nearest_distance_km": 0.50, "count_within_radius": 3 }
    }
  }
  ```

---

## 5. Frontend Visual Integration

- **Search Page (`/search`)**:
  - Floating "Nearby Places" badge allows users to toggle the category filter.
  - Selecting categories displays non-intrusive, category-color-coded dot markers on the MapLibre map.
  - Clicking any POI marker displays a concise `POIPopup` with category, name, and locality.
- **Property Detail Page (`/properties/[id]`)**:
  - Contains a dedicated "Location Intelligence" section beneath the interactive map.
  - Features structured columns for category, nearest distance (meters/km), and count within the search radius.
  - Handles loading, empty, and error fallback states cleanly.

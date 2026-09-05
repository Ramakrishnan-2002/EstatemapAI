# Commute & Travel Intelligence Feature Guide

## 1. Overview
The **Commute & Travel Intelligence** module enables EstateMap AI to compute road-network travel distances, realistic travel durations, and GeoJSON route paths between properties and key urban destinations (workplaces, tech parks, airports, metro stations, schools).

While **Phase 7 (Location Intelligence)** provides PostGIS straight-line geographic proximity, **Phase 8 (Commute Intelligence)** provides actual network routing reality across multiple travel modes (`driving`, `cycling`, `walking`).

---

## 2. Architecture & Key Components

```
+--------------------------------------------------------------------------+
|                            Next.js Frontend                              |
|   +--------------------------+          +----------------------------+   |
|   |   <CommutePanel />       | -------->|   <MapRoute /> (mapcn)     |   |
|   |  - Presets (CBD, Airport)|          |  - GeoJSON LineString path |   |
|   |  - Modes (Drive/Cycle)   |          |  - Reactive fitBounds      |   |
|   +--------------------------+          +----------------------------+   |
+--------------------------------------------------------------------------+
                                    |
                                    v HTTP REST
+--------------------------------------------------------------------------+
|                         FastAPI Backend Modular Monolith                 |
|   +------------------------------------------------------------------+   |
|   |   Routers: /api/v1/properties/{id}/commute                       |   |
|   |            /api/v1/properties/{id}/commute/batch                 |   |
|   |            /api/v1/commute/compare                               |   |
|   |            /api/v1/commute/route                                 |   |
|   +------------------------------------------------------------------+   |
|                                   |                                      |
|                                   v                                      |
|   +------------------------------------------------------------------+   |
|   |                        CommuteService                            |   |
|   |   1. Extracts authoritative property coords from PostGIS         |   |
|   |   2. Checks Redis route cache (key: route:{provider}:{mode}:...) |   |
|   |   3. Calls RoutingProvider (Mock or OSRM) on cache miss          |   |
|   +------------------------------------------------------------------+   |
|                |                                      |                  |
|                v                                      v                  |
|   +--------------------------+          +----------------------------+   |
|   |   Redis Cache (TTL 600s) |          |      RoutingProvider       |   |
|   |  - Graceful degradation  |          |  - MockRoutingProvider     |   |
|   |  - Normalized coords key |          |  - OSRMProvider (HTTP)     |   |
|   +--------------------------+          +----------------------------+   |
+--------------------------------------------------------------------------+
```

---

## 3. API Endpoints

### `GET /api/v1/properties/{id}/commute`
Calculate single commute route from property's database location to a destination.

**Query Parameters:**
- `destination_lat` (float, required): Target latitude (-90 to 90)
- `destination_lng` (float, required): Target longitude (-180 to 180)
- `destination_name` (string, optional): Human-readable target name
- `mode` (string, optional, default `"driving"`): `"driving"`, `"cycling"`, or `"walking"`

**Response Schema (`CommuteResponse`):**
```json
{
  "property_id": 1,
  "origin": {
    "latitude": 12.9784,
    "longitude": 77.6408
  },
  "destination": {
    "name": "Electronic City",
    "latitude": 12.8399,
    "longitude": 77.6770
  },
  "mode": "driving",
  "distance_meters": 18520.0,
  "distance_km": 18.52,
  "duration_seconds": 2083.2,
  "duration_minutes": 34.7,
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [77.6408, 12.9784],
      [77.6515, 12.9421],
      [77.6770, 12.8399]
    ]
  },
  "summary": "Via Primary Urban Arterial Roads",
  "provider": "mock",
  "cached": false
}
```

---

### `POST /api/v1/properties/{id}/commute/batch`
Calculate commutes from a property to up to 5 target destinations.

**Request Payload (`BatchCommuteRequest`):**
```json
{
  "destinations": [
    { "name": "MG Road CBD", "latitude": 12.9756, "longitude": 77.6066 },
    { "name": "Kempegowda Airport", "latitude": 13.1986, "longitude": 77.7066 }
  ],
  "mode": "driving"
}
```

---

### `POST /api/v1/commute/compare`
Compare travel times and distances from multiple properties (2 to 10) to a target destination.

**Request Payload (`CommuteCompareRequest`):**
```json
{
  "property_ids": [1, 2, 3],
  "destination": {
    "name": "Electronic City Phase 1",
    "latitude": 12.8399,
    "longitude": 77.6770
  },
  "mode": "driving"
}
```

**Response Schema (`CommuteCompareResponse`):**
```json
{
  "destination": {
    "name": "Electronic City Phase 1",
    "latitude": 12.8399,
    "longitude": 77.6770
  },
  "mode": "driving",
  "comparisons": [ ... ],
  "fastest_property_id": 1,
  "shortest_property_id": 1
}
```

---

## 4. Frontend Integration

1. **`CommutePanel` (`frontend/components/commute/commute-panel.tsx`)**:
   - Preset destinations for key Bengaluru commercial hubs.
   - Inline form for custom coordinate target inputs.
   - Travel mode selection tabs (`Drive`, `Cycle`, `Walk`).
   - Displays estimated duration (minutes), road distance (km), route summary, cache status, and routing engine badge.

2. **`MapRoute` Integration (`frontend/components/map/estate-map.tsx`)**:
   - Renders GeoJSON `LineString` route layer on the MapLibre GL map.
   - Fits the map viewport automatically to encompass both origin and destination with padding.

---

## 5. Verification & Tests

- **Unit Tests**:
  - `backend/tests/unit/test_routing_models.py` (model validations, factory resolution, mode mappings)
  - `backend/tests/unit/test_commute_service.py` (cache keys, batch limits, service logic)
  - `frontend/__tests__/commute-api.test.mjs` (query serialization, RFC 7946 GeoJSON structure)
- **Integration Tests**:
  - `backend/tests/integration/test_commute.py` (single route, batch routes, comparisons, 404/422 validation, Redis caching)

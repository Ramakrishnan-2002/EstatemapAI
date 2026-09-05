# EstateMap AI — API Design & Contracts

## 1. Design Standards
All EstateMap AI APIs adhere to the following standards:
- **Base Route**: `/api/v1`
- **Request Correlation**: Handled via `X-Request-ID` middleware, injected into all logging and error responses.
- **Error Format**: Unified error envelope:
  ```json
  {
    "error": {
      "code": "RESOURCE_NOT_FOUND",
      "message": "Property with identifier '999' was not found.",
      "request_id": "req-xyz-123",
      "details": null
    }
  }
  ```
- **Spatial Serialization**: RFC 7946 GeoJSON with strict `[longitude, latitude]` WGS84 coordinate ordering.
- **Units**: API input/output units are always in **kilometers** (`radius_km`, `distance_km`). PostGIS internal calculations convert to meters where appropriate.

---

## 2. Location Intelligence & Points of Interest (Phase 7)

### `GET /api/v1/pois/nearby`
Find active Points of Interest within a specified radius of a geographic coordinate.
- **Auth**: None (Public)
- **Parameters**:
  - `latitude` (`float`, required): -90.0 to +90.0
  - `longitude` (`float`, required): -180.0 to +180.0
  - `radius_km` (`float`, default `3.0`): 0.1 to 50.0
  - `category` (`POICategory`, optional): Enum string (`hospital`, `school`, `transit`, `supermarket`, `park`, `pharmacy`, `bank`)
  - `limit` (`int`, default `50`): 1 to 200
- **Response**: `200 OK`
  ```json
  {
    "items": [
      {
        "poi": {
          "id": 1,
          "name": "Manipal Hospital",
          "category": "hospital",
          "subcategory": "private",
          "latitude": 12.9592,
          "longitude": 77.6456,
          "address": "98, HAL Airport Road",
          "city": "Bengaluru",
          "locality": "Indiranagar",
          "is_active": true,
          "created_at": "2026-09-04T12:00:00Z"
        },
        "distance_km": 0.42
      }
    ],
    "total": 1,
    "radius_km": 3.0,
    "category": "hospital"
  }
  ```

---

### `POST /api/v1/pois`
Create a new Point of Interest.
- **Auth**: Required (`Bearer <JWT>`)
- **Request Body**:
  ```json
  {
    "name": "City General Hospital",
    "category": "hospital",
    "subcategory": "government",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "123 Central Ave",
    "city": "Bengaluru",
    "locality": "Central",
    "is_active": true
  }
  ```
- **Response**: `201 Created` (`POIResponse`)

---

### `GET /api/v1/pois/{poi_id}`
Retrieve a single POI by integer primary key.
- **Auth**: None
- **Response**: `200 OK` (`POIResponse`) or `404 Not Found`.

---

### `GET /api/v1/maps/pois`
Query POIs within a geographic bounding box as an RFC 7946 GeoJSON `FeatureCollection`.
- **Auth**: None
- **Parameters**:
  - `north`, `south` (`float`, -90 to +90)
  - `east`, `west` (`float`, -180 to +180)
  - `category` (`POICategory`, optional)
  - `limit` (`int`, default `200`, max `500`)
- **Response**: `200 OK`
  ```json
  {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "id": 1,
        "geometry": {
          "type": "Point",
          "coordinates": [77.6456, 12.9592]
        },
        "properties": {
          "id": 1,
          "name": "Manipal Hospital",
          "category": "hospital",
          "subcategory": "private",
          "locality": "Indiranagar",
          "city": "Bengaluru",
          "is_active": true
        }
      }
    ],
    "total": 1
  }
  ```

---

### `GET /api/v1/properties/{property_id}/nearby`
Retrieve POIs near a stored property listing.
- **Auth**: None
- **Parameters**:
  - `category` (`POICategory`, optional)
  - `radius_km` (`float`, default `5.0`, max `50.0`)
  - `limit` (`int`, default `20`, max `100`)
- **Response**: `200 OK` (`NearbyPOIsResponse`)

---

### `GET /api/v1/properties/{property_id}/location-intelligence`
Retrieve deterministic per-category nearest distance and counts within radius for a property.
- **Auth**: None
- **Parameters**:
  - `radius_km` (`float`, default `3.0`, max `50.0`)
- **Response**: `200 OK`
  ```json
  {
    "property_id": 101,
    "radius_km": 3.0,
    "categories": {
      "hospital": {
        "nearest_distance_km": 0.85,
        "count_within_radius": 4
      },
      "school": {
        "nearest_distance_km": 0.42,
        "count_within_radius": 7
      },
      "transit": {
        "nearest_distance_km": 0.25,
        "count_within_radius": 3
      },
      "supermarket": {
        "nearest_distance_km": 0.60,
        "count_within_radius": 5
      },
      "park": {
        "nearest_distance_km": 1.10,
        "count_within_radius": 2
      },
      "pharmacy": {
        "nearest_distance_km": 0.30,
        "count_within_radius": 6
      },
      "bank": {
        "nearest_distance_km": 0.50,
        "count_within_radius": 4
      }
    }
  }
  ```

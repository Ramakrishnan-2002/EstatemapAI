# EstateMap AI — System Design & Data Flow

## 1. Primary Request Flows

### A. Geographically-Driven Property Search
1. User pans or zooms the map in the Next.js UI (rendered via **mapcn**).
2. The frontend debounces viewport coordinates `[north, south, east, west]` and sends a GET request to `/api/v1/maps/viewport`.
3. FastAPI invokes `SearchService` and `GeoService`.
4. `GeoService` queries PostgreSQL via PostGIS using `ST_MakeEnvelope(west, south, east, north, 4326) && location`.
5. Results are ranked via `RankingService` and serialized into a standard GeoJSON `FeatureCollection`.
6. mapcn ingests the GeoJSON and updates vector layers/clusters seamlessly.

### B. Natural Language "Ask the Map" / AI Search Flow
```
User Query: "Find me a 2 BHK under ₹70 lakh near OMR with a hospital nearby"
   │
   ▼
[AIRouter] (Evaluates query complexity / provider availability)
   ├── Primary: Local Ollama (llama3.2:3b)
   └── Complex / Fallback: Google Gemini (gemini-1.5-flash)
   │
   ▼
Parsed JSON extracted:
{
  "bedrooms": 2,
  "max_price": 7000000,
  "locality": "OMR",
  "nearby_amenities": ["hospital"]
}
   │
   ▼
[Pydantic Validation] (ParsedSearchIntent schema validation)
   │
   ▼
[UI Confirmation Step] (User sees extracted parameters and can adjust)
   │
   ▼
[SearchService + PostGIS] (Executes parameterized spatial query)
   │
   ▼
[Deterministic Ranking Engine] (Affordability, distance, amenity score)
   │
   ▼
[GeoJSON Response] -> Map rendered on mapcn with synced card list
```

## 2. Scaling Strategy
- **100 Properties**: Direct DOM markers.
- **10,000 Properties**: Viewport bounding box querying + GeoJSON + client-side map clustering.
- **1,000,000+ Properties**: GiST index on PostGIS geometry, viewport limits with server-side tile clustering / vector tiles (MVT), read replicas, and Redis cache layer.

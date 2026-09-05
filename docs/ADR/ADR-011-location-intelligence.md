# ADR-011: Location Intelligence & Points of Interest (POI) Domain

## Status
Accepted

## Context
EstateMap AI requires a factual, location-first intelligence layer to evaluate property proximity to essential amenities and infrastructure (hospitals, schools, transit, supermarkets, parks, pharmacies, banks). In traditional platforms, location intelligence is either hardcoded, scraped without coordinates, calculated with planar Euclidean distance approximations, or delegated to opaque external black-box APIs that cannot be indexed or deterministically audited.

## Decisions

### D1: Python Enum for POI Categories (`POICategory`)
- **Decision**: Define POI categories via Python `StrEnum` (`hospital`, `school`, `transit`, `supermarket`, `park`, `pharmacy`, `bank`) and a `VARCHAR` with a `CheckConstraint` in PostgreSQL, rather than creating a separate dynamic `poi_categories` table.
- **Why**: The category vocabulary is fixed for the platform domain, provides compile-time safety across Pydantic and TypeScript, and eliminates unnecessary table joins on every spatial query.
- **Alternatives Considered**: Dynamic database table for categories. Rejected because categories are currently static and do not require user-administered runtime schema alterations.
- **Future Evolution**: If categories require dynamic icon bindings, localized descriptions, or runtime user additions in Phase 8+, migrate to a referenced table with an Alembic migration.

### D2: Dynamic Distance Computation via PostGIS (No Stored Distances)
- **Decision**: Calculate all property-to-POI and origin-to-POI distances on-the-fly using `ST_Distance(location::geography, target::geography) / 1000.0`. Never persist distance values in property or POI tables.
- **Why**: Stored distances become immediately stale whenever POIs are added, updated, or deactivated. Dynamic PostGIS calculations over GiST-indexed geometries execute in sub-milliseconds.
- **Alternatives Considered**: Storing precomputed distance matrices or scalar `nearest_*_km` columns on the `Property` model. Rejected due to cache invalidation complexity and stale data risk.

### D3: Decoupled Spatial Relationship (No Property↔POI Junction Table)
- **Decision**: Maintain `pois` as an independent spatial entity table without foreign keys or junction tables (`property_pois`) linking to `properties`.
- **Why**: Proximity is inherently continuous and geometric. Connecting properties to POIs through relational foreign keys introduces artificial cardinality and synchronization overhead.
- **Alternatives Considered**: Many-to-Many junction table (`property_pois`). Rejected as anti-pattern for spatial databases.

### D4: RFC 7946 GeoJSON Serialization for Transport
- **Decision**: Serialize POIs into `POIGeoJSONFeatureCollection` and `POIGeoJSONFeature` with strict `[longitude, latitude]` WGS84 coordinate ordering.
- **Why**: Direct compatibility with mapcn / MapLibre GL vector layer rendering without coordinate transposition on the client.
- **Alternatives Considered**: Custom JSON coordinate objects (`{lat, lng}`). Rejected to adhere to geospatial web standards.

### D5: Deterministic Demo Seeds & Clean Repository Boundaries
- **Decision**: Seed deterministic demo POIs centered in the Bengaluru metropolitan area without invoking external live third-party APIs (Google Places, Mapbox, OSM) in Phase 7.
- **Why**: Ensures 100% reproducible test suites, deterministic continuous integration runs, zero external API costs or rate limits during development, and guarantees geographic alignment with seeded property listings.
- **Future Evolution**: External provider adapters (e.g. Overpass/OSM ingesters) will implement the `POIRepository` interface in future phases.

### D6: Category-Scoped Proximity Queries
- **Decision**: For a single property's location intelligence summary, execute sequential category queries (nearest distance via `ORDER BY distance ASC LIMIT 1` and counts via `COUNT(*) WHERE ST_DWithin`).
- **Why**: Keeps SQLAlchemy `AsyncSession` usage thread-safe without concurrency race conditions on a single database connection. Each query leverages the `idx_pois_location_gist` index, completing in < 2ms.
- **Tradeoffs**: Executing 7 category checks takes ~10-15ms total, well within the sub-50ms API SLA, while avoiding session contention or connection pool exhaustion.

## Consequences
- Location intelligence endpoints (`/api/v1/pois/nearby`, `/api/v1/maps/pois`, `/api/v1/properties/{id}/nearby`, `/api/v1/properties/{id}/location-intelligence`) provide deterministic, verifiable facts.
- Future AI explanations (Phase 12) will consume these factual numbers directly, guaranteeing zero geographic hallucination.

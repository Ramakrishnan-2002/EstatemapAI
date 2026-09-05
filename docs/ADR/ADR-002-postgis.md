# ADR-002: PostgreSQL with PostGIS for Spatial Data

## Status
Accepted

## Context
Location-first discovery requires high-performance spatial queries, such as bounding-box filters, radius searches, polygon containment, and distance calculations across thousands of properties.

## Decision
Use **PostgreSQL with the PostGIS extension** (`GEOMETRY(Point, 4326)`) and GiST spatial indexing as the primary geospatial storage and query engine.

## Alternatives Considered
- **In-Memory Python Filtering**: Fetching all records and calculating distance with Haversine in Python. Rejected because it scales poorly (`O(N)`) and exhausts server memory.
- **MongoDB Geospatial / Elasticsearch**: Viable for document search, but lacks relational integrity with foreign keys, transactional safety, and the depth of spatial operations provided by PostGIS.

## Consequences
- Spatial queries execute at database level utilizing hardware-accelerated R-Tree / GiST index scans.
- Native GeoJSON output generation via `ST_AsGeoJSON`.
- Full ACID compliance for property records and user relationships.

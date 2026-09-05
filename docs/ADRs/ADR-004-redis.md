# ADR-004: Targeted Redis Caching Strategy

## Status
Accepted

## Context
Viewport map queries and popular search areas generate frequent duplicate database hits when multiple users inspect the same geographical areas.

## Decision
Use Redis exclusively for **short-lived viewport map query caching** (TTL ~60s) and property detail caching, with graceful fallback to PostGIS if Redis becomes temporarily unavailable.

## Alternatives Considered
- **Caching all database queries**: Leads to stale data and cache invalidation complexity.
- **No caching**: Higher PostGIS query load during peak traffic.

## Consequences
- Significant reduction in database load for high-traffic geographic areas.
- The application never crashes if Redis goes offline.

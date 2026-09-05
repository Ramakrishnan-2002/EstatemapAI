# ADR 014: Redis Multi-Domain Caching and Sliding-Window Rate Limiting

## Status
Accepted

## Context
EstateMap AI requires low-latency responses for computationally demanding workflows including:
1. Multi-criteria deterministic ranking calculations (Phase 9).
2. Point-to-point road network commute calculations (Phase 8).
3. PostGIS nearest-neighbor location intelligence summaries (Phase 7).
4. High-frequency map viewport pans and tile queries (Phases 5–6).

Additionally, open public endpoints require rate limiting to prevent denial-of-service and routing provider quota exhaustion while safeguarding authentication endpoints against credential stuffing.

## Decision
1. **Source of Truth Invariant**: PostgreSQL / PostGIS remains the single source of truth. Redis 7 is strictly an ephemeral acceleration and rate-limiting layer.
2. **Canonical Versioned Namespace**: All cache keys follow `estatemap:{domain}:v1:{parameters_or_hash}` with coordinate normalization to 4 decimal places (~11m).
3. **No Unsafe Serialization**: Use `SafeJSONEncoder` / `serialize_json` instead of Python `pickle` to prevent arbitrary code execution vulnerabilities.
4. **Sliding-Window Rate Limiting via ZSET**: Implement sliding-window logs with Redis sorted sets to avoid fixed-window boundary spikes.
5. **Differentiated Fail-Safe Policies**: Search and commute endpoints fail-open if Redis fails; authentication endpoints fail-closed to preserve security.
6. **Non-Blocking Invalidation**: Pattern invalidations use `client.scan_iter` and `client.unlink` rather than blocking `KEYS *`.

## Consequences
### Positive
- **Dramatic Latency Reductions**: Sub-5ms warm responses for complex commute and ranked search queries (>16x speedup).
- **Graceful Degradation**: Zero application crashes if Redis experiences network partitions or service restarts.
- **Accurate Rate Limiting**: Fair and tamper-resistant rate limits per user/IP.

### Negative
- Ephemeral memory overhead in Redis instance.
- Cache invalidation coordination required during property/POI mutation flows.

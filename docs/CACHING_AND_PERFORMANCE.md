# Caching, Performance & Rate Limiting Architecture — Phase 10

## 1. Executive Summary & Philosophy

EstateMap AI implements a multi-tiered caching and resilience architecture where **PostgreSQL / PostGIS** remains the single authoritative source of truth, while **Redis 7** functions strictly as an ephemeral, derived-data acceleration and rate-limiting layer.

Every cached payload is deterministic, version-namespaced, and safely serializable without unsafe pickle operations. System resilience is safeguarded by strict **fail-safe degradation policies**: if Redis is unavailable or sluggish, search and commute queries fall back gracefully to the primary spatial database and routing engines.

---

## 2. Redis Key Hierarchy & Design

All cache keys adhere to the standardized canonical namespace:
```text
estatemap:{domain}:{version}:{parameters_or_digest}
```

### Coordinate Normalization Invariant
To maximize cache hit rates across mobile devices and map panning without sacrificing physical accuracy, geographic coordinates in cache keys are normalized to **4 decimal places** (`~11.1 meters` spatial resolution):
```python
CacheKeys.normalize_coord(12.971598) -> 12.9716
```

### Domain Keys Summary

| Domain | Key Pattern | TTL | Invalidation Trigger |
| :--- | :--- | :--- | :--- |
| **Commute Routes** | `estatemap:route:v1:{provider}:{mode}:{orig_lat},{orig_lng}:{dest_lat},{dest_lng}` | 600s (10m) | Natural TTL expiry (read-through) |
| **Location Intelligence** | `estatemap:poi:v1:property:{property_id}:radius:{radius_km}` | 1800s (30m) | POI creation/deletion; Property update/deletion |
| **Map Properties** | `estatemap:map:v1:properties:{n}:{s}:{e}:{w}:{params_sha256}` | 120s (2m) | Property creation, update, deletion |
| **Map POIs** | `estatemap:map:v1:pois:{n}:{s}:{e}:{w}:{category}` | 120s (2m) | POI creation, update, deletion |
| **Ranked Search** | `estatemap:ranking:v1:{request_sha256}` | 300s (5m) | Property creation, update, deletion; POI mutation |
| **Rate Limiter** | `estatemap:ratelimit:v1:{scope}:{user_id|client_ip}` | Window + 5s | Sliding window rolling expiry |

---

## 3. Cache Invalidation Strategy

EstateMap avoids costly full-database flushes by using targeted, non-blocking cache invalidations:

### Non-blocking SCAN Iteration
Never use `KEYS *` in production as it locks the single-threaded Redis event loop. Cache invalidation utilizes `client.scan_iter(match=pattern, count=100)` accompanied by `client.unlink()` for asynchronous background memory reclamation.

```python
async def delete_pattern(pattern: str) -> int:
    # Uses non-blocking scan_iter and batch unlink
    ...
```

### Mutation Triggers
- **Property Created / Updated / Deleted**:
  - Invalidates `estatemap:map:v1:*`
  - Invalidates `estatemap:ranking:v1:*`
  - Invalidates `estatemap:poi:v1:property:{id}:*`
- **POI Created / Updated / Deleted**:
  - Invalidates `estatemap:map:v1:*`
  - Invalidates `estatemap:ranking:v1:*`
  - Invalidates `estatemap:poi:v1:*`

---

## 4. Sliding-Window Rate Limiting

EstateMap replaces naive fixed-window counters with a precision **sliding-window log** implemented over Redis sorted sets (`ZSET`):

### Mechanism
1. Each incoming request is identified by `user:{id}` (authenticated) or `ip:{client_ip}` (anonymous fallback with `X-Forwarded-For` support).
2. Atomic Redis pipeline:
   - `ZREMRANGEBYSCORE key 0 (now - window)`: purge elements outside window.
   - `ZCARD key`: count current requests in sliding window.
   - `ZADD key {member_id: now}`: record current attempt.
   - `EXPIRE key (window + 5)`: ensure idle keys expire.
3. If count breaches limit:
   - Calculate exact remaining cooldown (`retry_after`).
   - Raise `RateLimitExceededException` mapped to `HTTP 429 Too Many Requests`.
   - Set standard `Retry-After: <seconds>` HTTP response header.

### Endpoint Thresholds

| Endpoint Scope | Limit | Window | Failure Policy |
| :--- | :--- | :--- | :--- |
| `search_ranked` | 20 req | 60s | Fail-open |
| `commute_route` | 30 req | 60s | Fail-open |
| `auth_login` | 10 req | 60s | Fail-closed |
| `auth_register` | 10 req | 60s | Fail-closed |

---

## 5. Performance Benchmarks

Measured on local containerized PostgreSQL/PostGIS and Redis infrastructure:

| Endpoint / Operation | Cold (Database / Routing) | Warm (Redis Cache Hit) | Latency Reduction |
| :--- | :--- | :--- | :--- |
| **Commute Direct Route** | 46.72 ms | 2.87 ms | **~16.3x faster** |
| **Ranked Multi-Criteria Search** | 70.23 ms | 3.38 ms | **~20.8x faster** |
| **Location Intelligence Summary** | 35.10 ms | 2.10 ms | **~16.7x faster** |

---

## 6. Failure Modes & Resilience (Graceful Degradation)

1. **Redis Offline / Network Partition**:
   - `CacheService.get_json` returns `None` and logs structured warning; downstream queries execute against PostgreSQL/PostGIS.
   - Search and commute endpoints continue functioning without customer-facing errors (`fail_open=True`).
   - Auth endpoints fail closed (`fail_open=False`) to protect against brute-force attacks during Redis downtime.
2. **Corrupted / Invalid Cache JSON**:
   - `SafeJSONSerializer` catches decoding errors, logs warnings, purges key, and triggers database fetch.

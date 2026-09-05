# EstateMap AI — Backend Engineering Stories Master Curriculum
> **Focus: Python Backend Development & System Design**
> **Total Stories: 48 Focused Learning Units across 15 Cohesive Modules | 0 Frontend/DevOps Fluff**

Welcome to the EstateMap AI Backend Engineering Curriculum. Every learning unit is strictly focused on backend engineering (FastAPI, PostgreSQL, PostGIS, Redis, Caching, Rate Limiting, Ranking, Multi-Provider AI, System Design).

## 15-Module Backend Index
1. **Module 01: Python & FastAPI Foundations** (Stories 01–04) — `[ESSENTIAL]`
2. **Module 02: REST API Design & Validation** (Stories 05–07) — `[ESSENTIAL]`
3. **Module 03: PostgreSQL & SQLAlchemy 2.0 Async** (Stories 08–12) — `[ESSENTIAL / IMPORTANT]`
4. **Module 04: Authentication & Security Boundaries** (Stories 13–15) — `[ESSENTIAL]`
5. **Module 05: PostGIS Spatial Search** (Stories 16–21) — `[ESSENTIAL / IMPORTANT]`
6. **Module 06: Location Intelligence & Routing** (Stories 22–24) — `[ESSENTIAL]`
7. **Module 07: Deterministic Ranking & Business Logic** (Stories 25–28) — `[ESSENTIAL / IMPORTANT]`
8. **Module 08: Redis In-Memory Caching** (Stories 29–31) — `[ESSENTIAL / IMPORTANT]`
9. **Module 09: Rate Limiting & Resilience** (Stories 32–34) — `[ESSENTIAL / IMPORTANT]`
10. **Module 10: Multi-Provider AI Architecture** (Stories 35–38) — `[ESSENTIAL / IMPORTANT]`
11. **Module 11: Ask-the-Map Conversational Orchestration** (Stories 39–41) — `[ESSENTIAL]`
12. **Module 12: Backend ↔ Frontend API Integration** (Story 42) — `[ESSENTIAL]`
13. **Module 13: Backend Testing & Debugging** (Stories 43–44) — `[IMPORTANT]`
14. **Module 14: Docker for Backend Developers** (Story 45) — `[IMPORTANT]`
15. **Module 15: EstateMap System Design & Architecture Synthesis** (Stories 46–48) — `[ESSENTIAL]`

---

## Module 01: Python & FastAPI Foundations

### Story 01: Python Project Layout, Clean Modular Monolith & ASGI App Factory

* **Module**: Module 01: Python & FastAPI Foundations
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: None (Foundational)
* **Leads To**: Story 02, Story 03, Story 04
* **Primary Code Files**: `backend/app/main.py`, `backend/pyproject.toml`, `backend/app/core/config.py`
* **Concrete Symbol / Class**: `app.main:app / create_application`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters
Clean separation of concerns isolates HTTP serialization from domain logic and prevents circular imports across services.

#### 2. Concept & Architecture
ASGI (Asynchronous Server Gateway Interface) event loop request dispatching vs WSGI synchronous execution.

#### 3. How It Works Internally
Uvicorn runs ASGI event loops. FastAPI initializes middleware (CORS, RequestID) and mounts versioned routers (/api/v1).

#### 4. EstateMap Implementation
backend/app/main.py defines the FastAPI application factory, initializes middleware pipelines, mounts /api/v1 routers, and configures lifespan handlers.

#### 5. Code Flow & Request Lifecycle
```text
Client Request -> Uvicorn ASGI Server -> Middleware Stack (RequestID, CORS) -> FastAPI Router (/api/v1/properties) -> Dependency Injection (get_db) -> Service Layer -> Response.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up resources...")
    yield
    print("Shutting down resources...")

def create_app() -> FastAPI:
    app = FastAPI(title="EstateMap Backend", lifespan=lifespan)
    return app

app = create_app()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Introducing a circular import (e.g. importing a service in a router that imports the router) crashes Python with an ImportError during boot.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_health.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Modular Monolith was chosen over microservices to eliminate distributed latency, RPC serialization overhead, and multi-repo operational complexity.

#### 9. System Design & Scaling Angle
Stateless ASGI workers scale horizontally behind an NGINX / Cloud load balancer with zero shared in-process memory.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why use FastAPI over traditional frameworks like Django or Flask for high-performance APIs?
* **Answer**: FastAPI is built natively on Starlette and asyncio, allowing non-blocking concurrent I/O on a single thread event loop. It integrates Pydantic for high-throughput C-based schema validation.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_health.py
```

---

### Story 02: Async Event Loop, Non-Blocking Concurrency & Lifespan Management

* **Module**: Module 01: Python & FastAPI Foundations
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01
* **Leads To**: Story 08, Story 09, Story 29
* **Primary Code Files**: `backend/app/main.py`, `backend/app/cache/redis.py`, `backend/app/db/session.py`
* **Concrete Symbol / Class**: `app.main:lifespan / asynccontextmanager`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters
Proper lifecycle management guarantees that database pools, Redis clients, and seed fixtures are safely initialized before taking traffic and gracefully closed on SIGTERM.

#### 2. Concept & Architecture
Python asyncio event loop cooperative multitasking: I/O operations yield control with await, allowing thousands of concurrent requests per worker.

#### 3. How It Works Internally
lifespan context manager runs code before yield on server startup and code after yield on server shutdown.

#### 4. EstateMap Implementation
app/main.py lifespan initializes Redis connection pools, verifies PostgreSQL connectivity, runs seed_all(), and teardowns pools on exit.

#### 5. Code Flow & Request Lifecycle
```text
Process Start -> Uvicorn triggers lifespan -> init_redis() -> init_db() -> seed_all() -> yield (Serve Requests) -> close_redis() -> dispose_engine() -> Process Exit.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup resources before taking requests
    db_pool = await create_db_pool()
    redis_client = await init_redis()
    yield
    # Cleanup resources on shutdown
    await redis_client.close()
    await db_pool.close()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Forgetting the yield statement in the lifespan context manager causes FastAPI to hang during startup, timing out health checks.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_database.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Lifespan context managers replace deprecated @app.on_event('startup') with structured, type-safe exception handling.

#### 9. System Design & Scaling Angle
Graceful shutdown allows in-flight database transactions and HTTP requests to complete before closing sockets during rolling deployments.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How does Python asyncio handle 10,000 concurrent I/O-bound requests on a single CPU core?
* **Answer**: When a coroutine awaits network I/O (database query or HTTP call), it yields control to the event loop, which immediately schedules other ready coroutines, preventing thread blocking.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_database.py
```

---

### Story 03: Type-Safe Environment Configuration with Pydantic-Settings

* **Module**: Module 01: Python & FastAPI Foundations
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01
* **Leads To**: Story 04, Story 08, Story 13, Story 29, Story 35
* **Primary Code Files**: `backend/app/core/config.py`, `.env.example`
* **Concrete Symbol / Class**: `app.core.config:Settings / get_settings`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters
Failing fast during boot when environment variables (DB URLs, API keys, TTLs) are invalid prevents runtime 500 errors in production.

#### 2. Concept & Architecture
Strict schema parsing transforms raw environment string values into typed integers, booleans, and PostgresDsn objects with default fallbacks.

#### 3. How It Works Internally
Pydantic BaseSettings reads .env files, coerces data types, and validates constraints (e.g. rate limits > 0, valid log levels).

#### 4. EstateMap Implementation
app/core/config.py defines Settings with database URLs, Redis parameters, rate limits, AI provider credentials, and exposes get_settings().

#### 5. Code Flow & Request Lifecycle
```text
App Start -> get_settings() -> Reads os.environ & .env -> Pydantic validates types -> Cached singleton injected across services.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_PER_MINUTE: int = 100
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Setting an invalid port string like DATABASE_URL='postgres://user:pass@localhost:abc/db' raises a ValidationError, halting the app immediately.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_health.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Pydantic-Settings provides compile-time typing and automated validation over fragile, manual os.environ.get() dictionaries.

#### 9. System Design & Scaling Angle
12-Factor App config separation allows the exact same Docker image to run across local, staging, and production environments with different .env files.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why is Pydantic-Settings preferred over os.getenv in production backend systems?
* **Answer**: Pydantic-Settings automatically parses and validates types, enforces mandatory fields at startup, prevents type-coercion bugs, and supports hierarchical config injection.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_health.py
```

---

### Story 04: RFC 7807 Centralized Error Handling & Structured Request ID Logging

* **Module**: Module 01: Python & FastAPI Foundations
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01, Story 03
* **Leads To**: Story 05, Story 14, Story 32
* **Primary Code Files**: `backend/app/core/exceptions.py`, `backend/app/core/exception_handlers.py`, `backend/app/core/middleware.py`
* **Concrete Symbol / Class**: `AppException / validation_exception_handler / RequestIDMiddleware`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_exceptions.py`

#### 1. Why This Matters
Consistent error contracts prevent leaking raw database stack traces and enable correlated distributed log debugging.

#### 2. Concept & Architecture
RFC 7807 Problem Details for HTTP APIs standardizes error JSON responses (type, title, status, detail, instance).

#### 3. How It Works Internally
Custom exception classes inherit from AppException. FastAPI exception handlers intercept exceptions and format structured JSON responses.

#### 4. EstateMap Implementation
app/core/exceptions.py defines NotFoundException, RateLimitExceededException, ValidationException. Middleware injects X-Request-ID.

#### 5. Code Flow & Request Lifecycle
```text
Incoming Request -> RequestIDMiddleware generates/extracts X-Request-ID -> Route raises AppException -> Exception Handler formats RFC 7807 JSON -> Response returned with X-Request-ID header.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"type": exc.error_code, "title": exc.detail, "status": exc.status_code, "instance": str(request.url)}
    )
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Letting raw SQLAlchemy exceptions bubble up returns HTTP 500 containing raw SQL queries, column names, and internal server paths.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_exceptions.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
RFC 7807 standardized schema over custom error dicts allows frontend clients and API consumers to handle errors uniformly.

#### 9. System Design & Scaling Angle
Logging X-Request-ID in every log entry allows DevOps and developers to trace an entire request journey across microservices with a single grep.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you handle exceptions and error responses cleanly across a large FastAPI application?
* **Answer**: Define a domain exception hierarchy inheriting from a base AppException. Register centralized FastAPI exception handlers that format errors according to RFC 7807 Problem Details.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_exceptions.py
```

---

## Module 02: REST API Design & Validation

### Story 05: Request & Response Schema Validation with Pydantic v2

* **Module**: Module 02: REST API Design & Validation
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01, Story 03, Story 04
* **Leads To**: Story 06, Story 07, Story 10, Story 21, Story 36
* **Primary Code Files**: `backend/app/schemas/property.py`, `backend/app/schemas/search.py`, `backend/app/schemas/auth.py`
* **Concrete Symbol / Class**: `PropertyResponse / PropertyCreate / PropertyFilterParams`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_property_schemas.py`

#### 1. Why This Matters
Input validation at the API boundary protects domain services and SQL queries from malformed payloads.

#### 2. Concept & Architecture
Pydantic v2 Rust core (pydantic-core) delivers high-throughput serialization and schema validation.

#### 3. How It Works Internally
app/schemas/ defines strict BaseModel schemas with Field constraints (e.g. price > 0, latitude [-90, 90]).

#### 4. EstateMap Implementation
app/schemas/ defines PropertyCreate, PropertyUpdate, PropertyResponse models with exact typing and field aliases.

#### 5. Code Flow & Request Lifecycle
```text
HTTP Request Payload -> FastAPI body parser -> Pydantic model validation -> Clean typed object passed to endpoint -> Return schema serializes output.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from pydantic import BaseModel, Field

class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    price: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=1, le=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Passing negative prices or out-of-range coordinates returns HTTP 422 Unprocessable Entity with exact field pointers.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_property_schemas.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Pydantic schemas decouple database model structures from public API contracts (preventing over-fetching and unintended schema exposure).

#### 9. System Design & Scaling Angle
Validated request schemas act as compile-time documentation for OpenAPI/Swagger and protect internal systems from invalid input formats.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is the difference between ORM models and Pydantic schemas?
* **Answer**: ORM models map to database tables and relationships; Pydantic schemas enforce API input/output validation, serialization, and type boundaries.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_property_schemas.py
```

---

### Story 06: Deterministic Pagination, Sorting & Query Parameter Contracts

* **Module**: Module 02: REST API Design & Validation
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05
* **Leads To**: Story 07, Story 10
* **Primary Code Files**: `backend/app/utils/pagination.py`, `backend/app/repositories/property_repository.py`
* **Concrete Symbol / Class**: `PropertyRepository.list / PropertyRepository._apply_sorting`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters
Non-deterministic sorting causes duplicate or missing items across paginated API requests during concurrent database writes.

#### 2. Concept & Architecture
Stable sorting requires appending a unique primary key tie-breaker to all ORDER BY clauses.

#### 3. How It Works Internally
PropertyRepository._apply_sorting adds Property.id.desc() as the final sorting clause.

#### 4. EstateMap Implementation
app/utils/pagination.py and PropertyRepository apply LIMIT, OFFSET, and compound ORDER BY clauses with tie-breakers.

#### 5. Code Flow & Request Lifecycle
```text
GET /api/v1/properties?limit=20&offset=40 -> Query params parsed -> Repository appends ORDER BY price ASC, id DESC -> Database executes indexed fetch -> Paginated list returned.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def apply_sorting(query, sort_by: str, sort_order: str):
    order_col = getattr(Property, sort_by, Property.created_at)
    if sort_order == "asc":
        return query.order_by(order_col.asc(), Property.id.asc())
    return query.order_by(order_col.desc(), Property.id.desc())
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Sorting by price alone causes unstable row ordering when multiple properties share the exact same price, resulting in duplicate items across pages.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_properties.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Offset pagination is simple and flexible for moderate datasets; Keyset/Cursor pagination is reserved for millions of rows.

#### 9. System Design & Scaling Angle
Pagination bounds database memory consumption and network payload sizes, preventing out-of-memory errors on large tables.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why is tie-breaking necessary in database pagination?
* **Answer**: Without unique tie-breaking, database query planners return rows with identical sort values in arbitrary physical disk order, creating duplicates or missing items across pages.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_properties.py
```

---

### Story 07: Advanced Multi-Facet Filter Query Generation

* **Module**: Module 02: REST API Design & Validation
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05, Story 06
* **Leads To**: Story 10, Story 18
* **Primary Code Files**: `backend/app/repositories/property_repository.py`, `backend/app/schemas/property.py`
* **Concrete Symbol / Class**: `PropertyRepository._apply_common_filters / PropertyFilterParams`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_filter_equivalence.py`

#### 1. Why This Matters
Hardcoded SQL strings lead to SQL injection vulnerabilities and unmaintainable conditional branching.

#### 2. Concept & Architecture
Composable AST query building appends binary filter expressions to the query object only when parameters are present.

#### 3. How It Works Internally
PropertyRepository._apply_common_filters checks filter params and chains .where() conditions cleanly.

#### 4. EstateMap Implementation
PropertyRepository encapsulates filter generation, applying min_price, max_price, bedrooms, property_type, and city conditions.

#### 5. Code Flow & Request Lifecycle
```text
FilterParams received -> Repository initializes select(Property) -> _apply_common_filters chains active conditions -> Query executed via async session.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def apply_filters(query, filters: PropertyFilterParams):
    if filters.min_price is not None:
        query = query.where(Property.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Property.price <= filters.max_price)
    if filters.bedrooms is not None:
        query = query.where(Property.bedrooms == filters.bedrooms)
    return query
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Applying filters without index coverage on large tables results in full table sequential scans and high query latency.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_filter_equivalence.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Dynamic SQLAlchemy query compilation ensures parameterized safety while supporting arbitrary filter combinations.

#### 9. System Design & Scaling Angle
Composite and partial B-Tree indexes must align with the most frequent multi-facet filter combinations (e.g. city + property_type + price).

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you prevent SQL injection in complex dynamic search queries?
* **Answer**: Use parameterized query builders like SQLAlchemy where values are passed out-of-band and never concatenated directly as raw SQL strings.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_filter_equivalence.py
```

---

## Module 03: PostgreSQL & SQLAlchemy 2.0 Async

### Story 08: Relational Data Modeling, Foreign Keys & Schema Integrity

* **Module**: Module 03: PostgreSQL & SQLAlchemy 2.0 Async
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01, Story 03
* **Leads To**: Story 09, Story 10, Story 11, Story 16
* **Primary Code Files**: `backend/app/models/property.py`, `backend/app/models/user.py`, `backend/app/models/poi.py`
* **Concrete Symbol / Class**: `Property / User / PointOfInterest / Base`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters
Database constraints provide the final defense line for data integrity even if application bugs occur.

#### 2. Concept & Architecture
Relational normalization (3NF) eliminates data redundancy while foreign keys enforce referential integrity.

#### 3. How It Works Internally
app/models/ defines declarative tables with mapped_column, CheckConstraint('price > 0'), and foreign keys.

#### 4. EstateMap Implementation
app/models/property.py, user.py, and poi.py define declarative SQLAlchemy 2.0 models with relationships, cascades, and constraints.

#### 5. Code Flow & Request Lifecycle
```text
Domain Entity Definition -> Base declarative metadata -> Table definition with foreign keys and check constraints -> Database schema synchronization.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, ForeignKey, CheckConstraint

class Base(DeclarativeBase):
    pass

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    __table_args__ = (CheckConstraint("price > 0", name="chk_price_positive"),)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Deleting a user without CASCADE rules on related properties triggers a ForeignKeyViolation error and fails the operation.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_database.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Relational PostgreSQL was chosen over document stores to guarantee strict transactional ACID consistency for real estate listings.

#### 9. System Design & Scaling Angle
Normalized tables prevent update anomalies; foreign keys and check constraints guarantee data consistency at the storage layer.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why enforce check constraints at the database level when Pydantic already validates inputs?
* **Answer**: Defense-in-depth: database constraints protect against direct database updates, migrations, asynchronous background jobs, and multi-service writes.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_database.py
```

---

### Story 09: SQLAlchemy 2.0 Async Session Lifecycles & Asyncpg Connection Pooling

* **Module**: Module 03: PostgreSQL & SQLAlchemy 2.0 Async
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 02, Story 08
* **Leads To**: Story 10, Story 13, Story 18
* **Primary Code Files**: `backend/app/db/session.py`, `backend/app/db/base.py`
* **Concrete Symbol / Class**: `async_session_factory / create_async_engine / get_db`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters
Synchronous database drivers block the Python asyncio event loop, collapsing concurrent API throughput.

#### 2. Concept & Architecture
AsyncSession with asyncpg performs non-blocking socket I/O, yielding control during query execution.

#### 3. How It Works Internally
app/db/session.py initializes create_async_engine and yields AsyncSession via FastAPI Depends(get_db).

#### 4. EstateMap Implementation
app/db/session.py configures connection pool parameters (pool_size=20, max_overflow=10, pool_recycle, pool_pre_ping) and get_db dependency.

#### 5. Code Flow & Request Lifecycle
```text
HTTP Request -> FastAPI get_db dependency acquires session from pool -> Route executes queries -> Request ends -> get_db commits/closes session back to pool.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db", pool_size=20, max_overflow=10)
session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Forgetting to commit or rollback a session leaves transactions in 'idle in transaction' state, locking rows and starving the connection pool.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_database.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Asyncpg delivers 3-5x higher throughput compared to traditional synchronous psycopg2 under high concurrency.

#### 9. System Design & Scaling Angle
Connection pooling reuses persistent TCP connections, avoiding expensive TLS/TCP handshakes on every incoming HTTP request.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What happens if an async endpoint calls a synchronous blocking database library?
* **Answer**: It blocks the single asyncio event loop thread, preventing all concurrent requests from making progress until the query finishes.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_database.py
```

---

### Story 10: Repository Pattern & Async Database Encapsulation

* **Module**: Module 03: PostgreSQL & SQLAlchemy 2.0 Async
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 08, Story 09
* **Leads To**: Story 18, Story 22, Story 25
* **Primary Code Files**: `backend/app/repositories/property_repository.py`, `backend/app/repositories/user_repository.py`
* **Concrete Symbol / Class**: `PropertyRepository / UserRepository`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters
Direct SQL queries inside API route handlers make code untestable and violate single-responsibility principles.

#### 2. Concept & Architecture
Repository pattern acts as an in-memory collection interface over persistent storage.

#### 3. How It Works Internally
PropertyRepository receives AsyncSession and exposes get_by_id, list, search_radius, and search_bbox methods.

#### 4. EstateMap Implementation
app/repositories/property_repository.py encapsulates all SQL operations for properties, abstracting session execution from service logic.

#### 5. Code Flow & Request Lifecycle
```text
API Router calls PropertyService -> PropertyService calls PropertyRepository.get_by_id(session, id) -> Repository executes select() -> Returns entity.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class PropertyRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, property_id: int) -> Optional[Property]:
        stmt = select(Property).where(Property.id == property_id, Property.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Leaking raw SQLAlchemy query objects to the presentation layer creates lazy-loading MissingGreenlet errors in async contexts.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_properties.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Repository pattern introduces minor boilerplate but enables straightforward unit testing and centralized query performance optimization.

#### 9. System Design & Scaling Angle
Data access layer encapsulation allows swapping storage engines or optimizing queries without altering business service logic.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why use the Repository pattern with an ORM?
* **Answer**: It isolates data access logic, making unit testing simpler with mocks and query optimization centralized in one file.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_properties.py
```

---

### Story 11: Schema Migrations with Alembic & Reproducible Database Versioning

* **Module**: Module 03: PostgreSQL & SQLAlchemy 2.0 Async
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 08, Story 10
* **Leads To**: Story 12, Story 16
* **Primary Code Files**: `backend/alembic/env.py`, `backend/alembic/versions/2026_09_04_0001-0001_initial_postgis.py`
* **Concrete Symbol / Class**: `run_migrations_online / Alembic Revisions 0001-0004`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters
Manual SQL alter scripts lead to environment drift, unrepeatable deployments, and broken production schemas.

#### 2. Concept & Architecture
Linear migration DAG tracks applied revisions in the alembic_version table.

#### 3. How It Works Internally
backend/alembic/ manages 4 sequential revisions: PostGIS extension, users table, properties/amenities, and POIs.

#### 4. EstateMap Implementation
backend/alembic/env.py imports Base metadata, configures async connection, and applies versioned migration scripts.

#### 5. Code Flow & Request Lifecycle
```text
Developer runs alembic upgrade head -> Alembic checks alembic_version table -> Executes missing revision scripts in transaction -> Updates alembic_version.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# alembic revision script example
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
def downgrade() -> None:
    op.drop_table('users')
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Applying a migration with a non-nullable column without a default value fails if rows already exist in production.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_database.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Alembic integrates directly with SQLAlchemy declarative metadata for automated schema diff detection.

#### 9. System Design & Scaling Angle
Database schema versioning enables reproducible CI/CD test environments and safe rollbacks during blue/green deployments.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you handle database migrations with zero downtime?
* **Answer**: Use the Expand/Contract pattern: add new nullable columns first, deploy updated code, backfill data, and finally make columns non-nullable in a subsequent migration.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_database.py
```

---

### Story 12: Deterministic Database Seeding & Fixture Management

* **Module**: Module 03: PostgreSQL & SQLAlchemy 2.0 Async
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 08, Story 10, Story 11
* **Leads To**: Story 18, Story 22
* **Primary Code Files**: `backend/app/db/seed_all.py`, `backend/app/db/seed_properties.py`, `backend/app/db/seed_pois.py`
* **Concrete Symbol / Class**: `seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters
Deterministic seed fixtures ensure that local testing, spatial queries, and demo search flows produce predictable results.

#### 2. Concept & Architecture
Idempotent seeding scripts verify existing records before inserting to avoid primary key collisions.

#### 3. How It Works Internally
app/db/seed_all.py is called during FastAPI lifespan startup to seed listings and POIs if tables are empty.

#### 4. EstateMap Implementation
app/db/seed_properties.py and seed_pois.py load structured geographic coordinates, amenities, and price tiers into the database.

#### 5. Code Flow & Request Lifecycle
```text
Lifespan Startup -> seed_all() checks SELECT count(*) FROM properties -> If 0, inserts curated properties and POIs in a single transaction.
```

#### 6. Build It Yourself (Python Blueprint)
```python
async def seed_properties(session: AsyncSession):
    stmt = select(func.count(Property.id))
    count = (await session.execute(stmt)).scalar()
    if count == 0:
        for data in SEED_DATA:
            prop = Property(**data)
            session.add(prop)
        await session.commit()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Non-deterministic seeding with random coordinates causes spatial distance tests to fail intermittently.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_database.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Hardcoded curated seed fixtures provide immediate out-of-the-box local developer onboarding.

#### 9. System Design & Scaling Angle
Seed fixtures replicate realistic real-world geographic clusters, enabling accurate spatial index testing and ranking calibration.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you ensure integration tests run against predictable data?
* **Answer**: Idempotent database seeders and deterministic fixtures loaded in test transaction boundaries with rollback on test completion.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_database.py
```

---

## Module 04: Authentication & Security Boundaries

### Story 13: Password Hashing with Argon2id & Cryptographic Salting

* **Module**: Module 04: Authentication & Security Boundaries
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 03, Story 08
* **Leads To**: Story 14, Story 15
* **Primary Code Files**: `backend/app/core/security.py`, `backend/app/services/auth_service.py`
* **Concrete Symbol / Class**: `get_password_hash / verify_password / PasswordHasher`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_security.py`

#### 1. Why This Matters
Storing plaintext or MD5/SHA256 hashed passwords exposes user accounts to instant rainbow table compromise.

#### 2. Concept & Architecture
Argon2id combines data-independent and data-dependent memory access for maximum side-channel and ASIC resistance.

#### 3. How It Works Internally
app/core/security.py implements get_password_hash and verify_password using passlib/argon2.

#### 4. EstateMap Implementation
app/core/security.py uses argon2-cffi to hash passwords with calibrated time cost and memory parameters.

#### 5. Code Flow & Request Lifecycle
```text
User Registration -> Plaintext Password -> Argon2id generates salt & hash -> Hash stored in users.hashed_password.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Using fast cryptographic hashes (SHA-256) allows attackers to compute billions of guesses per second on modern GPUs.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_security.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Argon2id is computationally heavier than bcrypt but provides superior resistance to dedicated hardware cracking.

#### 9. System Design & Scaling Angle
Memory-hard hashing forces attackers to allocate significant RAM per crack attempt, making parallel attacks economically infeasible.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why is SHA-256 unsuitable for password storage?
* **Answer**: SHA-256 is designed to be fast for data integrity; password hashing requires slow, memory-hard algorithms like Argon2id to defeat brute-force and GPU rainbow table attacks.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_security.py
```

---

### Story 14: Stateless JWT Authentication, Token Expiration & Signature Verification

* **Module**: Module 04: Authentication & Security Boundaries
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 03, Story 13
* **Leads To**: Story 15, Story 33
* **Primary Code Files**: `backend/app/core/security.py`, `backend/app/api/v1/auth.py`
* **Concrete Symbol / Class**: `create_access_token / decode_access_token / TokenSchema`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_auth.py`

#### 1. Why This Matters
Stateless JWTs allow backend API instances to verify user identity without querying a central session database on every request.

#### 2. Concept & Architecture
JWT consists of Header, Payload (claims), and HMAC-SHA256 Signature verified via secret key.

#### 3. How It Works Internally
app/core/security.py generates tokens with ACCESS_TOKEN_EXPIRE_MINUTES (60 min) and decodes sub/role claims.

#### 4. EstateMap Implementation
app/core/security.py implements create_access_token and decode_access_token with PyJWT HS256 validation.

#### 5. Code Flow & Request Lifecycle
```text
POST /api/v1/auth/login -> AuthService verifies password -> create_access_token() signs payload -> Returns access_token -> Client sends Bearer token.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Failing to verify the 'exp' claim allows expired tokens to remain valid indefinitely.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_auth.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Stateless JWTs eliminate database session lookups but require token revocation strategies (e.g. short TTLs) for instant logout.

#### 9. System Design & Scaling Angle
Stateless tokens allow seamless horizontal scaling of backend servers because any worker node can verify the signature independently.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do stateless JWTs scale better than session IDs?
* **Answer**: The server verifies the cryptographic signature locally using the shared secret key without needing shared session database lookups on every request.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_auth.py
```

---

### Story 15: Dependency-Based Role Authorization & Resource Ownership Validation

* **Module**: Module 04: Authentication & Security Boundaries
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 13, Story 14
* **Leads To**: Story 18, Story 42
* **Primary Code Files**: `backend/app/core/dependencies.py`, `backend/app/services/property_service.py`
* **Concrete Symbol / Class**: `get_current_user / get_current_active_user / require_role`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_auth.py`

#### 1. Why This Matters
Prevent Broken Object Level Authorization (BOLA/IDOR) where users modify resources owned by other users.

#### 2. Concept & Architecture
FastAPI Depends() injects verified user objects into endpoint parameters before handler execution.

#### 3. How It Works Internally
app/core/dependencies.py extracts Bearer token, fetches user, and PropertyService verifies property.owner_id == user.id.

#### 4. EstateMap Implementation
app/core/dependencies.py provides reusable security dependencies (get_current_user, get_current_active_admin) that parse tokens.

#### 5. Code Flow & Request Lifecycle
```text
Incoming Request -> Depends(get_current_user) extracts Bearer token -> Validates token signature -> Fetches User entity -> Passes user to route handler.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user = await UserRepository.get_by_id(db, int(payload.get("sub")))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Relying solely on frontend role hiding allows malicious users to send direct POST/DELETE requests to API endpoints.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_auth.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Dependency injection centralizes security checks, preventing boilerplate code duplication across route handlers.

#### 9. System Design & Scaling Angle
Declarative security dependencies ensure authorization rules are enforced consistently across all private API endpoints.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is an IDOR vulnerability and how do you prevent it?
* **Answer**: Insecure Direct Object Reference occurs when an API accepts an object ID without verifying that the requesting user owns that object. Prevent it by checking ownership in the service layer before mutation.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_auth.py
```

---

## Module 05: PostGIS Spatial Search

### Story 16: Geospatial Coordinates, WGS84 (EPSG:4326) & PostGIS POINT Storage

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 08, Story 11
* **Leads To**: Story 17, Story 18, Story 19
* **Primary Code Files**: `backend/app/models/property.py`, `backend/app/models/poi.py`
* **Concrete Symbol / Class**: `mapped_column(Geometry(geometry_type='POINT', srid=4326)) / idx_properties_location`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters
Standard SQL numeric columns cannot perform spherical distance calculations or spatial bounding box containment.

#### 2. Concept & Architecture
WGS84 (EPSG:4326) defines points on the Earth's ellipsoidal surface using (Longitude, Latitude) coordinates.

#### 3. How It Works Internally
app/models/property.py defines location as Geometry('POINT', srid=4326) with explicit longitude-first ordering.

#### 4. EstateMap Implementation
app/models/property.py and poi.py map location columns using GeoAlchemy2 Geometry with SRID 4326.

#### 5. Code Flow & Request Lifecycle
```text
Insert Property -> GeoAlchemy2 converts (lon, lat) to WKT (POINT(lon lat)) -> PostgreSQL stores binary geometry representation.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Swapping latitude and longitude coordinates places points in the wrong hemisphere or ocean.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_spatial_search.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Storing as geometry with runtime geography casting combines fast Cartesian indexing with accurate ellipsoidal distance math.

#### 9. System Design & Scaling Angle
Spatial point storage enables spatial indexing, polygon intersection, and radius filtering natively inside PostgreSQL.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why does PostGIS use (Longitude, Latitude) ordering instead of (Lat, Lon)?
* **Answer**: PostGIS follows standard Cartesian (X, Y) coordinate conventions where Longitude is the horizontal X axis and Latitude is the vertical Y axis.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_spatial_search.py
```

---

### Story 17: GiST Spatial Indexing & Logarithmic Search Performance

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 16
* **Leads To**: Story 18, Story 19, Story 47
* **Primary Code Files**: `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`, `backend/app/models/property.py`
* **Concrete Symbol / Class**: `spatial_index=True / idx_properties_location (USING gist)`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters
Without spatial indexes, querying 100,000 properties requires computing mathematical distances for every row (O(N) full scan).

#### 2. Concept & Architecture
GiST organizes points into nested minimum bounding boxes (MBRs), reducing spatial search complexity to O(log N).

#### 3. How It Works Internally
Alembic revision 0003 creates idx_properties_location USING gist on the location geometry column.

#### 4. EstateMap Implementation
Database schema sets spatial_index=True on Geometry columns, instructing PostgreSQL to create a GiST R-Tree index.

#### 5. Code Flow & Request Lifecycle
```text
Spatial Query -> Query Planner checks GiST index -> Traverses R-Tree bounding boxes -> Eliminates non-overlapping nodes -> Returns matching rows in <5ms.
```

#### 6. Build It Yourself (Python Blueprint)
```python
-- Alembic SQL Migration for GiST Index
CREATE INDEX idx_properties_location ON properties USING gist (location);
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Calling functions on indexed columns without spatial operators prevents the PostgreSQL query planner from using the GiST index.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_spatial_search.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
GiST indexes have slightly higher write overhead during inserts but provide sub-10ms spatial filtering on large datasets.

#### 9. System Design & Scaling Angle
Spatial indexing enables the database to filter millions of geospatial listings across bounding boxes in single-digit milliseconds.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How does a GiST spatial index work internally?
* **Answer**: It builds an R-Tree hierarchy of bounding boxes. Searches eliminate entire tree branches whose bounding boxes do not intersect the query envelope.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_spatial_search.py
```

---

### Story 18: Geodesic Radius Search via ST_DWithin on Runtime Cast Geography

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 16, Story 17
* **Leads To**: Story 20, Story 24, Story 25
* **Primary Code Files**: `backend/app/services/geo_service.py`, `backend/app/repositories/property_repository.py`
* **Concrete Symbol / Class**: `PropertyRepository.search_radius / func.ST_DWithin / func.ST_Distance`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters
Querying Euclidean distance in degrees on EPSG:4326 results in massive distortion because degrees of longitude shrink near poles.

#### 2. Concept & Architecture
Casting geometry to geography enables spherical great-circle distance calculations directly in meters.

#### 3. How It Works Internally
PropertyRepository.search_radius casts Property.location to geography and executes ST_DWithin(loc, point, radius_m).

#### 4. EstateMap Implementation
app/repositories/property_repository.py casts location to Geography and applies func.ST_DWithin and func.ST_Distance.

#### 5. Code Flow & Request Lifecycle
```text
GET /api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=5000 -> Repository constructs ST_DWithin query -> PostGIS index filters bounding box -> Returns properties with distance_m.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint
from geoalchemy2 import Geography

def search_radius(session, lat: float, lon: float, radius_m: float):
    point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
    loc_geog = func.cast(Property.location, Geography)
    point_geog = func.cast(point, Geography)
    stmt = select(Property, ST_Distance(loc_geog, point_geog).label("distance_m")).where(
        ST_DWithin(loc_geog, point_geog, radius_m)
    ).order_by("distance_m")
    return session.execute(stmt)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Passing radius in meters to ST_DWithin on uncast geometry treats the radius as degrees (e.g. 5000 degrees covers the entire Earth).
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_spatial_search.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
ST_DWithin uses the index bounding box filter before computing exact geodesic distances, maximizing query speed.

#### 9. System Design & Scaling Angle
Geodesic radius search is the fundamental building block for location-based discovery in mobile and map applications.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why must you cast geometry to geography for ST_DWithin(geom, point, 5000)?
* **Answer**: Geometry calculations occur in planar units (degrees); casting to geography computes distances in real-world meters along the curved Earth spheroid.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_spatial_search.py
```

---

### Story 19: Viewport Bounding Box Filtering via ST_MakeEnvelope & GiST Intersects

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 16, Story 17
* **Leads To**: Story 21, Story 42
* **Primary Code Files**: `backend/app/services/geo_service.py`, `backend/app/api/v1/maps.py`, `backend/app/repositories/property_repository.py`
* **Concrete Symbol / Class**: `PropertyRepository.search_bbox / func.ST_MakeEnvelope / func.ST_Within`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters
Map-driven discovery requires fetching only the properties currently visible in the user's viewport bounding box.

#### 2. Concept & Architecture
ST_MakeEnvelope constructs a polygon envelope that checks bounding-box overlap directly against GiST index nodes.

#### 3. How It Works Internally
GET /api/v1/properties/map takes min_lat, max_lat, min_lon, max_lon and queries PropertyRepository.search_bbox.

#### 4. EstateMap Implementation
app/repositories/property_repository.py builds ST_MakeEnvelope polygon and filters properties with ST_Within / ST_Intersects.

#### 5. Code Flow & Request Lifecycle
```text
Map Pan/Zoom -> Frontend sends bounds (min_lat, min_lon, max_lat, max_lon) -> Repository generates ST_MakeEnvelope -> GiST index scans matching box -> Returns visible GeoJSON.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from geoalchemy2.functions import ST_MakeEnvelope, ST_Within

def search_bbox(session, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    stmt = select(Property).where(ST_Within(Property.location, envelope))
    return session.execute(stmt)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Passing min_lon > max_lon on queries crossing the 180th meridian produces an invalid inverted envelope.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_spatial_search.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Bounding box queries are significantly faster than radius calculations because they only require 2D box intersection checks.

#### 9. System Design & Scaling Angle
Viewport filtering prevents frontend maps from downloading hundreds of thousands of irrelevant points outside the visible screen.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How does a map viewport search query work in PostGIS?
* **Answer**: The API constructs a bounding envelope via ST_MakeEnvelope and uses the ST_Within or && operator to leverage the GiST spatial index efficiently.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_spatial_search.py
```

---

### Story 20: Points of Interest (POI) Proximity Aggregation & Spatial Intelligence

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 16, Story 18
* **Leads To**: Story 25, Story 27
* **Primary Code Files**: `backend/app/models/poi.py`, `backend/app/services/poi_service.py`, `backend/app/repositories/poi_repository.py`
* **Concrete Symbol / Class**: `POIService.get_location_intelligence / POIRepository.get_nearby_pois`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_pois.py`

#### 1. Why This Matters
Property buyers require neighborhood intelligence (walkability, transit proximity) to make informed purchasing decisions.

#### 2. Concept & Architecture
Spatial joins and radius counts group nearby POIs by category and compute nearest facility distances.

#### 3. How It Works Internally
POIService.get_location_intelligence queries POIRepository for nearby POIs, categorizes them, and caches the summary.

#### 4. EstateMap Implementation
app/services/poi_service.py coordinates spatial queries across POI categories and calculates summary statistics.

#### 5. Code Flow & Request Lifecycle
```text
Property ID requested -> POIService fetches property coordinates -> Queries POIRepository for POIs within radius -> Computes count per category & nearest distance -> Returns LocationIntelligenceResponse.
```

#### 6. Build It Yourself (Python Blueprint)
```python
async def get_nearby_pois(session, lat: float, lon: float, radius_m: float = 2000):
    point = func.cast(ST_SetSRID(ST_MakePoint(lon, lat), 4326), Geography)
    stmt = select(PointOfInterest, func.ST_Distance(func.cast(PointOfInterest.location, Geography), point).label("dist")).where(
        func.ST_DWithin(func.cast(PointOfInterest.location, Geography), point, radius_m)
    )
    return (await session.execute(stmt)).all()
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Executing separate spatial queries for every individual listing causes an N+1 spatial query bottleneck.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_pois.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Location intelligence is calculated on-demand with Redis caching (TTL=300s) to balance freshness with query performance.

#### 9. System Design & Scaling Angle
Pre-computed spatial joins or cached category aggregations allow fast real-time score calculation during property discovery.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you optimize spatial proximity aggregation for listings?
* **Answer**: Pre-index POIs with GiST, query with ST_DWithin radius buffers, and cache aggregate category summaries in Redis.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_pois.py
```

---

### Story 21: RFC 7946 GeoJSON Serialization & Strict Coordinate Ordering

* **Module**: Module 05: PostGIS Spatial Search
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 05, Story 16
* **Leads To**: Story 42
* **Primary Code Files**: `backend/app/schemas/geo.py`, `backend/app/api/v1/properties.py`
* **Concrete Symbol / Class**: `PropertyGeoJSONFeature / PropertyGeoJSONFeatureCollection / PointGeometry`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_geo_schemas.py`

#### 1. Why This Matters
Standardized GeoJSON payloads ensure seamless rendering across map libraries (MapLibre, Mapbox, Leaflet, QGIS).

#### 2. Concept & Architecture
RFC 7946 specifies that GeoJSON coordinate positions MUST be ordered as [easting, northing] -> [lon, lat].

#### 3. How It Works Internally
app/schemas/geo.py defines Pydantic models for GeoJSON Feature, FeatureCollection, and Point geometry serialization.

#### 4. EstateMap Implementation
app/schemas/geo.py defines type-safe Pydantic models enforcing GeoJSON specifications and property attributes.

#### 5. Code Flow & Request Lifecycle
```text
Database Property entity -> Pydantic validator extracts WKB/WKT coordinates -> Formats into FeatureCollection with [lon, lat] geometry -> Serialized to JSON.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from pydantic import BaseModel
from typing import List, Literal

class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] # [lon, lat]

class PropertyGeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: dict
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Emitting [lat, lon] coordinates in GeoJSON violates RFC 7946 and causes map clients to render markers in Antarctica.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_geo_schemas.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Serializing directly in Pydantic ensures schema validation without requiring heavy external GIS serialization dependencies.

#### 9. System Design & Scaling Angle
Standard GeoJSON schemas allow the backend API to be consumed by any GIS platform, web client, or mobile application.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is the RFC 7946 coordinate ordering standard?
* **Answer**: [Longitude, Latitude, Elevation], representing X (easting) then Y (northing).

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_geo_schemas.py
```

---

## Module 06: Location Intelligence & Routing

### Story 22: Deterministic Location Resolver for Tech Parks & Metropolitan Hubs

* **Module**: Module 06: Location Intelligence & Routing
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 16, Story 21
* **Leads To**: Story 23, Story 24, Story 39
* **Primary Code Files**: `backend/app/utils/location_resolver.py`, `backend/app/api/v1/search.py`
* **Concrete Symbol / Class**: `LocationResolver.resolve / KNOWN_LOCATIONS / METRO_BOUNDS`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_location_resolver.py`

#### 1. Why This Matters
Natural language searches contain informal locality names that need instant, deterministic coordinate resolution.

#### 2. Concept & Architecture
In-memory alias dictionary and normalized substring matching resolve known hubs with zero external network latency.

#### 3. How It Works Internally
LocationResolver matches query strings against 50+ curated Bengaluru and Chennai landmarks with bounding box checks.

#### 4. EstateMap Implementation
app/utils/location_resolver.py implements string normalization, alias dictionary lookup, and city bounding box verification.

#### 5. Code Flow & Request Lifecycle
```text
Query string received (e.g. 'near Electronic City') -> LocationResolver normalizes string -> Matches alias in dictionary -> Returns exact (lat, lon) coordinates.
```

#### 6. Build It Yourself (Python Blueprint)
```python
class LocationResolver:
    KNOWN_LOCATIONS = {
        "electronic city": (12.8399, 77.6770),
        "whitefield": (12.9698, 77.7500),
        "tidel park": (12.9893, 80.2483),
    }
    @classmethod
    def resolve(cls, query: str):
        normalized = query.lower().strip()
        for alias, coords in cls.KNOWN_LOCATIONS.items():
            if alias in normalized:
                return {"lat": coords[0], "lon": coords[1], "name": alias}
        return None
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Resolving locations outside supported city boundaries without error bounds causes searches to return empty results.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_location_resolver.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
In-memory deterministic resolver avoids expensive third-party geocoding API rate limits and external latency.

#### 9. System Design & Scaling Angle
Layered location resolution: check in-memory catalog first (sub-millisecond), fallback to external geocoders only for unknown addresses.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why use an in-memory landmark resolver before calling external geocoders?
* **Answer**: It resolves 90%+ of common local destination queries in sub-millisecond time with zero external API cost and zero network dependency.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_location_resolver.py
```

---

### Story 23: External HTTP Client with Async Httpx & OSRM Engine Integration

* **Module**: Module 06: Location Intelligence & Routing
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 02, Story 03
* **Leads To**: Story 24, Story 47
* **Primary Code Files**: `backend/app/services/routing/osrm_provider.py`, `backend/app/services/routing/factory.py`
* **Concrete Symbol / Class**: `OSRMProvider.calculate_route / RoutingProviderFactory / RoutingProvider`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_commute.py`

#### 1. Why This Matters
Straight-line distance ignores physical road geometry, traffic directionality, and water bodies (bridges vs direct lines).

#### 2. Concept & Architecture
Async httpx.AsyncClient queries OSRM routing endpoints using Contraction Hierarchies graph traversal.

#### 3. How It Works Internally
OSRMProvider sends coordinate pairs to OSRM /route/v1/driving/ and extracts duration (seconds) and distance (meters).

#### 4. EstateMap Implementation
app/services/routing/osrm_provider.py encapsulates async HTTP requests to OSRM with connection timeouts and response parsing.

#### 5. Code Flow & Request Lifecycle
```text
Commute request -> OSRMProvider formats coordinate URL -> httpx.AsyncClient executes GET with 5s timeout -> Parses route polyline and duration.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import httpx

class OSRMProvider:
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        self.base_url = base_url

    async def calculate_route(self, orig_lat: float, orig_lon: float, dest_lat: float, dest_lon: float):
        url = f"{self.base_url}/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=full"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            data = resp.json()
            route = data["routes"][0]
            return {"duration_sec": route["duration"], "distance_m": route["distance"], "geometry": route["geometry"]}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Not setting HTTP timeouts on external routing calls causes backend worker threads to hang when OSRM is slow.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_commute.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
OSRM provides open-source routing without commercial API fees (e.g. Google Maps API costs at scale).

#### 9. System Design & Scaling Angle
External API wrappers must encapsulate timeouts, retries with exponential backoff, and circuit breakers to prevent cascading system failures.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you safely integrate third-party HTTP services in an async backend?
* **Answer**: Use async HTTP clients (httpx) with strict connection/read timeouts, connection pooling, and circuit breaker fallbacks.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_commute.py
```

---

### Story 24: Multi-Modal Commute Matrix & Great-Circle Haversine Fallback

* **Module**: Module 06: Location Intelligence & Routing
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 18, Story 22, Story 23
* **Leads To**: Story 25, Story 30
* **Primary Code Files**: `backend/app/services/commute_service.py`, `backend/app/utils/geo.py`
* **Concrete Symbol / Class**: `CommuteService.calculate_commute_matrix / haversine_distance_km`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_commute.py`

#### 1. Why This Matters
Commute duration is the #1 decision factor for real estate buyers; routing failures must never crash the search pipeline.

#### 2. Concept & Architecture
Haversine formula calculates great-circle distance on a spherical Earth as a robust mathematical fallback.

#### 3. How It Works Internally
CommuteService checks Redis route cache, queries OSRM, and falls back to estimated speed-profile Haversine math on failure.

#### 4. EstateMap Implementation
app/services/commute_service.py coordinates multi-property commute calculations, route caching, and Haversine fallback logic.

#### 5. Code Flow & Request Lifecycle
```text
Properties & Destination passed -> CommuteService checks Redis cache -> Queries OSRM for uncached pairs -> If OSRM fails, applies Haversine fallback -> Returns matrix.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Dividing by zero speed in fallback calculations or failing to catch HTTP timeouts crashes the commute endpoint.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_commute.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Cached route matrices combined with mathematical fallbacks provide sub-50ms commute responses even during network outages.

#### 9. System Design & Scaling Angle
Computing commute matrices for 20 properties concurrently requires parallel async requests or batch matrix API endpoints to avoid latency bloat.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is your fallback strategy if external routing APIs fail?
* **Answer**: Gracefully degrade to in-memory Haversine distance with calibrated mode-specific velocity models (e.g. 25 km/h driving, 4 km/h walking).

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_commute.py
```

---

## Module 07: Deterministic Ranking & Business Logic

### Story 25: 6-Factor Mathematical Ranking Engine & Min-Max Score Normalization

* **Module**: Module 07: Deterministic Ranking & Business Logic
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05, Story 18, Story 24
* **Leads To**: Story 26, Story 27, Story 28
* **Primary Code Files**: `backend/app/services/ranking_service.py`, `backend/app/utils/ranking.py`
* **Concrete Symbol / Class**: `RankingService.rank_properties / calculate_price_score / calculate_bedroom_score`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ranking.py`

#### 1. Why This Matters
Black-box ML ranking produces non-reproducible, untestable results; deterministic MCDA ensures transparent, auditable scoring.

#### 2. Concept & Architecture
Multi-Criteria Decision Analysis (MCDA) linearly normalizes heterogeneous metrics (INR, sqft, minutes) into comparable [0, 1] scales.

#### 3. How It Works Internally
app/utils/ranking.py implements mathematical scoring functions with user-configurable or preset weight vectors.

#### 4. EstateMap Implementation
app/services/ranking_service.py coordinates scoring calculations across candidate properties and sorts by final composite score.

#### 5. Code Flow & Request Lifecycle
```text
Filtered properties passed to RankingService -> Evaluates 6 dimension scoring functions -> Multiplies by weight vector -> Sums to composite score -> Returns ranked list.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def calculate_price_score(price: float, min_p: float, max_p: float) -> float:
    if max_p <= min_p:
        return 1.0
    # Lower price gets higher score
    return max(0.0, min(1.0, 1.0 - (price - min_p) / (max_p - min_p)))
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Unnormalized raw prices (millions) dominating area scores (thousands) distorts composite ranking scores completely.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ranking.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Deterministic mathematical ranking guarantees identical inputs produce identical rank ordering every time.

#### 9. System Design & Scaling Angle
Separating hard database filters (WHERE price <= max_price) from soft ranking preferences (score based on budget affinity) delivers optimal user relevance.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why use deterministic mathematical ranking over an LLM for search results?
* **Answer**: Deterministic scoring is fast (sub-5ms), 100% reproducible, cost-free, and mathematically immune to hallucinations.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ranking.py
```

---

### Story 26: Dynamic Missing-Factor Weight Redistribution & Active Weight Sums

* **Module**: Module 07: Deterministic Ranking & Business Logic
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 25
* **Leads To**: Story 27, Story 28
* **Primary Code Files**: `backend/app/services/ranking_service.py`, `backend/app/utils/ranking.py`
* **Concrete Symbol / Class**: `RankingService._redistribute_weights / active_weight_sum normalization`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_ranking_scoring.py`

#### 1. Why This Matters
If an optional factor (e.g. commute weight = 0.25) is missing, total scores would cap at 0.75, penalizing all listings unfairly.

#### 2. Concept & Architecture
Active weight renormalization computes W_i' = W_i / sum(W_active), ensuring composite scores always sum to exactly 1.0.

#### 3. How It Works Internally
RankingService._redistribute_weights filters out inactive criteria and divides active weights by active_weight_sum.

#### 4. EstateMap Implementation
app/services/ranking_service.py checks active scoring factors and rescales weight vectors dynamically before scoring.

#### 5. Code Flow & Request Lifecycle
```text
Ranking query without commute destination -> Commute factor marked inactive -> Active weights summed -> Each active weight divided by sum -> Composite scores sum to 1.0.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def redistribute_weights(weights: dict, active_factors: set) -> dict:
    active_sum = sum(w for k, w in weights.items() if k in active_factors)
    if active_sum == 0:
        return {k: 1.0 / len(active_factors) if k in active_factors else 0.0 for k in weights}
    return {k: (w / active_sum if k in active_factors else 0.0) for k, w in weights.items()}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Hardcoding static weights when optional filters are omitted produces skewed scores and incorrect ranking order.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_ranking_scoring.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Proportional redistribution preserves relative user priority ratios among the remaining active factors.

#### 9. System Design & Scaling Angle
Dynamic weight normalization ensures multi-attribute scoring systems remain statistically valid regardless of missing input dimensions.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you handle missing criteria in multi-attribute scoring?
* **Answer**: Dynamically rescale active weights so their sum equals 1.0, preserving relative priority ratios.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_ranking_scoring.py
```

---

### Story 27: Factual Score Explainability & Human-Readable Score Breakdowns

* **Module**: Module 07: Deterministic Ranking & Business Logic
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 25, Story 26
* **Leads To**: Story 28, Story 38
* **Primary Code Files**: `backend/app/utils/ranking.py`, `backend/app/schemas/ranking.py`
* **Concrete Symbol / Class**: `generate_deterministic_explanations / FactorScoreDetail`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ranking.py`

#### 1. Why This Matters
Users trust search rankings when the system transparently explains WHY a listing ranked #1 versus #5.

#### 2. Concept & Architecture
Rule-based template generation derived directly from computed sub-scores guarantees factual explainability.

#### 3. How It Works Internally
app/utils/ranking.py generates FactorScoreDetail arrays attached to every RankedPropertyResponse.

#### 4. EstateMap Implementation
app/utils/ranking.py maps dimension scores and calculated deltas to human-readable factual strings.

#### 5. Code Flow & Request Lifecycle
```text
Score calculation finishes -> generate_deterministic_explanations() inspects top positive/negative score factors -> Formats string explanations -> Attached to response.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def explain_score(factor: str, score: float, raw_value: float) -> str:
    if factor == "price" and score > 0.8:
        return f"Priced competitively at ₹{raw_value:,.0f}"
    elif factor == "commute" and score > 0.8:
        return f"Convenient commute duration ({raw_value:.0f} mins)"
    return f"{factor.capitalize()} rating: {score*100:.0f}%" 
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Allowing LLMs to generate score explanations from scratch risks fabricating non-existent amenities or travel times.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ranking.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Deterministic explanation generation requires zero LLM tokens and executes in microseconds.

#### 9. System Design & Scaling Angle
Exposing structured explainability objects enables client applications to highlight key decision drivers without extra API roundtrips.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you provide explainability in recommendation systems?
* **Answer**: Expose atomic sub-score breakdowns and template-driven factual reasoning derived directly from scoring metrics.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ranking.py
```

---

### Story 28: Deterministic Property Comparison Engine & Dimension Winners

* **Module**: Module 07: Deterministic Ranking & Business Logic
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 25, Story 26, Story 27
* **Leads To**: Story 38, Story 42
* **Primary Code Files**: `backend/app/services/comparison_service.py`, `backend/app/schemas/comparison.py`
* **Concrete Symbol / Class**: `ComparisonService.compare_properties / ComparisonResult / DimensionWinner`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ai_comparison.py`

#### 1. Why This Matters
Comparing properties side-by-side requires objective numerical diffs before synthesizing a narrative summary.

#### 2. Concept & Architecture
Pairwise and 3-way dimensional min/max comparisons select verified winners for price per sqft, bedroom count, and commute.

#### 3. How It Works Internally
ComparisonService.compare_properties fetches listings, computes metric diffs, determines winners, and packages ComparisonResult.

#### 4. EstateMap Implementation
app/services/comparison_service.py implements structured metric diffing, price per sqft calculation, and winner selection.

#### 5. Code Flow & Request Lifecycle
```text
POST /api/v1/properties/compare [ids] -> Service fetches properties -> Calculates metric deltas -> Selects dimension winners -> Returns structured ComparisonResult.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def select_dimension_winner(properties: list, metric_key: str, lower_is_better: bool = False):
    if lower_is_better:
        winner = min(properties, key=lambda p: getattr(p, metric_key))
    else:
        winner = max(properties, key=lambda p: getattr(p, metric_key))
    return {"winner_id": winner.id, "metric": metric_key, "value": getattr(winner, metric_key)}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Comparing non-existent property IDs or mismatched city properties without validation creates invalid comparisons.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ai_comparison.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Deterministic dimension winners provide hard facts that ground subsequent AI-generated comparison summaries.

#### 9. System Design & Scaling Angle
Decoupling metric comparison from narrative generation allows caching the deterministic comparison result independently.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you structure property comparison in the backend?
* **Answer**: Compute deterministic dimensional deltas and metric winners first, then pass those verified facts to the presentation or AI layer.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ai_comparison.py
```

---

## Module 08: Redis In-Memory Caching

### Story 29: Redis Async Client & Cache-Aside (Lazy Loading) Architecture

* **Module**: Module 08: Redis In-Memory Caching
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 02, Story 03
* **Leads To**: Story 30, Story 31, Story 32
* **Primary Code Files**: `backend/app/cache/redis.py`, `backend/app/cache/cache_service.py`
* **Concrete Symbol / Class**: `CacheService.get_json / CacheService.set_json / init_redis`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_cache_service.py`

#### 1. Why This Matters
Repeated spatial and ranking queries saturate database CPU; caching identical viewport requests cuts latency from 50ms to 2ms.

#### 2. Concept & Architecture
Cache-Aside pattern loads data on-demand, keeping in-memory footprints bounded to active query working sets.

#### 3. How It Works Internally
CacheService wraps redis.asyncio client with JSON serialization and transparent database fallback on cache miss.

#### 4. EstateMap Implementation
app/cache/redis.py manages connection pool; app/cache/cache_service.py provides get_json, set_json, and delete methods.

#### 5. Code Flow & Request Lifecycle
```text
Client Request -> CacheService.get_json(key) -> Cache HIT: return cached JSON (2ms) -> Cache MISS: query DB (50ms) -> CacheService.set_json(key, data, ttl) -> Return response.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import json
import redis.asyncio as redis

class CacheService:
    def __init__(self, client: redis.Redis):
        self.redis = client

    async def get_json(self, key: str):
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def set_json(self, key: str, data: dict, ttl_seconds: int = 120):
        await self.redis.set(key, json.dumps(data), ex=ttl_seconds)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Storing un-versioned cache keys causes deserialization errors when Pydantic model schemas are updated in new deployments.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_cache_service.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Cache-Aside handles cache node restarts gracefully because the database remains the authoritative single source of truth.

#### 9. System Design & Scaling Angle
Caching read-heavy geospatial and ranking responses protects database connection pools and scales read throughput 10x.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How does the Cache-Aside pattern work and what are its failure modes?
* **Answer**: Application queries cache first; on miss, loads from DB and writes to cache with TTL. If cache fails, app gracefully falls back to querying the database directly.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_cache_service.py
```

---

### Story 30: Canonical Cache Key Design, Coordinate Precision & SHA-256 Hashing

* **Module**: Module 08: Redis In-Memory Caching
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 29
* **Leads To**: Story 31, Story 32
* **Primary Code Files**: `backend/app/cache/cache_keys.py`, `backend/app/cache/cache_service.py`
* **Concrete Symbol / Class**: `CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_cache_keys.py`

#### 1. Why This Matters
Slight float precision differences (12.9715999 vs 12.9716001) destroy cache hit ratios; coordinate rounding normalizes nearby requests.

#### 2. Concept & Architecture
Rounding coordinates to 4 decimal places (~11 meters) collapses microscopic GPS drift into canonical cache buckets.

#### 3. How It Works Internally
CacheKeys.normalize_coord rounds floats to 4 decimals; filter dicts are sorted and hashed with SHA-256.

#### 4. EstateMap Implementation
app/cache/cache_keys.py implements key generator functions with version prefixes (estatemap:v1:*) and deterministic hashing.

#### 5. Code Flow & Request Lifecycle
```text
Parameters received -> CacheKeys formats key: estatemap:v1:map:{min_lat}:{min_lon}:{max_lat}:{max_lon}:{sha256(filters)} -> Canonical key used in Redis lookup.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import hashlib
import json

class CacheKeys:
    @staticmethod
    def map_bbox_key(min_lat: float, min_lon: float, max_lat: float, max_lon: float, filters: dict) -> str:
        coords = f"{min_lat:.4f}:{min_lon:.4f}:{max_lat:.4f}:{max_lon:.4f}"
        filter_str = json.dumps(filters, sort_keys=True)
        h = hashlib.sha256(filter_str.encode()).hexdigest()[:12]
        return f"estatemap:v1:map:{coords}:{h}" 
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Unsorted dictionary serialization produces different JSON strings for identical filter sets, causing cache misses.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_cache_keys.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
SHA-256 digests keep Redis key lengths fixed and predictable regardless of complex filter parameter counts.

#### 9. System Design & Scaling Angle
Well-designed hierarchical key namespaces simplify monitoring, debugging, and targeted wildcard key invalidation.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you design cache keys for geospatial search queries?
* **Answer**: Normalize coordinates to fixed precision (e.g. 4 decimals), sort filter parameters deterministically, and hash with version prefixes to guarantee collision-free lookups.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_cache_keys.py
```

---

### Story 31: Cache Invalidation via Non-Blocking SCAN & TTL Stampede Mitigation

* **Module**: Module 08: Redis In-Memory Caching
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 29, Story 30
* **Leads To**: Story 32, Story 47
* **Primary Code Files**: `backend/app/cache/cache_service.py`, `backend/app/core/config.py`
* **Concrete Symbol / Class**: `CacheService.delete_pattern / CacheService.delete / CACHE_MAP_TTL_SECONDS`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_cache_service.py`

#### 1. Why This Matters
Using the blocking KEYS * command halts Redis event loops in production; SCAN iterates cursor-by-cursor safely.

#### 2. Concept & Architecture
TTL-based expiration guarantees eventual consistency; mutation hooks trigger active prefix invalidation.

#### 3. How It Works Internally
CacheService.delete_pattern uses redis.scan_iter(match=pattern, count=100) to delete matching keys without blocking.

#### 4. EstateMap Implementation
app/cache/cache_service.py implements delete_pattern using async scan_iter and applies configurable TTLs from Settings.

#### 5. Code Flow & Request Lifecycle
```text
Property Updated -> PropertyService calls CacheService.delete_pattern('estatemap:v1:map:*') -> redis.scan_iter iterates batches -> Keys deleted -> Next read re-caches fresh data.
```

#### 6. Build It Yourself (Python Blueprint)
```python
async def delete_pattern(redis_client, pattern: str):
    async for key in redis_client.scan_iter(match=pattern, count=100):
        await redis_client.delete(key)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Running KEYS 'estatemap:*' on a Redis instance with 1,000,000 keys locks Redis for several seconds, timing out all API requests.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_cache_service.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
SCAN has O(N) overall complexity across iterations but never blocks the single-threaded Redis event loop.

#### 9. System Design & Scaling Angle
Cache stampede mitigation: staggered TTL jitter and probabilistic early recomputation prevent database spikes when hot keys expire.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why is KEYS * dangerous in production Redis, and what is the alternative?
* **Answer**: KEYS * blocks the single-threaded Redis server until all keys are scanned, stalling all traffic. Use SCAN with cursor pagination instead.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_cache_service.py
```

---

## Module 09: Rate Limiting & Resilience

### Story 32: Sliding-Window Log Rate Limiting via Redis Sorted Sets (ZSET)

* **Module**: Module 09: Rate Limiting & Resilience
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 04, Story 29
* **Leads To**: Story 33, Story 34
* **Primary Code Files**: `backend/app/core/rate_limit.py`, `backend/app/core/middleware.py`
* **Concrete Symbol / Class**: `RateLimiter.is_rate_limited / redis.pipeline() / ZADD / ZREMRANGEBYSCORE`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_rate_limiting.py`

#### 1. Why This Matters
Fixed window rate limiters allow 2x traffic bursts across window boundaries (e.g. 100 requests at 00:59 and 100 at 01:00).

#### 2. Concept & Architecture
Sliding Window Log scores timestamps in a ZSET: removes items older than (now - window), counts remaining, and adds current timestamp.

#### 3. How It Works Internally
RateLimiter executes pipelined ZREMRANGEBYSCORE -> ZCARD -> ZADD -> EXPIRE, rejecting requests exceeding limit with HTTP 429.

#### 4. EstateMap Implementation
app/core/rate_limit.py implements RateLimiter class using async Redis pipelines for atomic sliding-window evaluation.

#### 5. Code Flow & Request Lifecycle
```text
Incoming Request -> RateLimiter executes Redis pipeline: ZREMRANGEBYSCORE(0, now-60) -> ZCARD -> If count >= limit: raise RateLimitExceededException -> Else ZADD(now, now) -> Allow request.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import time

async def is_rate_limited(redis_client, key: str, limit: int, window_sec: int = 60) -> tuple[bool, int]:
    now = time.time()
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window_sec)
    results = await pipe.execute()
    count = results[1]
    return (count >= limit, max(0, limit - count))
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Executing rate limiter Redis commands as separate non-pipelined network calls introduces race conditions under concurrency.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_rate_limiting.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Redis ZSET sliding window offers precision and burst protection with minimal memory per active client IP.

#### 9. System Design & Scaling Angle
Rate limiting protects downstream database connection pools and expensive AI endpoints from denial-of-service exhaustion.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How does a Redis sliding window log rate limiter work?
* **Answer**: Stores request timestamps in a ZSET, prunes timestamps older than now - window with ZREMRANGEBYSCORE, checks if ZCARD exceeds the limit, and records the current timestamp.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_rate_limiting.py
```

---

### Story 33: Multi-Tier Endpoint Scopes & RFC Rate Limit Headers

* **Module**: Module 09: Rate Limiting & Resilience
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 32
* **Leads To**: Story 34, Story 42
* **Primary Code Files**: `backend/app/core/rate_limit.py`, `backend/app/core/config.py`
* **Concrete Symbol / Class**: `X-RateLimit-Limit / X-RateLimit-Remaining / RateLimitExceededException`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_rate_limiting.py`

#### 1. Why This Matters
Expensive LLM and spatial ranking endpoints must have stricter limits than lightweight health and listing read endpoints.

#### 2. Concept & Architecture
Rate limiting keys are scoped by client identifier (IP or User ID) combined with the target endpoint tier.

#### 3. How It Works Internally
RateLimiter inspects request path, applies configured tier thresholds, and appends X-RateLimit-Remaining headers.

#### 4. EstateMap Implementation
app/core/rate_limit.py maps route paths to tier limits and formats RFC response headers (Limit, Remaining, Retry-After).

#### 5. Code Flow & Request Lifecycle
```text
Request evaluated -> RateLimiter determines remaining tokens -> Injects X-RateLimit-Limit & X-RateLimit-Remaining headers -> If blocked, returns HTTP 429 with Retry-After: 60.
```

#### 6. Build It Yourself (Python Blueprint)
```python
TIER_LIMITS = {
    "/api/v1/search/orchestrated": 15, # Expensive AI
    "/api/v1/search/ranked": 20,       # Ranking engine
    "default": 100                     # General reads
}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Omitting Retry-After headers on HTTP 429 causes aggressive frontend clients to hammer the server in a tight retry loop.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_rate_limiting.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Tiered scoping prevents heavy AI feature abuse from starving general browsing traffic.

#### 9. System Design & Scaling Angle
Cost-based rate limiting allocates infrastructure resources proportionally to business value and compute cost.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What headers should a well-designed rate-limited API return?
* **Answer**: X-RateLimit-Limit (max requests), X-RateLimit-Remaining (requests left in window), and Retry-After (seconds to wait when rate limited with HTTP 429).

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_rate_limiting.py
```

---

### Story 34: Fail-Open vs Fail-Closed Resiliency Policies on Cache Outage

* **Module**: Module 09: Rate Limiting & Resilience
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 32, Story 33
* **Leads To**: Story 37, Story 47
* **Primary Code Files**: `backend/app/core/rate_limit.py`, `backend/app/cache/cache_service.py`
* **Concrete Symbol / Class**: `RATE_LIMIT_FAIL_OPEN=True / RedisConnectionError handling`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_redis_degradation.py`

#### 1. Why This Matters
An auxiliary cache/rate-limiter outage should not bring down the entire property search application.

#### 2. Concept & Architecture
Circuit breaker and exception isolation catch RedisConnectionError and allow requests through when configured to fail open.

#### 3. How It Works Internally
RateLimiter and CacheService wrap Redis calls in try/except RedisError; on exception, log warning and return degraded fallback.

#### 4. EstateMap Implementation
app/core/rate_limit.py and app/cache/cache_service.py handle Redis connection errors gracefully based on RATE_LIMIT_FAIL_OPEN setting.

#### 5. Code Flow & Request Lifecycle
```text
Redis crashes -> RateLimiter attempts pipeline -> Catches ConnectionError -> Logs warning -> If fail_open=True: permits request -> Main API functionality continues uninterrupted.
```

#### 6. Build It Yourself (Python Blueprint)
```python
try:
    is_limited, remaining = await rate_limiter.check(ip)
except redis.RedisError as e:
    logger.warning("Redis rate limiter down: %s", e)
    if settings.RATE_LIMIT_FAIL_OPEN:
        is_limited, remaining = False, 999
    else:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Uncaught Redis connection errors bubbling to FastAPI middleware turn every API request into an HTTP 500 error.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_redis_degradation.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Failing open prioritizes system availability over strict rate enforcement during infrastructure degradation.

#### 9. System Design & Scaling Angle
Graceful degradation ensures non-essential auxiliary subsystem failures do not cause catastrophic core business outages.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is the difference between fail-open and fail-closed in rate limiting?
* **Answer**: Fail-open permits requests if the limiter is unreachable (prioritizing availability); fail-closed blocks requests (prioritizing resource protection).

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_redis_degradation.py
```

---

## Module 10: Multi-Provider AI Architecture

### Story 35: AI Provider Protocol & Structural Parity (Ollama Local & Gemini Cloud)

* **Module**: Module 10: Multi-Provider AI Architecture
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 03, Story 05
* **Leads To**: Story 36, Story 37, Story 38
* **Primary Code Files**: `backend/app/ai/protocol.py`, `backend/app/ai/ollama_provider.py`, `backend/app/ai/gemini_provider.py`
* **Concrete Symbol / Class**: `AIProvider / OllamaProvider / GeminiProvider / AIResponse`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_cross_provider_parity.py`

#### 1. Why This Matters
Tight coupling to a single commercial LLM vendor creates vendor lock-in and leaves the backend vulnerable to API outages.

#### 2. Concept & Architecture
Python Protocol enables structural subtyping (duck typing with static type checking) for swappable AI providers.

#### 3. How It Works Internally
app/ai/protocol.py defines AIProvider with parse_intent, explain_property, and compare_properties methods.

#### 4. EstateMap Implementation
app/ai/protocol.py defines the interface; ollama_provider.py and gemini_provider.py implement adapter classes.

#### 5. Code Flow & Request Lifecycle
```text
AI Service calls AIProvider method -> Active provider executes HTTP call to LLM engine -> Formats response into common AIResponse schema -> Returns to service.
```

#### 6. Build It Yourself (Python Blueprint)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class AIProvider(Protocol):
    async def parse_search_intent(self, query: str) -> dict: ...
    async def explain_property(self, property_data: dict, score_details: list) -> str: ...
    async def compare_properties(self, comparison_facts: dict) -> str: ...
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Provider implementations returning differing JSON structures break downstream state orchestrators.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_cross_provider_parity.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Unified AI protocol allows running cost-free local Ollama in development and scalable cloud Gemini in production.

#### 9. System Design & Scaling Angle
Adapter pattern isolates external SDK idiosyncrasies from core application domain logic.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you prevent vendor lock-in when integrating LLMs?
* **Answer**: Define a strict provider Protocol/Interface with standardized Pydantic input/output schemas implemented by all provider adapters.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_cross_provider_parity.py
```

---

### Story 36: Strict LLM Output Validation via Pydantic v2 Schemas

* **Module**: Module 10: Multi-Provider AI Architecture
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05, Story 35
* **Leads To**: Story 37, Story 38, Story 39
* **Primary Code Files**: `backend/app/schemas/ai.py`, `backend/app/services/ai_service.py`
* **Concrete Symbol / Class**: `AIExplanationResponse / AISearchIntent / ParseSearchResponse`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_ai_schemas.py`

#### 1. Why This Matters
LLMs frequently hallucinate invalid JSON, invent property IDs, or output negative budget values.

#### 2. Concept & Architecture
Regex JSON extraction followed by strict Pydantic model validation transforms non-deterministic text into type-safe domain objects.

#### 3. How It Works Internally
AIService parses LLM responses through Pydantic schemas, validating extracted criteria against known bounds.

#### 4. EstateMap Implementation
app/schemas/ai.py defines strict response schemas; app/services/ai_service.py extracts JSON and validates with model_validate_json.

#### 5. Code Flow & Request Lifecycle
```text
LLM returns raw text -> Regex extracts JSON block -> Pydantic model_validate() checks types and bounds -> If valid: return object -> If invalid: trigger fallback.
```

#### 6. Build It Yourself (Python Blueprint)
```python
class AISearchIntent(BaseModel):
    city: Optional[str] = None
    locality: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=1, le=10)
    destination: Optional[str] = None
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Directly parsing raw LLM JSON with json.loads() without Pydantic validation crashes downstream services on unexpected fields.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_ai_schemas.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Pydantic validation provides a resilient firewall between non-deterministic AI generation and deterministic database logic.

#### 9. System Design & Scaling Angle
Input sanitization and output schema validation are essential defenses against prompt injection and LLM hallucination.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you handle non-deterministic LLM responses in production?
* **Answer**: Request JSON mode, extract with regex, validate against Pydantic schemas, and fallback to deterministic logic on validation error.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_ai_schemas.py
```

---

### Story 37: Dynamic Provider Routing, Latency Timeouts & Circuit Failover

* **Module**: Module 10: Multi-Provider AI Architecture
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 35, Story 36
* **Leads To**: Story 38, Story 39
* **Primary Code Files**: `backend/app/ai/router.py`, `backend/app/services/ai_service.py`
* **Concrete Symbol / Class**: `AIRouter.get_provider / AIService._execute_with_fallback / AI_TIMEOUT_SECONDS`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ai_failover.py`

#### 1. Why This Matters
Local Ollama instances may hang under CPU load; cloud APIs may experience rate limiting (HTTP 429); the app must failover instantly.

#### 2. Concept & Architecture
Circuit failover tries the primary provider with asyncio.wait_for timeout, immediately routing to backup on failure.

#### 3. How It Works Internally
AIRouter inspects AI_PROVIDER setting; AIService executes primary provider and catches timeouts/errors to trigger fallback.

#### 4. EstateMap Implementation
app/ai/router.py resolves provider instances; app/services/ai_service.py wraps executions in asyncio.wait_for with try/except failover.

#### 5. Code Flow & Request Lifecycle
```text
AI Request -> AIRouter selects Primary (Ollama) -> asyncio.wait_for(primary.call(), timeout=5s) -> If Timeout/Error: Log warning -> AIRouter selects Backup (Gemini) -> Return response.
```

#### 6. Build It Yourself (Python Blueprint)
```python
async def execute_ai_with_failover(primary: AIProvider, backup: AIProvider, prompt: str):
    try:
        return await asyncio.wait_for(primary.call(prompt), timeout=5.0)
    except Exception as e:
        logger.warning("Primary AI failed (%s), switching to backup...", e)
        return await asyncio.wait_for(backup.call(prompt), timeout=5.0)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Unbounded async calls to external LLM APIs can hold open client connections for 60+ seconds, exhausting backend worker pools.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ai_failover.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Configurable provider routing allows cost optimization (local dev, hybrid staging, cloud prod).

#### 9. System Design & Scaling Angle
Multi-provider failover circuits provide 99.9%+ availability for AI-driven features despite third-party API instability.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you design a resilient multi-provider AI pipeline?
* **Answer**: Implement an AI router with strict execution timeouts (5s), automatic failover from local to cloud provider, and algorithmic fallbacks on complete outage.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ai_failover.py
```

---

### Story 38: Algorithmic Grounded Fallbacks & Hallucination Elimination

* **Module**: Module 10: Multi-Provider AI Architecture
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 27, Story 28, Story 36, Story 37
* **Leads To**: Story 39, Story 41
* **Primary Code Files**: `backend/app/services/ai_service.py`, `backend/app/services/comparison_service.py`
* **Concrete Symbol / Class**: `AIService.generate_fallback_explanation / AIService.generate_fallback_comparison`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ai_endpoints.py`

#### 1. Why This Matters
Total AI provider outages must never prevent users from seeing property search explanations or comparisons.

#### 2. Concept & Architecture
Rule-based template generation using deterministic score breakdown facts guarantees 100% uptime with zero hallucination.

#### 3. How It Works Internally
AIService generates structured fallback summaries using listing price, area, locality, and dimension winner data.

#### 4. EstateMap Implementation
app/services/ai_service.py implements template-based fallback generators that assemble verified property attributes into natural language.

#### 5. Code Flow & Request Lifecycle
```text
Primary & Backup AI providers fail -> AIService catches exception -> Calls generate_fallback_explanation(property, score_details) -> Assembles factual summary -> Returns with fallback=True flag.
```

#### 6. Build It Yourself (Python Blueprint)
```python
def generate_fallback_summary(prop: Property, winner: dict) -> str:
    return (
        f"{prop.title} in {prop.locality} offers {prop.bedrooms} BHK across {prop.area_sqft} sqft. "
        f"It is ranked #1 for {winner['metric']} with a competitive rate of ₹{prop.price:,.0f}."
    )
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Returning empty explanation strings or HTTP 500 when AI fails degrades user experience unnecessarily.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ai_endpoints.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Algorithmic fallbacks are instant and 100% accurate, though less linguistically varied than LLM output.

#### 9. System Design & Scaling Angle
Deterministic grounding guarantees that AI-augmented applications never display factually incorrect claims to end users.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you eliminate hallucination risk in mission-critical AI features?
* **Answer**: Ground all prompts strictly in deterministic database facts and provide rule-based algorithmic fallbacks when AI is unavailable.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ai_endpoints.py
```

---

## Module 11: Ask-the-Map Conversational Orchestration

### Story 39: Natural Language Search Intent Parsing & Backend Authority Boundary

* **Module**: Module 11: Ask-the-Map Conversational Orchestration
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05, Story 22, Story 36, Story 37
* **Leads To**: Story 40, Story 41
* **Primary Code Files**: `backend/app/services/search_orchestrator.py`, `backend/app/schemas/search.py`
* **Concrete Symbol / Class**: `SearchOrchestrator.orchestrate_search / SearchStatePatch / AskMapRequest`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ask_the_map.py`

#### 1. Why This Matters
AI models must only extract proposed search intent; the backend retains complete authority over database query execution.

#### 2. Concept & Architecture
Backend Authority Boundary: LLM output is strictly an untrusted patch proposal validated before application to state.

#### 3. How It Works Internally
SearchOrchestrator sends query to AI provider, parses SearchStatePatch, and validates location via LocationResolver.

#### 4. EstateMap Implementation
app/services/search_orchestrator.py implements intent parsing, state merging, and PostGIS query execution pipeline.

#### 5. Code Flow & Request Lifecycle
```text
User submits text -> AIService extracts SearchStatePatch -> LocationResolver validates destination -> SearchOrchestrator applies patch to state -> Executes DB query.
```

#### 6. Build It Yourself (Python Blueprint)
```python
class SearchStatePatch(BaseModel):
    city: Optional[str] = None
    locality: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    destination: Optional[str] = None
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Allowing the LLM to directly generate SQL WHERE clauses exposes the database to prompt injection and syntax errors.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ask_the_map.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Structured intent parsing separates natural language comprehension from secure PostGIS SQL execution.

#### 9. System Design & Scaling Angle
Intent extraction with backend query execution provides AI convenience while maintaining strict database security.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you prevent prompt injection in conversational database search?
* **Answer**: The LLM never writes SQL. It outputs a validated Pydantic patch schema which the backend applies to deterministic query builders.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ask_the_map.py
```

---

### Story 40: Stateless Conversational Search State Machine & State Reducer

* **Module**: Module 11: Ask-the-Map Conversational Orchestration
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 39
* **Leads To**: Story 41, Story 42
* **Primary Code Files**: `backend/app/services/search_orchestrator.py`, `backend/app/schemas/search.py`
* **Concrete Symbol / Class**: `ConversationalSearchState / SearchOrchestrator._apply_patch / state reducer`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_search_orchestrator.py`

#### 1. Why This Matters
Storing conversational search sessions in server memory breaks horizontal scaling when requests hit different backend instances.

#### 2. Concept & Architecture
Stateless state reducer: New State = Reducer(Old State, Patch), eliminating server-side session stickiness.

#### 3. How It Works Internally
AskMapRequest carries ConversationalSearchState; SearchOrchestrator merges patches and returns updated state in AskMapResponse.

#### 4. EstateMap Implementation
app/schemas/search.py defines ConversationalSearchState; app/services/search_orchestrator.py applies functional state reduction.

#### 5. Code Flow & Request Lifecycle
```text
POST /api/v1/search/orchestrated {query, state} -> Orchestrator extracts patch -> _apply_patch(current_state, patch) -> Returns (results, new_state).
```

#### 6. Build It Yourself (Python Blueprint)
```python
def reduce_state(current: ConversationalSearchState, patch: SearchStatePatch) -> ConversationalSearchState:
    new_state = current.model_copy()
    for field, val in patch.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(new_state, field, val)
    return new_state
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Relying on in-memory session dictionaries causes state loss whenever backend pods restart or scale horizontally.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_search_orchestrator.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Client-held state simplifies backend scaling at the cost of slightly larger HTTP request payloads.

#### 9. System Design & Scaling Angle
Stateless state machines allow backend API replicas to process any conversation turn without sticky session routing.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you design multi-turn conversational search without sticky sessions?
* **Answer**: Keep the backend stateless: client passes current search state in the request, backend reducer applies patches and returns the new state.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_search_orchestrator.py
```

---

### Story 41: Multi-Turn Criteria Modification, History Merging & Grounded Results

* **Module**: Module 11: Ask-the-Map Conversational Orchestration
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 39, Story 40
* **Leads To**: Story 42, Story 46
* **Primary Code Files**: `backend/app/services/search_orchestrator.py`, `backend/app/services/property_service.py`
* **Concrete Symbol / Class**: `SearchOrchestrator._execute_search / SearchOrchestrator._resolve_destination`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_ask_the_map.py`

#### 1. Why This Matters
A conversational assistant must support iterative refinement (now filter under 1 Cr, make it 2 bedrooms) seamlessly.

#### 2. Concept & Architecture
Orchestrator chains Domain Services (LocationResolver -> PropertyRepository -> RankingService -> POIService).

#### 3. How It Works Internally
SearchOrchestrator coordinates the complete search pipeline, producing matching properties, GeoJSON, and feedback.

#### 4. EstateMap Implementation
app/services/search_orchestrator.py coordinates multi-service execution, handles destination ambiguity, and formats conversational responses.

#### 5. Code Flow & Request Lifecycle
```text
Turn 1: 'Find 3BHK in Whitefield' -> Sets city=Bengaluru, bedrooms=3, locality=Whitefield -> Turn 2: 'Under 1.2 Cr' -> Merges max_price=12000000 -> Re-executes search.
```

#### 6. Build It Yourself (Python Blueprint)
```python
async def orchestrate(query: str, current_state: ConversationalSearchState):
    patch = await ai_service.parse_intent(query)
    updated_state = reduce_state(current_state, patch)
    properties = await property_repo.search(updated_state.to_filter_params())
    ranked = ranking_service.rank(properties, updated_state.ranking_weights)
    return {"results": ranked, "state": updated_state}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Failing to clear conflicting filter criteria (e.g. min_price > max_price after a patch) produces 0 search results.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_ask_the_map.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Centralizing orchestration in a dedicated service keeps API route handlers clean and easily testable.

#### 9. System Design & Scaling Angle
Domain service orchestration decouples conversational logic from raw database storage and third-party APIs.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Trace the end-to-end execution of a natural language search query.
* **Answer**: 1. AI extracts patch; 2. Resolver finds coordinates; 3. State Reducer updates criteria; 4. PostGIS filters DB; 5. Ranking scores results; 6. Response returned.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_ask_the_map.py
```

---

## Module 12: Backend ↔ Frontend API Integration

### Story 42: Backend ↔ Frontend API Integration Contract & Data Boundary

* **Module**: Module 12: Backend ↔ Frontend API Integration
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 05, Story 14, Story 21, Story 33, Story 40
* **Leads To**: Story 46, Story 48
* **Primary Code Files**: `backend/app/api/v1/properties.py`, `backend/app/api/v1/search.py`, `backend/app/api/v1/auth.py`
* **Concrete Symbol / Class**: `API Router definitions / OpenAPI JSON schemas / CORS middleware`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters
Clear API contracts enable frontend and backend teams to develop, test, and mock independently without coupling.

#### 2. Concept & Architecture
RESTful HTTP endpoints communicate strictly via standard JSON, GeoJSON, Authorization headers, and HTTP status codes.

#### 3. How It Works Internally
FastAPI automatically generates interactive OpenAPI docs (/docs) matching Pydantic schemas and error contracts.

#### 4. EstateMap Implementation
backend/app/api/v1/ defines versioned routers exposing properties, search, commute, ranking, and auth endpoints.

#### 5. Code Flow & Request Lifecycle
```text
Frontend makes fetch(url, {headers: {Authorization: Bearer token}}) -> FastAPI routes request -> Pydantic serializes response -> Frontend consumes JSON/GeoJSON.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# Standard FastAPI Router mounting
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Changing a response field name in the backend without updating the Pydantic schema causes frontend runtime type crashes.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_properties.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Strict JSON/GeoJSON contracts decouple the Python backend from specific frontend frameworks (Next.js, mobile apps).

#### 9. System Design & Scaling Angle
API contract stability guarantees backward compatibility for existing mobile and web clients during backend upgrades.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you design clean API integration boundaries?
* **Answer**: Use versioned REST endpoints (/api/v1), explicit Pydantic response schemas, RFC 7807 error structures, and automated OpenAPI contract generation.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_properties.py
```

---

## Module 13: Backend Testing & Debugging

### Story 43: Pytest Fundamentals, Async Fixtures & Dependency Overrides

* **Module**: Module 13: Backend Testing & Debugging
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 01, Story 09, Story 10
* **Leads To**: Story 44
* **Primary Code Files**: `backend/tests/conftest.py`, `backend/tests/unit/test_health.py`
* **Concrete Symbol / Class**: `pytest_asyncio / app.dependency_overrides / async_session fixture`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters
Automated tests give developers confidence to refactor code without introducing silent regressions.

#### 2. Concept & Architecture
Arrange-Act-Assert pattern with isolated test database sessions and mocked third-party dependencies.

#### 3. How It Works Internally
backend/tests/conftest.py initializes test clients, database engines, and clean session fixtures.

#### 4. EstateMap Implementation
tests/conftest.py defines async fixtures for db_session, async_client, test_settings, and mock_ai_provider.

#### 5. Code Flow & Request Lifecycle
```text
pytest runs -> conftest initializes in-memory test database -> Injects async_session into test -> Test executes Arrange-Act-Assert -> Session rolled back.
```

#### 6. Build It Yourself (Python Blueprint)
```python
import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Sharing mutable state across tests without cleanup causes flaky tests that fail only when run in specific orders.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_health.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Dependency overrides allow testing authenticated routes and database repositories in complete isolation.

#### 9. System Design & Scaling Angle
Fast unit tests running in under 5 seconds encourage continuous test-driven development (TDD) during feature additions.

#### 10. Interview Defense (STAR Q&A)
* **Question**: How do you test authenticated FastAPI routes without making real login calls?
* **Answer**: Use app.dependency_overrides[get_current_user] = lambda: mock_user in your test fixture to inject a mock authenticated user directly.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_health.py
```

---

### Story 44: Integration Testing of Repositories, Redis, External APIs & Error Paths

* **Module**: Module 13: Backend Testing & Debugging
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 43
* **Leads To**: Story 46
* **Primary Code Files**: `backend/tests/integration/test_properties.py`, `backend/tests/integration/test_rate_limiting.py`
* **Concrete Symbol / Class**: `pytest integration test suites (288 tests)`
* **Automated Verification**: `docker compose exec backend pytest`

#### 1. Why This Matters
Unit tests with mocks cannot catch SQL syntax errors, GiST index misconfigurations, or Redis connection bugs.

#### 2. Concept & Architecture
Integration tests run against real containerized services (Postgres, Redis) to verify end-to-end component interaction.

#### 3. How It Works Internally
tests/integration/ covers auth, properties, spatial search, commute routing, ranking, AI failover, and rate limiting.

#### 4. EstateMap Implementation
tests/integration/ contains 288 comprehensive integration tests testing end-to-end API workflows against real Postgres and Redis.

#### 5. Code Flow & Request Lifecycle
```text
docker compose exec backend pytest -> Pytest runs 288 tests -> Tests verify real DB queries, Redis caching hits/misses, and AI failovers -> 100% pass.
```

#### 6. Build It Yourself (Python Blueprint)
```python
@pytest.mark.asyncio
async def test_property_creation_and_spatial_query(async_client, auth_headers):
    payload = {"title": "Test Apartment", "price": 8500000, "bedrooms": 2, "latitude": 12.9716, "longitude": 77.5946}
    resp = await async_client.post("/api/v1/properties", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    prop_id = resp.json()["id"]
    
    # Verify spatial radius query
    search_resp = await async_client.get("/api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=2000")
    assert any(p["id"] == prop_id for p in search_resp.json()["items"])
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Testing only happy paths leaves edge cases (e.g. database disconnect, invalid token format) untested for production.
* **Debugging Command / Step**: Run `docker compose exec backend pytest` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Integration tests are slower than unit tests but provide the highest fidelity proof of system correctness.

#### 9. System Design & Scaling Angle
Automated test suites in CI/CD block regressions from reaching staging and production environments.

#### 10. Interview Defense (STAR Q&A)
* **Question**: What is the difference between unit and integration tests in a FastAPI project?
* **Answer**: Unit tests test isolated functions with mocked dependencies; integration tests verify API endpoints against real databases and Redis.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest
```

---

## Module 14: Docker for Backend Developers

### Story 45: Multi-Container Backend Orchestration with Docker Compose

* **Module**: Module 14: Docker for Backend Developers
* **Importance Level**: `[IMPORTANT]`
* **Prerequisites**: Story 01, Story 09, Story 29
* **Leads To**: Story 46
* **Primary Code Files**: `docker-compose.yml`, `backend/Dockerfile`, `.env`
* **Concrete Symbol / Class**: `services: postgres-postgis, redis, backend, frontend / healthcheck`
* **Automated Verification**: `docker compose ps`

#### 1. Why This Matters
Containerization eliminates 'works on my machine' issues by providing identical local and production runtime environments.

#### 2. Concept & Architecture
Docker Compose manages container networks, port bindings, persistent volumes, environment files, and healthcheck dependencies.

#### 3. How It Works Internally
docker-compose.yml defines 4 services with depends_on condition: service_healthy ensuring DB is ready before backend boots.

#### 4. EstateMap Implementation
docker-compose.yml coordinates postgres-postgis, redis, backend, and frontend containers on a shared bridge network.

#### 5. Code Flow & Request Lifecycle
```text
docker compose up -> Postgres & Redis boot -> Healthchecks pass -> Backend container boots -> Alembic runs -> FastAPI starts serving traffic.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# docker-compose.yml service snippet
services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: estatemap
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U estatemap"]
      interval: 5s
  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Backend starting before PostgreSQL is healthy causes initial connection attempts to fail and crash the container.
* **Debugging Command / Step**: Run `docker compose ps` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Docker Compose provides lightweight local orchestration without the operational complexity of Kubernetes.

#### 9. System Design & Scaling Angle
Standardized container definitions allow any developer to clone the repo and run the full stack with a single docker compose up command.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why use service health checks in docker-compose.yml?
* **Answer**: To ensure dependent services (like PostgreSQL) are fully initialized and ready to accept connections before the backend starts, preventing startup crashes.

#### 11. Mastery Verification Check
```bash
docker compose ps
```

---

## Module 15: EstateMap System Design & Architecture Synthesis

### Story 46: EstateMap Modular Monolith Architecture & Request Lifecycle Synthesis

* **Module**: Module 15: EstateMap System Design & Architecture Synthesis
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 01, Story 09, Story 18, Story 25, Story 29, Story 32, Story 35, Story 40, Story 42
* **Leads To**: Story 47, Story 48
* **Primary Code Files**: `backend/app/main.py`, `docs/mastery/ARCHITECTURE.md`
* **Concrete Symbol / Class**: `Modular Monolith Topology / End-to-End Request Lifecycle`
* **Automated Verification**: `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters
Senior backend engineers must explain how all system components interact across the entire end-to-end request lifecycle.

#### 2. Concept & Architecture
Modular Monolith enforces strict domain boundaries inside a single deployable process, avoiding distributed network overhead.

#### 3. How It Works Internally
Request enters Uvicorn -> Middleware (CORS, RequestID) -> Router -> Service -> Repository/Cache/AI -> Database.

#### 4. EstateMap Implementation
app/main.py wires all modules; ARCHITECTURE.md details the runtime topology, schema, and data flows.

#### 5. Code Flow & Request Lifecycle
```text
HTTP Request -> ASGI Pipeline -> Middleware -> APIRouter -> Dependency Injection -> Domain Service -> Repository -> PostGIS DB -> Response.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# End-to-End Architecture Flow
# Client -> Uvicorn -> Middleware -> FastAPI APIRouter
# -> Dependency Injection (get_db, get_current_user)
# -> Domain Service (PropertyService, RankingService, AIService)
# -> Data Layer (PropertyRepository, CacheService, PostGIS DB)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Blurring domain boundaries by allowing API routes to directly execute raw SQL queries destroys maintainability.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/unit/test_health.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
A modular monolith handles up to 50,000+ daily active users on a single modest server before requiring microservice decomposition.

#### 9. System Design & Scaling Angle
Clear modular boundaries inside a monolith allow future extraction of high-load domains into separate microservices if required.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Why did you choose a Modular Monolith over Microservices?
* **Answer**: To eliminate distributed system overhead (network latency, distributed tracing, two-phase commits) while maintaining clean domain module boundaries that can be extracted later if needed.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/unit/test_health.py
```

---

### Story 47: Requirement-Driven Scalability, Bottleneck Analysis & Caching Evolution

* **Module**: Module 15: EstateMap System Design & Architecture Synthesis
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 17, Story 29, Story 32, Story 46
* **Leads To**: Story 48
* **Primary Code Files**: `docs/mastery/SYSTEM_DESIGN.md`
* **Concrete Symbol / Class**: `Scale Evolution: 10k -> 100k -> 1M DAU / Bottleneck Mitigation`
* **Automated Verification**: `docker compose exec backend pytest tests/integration/test_rate_limiting.py`

#### 1. Why This Matters
System design interviews require explaining WHEN and WHY to introduce caching, read replicas, connection pooling, or partitioning.

#### 2. Concept & Architecture
Identify bottleneck -> Evaluate simplest response (Index -> Cache -> Read Replica -> Sharding) based on quantitative metrics.

#### 3. How It Works Internally
SYSTEM_DESIGN.md documents scaling evolution milestones from single-node deployment up to 1M daily active users.

#### 4. EstateMap Implementation
SYSTEM_DESIGN.md details scale milestones (10k, 100k, 1M users), latency budgets, and caching hierarchies.

#### 5. Code Flow & Request Lifecycle
```text
Load Increases -> Bottleneck identified (DB Read CPU) -> Mitigation 1: Add GiST index -> Mitigation 2: Add Redis Cache-Aside -> Mitigation 3: Add Postgres Read Replicas.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# Scalability Hierarchy
# Level 1: Single Postgres Node + GiST Spatial Indexes (< 10k DAU)
# Level 2: Add Redis Cache-Aside for Viewport & Ranking (< 100k DAU)
# Level 3: Add PostgreSQL Read Replicas for Search Queries (< 500k DAU)
# Level 4: Spatial Hash Partitioning / Sharding (1M+ DAU)
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Introducing premature complexity (Kafka, Sharding) before exhausting database indexes and Redis caching wastes engineering resources.
* **Debugging Command / Step**: Run `docker compose exec backend pytest tests/integration/test_rate_limiting.py` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Horizontal scaling of stateless FastAPI workers behind a load balancer is the first and most cost-effective scaling lever.

#### 9. System Design & Scaling Angle
Scalability is requirement-driven: scale the bottleneck component only when performance metrics exceed service level objectives.

#### 10. Interview Defense (STAR Q&A)
* **Question**: If your database read latency spikes under heavy load, what steps do you take?
* **Answer**: 1. Check EXPLAIN ANALYZE for missing indexes; 2. Add Redis Cache-Aside for hot queries; 3. Add PostgreSQL read replicas before considering sharding.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest tests/integration/test_rate_limiting.py
```

---

### Story 48: Senior Backend Architectural Defense, Tradeoffs & Whiteboard Mastery

* **Module**: Module 15: EstateMap System Design & Architecture Synthesis
* **Importance Level**: `[ESSENTIAL]`
* **Prerequisites**: Story 46, Story 47
* **Leads To**: None (Terminal Story)
* **Primary Code Files**: `docs/mastery/SYSTEM_DESIGN.md`, `docs/mastery/INTERVIEW_PREP.md`
* **Concrete Symbol / Class**: `15 Core Architectural Tradeoffs / Whiteboard Challenge Blueprints`
* **Automated Verification**: `docker compose exec backend pytest`

#### 1. Why This Matters
Interviewers evaluate your ability to justify WHY an architecture was chosen, what tradeoffs were accepted, and how it fails.

#### 2. Concept & Architecture
Structured STAR-format defense linking business requirements to concrete technical decisions and failure mitigation.

#### 3. How It Works Internally
INTERVIEW_PREP.md provides elevator pitches, Top 25 STAR Q&As, and 10 Whiteboard challenge blueprints.

#### 4. EstateMap Implementation
INTERVIEW_PREP.md and SYSTEM_DESIGN.md consolidate all architectural defenses, failure modes, and whiteboard blueprints.

#### 5. Code Flow & Request Lifecycle
```text
Interview Question -> Candidate delivers 30-second high-level summary -> Follows with 2-minute technical deep dive -> Draws component architecture on whiteboard -> Explains tradeoffs & failure modes.
```

#### 6. Build It Yourself (Python Blueprint)
```python
# Senior Architectural Pitch Framework
# 1. Problem: Real estate discovery requires multi-modal geospatial search, ranking, and conversational intent parsing.
# 2. Architecture: FastAPI ASGI modular monolith, PostGIS GiST spatial indexing, Redis caching & ZSET sliding window rate limiting.
# 3. Key Decision: Deterministic MCDA ranking + multi-provider AI fallback circuit (Ollama local -> Gemini cloud -> Algorithmic fallback).
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: Saying 'we used Redis because it is fast' without explaining data structures, eviction policies, or failure modes signals junior thinking.
* **Debugging Command / Step**: Run `docker compose exec backend pytest` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
Every technical decision is a tradeoff: PostGIS vs ElasticSearch, Redis ZSET vs Token Bucket, Local Ollama vs Cloud Gemini.

#### 9. System Design & Scaling Angle
Mastery means being able to defend why each technology was chosen, what alternatives were rejected, and how the system degrades under failure.

#### 10. Interview Defense (STAR Q&A)
* **Question**: Walk me through the architecture of EstateMap AI.
* **Answer**: Deliver the structured 2-minute architectural pitch covering FastAPI ASGI, PostGIS spatial indexing, Redis caching, deterministic ranking, and multi-provider AI.

#### 11. Mastery Verification Check
```bash
docker compose exec backend pytest
```

---

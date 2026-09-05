# EstateMap AI — 48 Backend Engineering Stories

> **Role Target:** Python Backend Engineer / Backend System Designer  
> **Core Focus:** Python 3.12, FastAPI, PostgreSQL 16, PostGIS 3.4, SQLAlchemy 2.0 (Asyncpg), Redis 7, Multi-Provider AI (Ollama + Gemini), Deterministic Ranking, Spatial Indexing & System Design.  
> **Structure:** 48 Deep Stories across 15 Modules | 37 Essential, 11 Important, 0 Optional.  

---

## Module 01: Python & FastAPI Foundations

### Story 01: Python Project Layout, Clean Modular Monolith & ASGI App Factory [ESSENTIAL]
- **Module:** Module 01: Python & FastAPI Foundations
- **Prerequisites:** None (Entry Point)
- **Leads To:** Story 02, Story 03, Story 04
- **Code Truth Files:** `backend/app/main.py`, `backend/pyproject.toml`, `backend/app/core/config.py`
- **Key Symbol(s):** `app.main:app / create_application`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters in Production
Clean separation of concerns isolates HTTP serialization from domain logic and prevents circular imports across services.

#### 2. Core Engineering Concept
ASGI (Asynchronous Server Gateway Interface) event loop request dispatching vs WSGI synchronous execution.

#### 3. How It Works Under the Hood
Uvicorn runs ASGI event loops. FastAPI initializes middleware (CORS, RequestID) and mounts versioned routers (/api/v1).

#### 4. EstateMap Implementation Reality
backend/app/main.py defines the FastAPI application factory, initializes middleware pipelines, mounts /api/v1 routers, and configures lifespan handlers.

#### 5. Step-by-Step Code Flow
Client Request -> Uvicorn ASGI Server -> Middleware Stack (RequestID, CORS) -> FastAPI Router (/api/v1/properties) -> Dependency Injection (get_db) -> Service Layer -> Response.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement a minimal ASGI app factory with CORS and lifespan
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # Initialize background resources
    yield
    # Cleanup background resources

def build_api() -> FastAPI:
    app = FastAPI(title="RealEstate API", lifespan=app_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

app = build_api()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Circular import between router and service (e.g., router imports service instance that imports router module) causes Python to fail at boot with an ImportError.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Modular Monolith was chosen over microservices to eliminate distributed network latency, serialization overhead, and multi-repo operational complexity.

#### 9. System Design & Scalability Angle
Stateless ASGI workers scale horizontally behind an NGINX / Cloud load balancer with zero shared in-process memory.

#### 10. Senior Backend Interview Prep
**Q:** Why use FastAPI over traditional frameworks like Django or Flask for high-performance APIs?

**A:** FastAPI is built natively on Starlette and asyncio, allowing non-blocking concurrent I/O on a single thread event loop. It integrates Pydantic for fast schema validation and automatic OpenAPI generation.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 02: Async Event Loop, Non-Blocking Concurrency & Lifespan Management [ESSENTIAL]
- **Module:** Module 01: Python & FastAPI Foundations
- **Prerequisites:** Story 01
- **Leads To:** Story 08, Story 09, Story 29
- **Code Truth Files:** `backend/app/main.py`, `backend/app/cache/redis.py`, `backend/app/db/session.py`
- **Key Symbol(s):** `app.main:lifespan / asynccontextmanager`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters in Production
Proper lifecycle management ensures database pools and Redis clients are initialized before serving traffic and closed on SIGTERM.

#### 2. Core Engineering Concept
Python asyncio event loop cooperative multitasking: I/O operations yield control with await, allowing concurrent requests per worker.

#### 3. How It Works Under the Hood
lifespan context manager runs startup code before yield and teardown code after yield on server shutdown.

#### 4. EstateMap Implementation Reality
app/main.py lifespan initializes Redis connection pools, verifies PostgreSQL connectivity, runs seed_all(), and tears down pools on exit.

#### 5. Step-by-Step Code Flow
Process Start -> Uvicorn triggers lifespan -> init_redis() -> init_db() -> seed_all() -> yield (Serve Requests) -> close_redis() -> dispose_engine() -> Process Exit.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create an async lifespan manager that initializes and tears down mock DB & Redis pools
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio

class MockPool:
    async def connect(self): await asyncio.sleep(0.01)
    async def close(self): await asyncio.sleep(0.01)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_pool = MockPool()
    await db_pool.connect()
    app.state.db = db_pool
    yield
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Omitting the yield statement inside the @asynccontextmanager causes FastAPI startup to hang indefinitely, failing healthchecks.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Lifespan context managers replace deprecated startup/shutdown events with type-safe exception handling and clean context scopes.

#### 9. System Design & Scalability Angle
Graceful shutdown allows in-flight database transactions and HTTP requests to complete before closing sockets during rolling deployments.

#### 10. Senior Backend Interview Prep
**Q:** How does Python asyncio handle thousands of concurrent I/O-bound requests on a single CPU core?

**A:** When a coroutine awaits network I/O (database query or HTTP call), it yields control to the event loop, which immediately schedules other ready coroutines without thread context-switching overhead.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 03: Type-Safe Environment Configuration with Pydantic-Settings [ESSENTIAL]
- **Module:** Module 01: Python & FastAPI Foundations
- **Prerequisites:** Story 01
- **Leads To:** Story 04, Story 08, Story 13, Story 29, Story 35
- **Code Truth Files:** `backend/app/core/config.py`, `.env.example`
- **Key Symbol(s):** `app.core.config:Settings / settings`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters in Production
Failing fast during boot when environment variables (DB URLs, API keys, TTLs) are invalid prevents runtime 500 errors in production.

#### 2. Core Engineering Concept
Strict schema parsing transforms raw environment string values into typed integers, booleans, and DSN objects with default fallbacks.

#### 3. How It Works Under the Hood
Pydantic BaseSettings reads .env files, coerces data types, and validates constraints (e.g. rate limits > 0, valid log levels).

#### 4. EstateMap Implementation Reality
app/core/config.py defines Settings with database URLs, Redis parameters, cache TTLs, rate limits, AI provider credentials, and exports a singleton settings object.

#### 5. Step-by-Step Code Flow
App Start -> settings instantiated -> Reads os.environ & .env -> Pydantic validates types -> Singleton imported across modules.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a typed configuration class with cache TTLs and validation
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AppConfig(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_MAP_TTL_SECONDS: int = Field(default=120, gt=0)
    CACHE_RANKING_TTL_SECONDS: int = Field(default=300, gt=0)
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

config = AppConfig()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing an invalid integer string like CACHE_MAP_TTL_SECONDS='two_minutes' causes Pydantic to raise a ValidationError and abort startup immediately.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Pydantic-Settings provides compile-time typing and automated validation over fragile, untyped os.environ.get() dictionaries.

#### 9. System Design & Scalability Angle
12-Factor App config separation allows the exact same Docker image to run across local, staging, and production environments with different .env files.

#### 10. Senior Backend Interview Prep
**Q:** Why is Pydantic-Settings preferred over os.getenv in production backend systems?

**A:** Pydantic-Settings automatically parses and validates types, enforces mandatory fields at startup, prevents type-coercion bugs, and supports hierarchical config injection.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 04: RFC 7807 Centralized Error Handling & Structured Request ID Logging [ESSENTIAL]
- **Module:** Module 01: Python & FastAPI Foundations
- **Prerequisites:** Story 01, Story 03
- **Leads To:** Story 05, Story 14, Story 32
- **Code Truth Files:** `backend/app/core/exceptions.py`, `backend/app/core/exception_handlers.py`, `backend/app/core/middleware.py`
- **Key Symbol(s):** `AppException / app_exception_handler / RequestIDMiddleware`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_exceptions.py`

#### 1. Why This Matters in Production
Consistent error contracts prevent leaking raw database stack traces and enable correlated log debugging.

#### 2. Core Engineering Concept
RFC 7807 Problem Details for HTTP APIs standardizes error JSON responses (type, title, status, detail, instance).

#### 3. How It Works Under the Hood
Custom exception classes inherit from AppException. FastAPI exception handlers intercept exceptions and format structured JSON responses.

#### 4. EstateMap Implementation Reality
app/core/exceptions.py defines EntityNotFoundException, RateLimitExceededException, ValidationException. Middleware injects X-Request-ID into context and response headers.

#### 5. Step-by-Step Code Flow
Incoming Request -> RequestIDMiddleware generates/extracts X-Request-ID -> Route raises AppException -> Exception Handler formats RFC 7807 JSON -> Response returned with X-Request-ID header.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create an RFC 7807 base exception and exception handler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST", details: dict = None):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.estatemap.com/errors/{exc.code.lower()}",
            "title": exc.message,
            "status": exc.status_code,
            "code": exc.code,
            "details": exc.details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )
```

#### 7. Break It & Debug It (Specific Failure Mode)
Letting raw SQLAlchemy exceptions bubble up unhandled returns HTTP 500 containing internal database table names and connection parameters to the client.

#### 8. Architectural Tradeoffs & Rejected Alternatives
RFC 7807 standardized schema over custom error dicts allows API consumers to handle validation errors and business failures uniformly.

#### 9. System Design & Scalability Angle
Propagating X-Request-ID through logs and response headers enables engineers to trace a single request's execution across distributed components with log queries.

#### 10. Senior Backend Interview Prep
**Q:** How do you handle exceptions and error responses cleanly across a large FastAPI application?

**A:** Define a domain exception hierarchy inheriting from a base AppException. Register centralized FastAPI exception handlers that format errors according to RFC 7807 Problem Details.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 02: REST API Design & Validation

### Story 05: Request & Response Schema Validation with Pydantic v2 [ESSENTIAL]
- **Module:** Module 02: REST API Design & Validation
- **Prerequisites:** Story 01, Story 03, Story 04
- **Leads To:** Story 06, Story 07, Story 10, Story 21, Story 36
- **Code Truth Files:** `backend/app/schemas/property.py`, `backend/app/schemas/search.py`, `backend/app/schemas/auth.py`
- **Key Symbol(s):** `PropertyResponse / PropertyCreate / PropertyFilterParams`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_property_schemas.py`

#### 1. Why This Matters in Production
Input validation at the API boundary protects domain services and SQL queries from malformed payloads.

#### 2. Core Engineering Concept
Pydantic v2 core delivers high-throughput serialization and strict schema validation.

#### 3. How It Works Under the Hood
app/schemas/ defines strict BaseModel schemas with Field constraints (e.g. price > 0, latitude [-90, 90]).

#### 4. EstateMap Implementation Reality
app/schemas/ defines PropertyCreate, PropertyUpdate, PropertyResponse models with exact typing and field constraints.

#### 5. Step-by-Step Code Flow
HTTP Request Payload -> FastAPI body parser -> Pydantic model validation -> Clean typed object passed to endpoint -> Return schema serializes output.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create a Pydantic v2 property create schema with coordinate bounds
from pydantic import BaseModel, Field, field_validator

class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150)
    price: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=1, le=10)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    @field_validator("title")
    @classmethod
    def strip_title(cls, v: str) -> str:
        return v.strip()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing latitude > 90 or negative prices returns HTTP 422 Unprocessable Entity with exact error field locations in the response body.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Pydantic schemas decouple database model structures from public API contracts, preventing over-fetching and unintended internal column exposure.

#### 9. System Design & Scalability Angle
Validated request schemas serve as the contract for OpenAPI documentation and protect internal services from malformed inputs.

#### 10. Senior Backend Interview Prep
**Q:** What is the difference between ORM models and Pydantic schemas?

**A:** ORM models map to database tables and manage persistence; Pydantic schemas enforce API boundary validation, type coercion, and serialization.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 06: Deterministic Pagination, Sorting & Query Parameter Contracts [ESSENTIAL]
- **Module:** Module 02: REST API Design & Validation
- **Prerequisites:** Story 05
- **Leads To:** Story 07, Story 10
- **Code Truth Files:** `backend/app/utils/pagination.py`, `backend/app/repositories/property_repository.py`
- **Key Symbol(s):** `PropertyRepository.list / PropertyRepository._apply_sorting`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters in Production
Non-deterministic sorting causes duplicate or missing items across paginated API requests during concurrent database writes.

#### 2. Core Engineering Concept
Stable sorting requires appending a unique primary key tie-breaker to all ORDER BY clauses.

#### 3. How It Works Under the Hood
PropertyRepository._apply_sorting adds Property.id.desc() as the final sorting clause.

#### 4. EstateMap Implementation Reality
app/utils/pagination.py and PropertyRepository apply LIMIT, OFFSET, and compound ORDER BY clauses with primary key tie-breakers.

#### 5. Step-by-Step Code Flow
GET /api/v1/properties?limit=20&offset=40 -> Query params parsed -> Repository appends ORDER BY price ASC, id DESC -> Database executes indexed fetch -> Paginated list returned.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a reusable query sorter with primary key tie-breaking
from sqlalchemy import select, asc, desc

def apply_deterministic_sorting(stmt, model_cls, sort_by: str, sort_order: str = "asc"):
    col = getattr(model_cls, sort_by, model_cls.created_at)
    direction = asc if sort_order.lower() == "asc" else desc
    # Primary sort column + mandatory primary key tie-breaker
    return stmt.order_by(direction(col), desc(model_cls.id))
```

#### 7. Break It & Debug It (Specific Failure Mode)
Sorting by price alone causes rows with identical price values to shift position between page 1 and page 2, returning duplicate listings to users.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Offset pagination is simple and flexible for moderate datasets; Keyset/Cursor pagination is reserved for large unbounded tables.

#### 9. System Design & Scalability Angle
Pagination bounds database memory consumption and network payload sizes, preventing out-of-memory errors on large tables.

#### 10. Senior Backend Interview Prep
**Q:** Why is tie-breaking necessary in database pagination?

**A:** Without unique tie-breaking, database query planners return rows with identical sort values in arbitrary physical disk order, creating duplicates or missing items across pages.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 07: Composable Multi-Facet Filter Query Generation [ESSENTIAL]
- **Module:** Module 02: REST API Design & Validation
- **Prerequisites:** Story 05, Story 06
- **Leads To:** Story 10, Story 18
- **Code Truth Files:** `backend/app/repositories/property_repository.py`, `backend/app/schemas/property.py`
- **Key Symbol(s):** `PropertyRepository._apply_common_filters / PropertyFilterParams`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_filter_equivalence.py`

#### 1. Why This Matters in Production
Hardcoded SQL strings lead to SQL injection vulnerabilities and unmaintainable conditional branching.

#### 2. Core Engineering Concept
Composable AST query building appends binary filter expressions to the query object only when parameters are present.

#### 3. How It Works Under the Hood
PropertyRepository._apply_common_filters checks filter params and chains .where() conditions cleanly.

#### 4. EstateMap Implementation Reality
PropertyRepository encapsulates filter generation, applying min_price, max_price, bedrooms, property_type, and city conditions.

#### 5. Step-by-Step Code Flow
FilterParams received -> Repository initializes select(Property) -> _apply_common_filters chains active conditions -> Query executed via async session.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement a composable query filter builder using SQLAlchemy select
from sqlalchemy import select
from typing import Optional

def build_property_query(model, min_price: Optional[float] = None, max_price: Optional[float] = None, bedrooms: Optional[int] = None):
    stmt = select(model).where(model.is_active.is_(True))
    if min_price is not None:
        stmt = stmt.where(model.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(model.price <= max_price)
    if bedrooms is not None:
        stmt = stmt.where(model.bedrooms == bedrooms)
    return stmt
```

#### 7. Break It & Debug It (Specific Failure Mode)
Chaining filters without matching index coverage on large tables results in full sequential scans and elevated query execution time.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Dynamic SQLAlchemy query compilation ensures parameterized safety while supporting arbitrary filter combinations.

#### 9. System Design & Scalability Angle
Composite indexes should align with the most frequent multi-facet filter combinations (e.g. city + property_type + price).

#### 10. Senior Backend Interview Prep
**Q:** How do you prevent SQL injection in complex dynamic search queries?

**A:** Use parameterized query builders like SQLAlchemy where values are passed out-of-band and never concatenated directly as raw SQL strings.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 03: PostgreSQL & SQLAlchemy 2.0 Async

### Story 08: Relational Data Modeling, Foreign Keys & Schema Integrity [ESSENTIAL]
- **Module:** Module 03: PostgreSQL & SQLAlchemy 2.0 Async
- **Prerequisites:** Story 01, Story 03
- **Leads To:** Story 09, Story 10, Story 11, Story 16
- **Code Truth Files:** `backend/app/models/property.py`, `backend/app/models/user.py`, `backend/app/models/poi.py`
- **Key Symbol(s):** `Property / User / PointOfInterest / Base`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters in Production
Database constraints provide the final defense line for data integrity even if application bugs occur.

#### 2. Core Engineering Concept
Relational normalization (3NF) eliminates data redundancy while foreign keys enforce referential integrity.

#### 3. How It Works Under the Hood
app/models/ defines declarative tables with mapped_column, CheckConstraint('price > 0'), and foreign keys.

#### 4. EstateMap Implementation Reality
app/models/property.py, user.py, and poi.py define declarative SQLAlchemy 2.0 models with relationships, cascades, and constraints.

#### 5. Step-by-Step Code Flow
Domain Entity Definition -> Base declarative metadata -> Table definition with foreign keys and check constraints -> Database schema synchronization.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Define declarative SQLAlchemy 2.0 models with FK cascades and check constraints
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, CheckConstraint

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    properties: Mapped[list["Property"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped[User] = relationship(back_populates="properties")
    __table_args__ = (CheckConstraint("price > 0", name="chk_price_positive"),)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Inserting a record with price <= 0 triggers a database IntegrityError due to the check constraint, rolling back the transaction.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Relational PostgreSQL was chosen over document stores to guarantee strict transactional ACID consistency for real estate listings.

#### 9. System Design & Scalability Angle
Normalized tables prevent update anomalies; foreign keys and check constraints guarantee data consistency at the storage layer.

#### 10. Senior Backend Interview Prep
**Q:** Why enforce check constraints at the database level when Pydantic already validates inputs?

**A:** Defense-in-depth: database constraints protect against direct database updates, migrations, asynchronous background jobs, and multi-service writes.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 09: SQLAlchemy 2.0 Async Session Lifecycles & Asyncpg Connection Pooling [ESSENTIAL]
- **Module:** Module 03: PostgreSQL & SQLAlchemy 2.0 Async
- **Prerequisites:** Story 02, Story 08
- **Leads To:** Story 10, Story 13, Story 18
- **Code Truth Files:** `backend/app/db/session.py`, `backend/app/db/base.py`
- **Key Symbol(s):** `async_session_factory / create_async_engine / get_db`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters in Production
Synchronous database drivers block the Python asyncio event loop during I/O operations.

#### 2. Core Engineering Concept
Async database access avoids blocking the asyncio event loop during PostgreSQL network I/O and allows concurrent requests to make progress while queries are waiting on I/O.

#### 3. How It Works Under the Hood
app/db/session.py initializes create_async_engine and yields AsyncSession via FastAPI Depends(get_db).

#### 4. EstateMap Implementation Reality
app/db/session.py configures connection pool parameters (pool_size=20, max_overflow=10, pool_recycle, pool_pre_ping) and get_db dependency.

#### 5. Step-by-Step Code Flow
HTTP Request -> FastAPI get_db dependency acquires session from pool -> Route executes queries -> Request ends -> get_db commits/closes session back to pool.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Configure an async database engine, sessionmaker, and FastAPI get_db generator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost:5432/db",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)
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

#### 7. Break It & Debug It (Specific Failure Mode)
Failing to commit or rollback an unclosed session leaves transactions open, exhausting pool connections and timing out subsequent requests.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Asyncpg handles non-blocking socket I/O natively, keeping the single-thread event loop responsive across concurrent queries.

#### 9. System Design & Scalability Angle
Connection pooling reuses persistent TCP connections, avoiding expensive TLS/TCP handshakes on every incoming HTTP request.

#### 10. Senior Backend Interview Prep
**Q:** What happens if an async endpoint calls a synchronous blocking database driver?

**A:** It blocks the single asyncio event loop thread, preventing all concurrent requests from making progress until the query finishes.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 10: Repository Pattern & Async Database Encapsulation [ESSENTIAL]
- **Module:** Module 03: PostgreSQL & SQLAlchemy 2.0 Async
- **Prerequisites:** Story 08, Story 09
- **Leads To:** Story 18, Story 22, Story 25
- **Code Truth Files:** `backend/app/repositories/property_repository.py`, `backend/app/repositories/user_repository.py`
- **Key Symbol(s):** `PropertyRepository / UserRepository`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters in Production
Direct SQL queries inside API route handlers make code untestable and violate single-responsibility principles.

#### 2. Core Engineering Concept
Repository pattern acts as an in-memory collection interface over persistent storage.

#### 3. How It Works Under the Hood
PropertyRepository receives AsyncSession and exposes get_by_id, list, search_radius, and search_bbox methods.

#### 4. EstateMap Implementation Reality
app/repositories/property_repository.py encapsulates all SQL operations for properties, abstracting session execution from service logic.

#### 5. Step-by-Step Code Flow
API Router calls PropertyService -> PropertyService calls PropertyRepository.get_by_id(session, id) -> Repository executes select() -> Returns entity.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement an async property repository with get_by_id and list operations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Sequence

class PropertyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, prop_id: int) -> Optional[Property]:
        stmt = select(Property).where(Property.id == prop_id, Property.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 20, offset: int = 0) -> Sequence[Property]:
        stmt = select(Property).where(Property.is_active.is_(True)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Accessing unloaded async relationships outside the session context raises a MissingGreenlet exception.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Repository pattern introduces minor boilerplate but enables straightforward unit testing and centralized query performance optimization.

#### 9. System Design & Scalability Angle
Data access layer encapsulation allows swapping storage engines or optimizing queries without altering business service logic.

#### 10. Senior Backend Interview Prep
**Q:** Why use the Repository pattern with an ORM?

**A:** It isolates data access logic, making unit testing simpler with mocks and query optimization centralized in one file.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 11: Schema Migrations with Alembic & Reproducible Database Versioning [IMPORTANT]
- **Module:** Module 03: PostgreSQL & SQLAlchemy 2.0 Async
- **Prerequisites:** Story 08, Story 10
- **Leads To:** Story 12, Story 16
- **Code Truth Files:** `backend/alembic/env.py`, `backend/alembic/versions/2026_09_04_0001-0001_initial_postgis.py`
- **Key Symbol(s):** `run_migrations_online / Alembic Revisions 0001-0004`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters in Production
Manual SQL alter scripts lead to environment drift, unrepeatable deployments, and broken production schemas.

#### 2. Core Engineering Concept
Linear migration DAG tracks applied revisions in the alembic_version table.

#### 3. How It Works Under the Hood
backend/alembic/ manages 4 sequential revisions: PostGIS extension, users table, properties/amenities, and POIs.

#### 4. EstateMap Implementation Reality
backend/alembic/env.py imports Base metadata, configures async connection, and applies versioned migration scripts.

#### 5. Step-by-Step Code Flow
Developer runs alembic upgrade head -> Alembic checks alembic_version table -> Executes missing revision scripts in transaction -> Updates alembic_version.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Write an Alembic migration script creating a table and GiST index
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

def upgrade() -> None:
    op.create_table(
        'listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326), nullable=False)
    )
    op.create_index('idx_listings_location', 'listings', ['location'], postgresql_using='gist')

def downgrade() -> None:
    op.drop_index('idx_listings_location', table_name='listings')
    op.drop_table('listings')
```

#### 7. Break It & Debug It (Specific Failure Mode)
Adding a non-nullable column without a server default to an existing populated table causes the migration to fail with a NotNullViolation.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Alembic integrates directly with SQLAlchemy declarative metadata for automated schema diff detection.

#### 9. System Design & Scalability Angle
Database schema versioning enables reproducible test environments and safe rollback procedures.

#### 10. Senior Backend Interview Prep
**Q:** How do you handle database migrations with zero downtime?

**A:** Use the Expand/Contract pattern: add new nullable columns first, deploy updated code, backfill data, and finally enforce constraints in a subsequent migration.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 12: Deterministic Database Seeding & Fixture Management [IMPORTANT]
- **Module:** Module 03: PostgreSQL & SQLAlchemy 2.0 Async
- **Prerequisites:** Story 08, Story 10, Story 11
- **Leads To:** Story 18, Story 22
- **Code Truth Files:** `backend/app/db/seed_all.py`, `backend/app/db/seed_properties.py`, `backend/app/db/seed_pois.py`
- **Key Symbol(s):** `seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_database.py`

#### 1. Why This Matters in Production
Deterministic seed fixtures ensure that local testing, spatial queries, and demo search flows produce predictable results.

#### 2. Core Engineering Concept
Idempotent seeding scripts verify existing records before inserting to avoid primary key collisions.

#### 3. How It Works Under the Hood
app/db/seed_all.py is called during FastAPI lifespan startup to seed listings and POIs if tables are empty.

#### 4. EstateMap Implementation Reality
app/db/seed_properties.py and seed_pois.py load structured geographic coordinates, amenities, and price tiers into the database.

#### 5. Step-by-Step Code Flow
Lifespan Startup -> seed_all() checks SELECT count(*) FROM properties -> If 0, inserts curated properties and POIs in a single transaction.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create an idempotent seed function that populates initial properties
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_properties_if_empty(session: AsyncSession, seed_records: list[dict]):
    stmt = select(func.count(Property.id))
    count = (await session.execute(stmt)).scalar()
    if count == 0:
        for item in seed_records:
            prop = Property(**item)
            session.add(prop)
        await session.commit()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Non-deterministic seeding with randomized coordinates causes spatial distance tests and ranking tests to fail intermittently.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Hardcoded curated seed fixtures provide immediate out-of-the-box local developer onboarding.

#### 9. System Design & Scalability Angle
Seed fixtures replicate realistic real-world geographic clusters, enabling spatial query testing and ranking calibration.

#### 10. Senior Backend Interview Prep
**Q:** How do you ensure integration tests run against predictable data?

**A:** Idempotent database seeders and deterministic fixtures loaded in test transaction boundaries with rollback on test completion.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 04: Authentication & Security Boundaries

### Story 13: Password Hashing with Argon2id & Cryptographic Salting [ESSENTIAL]
- **Module:** Module 04: Authentication & Security Boundaries
- **Prerequisites:** Story 03, Story 08
- **Leads To:** Story 14, Story 15
- **Code Truth Files:** `backend/app/core/security.py`, `backend/app/services/auth_service.py`
- **Key Symbol(s):** `get_password_hash / verify_password / PasswordHasher`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_security.py`

#### 1. Why This Matters in Production
Storing plaintext or MD5/SHA256 hashed passwords exposes user accounts to rainbow table compromise.

#### 2. Core Engineering Concept
Argon2id combines data-independent and data-dependent memory access for side-channel and ASIC resistance.

#### 3. How It Works Under the Hood
app/core/security.py implements get_password_hash and verify_password using passlib/argon2.

#### 4. EstateMap Implementation Reality
app/core/security.py uses argon2-cffi to hash passwords with calibrated time cost and memory parameters.

#### 5. Step-by-Step Code Flow
User Registration -> Plaintext Password -> Argon2id generates salt & hash -> Hash stored in users.hashed_password.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement password hashing and verification using passlib Argon2 context
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_user_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_user_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing a non-string or None to verify_password raises a TypeError, which if unhandled turns into an uncaught 500 error.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Argon2id is computationally heavier than bcrypt but provides superior resistance to dedicated hardware cracking.

#### 9. System Design & Scalability Angle
Memory-hard hashing forces attackers to allocate significant RAM per crack attempt, making parallel attacks economically infeasible.

#### 10. Senior Backend Interview Prep
**Q:** Why is SHA-256 unsuitable for password storage?

**A:** SHA-256 is designed to be fast for data integrity; password hashing requires slow, memory-hard algorithms like Argon2id to defeat brute-force and GPU rainbow table attacks.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 14: Stateless JWT Authentication, Token Expiration & Signature Verification [ESSENTIAL]
- **Module:** Module 04: Authentication & Security Boundaries
- **Prerequisites:** Story 03, Story 13
- **Leads To:** Story 15, Story 33
- **Code Truth Files:** `backend/app/core/security.py`, `backend/app/api/v1/auth.py`
- **Key Symbol(s):** `create_access_token / decode_access_token / TokenSchema`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_auth.py`

#### 1. Why This Matters in Production
Stateless JWTs allow backend API instances to verify user identity without querying a central session database on every request.

#### 2. Core Engineering Concept
JWT consists of Header, Payload (claims), and HMAC-SHA256 Signature verified via secret key.

#### 3. How It Works Under the Hood
app/core/security.py generates tokens with ACCESS_TOKEN_EXPIRE_MINUTES (60 min) and decodes sub/role claims.

#### 4. EstateMap Implementation Reality
app/core/security.py implements create_access_token and decode_access_token with PyJWT HS256 validation.

#### 5. Step-by-Step Code Flow
POST /api/v1/auth/login -> AuthService verifies password -> create_access_token() signs payload -> Returns access_token -> Client sends Bearer token.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build token generation and decoding helpers with expiration validation
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "test_secret_key_change_in_production"
ALGORITHM = "HS256"

def generate_jwt(user_id: int, expires_delta: timedelta = timedelta(minutes=60)) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

#### 7. Break It & Debug It (Specific Failure Mode)
Decoding an expired token raises jwt.ExpiredSignatureError; decoding with the wrong secret key raises jwt.InvalidSignatureError.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Stateless JWTs eliminate database session lookups but require short TTLs or revocation lists for immediate logout.

#### 9. System Design & Scalability Angle
Stateless tokens allow horizontal scaling of backend servers because any worker node can verify the signature independently.

#### 10. Senior Backend Interview Prep
**Q:** How do stateless JWTs scale better than session IDs?

**A:** The server verifies the cryptographic signature locally using the shared secret key without needing shared session database lookups on every request.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 15: Dependency-Based Role Authorization & Resource Ownership Validation [ESSENTIAL]
- **Module:** Module 04: Authentication & Security Boundaries
- **Prerequisites:** Story 13, Story 14
- **Leads To:** Story 18, Story 42
- **Code Truth Files:** `backend/app/core/dependencies.py`, `backend/app/services/property_service.py`
- **Key Symbol(s):** `get_current_user / get_current_active_user / require_role`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_auth.py`

#### 1. Why This Matters in Production
Prevent Broken Object Level Authorization (BOLA/IDOR) where users modify resources owned by other users.

#### 2. Core Engineering Concept
FastAPI Depends() injects verified user objects into endpoint parameters before handler execution.

#### 3. How It Works Under the Hood
app/core/dependencies.py extracts Bearer token, fetches user, and PropertyService verifies property.owner_id == user.id.

#### 4. EstateMap Implementation Reality
app/core/dependencies.py provides reusable security dependencies (get_current_user, get_current_active_admin) that parse tokens.

#### 5. Step-by-Step Code Flow
Incoming Request -> Depends(get_current_user) extracts Bearer token -> Validates token signature -> Fetches User entity -> Passes user to route handler.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create a FastAPI get_current_user security dependency
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = int(payload.get("sub"))
    user = await UserRepository(db).get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
```

#### 7. Break It & Debug It (Specific Failure Mode)
Omitting the Bearer token or supplying a malformed authorization header returns HTTP 403 / 401 before the route handler is invoked.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Dependency injection centralizes security checks, preventing boilerplate code duplication across route handlers.

#### 9. System Design & Scalability Angle
Declarative security dependencies ensure authorization rules are enforced consistently across all private API endpoints.

#### 10. Senior Backend Interview Prep
**Q:** What is an IDOR vulnerability and how do you prevent it?

**A:** Insecure Direct Object Reference occurs when an API accepts an object ID without verifying that the requesting user owns that object. Prevent it by checking ownership in the service layer before mutation.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 05: PostGIS Spatial Search

### Story 16: Geospatial Coordinates, WGS84 (EPSG:4326) & PostGIS POINT Storage [ESSENTIAL]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 08, Story 11
- **Leads To:** Story 17, Story 18, Story 19
- **Code Truth Files:** `backend/app/models/property.py`, `backend/app/models/poi.py`
- **Key Symbol(s):** `mapped_column(Geometry(geometry_type='POINT', srid=4326)) / idx_properties_location`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters in Production
Standard SQL numeric columns cannot perform spherical distance calculations or spatial bounding box containment.

#### 2. Core Engineering Concept
WGS84 (EPSG:4326) defines points on the Earth's ellipsoidal surface using (Longitude, Latitude) coordinates.

#### 3. How It Works Under the Hood
app/models/property.py defines location as Geometry('POINT', srid=4326) with explicit longitude-first ordering.

#### 4. EstateMap Implementation Reality
app/models/property.py and poi.py map location columns using GeoAlchemy2 Geometry with SRID 4326.

#### 5. Step-by-Step Code Flow
Insert Property -> GeoAlchemy2 converts (lon, lat) to WKT (POINT(lon lat)) -> PostgreSQL stores binary geometry representation.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Define a GeoAlchemy2 POINT model and instantiate a spatial point
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass

class LocationModel(Base):
    __tablename__ = "spatial_points"
    id: Mapped[int] = mapped_column(primary_key=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

def create_point(lat: float, lon: float) -> WKTElement:
    # Notice: Longitude first, Latitude second in WKT POINT
    return WKTElement(f"POINT({lon} {lat})", srid=4326)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Swapping latitude and longitude coordinates (putting lat first in WKT) stores the point in the wrong quadrant of the globe.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Storing as geometry with runtime geography casting combines fast Cartesian indexing with accurate ellipsoidal distance math.

#### 9. System Design & Scalability Angle
Spatial point storage enables spatial indexing, polygon intersection, and radius filtering natively inside PostgreSQL.

#### 10. Senior Backend Interview Prep
**Q:** Why does PostGIS use (Longitude, Latitude) ordering instead of (Lat, Lon)?

**A:** PostGIS follows standard Cartesian (X, Y) coordinate conventions where Longitude is the horizontal X axis and Latitude is the vertical Y axis.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 17: GiST Spatial Indexing & Bounding-Box Search Pruning [ESSENTIAL]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 16
- **Leads To:** Story 18, Story 19, Story 47
- **Code Truth Files:** `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`, `backend/app/models/property.py`
- **Key Symbol(s):** `spatial_index=True / idx_properties_location (USING gist)`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters in Production
Without spatial indexes, querying spatial candidates requires sequential scans and per-row mathematical checks.

#### 2. Core Engineering Concept
GiST (Generalized Search Tree) is an indexing framework. PostGIS geometry commonly uses spatial operator classes based on bounding-box relationships to prune irrelevant candidates. Exact performance depends on dataset size, distribution, selectivity, planner decisions and hardware.

#### 3. How It Works Under the Hood
Alembic revision 0003 creates idx_properties_location USING gist on the location geometry column.

#### 4. EstateMap Implementation Reality
Database schema sets spatial_index=True on Geometry columns, instructing PostgreSQL to create a GiST index.

#### 5. Step-by-Step Code Flow
Spatial Query -> Query Planner evaluates GiST index -> Prunes non-overlapping bounding-box subtrees -> Filters candidate rows -> Verifies exact geometry predicate.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create a GiST index on a PostGIS geometry column using Alembic operations
from alembic import op

def create_gist_spatial_index():
    op.create_index(
        'idx_properties_location',
        'properties',
        ['location'],
        unique=False,
        postgresql_using='gist'
    )
```

#### 7. Break It & Debug It (Specific Failure Mode)
Wrapping the indexed location column in an unindexed function in the WHERE clause prevents the planner from utilizing the GiST index, falling back to Seq Scan.

#### 8. Architectural Tradeoffs & Rejected Alternatives
GiST indexes trade slightly higher write/update overhead for candidate pruning during spatial filtering.

#### 9. System Design & Scalability Angle
GiST reduces the candidate search space for selective spatial predicates; verify actual planner behavior using EXPLAIN ANALYZE.

#### 10. Senior Backend Interview Prep
**Q:** How does a GiST spatial index work internally for PostGIS queries?

**A:** GiST builds a hierarchical tree of bounding boxes (similar to an R-Tree). Spatial queries check bounding-box overlap and prune entire subtrees that do not intersect the search envelope.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 18: Geodesic Radius Search via ST_DWithin on Runtime Cast Geography [ESSENTIAL]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 16, Story 17
- **Leads To:** Story 20, Story 24, Story 25
- **Code Truth Files:** `backend/app/services/geo_service.py`, `backend/app/repositories/property_repository.py`
- **Key Symbol(s):** `PropertyRepository.search_radius / func.ST_DWithin / func.ST_Distance`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters in Production
Querying Euclidean distance in degrees on EPSG:4326 causes severe distortion because degrees of longitude shrink away from the equator.

#### 2. Core Engineering Concept
Casting geometry to geography enables spherical great-circle distance calculations directly in meters.

#### 3. How It Works Under the Hood
PropertyRepository.search_radius casts Property.location to geography and executes ST_DWithin(loc, point, radius_m).

#### 4. EstateMap Implementation Reality
app/repositories/property_repository.py casts location to Geography and applies func.ST_DWithin and func.ST_Distance.

#### 5. Step-by-Step Code Flow
GET /api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=5000 -> Repository constructs ST_DWithin query -> PostGIS index filters bounding box -> Returns properties with distance_m.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Construct an async ST_DWithin radius query with distance calculation
from sqlalchemy import select, func
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint

def query_radius(session, model, lat: float, lon: float, radius_meters: float):
    target_point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
    loc_geog = func.cast(model.location, Geography)
    target_geog = func.cast(target_point, Geography)
    
    stmt = select(
        model,
        func.round(func.cast(ST_Distance(loc_geog, target_geog), func.numeric), 2).label("distance_meters")
    ).where(
        ST_DWithin(loc_geog, target_geog, radius_meters)
    ).order_by("distance_meters")
    return stmt
```

#### 7. Break It & Debug It (Specific Failure Mode)
Calling ST_DWithin on uncast geometry with radius_meters=5000 treats the unit as 5,000 degrees, matching every listing on Earth.

#### 8. Architectural Tradeoffs & Rejected Alternatives
ST_DWithin leverages bounding box pruning before evaluating exact ellipsoidal distance math.

#### 9. System Design & Scalability Angle
Geodesic radius search is the fundamental building block for location-based discovery in mobile and map applications.

#### 10. Senior Backend Interview Prep
**Q:** Why must you cast geometry to geography for ST_DWithin(geom, point, 5000)?

**A:** Geometry calculations occur in planar units (degrees in EPSG:4326); casting to geography computes distances in meters along the curved Earth spheroid.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 19: Viewport Bounding Box Filtering via ST_MakeEnvelope & GiST Intersects [ESSENTIAL]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 16, Story 17
- **Leads To:** Story 21, Story 42
- **Code Truth Files:** `backend/app/services/geo_service.py`, `backend/app/api/v1/maps.py`, `backend/app/repositories/property_repository.py`
- **Key Symbol(s):** `PropertyRepository.search_bbox / func.ST_MakeEnvelope / func.ST_Within`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_spatial_search.py`

#### 1. Why This Matters in Production
Map-driven discovery requires fetching only the properties currently visible in the user's viewport bounding box.

#### 2. Core Engineering Concept
ST_MakeEnvelope constructs a polygon envelope that checks bounding-box overlap directly against GiST index nodes.

#### 3. How It Works Under the Hood
GET /api/v1/properties/map takes min_lat, max_lat, min_lon, max_lon and queries PropertyRepository.search_bbox.

#### 4. EstateMap Implementation Reality
app/repositories/property_repository.py builds ST_MakeEnvelope polygon and filters properties with ST_Within.

#### 5. Step-by-Step Code Flow
Map Pan/Zoom -> Frontend sends bounds (min_lat, min_lon, max_lat, max_lon) -> Repository generates ST_MakeEnvelope -> GiST index scans matching box -> Returns visible GeoJSON.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build an ST_MakeEnvelope viewport query for map bounding box search
from sqlalchemy import select
from geoalchemy2.functions import ST_MakeEnvelope, ST_Within

def query_viewport(model, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    # Envelope parameter order: (xmin, ymin, xmax, ymax, srid) -> (min_lon, min_lat, max_lon, max_lat, 4326)
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    return select(model).where(ST_Within(model.location, envelope))
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing min_lat > max_lat creates an inverted bounding box, returning zero results from the spatial index.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Bounding box queries are fast because they evaluate 2D box containment without trigonometric distance math.

#### 9. System Design & Scalability Angle
Viewport filtering prevents clients from downloading points outside the visible screen, bounding payload sizes.

#### 10. Senior Backend Interview Prep
**Q:** How does a map viewport search query work in PostGIS?

**A:** The API constructs a bounding envelope via ST_MakeEnvelope and uses ST_Within to leverage the GiST spatial index efficiently.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 20: Points of Interest (POI) Proximity Aggregation & Spatial Intelligence [IMPORTANT]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 16, Story 18
- **Leads To:** Story 25, Story 27
- **Code Truth Files:** `backend/app/models/poi.py`, `backend/app/services/poi_service.py`, `backend/app/repositories/poi_repository.py`
- **Key Symbol(s):** `POIService.get_location_intelligence / POIRepository.get_nearby_pois`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_pois.py`

#### 1. Why This Matters in Production
Listing evaluation requires neighborhood intelligence (proximity to schools, hospitals, transit hubs).

#### 2. Core Engineering Concept
Spatial aggregation groups nearby POIs by category and computes nearest facility distances within a target radius.

#### 3. How It Works Under the Hood
POIService.get_location_intelligence queries POIRepository for nearby POIs, categorizes them, and caches the summary with CACHE_POI_TTL_SECONDS (1800s).

#### 4. EstateMap Implementation Reality
app/services/poi_service.py coordinates spatial queries across POI categories and calculates summary counts and nearest distances.

#### 5. Step-by-Step Code Flow
Property ID requested -> POIService fetches property coordinates -> Queries POIRepository for POIs within radius -> Computes count per category & nearest distance -> Returns LocationIntelligenceResponse.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Aggregate POIs by category and compute nearest distance
from collections import defaultdict

def aggregate_pois_by_category(poi_distance_tuples: list[tuple]) -> dict:
    categories = defaultdict(lambda: {"count": 0, "nearest_km": None})
    for poi, dist_meters in poi_distance_tuples:
        cat = poi.category
        dist_km = round(dist_meters / 1000.0, 2)
        categories[cat]["count"] += 1
        if categories[cat]["nearest_km"] is None or dist_km < categories[cat]["nearest_km"]:
            categories[cat]["nearest_km"] = dist_km
    return dict(categories)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Executing separate un-indexed spatial queries for each POI category individually produces an N+1 query pattern.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Location intelligence is calculated on-demand with Redis caching (TTL=1800s) to balance freshness with query performance.

#### 9. System Design & Scalability Angle
Cached POI category aggregations allow fast real-time score calculation during property discovery.

#### 10. Senior Backend Interview Prep
**Q:** How do you optimize spatial proximity aggregation for listings?

**A:** Pre-index POIs with GiST, query with ST_DWithin radius buffers, and cache aggregate category summaries in Redis.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 21: RFC 7946 GeoJSON Serialization & Strict Coordinate Ordering [IMPORTANT]
- **Module:** Module 05: PostGIS Spatial Search
- **Prerequisites:** Story 05, Story 16
- **Leads To:** Story 42
- **Code Truth Files:** `backend/app/schemas/geo.py`, `backend/app/api/v1/properties.py`
- **Key Symbol(s):** `PropertyGeoJSONFeature / PropertyGeoJSONFeatureCollection / PointGeometry`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_geo_schemas.py`

#### 1. Why This Matters in Production
Standardized GeoJSON payloads ensure seamless rendering across map libraries (MapLibre, Mapbox, Leaflet, QGIS).

#### 2. Core Engineering Concept
RFC 7946 specifies that GeoJSON coordinate positions MUST be ordered as [easting, northing] -> [longitude, latitude].

#### 3. How It Works Under the Hood
app/schemas/geo.py defines Pydantic models for GeoJSON Feature, FeatureCollection, and Point geometry serialization.

#### 4. EstateMap Implementation Reality
app/schemas/geo.py defines type-safe Pydantic models enforcing GeoJSON specifications and property attributes.

#### 5. Step-by-Step Code Flow
Database Property entity -> Pydantic validator extracts WKB/WKT coordinates -> Formats into FeatureCollection with [lon, lat] geometry -> Serialized to JSON.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build RFC 7946 GeoJSON Feature and FeatureCollection Pydantic schemas
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=2, description="[lon, lat]")

class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoJSONFeature]
```

#### 7. Break It & Debug It (Specific Failure Mode)
Emitting [latitude, longitude] order in GeoJSON violates RFC 7946 and causes map clients to plot markers in Antarctica.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Serializing directly in Pydantic ensures schema validation without requiring heavy external GIS serialization libraries.

#### 9. System Design & Scalability Angle
Standard GeoJSON schemas allow the backend API to be consumed by any GIS platform, web client, or mobile application.

#### 10. Senior Backend Interview Prep
**Q:** What is the RFC 7946 coordinate ordering standard?

**A:** [Longitude, Latitude, Elevation], representing X (easting) then Y (northing).

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 06: Location Intelligence & Routing

### Story 22: Deterministic In-Memory Location Resolver for Metropolitan Hubs [ESSENTIAL]
- **Module:** Module 06: Location Intelligence & Routing
- **Prerequisites:** Story 16, Story 21
- **Leads To:** Story 23, Story 24, Story 39
- **Code Truth Files:** `backend/app/utils/location_resolver.py`, `backend/app/api/v1/search.py`
- **Key Symbol(s):** `LocationResolver.resolve_destination / KNOWN_LOCATIONS / METRO_BOUNDS`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_location_resolver.py`

#### 1. Why This Matters in Production
Natural language searches contain informal locality names that need deterministic coordinate resolution.

#### 2. Core Engineering Concept
In-memory alias dictionary and normalized matching resolve known metropolitan hubs (Bengaluru and Chennai) without external network dependencies.

#### 3. How It Works Under the Hood
LocationResolver matches query strings against KNOWN_LOCATIONS registry with metro bounding box validation (Bengaluru and Chennai).

#### 4. EstateMap Implementation Reality
app/utils/location_resolver.py implements string normalization, alias dictionary lookup, and city bounding box verification; returns None for unknown destinations to trigger clarification.

#### 5. Step-by-Step Code Flow
Query string received ('near Electronic City') -> LocationResolver normalizes string -> Matches alias in KNOWN_LOCATIONS -> Returns ResolvedLocation(name, lat, lng).

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build an in-memory landmark resolver with exact, word-boundary, and substring matching
import re
from typing import Optional
from pydantic import BaseModel

class ResolvedLoc(BaseModel):
    name: str
    lat: float
    lng: float

LANDMARKS = {
    "electronic city": (12.8452, 77.6602, "Electronic City"),
    "whitefield": (12.9698, 77.7499, "Whitefield"),
    "tidel park": (12.9897, 80.2483, "TIDEL Park"),
}

def resolve_landmark(query: Optional[str]) -> Optional[ResolvedLoc]:
    if not query or not query.strip(): return None
    cleaned = re.sub(r"[^\w\s]", " ", query.lower()).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    if cleaned in LANDMARKS:
        lat, lng, label = LANDMARKS[cleaned]
        return ResolvedLoc(name=label, lat=lat, lng=lng)
    return None
```

#### 7. Break It & Debug It (Specific Failure Mode)
Attempting to geocode arbitrary un-indexed strings without returning None causes false-positive coordinate matches on unrelated user queries.

#### 8. Architectural Tradeoffs & Rejected Alternatives
In-memory deterministic resolver avoids third-party geocoding API rate limits, costs, and external network latency.

#### 9. System Design & Scalability Angle
Layered location resolution: check in-memory catalog first; return clarification prompt if destination is unresolved.

#### 10. Senior Backend Interview Prep
**Q:** Why use an in-memory landmark resolver for domain search?

**A:** It provides predictable, fast coordinate resolution for known domain hubs with zero external API costs and no network dependency.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 23: External HTTP Client with Async Httpx & OSRM Engine Integration [ESSENTIAL]
- **Module:** Module 06: Location Intelligence & Routing
- **Prerequisites:** Story 02, Story 03
- **Leads To:** Story 24, Story 47
- **Code Truth Files:** `backend/app/services/routing/osrm_provider.py`, `backend/app/services/routing/factory.py`
- **Key Symbol(s):** `OSRMProvider.get_route / RoutingProviderFactory / RoutingProvider`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_commute.py`

#### 1. Why This Matters in Production
Straight-line distance ignores physical road geometry, traffic directionality, and water bodies.

#### 2. Core Engineering Concept
Async httpx.AsyncClient queries OSRM routing endpoints for driving, walking, and cycling modes.

#### 3. How It Works Under the Hood
OSRMProvider sends coordinate pairs to OSRM /route/v1/{profile}/ and extracts duration (seconds) and distance (meters).

#### 4. EstateMap Implementation Reality
app/services/routing/osrm_provider.py encapsulates async HTTP requests to OSRM with connection timeouts, profile mapping, and response parsing.

#### 5. Step-by-Step Code Flow
Commute request -> OSRMProvider formats coordinate URL -> httpx.AsyncClient executes GET with timeout -> Parses route polyline and duration.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create an async OSRM routing client with timeouts and profile mapping
import httpx

class OSRMClient:
    def __init__(self, base_url: str = "http://router.project-osrm.org", timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def fetch_driving_route(self, orig_lat: float, orig_lng: float, dest_lat: float, dest_lng: float) -> dict:
        url = f"{self.base_url}/route/v1/driving/{orig_lng},{orig_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            route = data["routes"][0]
            return {
                "distance_km": round(route["distance"] / 1000.0, 2),
                "duration_minutes": round(route["duration"] / 60.0, 1),
                "geometry": route["geometry"]
            }
```

#### 7. Break It & Debug It (Specific Failure Mode)
Not setting HTTP timeouts on external routing calls causes backend coroutines to hang if the OSRM server becomes unresponsive.

#### 8. Architectural Tradeoffs & Rejected Alternatives
OSRM provides road network routing without commercial API fees, though standard endpoints lack real-time dynamic traffic awareness.

#### 9. System Design & Scalability Angle
External API wrappers must encapsulate timeouts, retries, and fallbacks to prevent cascading system degradation.

#### 10. Senior Backend Interview Prep
**Q:** How do you safely integrate third-party HTTP services in an async backend?

**A:** Use async HTTP clients (httpx) with strict timeouts, connection pooling, and circuit breaker fallbacks.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 24: Multi-Modal Commute Calculation & Great-Circle Haversine Fallback [ESSENTIAL]
- **Module:** Module 06: Location Intelligence & Routing
- **Prerequisites:** Story 18, Story 22, Story 23
- **Leads To:** Story 25, Story 30
- **Code Truth Files:** `backend/app/services/commute_service.py`, `backend/app/utils/geo.py`
- **Key Symbol(s):** `CommuteService.calculate_route / haversine_distance_km`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_commute.py`

#### 1. Why This Matters in Production
Commute duration is a key search criterion; routing provider failures must never crash the search pipeline.

#### 2. Core Engineering Concept
Haversine formula calculates great-circle distance on a spherical Earth as a robust mathematical fallback.

#### 3. How It Works Under the Hood
CommuteService checks Redis route cache (CACHE_ROUTE_TTL_SECONDS=600s), queries OSRM, and falls back to speed-profile Haversine math on provider failure.

#### 4. EstateMap Implementation Reality
app/services/commute_service.py coordinates multi-property commute calculations, route caching, and Haversine fallback logic.

#### 5. Step-by-Step Code Flow
Properties & Destination passed -> CommuteService checks Redis cache -> Queries routing provider -> If routing fails, applies Haversine fallback -> Returns commute response.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement Haversine distance and duration estimation fallback
import math

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def estimate_fallback_duration(distance_km: float, speed_kmh: float = 25.0) -> float:
    return round((distance_km / speed_kmh) * 60.0, 1)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing negative or zero travel speed in fallback duration calculations causes a ZeroDivisionError.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Cached route results combined with mathematical fallbacks ensure commute endpoints remain responsive during external routing outages.

#### 9. System Design & Scalability Angle
Computing commutes across candidate listings requires batching and caching to avoid latency bottlenecks.

#### 10. Senior Backend Interview Prep
**Q:** What is your fallback strategy if external routing APIs fail?

**A:** Gracefully degrade to in-memory Haversine distance with calibrated mode-specific velocity models (e.g. 25 km/h driving, 4 km/h walking).

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 07: Deterministic Ranking & Business Logic

### Story 25: 6-Factor Mathematical Ranking Engine & Min-Max Score Normalization [ESSENTIAL]
- **Module:** Module 07: Deterministic Ranking & Business Logic
- **Prerequisites:** Story 05, Story 18, Story 24
- **Leads To:** Story 26, Story 27, Story 28
- **Code Truth Files:** `backend/app/services/ranking_service.py`, `backend/app/utils/ranking.py`
- **Key Symbol(s):** `RankingService.rank_properties / calculate_price_score / calculate_bedroom_score`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ranking.py`

#### 1. Why This Matters in Production
Deterministic MCDA ensures transparent, auditable, and reproducible scoring across candidate listings.

#### 2. Core Engineering Concept
Multi-Criteria Decision Analysis (MCDA) linearly normalizes heterogeneous metrics (INR, sqft, minutes) into comparable [0, 1] scales.

#### 3. How It Works Under the Hood
app/utils/ranking.py implements mathematical scoring functions with user-configurable or preset weight vectors.

#### 4. EstateMap Implementation Reality
app/services/ranking_service.py coordinates scoring calculations across candidate properties and sorts by final composite score; caches results with CACHE_RANKING_TTL_SECONDS (300s).

#### 5. Step-by-Step Code Flow
Filtered properties passed to RankingService -> Evaluates 6 dimension scoring functions -> Multiplies by weight vector -> Sums to composite score -> Returns ranked list.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a min-max normalizer for price and area scoring
def score_lower_is_better(val: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val: return 1.0
    normalized = 1.0 - (val - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def score_higher_is_better(val: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val: return 1.0
    normalized = (val - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))
```

#### 7. Break It & Debug It (Specific Failure Mode)
Failing to handle max_val == min_val causes a ZeroDivisionError when all candidate properties have identical price or area.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Deterministic mathematical ranking guarantees identical inputs produce identical rank ordering every time.

#### 9. System Design & Scalability Angle
Separating hard database filters (WHERE price <= max_price) from soft ranking preferences delivers optimal user relevance.

#### 10. Senior Backend Interview Prep
**Q:** Why use deterministic mathematical ranking over an LLM for search results?

**A:** Deterministic scoring is reproducible, computationally efficient, free of token costs, and immune to generative hallucinations.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 26: Dynamic Missing-Factor Weight Redistribution & Active Weight Sums [ESSENTIAL]
- **Module:** Module 07: Deterministic Ranking & Business Logic
- **Prerequisites:** Story 25
- **Leads To:** Story 27, Story 28
- **Code Truth Files:** `backend/app/services/ranking_service.py`, `backend/app/utils/ranking.py`
- **Key Symbol(s):** `RankingService._redistribute_weights / active_weight_sum normalization`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_ranking_scoring.py`

#### 1. Why This Matters in Production
If an optional factor (e.g. commute weight = 0.25) is missing, total scores would cap at 0.75, distorting comparisons.

#### 2. Core Engineering Concept
Active weight renormalization computes W_i' = W_i / sum(W_active), ensuring composite scores always scale to 1.0.

#### 3. How It Works Under the Hood
RankingService._redistribute_weights filters out inactive criteria and divides active weights by active_weight_sum.

#### 4. EstateMap Implementation Reality
app/services/ranking_service.py checks active scoring factors and rescales weight vectors dynamically before scoring.

#### 5. Step-by-Step Code Flow
Ranking query without commute destination -> Commute factor marked inactive -> Active weights summed -> Each active weight divided by sum -> Composite scores sum to 1.0.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement weight redistribution for missing scoring criteria
def redistribute_active_weights(raw_weights: dict[str, float], active_keys: set[str]) -> dict[str, float]:
    active_sum = sum(w for k, w in raw_weights.items() if k in active_keys)
    if active_sum <= 0:
        equal_weight = 1.0 / max(1, len(active_keys))
        return {k: equal_weight if k in active_keys else 0.0 for k in raw_weights}
    return {k: (w / active_sum if k in active_keys else 0.0) for k, w in raw_weights.items()}
```

#### 7. Break It & Debug It (Specific Failure Mode)
Hardcoding static weights when optional filters are omitted produces skewed scores that do not reflect user priority distributions.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Proportional redistribution preserves relative user priority ratios among the remaining active factors.

#### 9. System Design & Scalability Angle
Dynamic weight normalization ensures multi-attribute scoring systems remain statistically valid regardless of missing input dimensions.

#### 10. Senior Backend Interview Prep
**Q:** How do you handle missing criteria in multi-attribute scoring?

**A:** Dynamically rescale active weights so their sum equals 1.0, preserving relative priority ratios.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 27: Factual Score Explainability & Human-Readable Score Breakdowns [IMPORTANT]
- **Module:** Module 07: Deterministic Ranking & Business Logic
- **Prerequisites:** Story 25, Story 26
- **Leads To:** Story 28, Story 38
- **Code Truth Files:** `backend/app/utils/ranking.py`, `backend/app/schemas/ranking.py`
- **Key Symbol(s):** `generate_deterministic_explanations / FactorScoreDetail`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ranking.py`

#### 1. Why This Matters in Production
Users trust search rankings when the system transparently explains why a listing ranked in a specific position.

#### 2. Core Engineering Concept
Rule-based template generation derived directly from computed sub-scores guarantees factual explainability.

#### 3. How It Works Under the Hood
app/utils/ranking.py generates FactorScoreDetail arrays attached to every RankedPropertyResponse.

#### 4. EstateMap Implementation Reality
app/utils/ranking.py maps dimension scores and calculated deltas to human-readable factual strings.

#### 5. Step-by-Step Code Flow
Score calculation finishes -> generate_deterministic_explanations() inspects top positive/negative score factors -> Formats string explanations -> Attached to response.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Generate template-based factual explanations from factor scores
def generate_factor_explanation(factor_name: str, score: float, raw_val: float) -> str:
    if factor_name == "price" and score >= 0.8:
        return f"Competitively priced at ₹{raw_val:,.0f}"
    if factor_name == "commute" and score >= 0.8:
        return f"Short commute time ({raw_val:.0f} mins)"
    if factor_name == "location" and score >= 0.8:
        return "High density of nearby amenities"
    return f"{factor_name.title()} score: {score:.2f}" 
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing unformatted raw numbers (e.g. 15000000.0 instead of ₹1.5 Cr) reduces explainability and causes client UI formatting bugs.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Deterministic explanation generation requires zero LLM tokens and executes in-memory.

#### 9. System Design & Scalability Angle
Exposing structured explainability objects enables client applications to highlight key decision drivers without extra API roundtrips.

#### 10. Senior Backend Interview Prep
**Q:** How do you provide explainability in recommendation systems?

**A:** Expose atomic sub-score breakdowns and template-driven factual reasoning derived directly from scoring metrics.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 28: Deterministic Property Comparison Engine & Dimension Winners [ESSENTIAL]
- **Module:** Module 07: Deterministic Ranking & Business Logic
- **Prerequisites:** Story 25, Story 26, Story 27
- **Leads To:** Story 38, Story 42
- **Code Truth Files:** `backend/app/services/comparison_service.py`, `backend/app/schemas/comparison.py`
- **Key Symbol(s):** `ComparisonService.compare_properties / ComparisonResult / DimensionWinner`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ai_comparison.py`

#### 1. Why This Matters in Production
Comparing properties side-by-side requires objective numerical diffs before synthesizing a narrative summary.

#### 2. Core Engineering Concept
Pairwise and 3-way dimensional comparisons select verified winners for price per sqft, bedroom count, and commute.

#### 3. How It Works Under the Hood
ComparisonService.compare_properties fetches listings, computes metric diffs, determines winners, and packages ComparisonResult.

#### 4. EstateMap Implementation Reality
app/services/comparison_service.py implements structured metric diffing, price per sqft calculation, and winner selection.

#### 5. Step-by-Step Code Flow
POST /api/v1/properties/compare [ids] -> Service fetches properties -> Calculates metric deltas -> Selects dimension winners -> Returns structured ComparisonResult.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a dimensional winner evaluator for 2-3 properties
def pick_dimension_winner(items: list[dict], metric: str, lower_is_better: bool = False) -> dict:
    if not items: return {}
    comparator = min if lower_is_better else max
    winner = comparator(items, key=lambda x: x.get(metric, 0))
    return {
        "metric": metric,
        "winner_id": winner["id"],
        "winner_value": winner[metric]
    }
```

#### 7. Break It & Debug It (Specific Failure Mode)
Requesting comparison for non-existent property IDs raises an EntityNotFoundException if not validated before processing.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Deterministic dimension winners provide hard facts that ground subsequent narrative summaries.

#### 9. System Design & Scalability Angle
Decoupling metric comparison from narrative generation allows caching the deterministic comparison result independently.

#### 10. Senior Backend Interview Prep
**Q:** How do you structure property comparison in the backend?

**A:** Compute deterministic dimensional deltas and metric winners first, then pass those verified facts to the presentation or AI layer.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 08: Redis In-Memory Caching

### Story 29: Redis Async Client & Cache-Aside (Lazy Loading) Architecture [ESSENTIAL]
- **Module:** Module 08: Redis In-Memory Caching
- **Prerequisites:** Story 02, Story 03
- **Leads To:** Story 30, Story 31, Story 32
- **Code Truth Files:** `backend/app/cache/redis.py`, `backend/app/cache/cache_service.py`
- **Key Symbol(s):** `CacheService.get_json / CacheService.set_json / init_redis`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_cache_service.py`

#### 1. Why This Matters in Production
Repeated spatial and ranking queries consume database CPU; caching identical requests avoids redundant database queries.

#### 2. Core Engineering Concept
Cache-Aside pattern loads data on-demand, keeping in-memory footprints bounded to active query working sets.

#### 3. How It Works Under the Hood
CacheService wraps redis.asyncio client with JSON serialization and transparent database fallback on cache miss.

#### 4. EstateMap Implementation Reality
app/cache/redis.py manages connection pool; app/cache/cache_service.py provides get_json, set_json, and delete methods with domain TTLs.

#### 5. Step-by-Step Code Flow
Client Request -> CacheService.get_json(key) -> Cache HIT: return cached JSON -> Cache MISS: query DB -> CacheService.set_json(key, data, ttl) -> Return response.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement a generic Cache-Aside helper around an async fetch function
import json
import redis.asyncio as aioredis
from typing import Callable, Any

async def cached_fetch(redis: aioredis.Redis, key: str, ttl_sec: int, fetch_fn: Callable[[], Any]) -> Any:
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    data = await fetch_fn()
    await redis.set(key, json.dumps(data), ex=ttl_sec)
    return data
```

#### 7. Break It & Debug It (Specific Failure Mode)
Storing non-JSON-serializable objects (such as raw SQLAlchemy instances or datetime objects) in Redis without a custom encoder causes a TypeError.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Cache-Aside handles cache node restarts gracefully because the database remains the authoritative single source of truth.

#### 9. System Design & Scalability Angle
Caching read-heavy geospatial and ranking responses protects database connection pools and increases read capacity.

#### 10. Senior Backend Interview Prep
**Q:** How does the Cache-Aside pattern work and what are its failure modes?

**A:** The application queries cache first; on miss, loads from DB and writes to cache with TTL. If cache fails, app gracefully falls back to querying the database directly.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 30: Canonical Cache Key Design, Coordinate Precision & SHA-256 Hashing [ESSENTIAL]
- **Module:** Module 08: Redis In-Memory Caching
- **Prerequisites:** Story 29
- **Leads To:** Story 31, Story 32
- **Code Truth Files:** `backend/app/cache/cache_keys.py`, `backend/app/cache/cache_service.py`
- **Key Symbol(s):** `CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_cache_keys.py`

#### 1. Why This Matters in Production
Microscopic float precision differences destroy cache hit ratios; coordinate rounding normalizes nearby requests.

#### 2. Core Engineering Concept
Rounding coordinates to CACHE_COORDINATE_PRECISION (4 decimal places, ~11m precision) collapses GPS drift into canonical cache buckets.

#### 3. How It Works Under the Hood
CacheKeys.normalize_coord rounds floats to 4 decimals; filter dicts are sorted and hashed with SHA-256.

#### 4. EstateMap Implementation Reality
app/cache/cache_keys.py implements key generator functions with version prefixes (estatemap:v1:*) and deterministic hashing.

#### 5. Step-by-Step Code Flow
Parameters received -> CacheKeys formats key: estatemap:v1:map:{min_lat}:{min_lon}:{max_lat}:{max_lon}:{sha256(filters)} -> Canonical key used in Redis lookup.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a canonical geospatial cache key generator with SHA-256 hashing
import hashlib
import json

def make_geo_cache_key(prefix: str, min_lat: float, min_lon: float, max_lat: float, max_lon: float, params: dict, precision: int = 4) -> str:
    coords = f"{round(min_lat, precision)}:{round(min_lon, precision)}:{round(max_lat, precision)}:{round(max_lon, precision)}"
    param_str = json.dumps(params, sort_keys=True)
    digest = hashlib.sha256(param_str.encode()).hexdigest()[:12]
    return f"estatemap:v1:{prefix}:{coords}:{digest}" 
```

#### 7. Break It & Debug It (Specific Failure Mode)
Omitting sort_keys=True when serializing filter dictionaries produces different JSON hashes for identical filter combinations, causing unnecessary cache misses.

#### 8. Architectural Tradeoffs & Rejected Alternatives
SHA-256 digests keep Redis key lengths fixed and predictable regardless of complex filter parameter counts.

#### 9. System Design & Scalability Angle
Hierarchical key namespaces simplify monitoring, debugging, and targeted wildcard key invalidation.

#### 10. Senior Backend Interview Prep
**Q:** How do you design cache keys for geospatial search queries?

**A:** Normalize coordinates to fixed precision (e.g. 4 decimals), sort filter parameters deterministically, and hash with version prefixes to guarantee collision-free lookups.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 31: Cache Invalidation via Non-Blocking SCAN & TTL-Based Expiration [IMPORTANT]
- **Module:** Module 08: Redis In-Memory Caching
- **Prerequisites:** Story 29, Story 30
- **Leads To:** Story 32, Story 47
- **Code Truth Files:** `backend/app/cache/cache_service.py`, `backend/app/core/config.py`
- **Key Symbol(s):** `CacheService.delete_pattern / CacheService.delete / CACHE_MAP_TTL_SECONDS`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_cache_service.py`

#### 1. Why This Matters in Production
Using the blocking KEYS * command halts the single-threaded Redis event loop; SCAN iterates cursor-by-cursor safely.

#### 2. Core Engineering Concept
TTL-based expiration guarantees eventual consistency; mutation hooks trigger active prefix invalidation via SCAN.

#### 3. How It Works Under the Hood
CacheService.delete_pattern uses redis.scan_iter(match=pattern, count=100) to delete matching keys without blocking.

#### 4. EstateMap Implementation Reality
app/cache/cache_service.py implements delete_pattern using async scan_iter and applies configurable TTLs from Settings (Map: 120s, Ranking: 300s, Route: 600s, POI: 1800s).

#### 5. Step-by-Step Code Flow
Property Updated -> PropertyService calls CacheService.delete_pattern('estatemap:v1:map:*') -> redis.scan_iter iterates batches -> Keys deleted -> Next read re-caches fresh data.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement non-blocking batch cache invalidation using scan_iter
import redis.asyncio as aioredis

async def invalidate_cache_pattern(redis: aioredis.Redis, pattern: str, batch_size: int = 100):
    keys_to_del = []
    async for key in redis.scan_iter(match=pattern, count=batch_size):
        keys_to_del.append(key)
        if len(keys_to_del) >= batch_size:
            await redis.delete(*keys_to_del)
            keys_to_del.clear()
    if keys_to_del:
        await redis.delete(*keys_to_del)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Running KEYS 'estatemap:*' on a production Redis instance blocks all other Redis operations for the duration of the scan.

#### 8. Architectural Tradeoffs & Rejected Alternatives
SCAN has O(N) overall complexity across iterations but never blocks the single-threaded Redis event loop.

#### 9. System Design & Scalability Angle
Configuring distinct domain TTLs balances data freshness with database query reduction across fast-changing and slow-changing data.

#### 10. Senior Backend Interview Prep
**Q:** Why is KEYS * dangerous in production Redis, and what is the alternative?

**A:** KEYS * blocks the single-threaded Redis server until all keys are scanned, stalling all traffic. Use SCAN with cursor pagination instead.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 09: Rate Limiting & Resilience

### Story 32: Sliding-Window Log Rate Limiting via Redis Sorted Sets (ZSET) [ESSENTIAL]
- **Module:** Module 09: Rate Limiting & Resilience
- **Prerequisites:** Story 04, Story 29
- **Leads To:** Story 33, Story 34
- **Code Truth Files:** `backend/app/core/rate_limit.py`, `backend/app/core/middleware.py`
- **Key Symbol(s):** `RateLimiter / redis.pipeline() / ZADD / ZREMRANGEBYSCORE`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_rate_limiting.py`

#### 1. Why This Matters in Production
Fixed window rate limiters allow 2x traffic bursts across window boundaries; sliding windows provide uniform enforcement.

#### 2. Core Engineering Concept
Redis pipeline reduces network round trips; however, pipeline execution does not make the sliding-window decision fully atomic without Lua or transactional isolation. Concurrent clients may interleave operations.

#### 3. How It Works Under the Hood
RateLimiter executes pipelined ZREMRANGEBYSCORE -> ZCARD -> ZADD -> EXPIRE, rejecting requests exceeding limit with HTTP 429.

#### 4. EstateMap Implementation Reality
app/core/rate_limit.py implements RateLimiter class using async Redis pipelines for sliding-window log tracking; rolls back ZADD on limit breach.

#### 5. Step-by-Step Code Flow
Incoming Request -> RateLimiter executes Redis pipeline: ZREMRANGEBYSCORE(0, now-60) -> ZCARD -> If count >= limit: rollback ZADD & raise RateLimitExceededException -> Else allow request.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement a sliding-window rate limiter using Redis pipelines
import time
import uuid
import redis.asyncio as aioredis

async def check_rate_limit(redis: aioredis.Redis, key: str, limit: int, window_sec: int = 60) -> tuple[bool, int]:
    now = time.time()
    window_start = now - window_sec
    member = f"{now:.6f}_{uuid.uuid4().hex[:6]}"
    
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zcard(key)
    pipe.zadd(key, {member: now})
    pipe.expire(key, window_sec + 5)
    results = await pipe.execute()
    
    count_before = results[1]
    if count_before >= limit:
        await redis.zrem(key, member) # Rollback added member
        return True, 0
    return False, max(0, limit - (count_before + 1))
```

#### 7. Break It & Debug It (Specific Failure Mode)
In high concurrency, multiple requests reading ZCARD before ZADD can cause a slight over-limit race condition unless executed via server-side Lua scripts.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Redis ZSET sliding window offers precision and burst protection with minimal memory per active client IP.

#### 9. System Design & Scalability Angle
Rate limiting protects downstream database connection pools and external AI providers from traffic spikes and abuse.

#### 10. Senior Backend Interview Prep
**Q:** Does a Redis pipeline guarantee atomic rate limiting?

**A:** No. A pipeline batches commands to reduce network round trips, but other commands can interleave unless wrapped in MULTI/EXEC or executed via a Lua script.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 33: Multi-Tier Endpoint Scopes, HTTP 429 & Retry-After Semantics [ESSENTIAL]
- **Module:** Module 09: Rate Limiting & Resilience
- **Prerequisites:** Story 32
- **Leads To:** Story 34, Story 42
- **Code Truth Files:** `backend/app/core/rate_limit.py`, `backend/app/core/config.py`
- **Key Symbol(s):** `RateLimiter / RateLimitExceededException / HTTP 429`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_rate_limiting.py`

#### 1. Why This Matters in Production
Compute-heavy AI and ranking endpoints require stricter rate limits than lightweight health and listing endpoints.

#### 2. Core Engineering Concept
Tiered rate limiting scopes limits by identity (IP or user ID) and endpoint domain; standard HTTP 429 returns Retry-After.

#### 3. How It Works Under the Hood
RateLimiter applies domain configurations (Auth: 10/min, AI: 15/min, Ranked Search: 20/min, Commute: 30/min, Default: 100/min).

#### 4. EstateMap Implementation Reality
app/core/rate_limit.py maps route scopes to Settings limits and raises RateLimitExceededException with calculated Retry-After duration.

#### 5. Step-by-Step Code Flow
Request evaluated -> RateLimiter determines scope limit -> If exceeded, raises RateLimitExceededException -> Formats HTTP 429 with Retry-After header in seconds.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create scoped rate limiter dependencies with Retry-After calculation
from fastapi import Request, HTTPException

def create_scoped_limiter(scope_name: str, limit: int, window_sec: int = 60):
    async def limiter_dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"ratelimit:{scope_name}:{client_ip}"
        # Evaluate limiter...
        # If limited:
        # raise HTTPException(status_code=429, detail="Too Many Requests", headers={"Retry-After": str(window_sec)})
    return limiter_dependency
```

#### 7. Break It & Debug It (Specific Failure Mode)
Omitting the Retry-After header causes client frontends to retry immediately, worsening backend overload.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Tiered scoping prevents heavy AI feature usage from starving general browsing and health traffic.

#### 9. System Design & Scalability Angle
Tiered rate limiting protects upstream AI quotas and database resources while keeping read paths responsive.

#### 10. Senior Backend Interview Prep
**Q:** What headers should a rate-limited API return?

**A:** Standard HTTP 429 status code with the RFC Retry-After header indicating seconds to wait, and optional conventional metadata.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 34: Fail-Open vs Fail-Closed Resiliency Policies on Redis Degradation [IMPORTANT]
- **Module:** Module 09: Rate Limiting & Resilience
- **Prerequisites:** Story 32, Story 33
- **Leads To:** Story 37, Story 47
- **Code Truth Files:** `backend/app/core/rate_limit.py`, `backend/app/cache/cache_service.py`
- **Key Symbol(s):** `RATE_LIMIT_FAIL_OPEN / Redis error handling`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_redis_degradation.py`

#### 1. Why This Matters in Production
An auxiliary Redis outage should not bring down the entire property search application.

#### 2. Core Engineering Concept
Fail-open policy allows traffic through when rate limiting infrastructure is unreachable, prioritizing availability.

#### 3. How It Works Under the Hood
RateLimiter and CacheService catch Redis errors; if fail_open=True (default), log a warning and let the request proceed.

#### 4. EstateMap Implementation Reality
app/core/rate_limit.py and app/cache/cache_service.py implement try/except RedisError blocks governed by settings.RATE_LIMIT_FAIL_OPEN.

#### 5. Step-by-Step Code Flow
Redis connection drops -> RateLimiter catches RedisError -> Checks fail_open flag -> Logs warning -> Permits request to reach route handler.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Implement fail-open/fail-closed error handling around Redis operations
import logging
logger = logging.getLogger(__name__)

async def guarded_rate_limit(redis_client, key: str, limit: int, fail_open: bool = True) -> bool:
    try:
        if redis_client is None:
            if not fail_open: raise RuntimeError("Redis unavailable")
            return True # Allow
        # Execute rate limit check...
        return True
    except Exception as e:
        logger.warning("Rate limiter Redis check failed: %s (fail_open=%s)", e, fail_open)
        if not fail_open:
            raise
        return True # Fail open: permit request
```

#### 7. Break It & Debug It (Specific Failure Mode)
Uncaught Redis connection errors bubbling up to route handlers turn every incoming API call into an HTTP 500.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Failing open prioritizes availability over strict rate enforcement; strict security paths (e.g. auth brute-force) can be configured to fail closed.

#### 9. System Design & Scalability Angle
Graceful degradation ensures non-essential auxiliary subsystem failures do not cause catastrophic core business outages.

#### 10. Senior Backend Interview Prep
**Q:** What is the difference between fail-open and fail-closed in rate limiting?

**A:** Fail-open permits requests if the limiter is unreachable (prioritizing availability); fail-closed blocks requests (prioritizing resource protection).

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 10: Multi-Provider AI Architecture

### Story 35: Abstract AI Provider Interface & Structural Parity (Ollama & Gemini) [ESSENTIAL]
- **Module:** Module 10: Multi-Provider AI Architecture
- **Prerequisites:** Story 03, Story 05
- **Leads To:** Story 36, Story 37, Story 38
- **Code Truth Files:** `backend/app/ai/base.py`, `backend/app/ai/ollama_provider.py`, `backend/app/ai/gemini_provider.py`
- **Key Symbol(s):** `AIProvider / OllamaProvider / GeminiProvider / MockAIProvider`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_cross_provider_parity.py`

#### 1. Why This Matters in Production
Coupling domain services to a single commercial LLM vendor creates vendor lock-in and vulnerability to outages.

#### 2. Core Engineering Concept
Abstract Base Class (ABC) defines the provider contract: parse_search_intent, parse_search_patch, explain_property, explain_comparison.

#### 3. How It Works Under the Hood
app/ai/base.py defines AIProvider ABC; OllamaProvider, GeminiProvider, and MockAIProvider implement the exact same methods.

#### 4. EstateMap Implementation Reality
app/ai/base.py defines the AIProvider contract; concrete adapters implement API calls and return structured Pydantic schemas.

#### 5. Step-by-Step Code Flow
AI Service calls provider method -> Adapter formats vendor-specific prompt -> Sends HTTP request -> Validates response schema -> Returns typed object.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Define the abstract AI provider base class and a test mock implementation
from abc import ABC, abstractmethod
from typing import Any

class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: pass

    @abstractmethod
    async def parse_search_intent(self, query: str) -> tuple[Any, float]: pass

class MockProvider(AIProvider):
    @property
    def provider_name(self) -> str: return "mock"
    async def parse_search_intent(self, query: str) -> tuple[dict, float]:
        return {"raw_query": query, "confidence": 1.0}, 5.0
```

#### 7. Break It & Debug It (Specific Failure Mode)
A provider returning an unvalidated dictionary instead of the standard schema breaks downstream service methods.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Unified AI provider contract allows running cost-free local Ollama in development and cloud Gemini in production.

#### 9. System Design & Scalability Angle
Adapter pattern isolates external SDK idiosyncrasies from core application domain logic.

#### 10. Senior Backend Interview Prep
**Q:** How do you prevent vendor lock-in when integrating LLMs?

**A:** Define an abstract provider interface with standardized Pydantic input/output schemas implemented by all provider adapters.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 36: Strict LLM Output Validation via Pydantic v2 Schemas [ESSENTIAL]
- **Module:** Module 10: Multi-Provider AI Architecture
- **Prerequisites:** Story 05, Story 35
- **Leads To:** Story 37, Story 38, Story 39
- **Code Truth Files:** `backend/app/schemas/ai.py`, `backend/app/ai/gemini_provider.py`, `backend/app/ai/ollama_provider.py`
- **Key Symbol(s):** `PropertySearchIntent / AIExplanationResponse / AIOutputValidationException`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_ai_schemas.py`

#### 1. Why This Matters in Production
LLMs can return malformed JSON or out-of-range numerical values.

#### 2. Core Engineering Concept
Regex JSON extraction followed by strict Pydantic model validation transforms untrusted text into type-safe domain objects.

#### 3. How It Works Under the Hood
Provider implementations extract JSON substrings and validate with PropertySearchIntent.model_validate_json().

#### 4. EstateMap Implementation Reality
app/schemas/ai.py defines PropertySearchIntent and explanation models; providers validate model output and raise AIOutputValidationException on failure.

#### 5. Step-by-Step Code Flow
LLM returns raw text -> Regex extracts JSON block -> Pydantic model_validate() checks types and bounds -> If valid: return object -> If invalid: trigger failover.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a JSON extraction and Pydantic validation firewall for LLM text output
import re
import json
from pydantic import BaseModel, Field, ValidationError

class ExtractedIntent(BaseModel):
    locality: str | None = None
    max_price: float | None = Field(None, gt=0)
    bedrooms: int | None = Field(None, ge=1, le=10)

def extract_and_validate_intent(raw_llm_text: str) -> ExtractedIntent:
    match = re.search(r"\{.*?\}", raw_llm_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return ExtractedIntent.model_validate_json(match.group(0))
```

#### 7. Break It & Debug It (Specific Failure Mode)
Passing raw LLM text directly to json.loads() without regex parsing or Pydantic validation causes syntax errors on markdown code fences.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Pydantic validation acts as a resilient firewall between non-deterministic AI generation and deterministic database logic.

#### 9. System Design & Scalability Angle
Schema validation and sanitization are essential defenses against prompt injection and LLM hallucination.

#### 10. Senior Backend Interview Prep
**Q:** How do you handle non-deterministic LLM responses in production?

**A:** Request structured JSON mode, extract with regex, validate against Pydantic schemas, and trigger fallbacks on validation failure.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 37: Dynamic Provider Routing, Latency Timeouts & Loop-Bounded Failover [ESSENTIAL]
- **Module:** Module 10: Multi-Provider AI Architecture
- **Prerequisites:** Story 35, Story 36
- **Leads To:** Story 38, Story 39
- **Code Truth Files:** `backend/app/ai/router.py`, `backend/app/services/ai_service.py`, `backend/app/ai/routing_policy.py`
- **Key Symbol(s):** `AIRouter.get_provider / AIService.parse_search_intent / AI_TOTAL_TIMEOUT_SECONDS`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ai_failover.py`

#### 1. Why This Matters in Production
Local or cloud AI providers can experience timeouts, rate limits, or connectivity issues.

#### 2. Core Engineering Concept
Sequential loop failover tries configured providers within a global time budget bounded by AI_TOTAL_TIMEOUT_SECONDS (35.0s).

#### 3. How It Works Under the Hood
AIRoutingPolicy selects attempt order; AIService loops over providers with attempt_timeout = min(remaining_budget, prov_timeout) and executes at most once per provider.

#### 4. EstateMap Implementation Reality
app/ai/router.py resolves providers; app/services/ai_service.py iterates providers with asyncio.wait_for and falls back to deterministic rules if all fail.

#### 5. Step-by-Step Code Flow
AI Request -> AIService calculates remaining budget -> Calls Provider 1 with timeout -> On Timeout/Error: logs warning -> Calls Provider 2 with remaining budget -> If all fail: executes deterministic fallback.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a multi-provider failover loop with global deadline budgeting
import asyncio
import time

async def execute_with_failover(providers: list, execute_fn, total_timeout: float = 35.0):
    deadline = time.monotonic() + total_timeout
    last_err = None
    for prov in providers:
        remaining = deadline - time.monotonic()
        if remaining <= 0: break
        timeout = min(remaining, getattr(prov, "timeout", 20.0))
        try:
            return await asyncio.wait_for(execute_fn(prov), timeout=timeout)
        except Exception as e:
            last_err = e
            continue
    # Trigger deterministic fallback
    return {"fallback": True, "error": str(last_err)}
```

#### 7. Break It & Debug It (Specific Failure Mode)
Not checking remaining time budget before attempting the second provider causes total request duration to exceed API gateway limits.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Loop-bounded failover improves service resilience without unbounded execution time.

#### 9. System Design & Scalability Angle
Provider failover and deterministic fallbacks improve resilience when individual AI providers fail.

#### 10. Senior Backend Interview Prep
**Q:** How do you implement timeout budgets in multi-provider failover chains?

**A:** Set a global deadline at request start; for each provider attempt, set timeout to min(remaining_budget, provider_timeout), and fall back if the budget is exhausted.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 38: Algorithmic Grounded Fallbacks & Hallucination-Risk Reduction [IMPORTANT]
- **Module:** Module 10: Multi-Provider AI Architecture
- **Prerequisites:** Story 27, Story 28, Story 36, Story 37
- **Leads To:** Story 39, Story 41
- **Code Truth Files:** `backend/app/services/ai_service.py`, `backend/app/services/comparison_service.py`, `backend/app/utils/price_parser.py`
- **Key Symbol(s):** `AIService.explain_property fallback / IndianPriceParser / rule_based_v1`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ai_endpoints.py`

#### 1. Why This Matters in Production
When all AI providers fail, users must still receive valid search results and property explanations.

#### 2. Core Engineering Concept
When AI providers fail, EstateMap can generate deterministic fallback text from verified backend facts. This reduces dependence on generative output and reduces unsupported-generation risk, but does not justify universal factuality or availability guarantees.

#### 3. How It Works Under the Hood
AIService constructs structured summaries using verified property attributes, POI distances, and commute metrics directly from database records.

#### 4. EstateMap Implementation Reality
app/services/ai_service.py implements deterministic rule-based generators (IndianPriceParser for search, template formatting for property/comparison explanations).

#### 5. Step-by-Step Code Flow
All AI providers fail or timeout -> AIService catches error -> Invokes rule-based fallback generator -> Assembles verified facts into string -> Returns response with fallback_used=True.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a deterministic property explanation fallback from verified context
def build_factual_explanation_fallback(prop_dict: dict, pois_dict: dict, commute_dict: dict | None) -> str:
    parts = [f"{prop_dict.get('bedrooms', '')} BHK {prop_dict.get('property_type', 'property')} in {prop_dict.get('locality', '')}, {prop_dict.get('city', '')} listed at ₹{prop_dict.get('price_inr', 0):,.0f} ({prop_dict.get('area_sqft', 0):,.0f} sqft)."]
    if pois_dict:
        items = [f"{k.replace('_', ' ')} ({v['nearest_distance_km']} km)" for k, v in pois_dict.items() if v.get('nearest_distance_km')]
        if items: parts.append(f"Nearby amenities include {', '.join(items[:2])}.")
    if commute_dict:
        parts.append(f"Estimated commute to {commute_dict['destination']} is {commute_dict['duration_minutes']} mins ({commute_dict['distance_km']} km).")
    return " ".join(parts)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Returning empty strings or HTTP 500 when AI fails degrades user experience when verified database facts are already available.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Deterministic fallbacks are fast and reliable, though less linguistically varied than LLM output.

#### 9. System Design & Scalability Angle
Grounded fallbacks ensure user interfaces remain functional and informative during upstream AI outages.

#### 10. Senior Backend Interview Prep
**Q:** How do you handle AI provider downtime in production?

**A:** Fall back to algorithmic rule-based summaries assembled directly from verified database facts, returning the result with a fallback_used flag.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 11: Ask-the-Map Conversational Orchestration

### Story 39: Natural Language Search Intent Extraction & Backend Authority Boundary [ESSENTIAL]
- **Module:** Module 11: Ask-the-Map Conversational Orchestration
- **Prerequisites:** Story 05, Story 22, Story 36, Story 37
- **Leads To:** Story 40, Story 41
- **Code Truth Files:** `backend/app/services/search_orchestrator.py`, `backend/app/schemas/conversational_search.py`
- **Key Symbol(s):** `SearchStatePatch / AskMapRequest / AskMapResponse / SearchOrchestrator`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ask_the_map.py`

#### 1. Why This Matters in Production
AI models must only extract proposed search intent; the backend retains complete authority over database query execution.

#### 2. Core Engineering Concept
Backend Authority Boundary: LLM output is strictly an untrusted patch proposal validated before application to canonical state.

#### 3. How It Works Under the Hood
AIService extracts SearchStatePatch from user query; SearchOrchestrator applies the patch, resolves coordinates, and executes queries.

#### 4. EstateMap Implementation Reality
app/schemas/conversational_search.py defines SearchStatePatch; app/services/search_orchestrator.py applies patches and executes PostGIS/ranking queries.

#### 5. Step-by-Step Code Flow
User submits text -> AIService extracts SearchStatePatch -> SearchOrchestrator.apply_patch updates state -> LocationResolver validates destination -> Executes queries.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Define the conversational SearchStatePatch schema and validation bounds
from pydantic import BaseModel, Field
from typing import Optional, List

class SearchStatePatch(BaseModel):
    locality: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=1, le=10)
    commute_destination: Optional[str] = None
    clear_fields: List[str] = Field(default_factory=list)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Allowing the LLM to directly generate SQL WHERE clauses exposes the database to prompt injection and syntax errors.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Structured intent parsing separates natural language comprehension from secure PostGIS SQL execution.

#### 9. System Design & Scalability Angle
Intent extraction with backend query execution provides AI flexibility while maintaining database security.

#### 10. Senior Backend Interview Prep
**Q:** How do you prevent prompt injection in conversational database search?

**A:** The LLM never writes SQL. It outputs a validated Pydantic patch schema which the backend applies to deterministic query builders.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 40: Stateless Conversational Search State Machine & State Reducer [ESSENTIAL]
- **Module:** Module 11: Ask-the-Map Conversational Orchestration
- **Prerequisites:** Story 39
- **Leads To:** Story 41, Story 42
- **Code Truth Files:** `backend/app/services/search_orchestrator.py`, `backend/app/schemas/conversational_search.py`
- **Key Symbol(s):** `ConversationalSearchState / SearchOrchestrator.apply_patch / AppliedPatchFeedback`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_search_orchestrator.py`

#### 1. Why This Matters in Production
Storing conversational search sessions in server memory breaks horizontal scaling across backend instances.

#### 2. Core Engineering Concept
Stateless state reducer: New State = Reducer(Old State, Patch), eliminating server-side session stickiness.

#### 3. How It Works Under the Hood
AskMapRequest carries ConversationalSearchState; SearchOrchestrator.apply_patch merges changes and returns updated state in AskMapResponse.

#### 4. EstateMap Implementation Reality
app/schemas/conversational_search.py defines ConversationalSearchState; app/services/search_orchestrator.py apply_patch executes state reduction.

#### 5. Step-by-Step Code Flow
POST /api/v1/search/ask-the-map {message, current_state} -> Orchestrator extracts patch -> apply_patch(current_state, patch) -> Returns (new_state, feedback, results).

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Build a pure functional state reducer for conversational search filters
from pydantic import BaseModel
from typing import Optional

class SearchState(BaseModel):
    locality: Optional[str] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None

def apply_state_patch(current: SearchState, patch_data: dict, clear_fields: list[str]) -> SearchState:
    state_dict = current.model_dump()
    for field in clear_fields:
        if field in state_dict: state_dict[field] = None
    for k, v in patch_data.items():
        if v is not None: state_dict[k] = v
    return SearchState(**state_dict)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Relying on in-memory server session dictionaries causes state loss when backend instances restart or requests hit different pods.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Client-held state simplifies backend scaling at the cost of slightly larger HTTP request payloads.

#### 9. System Design & Scalability Angle
Stateless state machines allow backend API replicas to process any conversation turn without sticky session routing.

#### 10. Senior Backend Interview Prep
**Q:** How do you design multi-turn conversational search without sticky sessions?

**A:** Keep the backend stateless: client passes current search state in the request, backend reducer applies patches and returns the new state.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 41: Multi-Turn Criteria Modification, History Merging & Orchestrated Search [ESSENTIAL]
- **Module:** Module 11: Ask-the-Map Conversational Orchestration
- **Prerequisites:** Story 39, Story 40
- **Leads To:** Story 42, Story 46
- **Code Truth Files:** `backend/app/services/search_orchestrator.py`, `backend/app/services/ranking_service.py`
- **Key Symbol(s):** `SearchOrchestrator.execute / SearchOrchestrator._build_geojson / AskMapResponse`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_ask_the_map.py`

#### 1. Why This Matters in Production
A conversational assistant must support iterative refinement (e.g. 'under 1.5 Cr', 'now make it 3 BHK') seamlessly.

#### 2. Core Engineering Concept
SearchOrchestrator coordinates Domain Services (LocationResolver -> PropertyRepository -> RankingService -> ComparisonService).

#### 3. How It Works Under the Hood
SearchOrchestrator.execute coordinates the full pipeline, resolving destinations, applying ranking, and building GeoJSON responses.

#### 4. EstateMap Implementation Reality
app/services/search_orchestrator.py coordinates multi-service execution, handles destination ambiguity, and formats conversational responses.

#### 5. Step-by-Step Code Flow
Turn 1: 'Find 3BHK in Whitefield' -> Sets bedrooms=3, locality=Whitefield -> Turn 2: 'Under 1.5 Cr' -> Merges max_price=15000000 -> Re-executes ranked search.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Coordinate multi-turn state merging with domain service execution
async def orchestrate_turn(orchestrator, current_state, patch, user_message):
    new_state, feedback, notes, unresolved = orchestrator.apply_patch(current_state, patch)
    if unresolved:
        return {"needs_clarification": True, "prompt": f"Could you clarify '{unresolved}'?", "state": current_state}
    # Execute database filter and ranking...
    return {"state": new_state, "feedback": feedback, "results": []}
```

#### 7. Break It & Debug It (Specific Failure Mode)
Overwriting previous valid filters when applying a partial patch (e.g. wiping out bedrooms when updating max_price) breaks conversational context.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Centralizing orchestration in a dedicated domain service keeps API route handlers clean and testable.

#### 9. System Design & Scalability Angle
Domain service orchestration decouples conversational logic from raw database storage and third-party APIs.

#### 10. Senior Backend Interview Prep
**Q:** Trace the end-to-end execution of a natural language search query.

**A:** 1. AI extracts patch; 2. Resolver checks destination; 3. State Reducer updates criteria; 4. PostGIS filters DB; 5. Ranking scores results; 6. Response returned.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 12: Backend ↔ Frontend API Integration

### Story 42: Backend ↔ Frontend API Integration Contract & Data Boundary [ESSENTIAL]
- **Module:** Module 12: Backend ↔ Frontend API Integration
- **Prerequisites:** Story 05, Story 14, Story 21, Story 33, Story 40
- **Leads To:** Story 46, Story 48
- **Code Truth Files:** `backend/app/api/v1/properties.py`, `backend/app/api/v1/search.py`, `backend/app/api/v1/auth.py`
- **Key Symbol(s):** `API Router definitions / OpenAPI schemas / CORS middleware`
- **Automated Test Command:** `docker compose exec backend pytest tests/integration/test_properties.py`

#### 1. Why This Matters in Production
Clear API contracts enable frontend and backend teams to develop, test, and mock independently without tight coupling.

#### 2. Core Engineering Concept
RESTful HTTP endpoints communicate strictly via standard JSON, GeoJSON, Authorization headers, and HTTP status codes.

#### 3. How It Works Under the Hood
FastAPI automatically generates OpenAPI docs (/docs) matching Pydantic schemas and error contracts.

#### 4. EstateMap Implementation Reality
backend/app/api/v1/ defines versioned routers exposing properties, search, commute, ranking, and auth endpoints.

#### 5. Step-by-Step Code Flow
Frontend makes fetch(url, {headers: {Authorization: Bearer token}}) -> FastAPI routes request -> Pydantic serializes response -> Frontend consumes JSON/GeoJSON.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Assemble versioned API routers under /api/v1
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")
# Mount sub-routers
# api_v1_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
# api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
# api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
```

#### 7. Break It & Debug It (Specific Failure Mode)
Changing a response field name in the backend without updating the Pydantic schema causes frontend runtime crashes.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Strict JSON/GeoJSON contracts decouple the Python backend from specific frontend frameworks.

#### 9. System Design & Scalability Angle
API contract stability guarantees backward compatibility for existing clients during backend upgrades.

#### 10. Senior Backend Interview Prep
**Q:** How do you design clean API integration boundaries?

**A:** Use versioned REST endpoints (/api/v1), explicit Pydantic response schemas, RFC 7807 error structures, and automated OpenAPI contract generation.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 13: Backend Testing & Debugging

### Story 43: Pytest Fundamentals, Async Fixtures & Dependency Overrides [ESSENTIAL]
- **Module:** Module 13: Backend Testing & Debugging
- **Prerequisites:** Story 01, Story 09, Story 10
- **Leads To:** Story 44
- **Code Truth Files:** `backend/tests/conftest.py`, `backend/tests/unit/test_health.py`
- **Key Symbol(s):** `pytest_asyncio / app.dependency_overrides / async_session fixture`
- **Automated Test Command:** `docker compose exec backend pytest tests/unit/test_health.py`

#### 1. Why This Matters in Production
Automated tests give developers confidence to refactor code without introducing silent regressions.

#### 2. Core Engineering Concept
Arrange-Act-Assert pattern with isolated test database sessions and mocked third-party dependencies.

#### 3. How It Works Under the Hood
backend/tests/conftest.py initializes test clients, database engines, and clean session fixtures.

#### 4. EstateMap Implementation Reality
tests/conftest.py defines async fixtures for db_session, async_client, test_settings, and mock_ai_provider.

#### 5. Step-by-Step Code Flow
pytest runs -> conftest initializes test database connection -> Injects async_session into test -> Test executes Arrange-Act-Assert -> Session rolled back.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Create an async test client fixture with dependency overrides in pytest
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

@pytest_asyncio.fixture
async def test_client(app: FastAPI):
    # Override dependencies for test isolation
    # app.dependency_overrides[get_current_user] = lambda: MockUser()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
```

#### 7. Break It & Debug It (Specific Failure Mode)
Sharing mutable state across tests without cleanup causes flaky tests that fail only when run in specific test execution orders.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Dependency overrides allow testing authenticated routes and repositories in complete isolation.

#### 9. System Design & Scalability Angle
Fast unit test suites running in seconds encourage continuous test-driven development (TDD).

#### 10. Senior Backend Interview Prep
**Q:** How do you test authenticated FastAPI routes without making real login calls?

**A:** Use app.dependency_overrides[get_current_user] = lambda: mock_user in your test fixture to inject a mock authenticated user directly.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 44: Integration Testing of Repositories, Redis, External APIs & Error Paths [IMPORTANT]
- **Module:** Module 13: Backend Testing & Debugging
- **Prerequisites:** Story 43
- **Leads To:** Story 46
- **Code Truth Files:** `backend/tests/integration/test_properties.py`, `backend/tests/integration/test_rate_limiting.py`
- **Key Symbol(s):** `pytest integration test suites (288 tests)`
- **Automated Test Command:** `docker compose exec backend pytest`

#### 1. Why This Matters in Production
Unit tests with mocks cannot catch SQL syntax errors, GiST index misconfigurations, or Redis connection bugs.

#### 2. Core Engineering Concept
Integration tests run against real containerized services (Postgres, Redis) to verify end-to-end component interaction.

#### 3. How It Works Under the Hood
tests/integration/ covers auth, properties, spatial search, commute routing, ranking, AI failover, and rate limiting.

#### 4. EstateMap Implementation Reality
tests/integration/ contains 288 comprehensive integration tests verifying API workflows against real Postgres and Redis.

#### 5. Step-by-Step Code Flow
docker compose exec backend pytest -> Pytest runs 288 tests -> Verifies real DB queries, Redis caching hits/misses, and AI failovers -> 100% pass.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Write an integration test verifying spatial property creation and radius search
import pytest

@pytest.mark.asyncio
async def test_create_and_query_radius(test_client, auth_headers):
    payload = {"title": "Test Listing", "price": 9500000, "bedrooms": 3, "latitude": 12.9716, "longitude": 77.5946}
    create_res = await test_client.post("/api/v1/properties", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    
    search_res = await test_client.get("/api/v1/properties/radius?lat=12.9716&lon=77.5946&radius_m=1000")
    assert search_res.status_code == 200
    assert any(p["id"] == create_res.json()["id"] for p in search_res.json()["items"])
```

#### 7. Break It & Debug It (Specific Failure Mode)
Testing only happy paths leaves edge cases (e.g. database disconnect, invalid token format) untested for production.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Integration tests are slower than unit tests but provide the highest fidelity proof of system correctness.

#### 9. System Design & Scalability Angle
Automated test suites in CI/CD block regressions from reaching staging and production environments.

#### 10. Senior Backend Interview Prep
**Q:** What is the difference between unit and integration tests in a FastAPI project?

**A:** Unit tests test isolated functions with mocked dependencies; integration tests verify API endpoints against real databases and Redis.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 14: Docker for Backend Developers

### Story 45: Multi-Container Backend Orchestration with Docker Compose [IMPORTANT]
- **Module:** Module 14: Docker for Backend Developers
- **Prerequisites:** Story 01, Story 09, Story 29
- **Leads To:** Story 46
- **Code Truth Files:** `docker-compose.yml`, `backend/Dockerfile`, `.env`
- **Key Symbol(s):** `services: postgres-postgis, redis, backend / healthcheck`
- **Automated Test Command:** `docker compose ps`

#### 1. Why This Matters in Production
Containerization eliminates 'works on my machine' issues by providing identical local and production runtime environments.

#### 2. Core Engineering Concept
Docker Compose manages container networks, port bindings, persistent volumes, environment files, and healthcheck dependencies.

#### 3. How It Works Under the Hood
docker-compose.yml defines services with depends_on condition: service_healthy ensuring DB is ready before backend boots.

#### 4. EstateMap Implementation Reality
docker-compose.yml coordinates postgres-postgis, redis, and backend containers on a shared bridge network.

#### 5. Step-by-Step Code Flow
docker compose up -> Postgres & Redis boot -> Healthchecks pass -> Backend container boots -> Alembic runs -> FastAPI starts serving traffic.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Write a docker-compose.yml service block with PostgreSQL healthcheck
# services:
#   postgres:
#     image: postgis/postgis:16-3.4
#     environment:
#       POSTGRES_DB: estatemap_db
#       POSTGRES_USER: estatemap
#       POSTGRES_PASSWORD: password
#     healthcheck:
#       test: ["CMD-SHELL", "pg_isready -U estatemap -d estatemap_db"]
#       interval: 5s
#       timeout: 5s
#       retries: 5
```

#### 7. Break It & Debug It (Specific Failure Mode)
Backend starting before PostgreSQL is healthy causes initial connection attempts to fail and crash the container.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Docker Compose provides lightweight local orchestration without the operational complexity of Kubernetes.

#### 9. System Design & Scalability Angle
Standardized container definitions allow any developer to clone the repo and run the full stack with a single docker compose up command.

#### 10. Senior Backend Interview Prep
**Q:** Why use service health checks in docker-compose.yml?

**A:** To ensure dependent services (like PostgreSQL) are fully initialized and ready to accept connections before the backend starts, preventing startup crashes.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

## Module 15: EstateMap System Design & Architecture Synthesis

### Story 46: EstateMap Modular Monolith Architecture & Request Lifecycle Synthesis [ESSENTIAL]
- **Module:** Module 15: EstateMap System Design & Architecture Synthesis
- **Prerequisites:** Story 04, Story 10, Story 15, Story 21, Story 28, Story 31, Story 34, Story 38, Story 41, Story 42, Story 44, Story 45
- **Leads To:** Story 47, Story 48
- **Code Truth Files:** `backend/app/main.py`, `backend/app/services/search_orchestrator.py`, `docs/mastery/ARCHITECTURE.md`
- **Key Symbol(s):** `Request Lifecycle: Middleware -> Router -> Dependency -> Service -> Repository -> PostGIS/Redis -> Pydantic Response`
- **Automated Test Command:** `docker compose exec backend pytest`

#### 1. Why This Matters in Production
Senior engineers must be able to trace and defend the end-to-end lifecycle of any incoming HTTP request across all system layers.

#### 2. Core Engineering Concept
Clean layered architecture strictly isolates Presentation (FastAPI), Domain (Services), Data Access (Repositories), and Infrastructure (Postgres/Redis).

#### 3. How It Works Under the Hood
Every request traverses RequestID -> CORS -> RateLimiter -> Router -> get_db -> Service Layer -> Repository -> DB/Redis -> Pydantic serialization.

#### 4. EstateMap Implementation Reality
Complete repository codebase adheres to this layered architecture with explicit boundary isolation and dependency injection.

#### 5. Step-by-Step Code Flow
1. Client sends request -> 2. RequestID & CORS middleware -> 3. RateLimiter evaluates ZSET -> 4. Router parses schema -> 5. Service orchestrates business logic -> 6. Repository executes PostGIS query -> 7. Pydantic serializes response.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Map the complete 7-layer request pipeline in an architectural blueprint
# Layer 1: ASGI Server (Uvicorn)
# Layer 2: Middleware Pipeline (RequestID, CORS)
# Layer 3: Security & Rate Limiting (RateLimiter dependency, JWT auth)
# Layer 4: API Presentation (FastAPI Router + Pydantic validation)
# Layer 5: Domain Services (SearchOrchestrator, RankingService, CommuteService)
# Layer 6: Data Access (PropertyRepository, POIRepository via AsyncSession)
# Layer 7: Infrastructure Storage (PostgreSQL 16 + PostGIS, Redis 7)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Importing database session objects directly in route handlers bypassing the service layer creates architectural coupling and makes testing difficult.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Modular Monolith eliminates network serialization hops while maintaining clean domain module boundaries.

#### 9. System Design & Scalability Angle
Layered modular architecture allows future extraction of isolated high-throughput services if organizational or scaling requirements dictate.

#### 10. Senior Backend Interview Prep
**Q:** Walk me through the exact request lifecycle of a conversational search query in your system.

**A:** 1. RequestID middleware tags request; 2. Rate limiter checks ZSET; 3. Router validates schema; 4. AI Service extracts intent patch; 5. Resolver checks destination; 6. State Reducer updates state; 7. PostGIS filters candidates; 8. Ranking scores results; 9. GeoJSON response returned.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 47: 15 Core Architectural Tradeoffs & Engineering Justifications [ESSENTIAL]
- **Module:** Module 15: EstateMap System Design & Architecture Synthesis
- **Prerequisites:** Story 46
- **Leads To:** Story 48
- **Code Truth Files:** `docs/mastery/SYSTEM_DESIGN.md`, `backend/app/core/config.py`
- **Key Symbol(s):** `15 Architectural Decisions: Monolith vs Microservices, PostgreSQL+PostGIS vs Mongo, Redis ZSET vs Token Bucket, etc.`
- **Automated Test Command:** `python docs/mastery/generator/verify_backend_curriculum.py`

#### 1. Why This Matters in Production
Senior engineers are evaluated on their ability to justify architectural tradeoffs with concrete engineering reasoning rather than dogma.

#### 2. Core Engineering Concept
Engineering is the discipline of tradeoffs: every architectural choice trades simplicity, consistency, latency, cost, and operational overhead.

#### 3. How It Works Under the Hood
SYSTEM_DESIGN.md documents 15 core architectural decisions with What Was Chosen, What Was Rejected, and Why.

#### 4. EstateMap Implementation Reality
EstateMap implements Modular Monolith, PostgreSQL+PostGIS, Asyncpg, Redis Cache-Aside, Redis ZSET rate limiting, MCDA deterministic ranking, and multi-provider AI.

#### 5. Step-by-Step Code Flow
Architecture Review -> Evaluate functional requirements -> Analyze operational cost & latency -> Select technology -> Document rejected alternatives and tradeoffs.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Formulate a structured Tradeoff Defense matrix for technical interviews
# Format: [Decision] | [Chosen Tech] | [Rejected Alternative] | [Engineering Justification]
# 1. Architecture: Modular Monolith vs Microservices (Zero network RPC overhead, single deployment)
# 2. Database: PostgreSQL+PostGIS vs MongoDB (Native GiST spatial indexing, ACID referential integrity)
# 3. Driver: Asyncpg vs Psycopg2 (Non-blocking asyncio I/O, event loop concurrency)
# 4. Caching: Redis Cache-Aside vs In-Memory Dict (Shared across worker processes, TTL eviction)
# 5. Ranking: 6-Factor MCDA vs LLM-based (Deterministic, reproducible, fast, zero token cost)
```

#### 7. Break It & Debug It (Specific Failure Mode)
Choosing microservices or distributed event brokers prematurely for a single-developer or early-stage system introduces massive operational overhead without business benefit.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Every technology decision in EstateMap is defended with concrete latency, consistency, and operational complexity rationale.

#### 9. System Design & Scalability Angle
System design maturity is demonstrated by selecting the simplest architecture that fulfills all functional and non-functional requirements.

#### 10. Senior Backend Interview Prep
**Q:** Why did you choose PostgreSQL with PostGIS over MongoDB with Geospatial indexes?

**A:** PostgreSQL provides true ACID transactions, relational foreign key constraints for listings/owners, and PostGIS offers advanced geodesic functions (ST_DWithin, ST_MakeEnvelope) backed by GiST indexing.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

### Story 48: Scaling EstateMap from 10k to 1M Users (Evolutionary Roadmaps) [IMPORTANT]
- **Module:** Module 15: EstateMap System Design & Architecture Synthesis
- **Prerequisites:** Story 46, Story 47
- **Leads To:** Final Synthesis
- **Code Truth Files:** `docs/mastery/SYSTEM_DESIGN.md`
- **Key Symbol(s):** `Evolutionary Scaling: Stage 1 (Single Node) -> Stage 2 (Read Replicas + Redis Cache) -> Stage 3 (Async Task Queues + Sharding)`
- **Automated Test Command:** `python docs/mastery/generator/verify_backend_curriculum.py`

#### 1. Why This Matters in Production
Demonstrate system design maturity by mapping how an architecture evolves systematically as traffic and data volumes grow.

#### 2. Core Engineering Concept
Evolutionary Architecture: Scale bottlenecks incrementally based on measured constraints (CPU, DB I/O, Cache memory, Network).

#### 3. How It Works Under the Hood
SYSTEM_DESIGN.md details Stage 1 (10k DAU), Stage 2 (100k DAU with Read Replicas & Connection Pooling), and Stage 3 (1M DAU with Geo-partitioning and CDN caching).

#### 4. EstateMap Implementation Reality
EstateMap current architecture represents Stage 1/2 ready foundations with stateless workers and async database access.

#### 5. Step-by-Step Code Flow
Traffic Growth -> Identify bottleneck (DB Read I/O) -> Add Read Replicas -> Add Redis Cache -> Add Async Task Queue -> Add Geographic Partitioning.

#### 6. Build It Yourself (Topic-Specific Exercise)
```python
# Topic Build: Design a 3-Stage Evolutionary Scaling Blueprint
# Stage 1 (10k DAU): Single PostgreSQL container, Single Redis, 2 Uvicorn ASGI workers.
# Stage 2 (100k DAU): 1 Primary DB (writes) + 2 Read Replicas (spatial queries), PgBouncer connection pooler, Redis Cluster.
# Stage 3 (1M DAU): Geo-partitioned database clusters by metropolitan region, CDN edge tile caching, Celery/RabbitMQ async commute precomputation.
```

#### 7. Break It & Debug It (Specific Failure Mode)
Attempting to implement geographic sharding and Kafka brokers before reaching traffic scale creates accidental complexity and slows development velocity.

#### 8. Architectural Tradeoffs & Rejected Alternatives
Scale incrementally when metrics demand it rather than over-engineering upfront.

#### 9. System Design & Scalability Angle
Horizontal scaling of stateless backend containers combined with read replicas and caching supports orders of magnitude traffic growth.

#### 10. Senior Backend Interview Prep
**Q:** How would you scale this real estate backend from 10,000 to 1,000,000 daily active users?

**A:** 1. Deploy stateless ASGI workers behind load balancers; 2. Add PostgreSQL read replicas with PgBouncer; 3. Cache frequent viewport queries in Redis; 4. Precompute POI and commute matrices asynchronously via task queues; 5. Partition databases by metropolitan city.

#### 11. Self-Assessment & Mastery Check
- [ ] I can explain this mechanism from memory without looking at notes.
- [ ] I can implement this component in a clean Python file from scratch.
- [ ] I can diagnose and fix the specific failure mode described above.

---

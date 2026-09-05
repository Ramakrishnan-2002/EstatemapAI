# -*- coding: utf-8 -*-
"""
EstateMap AI — Reconciled Backend Mastery Curriculum Compiler
Compiles all 48 backend stories across 15 modules into 9 canonical documents with 100% code truth.
"""
import os
import sys
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MASTERY_DIR = os.path.join(BASE_DIR, "docs", "mastery")

STATUS_ESSENTIAL = "[ESSENTIAL]"
STATUS_IMPORTANT = "[IMPORTANT]"

# 48 Reconciled Backend Stories with topic-specific debugging, build tasks, and verified symbols
STORIES = [
    # Module 01: Python & FastAPI Foundations (1-4)
    {
        "id": 1, "title": "Python Project Layout, Clean Modular Monolith & ASGI App Factory",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [], "leads_to": [2, 3, 4],
        "files": ["backend/app/main.py", "backend/pyproject.toml", "backend/app/core/config.py"],
        "symbol": "app.main:app / create_application", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Clean separation of concerns isolates HTTP serialization from domain logic and prevents circular imports across services.",
        "concept": "ASGI (Asynchronous Server Gateway Interface) event loop request dispatching vs WSGI synchronous execution.",
        "how_it_works": "Uvicorn runs ASGI event loops. FastAPI initializes middleware (CORS, RequestID) and mounts versioned routers (/api/v1).",
        "estatemap": "backend/app/main.py defines the FastAPI application factory, initializes middleware pipelines, mounts /api/v1 routers, and configures lifespan handlers.",
        "code_flow": "Client Request -> Uvicorn ASGI Server -> Middleware Stack (RequestID, CORS) -> FastAPI Router (/api/v1/properties) -> Dependency Injection (get_db) -> Service Layer -> Response.",
        "build_snippet": """# Topic Build: Implement a minimal ASGI app factory with CORS and lifespan
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

app = build_api()""",
        "break_it": "Circular import between router and service (e.g., router imports service instance that imports router module) causes Python to fail at boot with an ImportError.",
        "tradeoffs": "Modular Monolith was chosen over microservices to eliminate distributed network latency, serialization overhead, and multi-repo operational complexity.",
        "system_design": "Stateless ASGI workers scale horizontally behind an NGINX / Cloud load balancer with zero shared in-process memory.",
        "interview_q": "Why use FastAPI over traditional frameworks like Django or Flask for high-performance APIs?",
        "interview_a": "FastAPI is built natively on Starlette and asyncio, allowing non-blocking concurrent I/O on a single thread event loop. It integrates Pydantic for fast schema validation and automatic OpenAPI generation."
    },
    {
        "id": 2, "title": "Async Event Loop, Non-Blocking Concurrency & Lifespan Management",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1], "leads_to": [8, 9, 29],
        "files": ["backend/app/main.py", "backend/app/cache/redis.py", "backend/app/db/session.py"],
        "symbol": "app.main:lifespan / asynccontextmanager", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Proper lifecycle management ensures database pools and Redis clients are initialized before serving traffic and closed on SIGTERM.",
        "concept": "Python asyncio event loop cooperative multitasking: I/O operations yield control with await, allowing concurrent requests per worker.",
        "how_it_works": "lifespan context manager runs startup code before yield and teardown code after yield on server shutdown.",
        "estatemap": "app/main.py lifespan initializes Redis connection pools, verifies PostgreSQL connectivity, runs seed_all(), and tears down pools on exit.",
        "code_flow": "Process Start -> Uvicorn triggers lifespan -> init_redis() -> init_db() -> seed_all() -> yield (Serve Requests) -> close_redis() -> dispose_engine() -> Process Exit.",
        "build_snippet": """# Topic Build: Create an async lifespan manager that initializes and tears down mock DB & Redis pools
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

app = FastAPI(lifespan=lifespan)""",
        "break_it": "Omitting the yield statement inside the @asynccontextmanager causes FastAPI startup to hang indefinitely, failing healthchecks.",
        "tradeoffs": "Lifespan context managers replace deprecated startup/shutdown events with type-safe exception handling and clean context scopes.",
        "system_design": "Graceful shutdown allows in-flight database transactions and HTTP requests to complete before closing sockets during rolling deployments.",
        "interview_q": "How does Python asyncio handle thousands of concurrent I/O-bound requests on a single CPU core?",
        "interview_a": "When a coroutine awaits network I/O (database query or HTTP call), it yields control to the event loop, which immediately schedules other ready coroutines without thread context-switching overhead."
    },
    {
        "id": 3, "title": "Type-Safe Environment Configuration with Pydantic-Settings",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1], "leads_to": [4, 8, 13, 29, 35],
        "files": ["backend/app/core/config.py", ".env.example"],
        "symbol": "app.core.config:Settings / settings", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Failing fast during boot when environment variables (DB URLs, API keys, TTLs) are invalid prevents runtime 500 errors in production.",
        "concept": "Strict schema parsing transforms raw environment string values into typed integers, booleans, and DSN objects with default fallbacks.",
        "how_it_works": "Pydantic BaseSettings reads .env files, coerces data types, and validates constraints (e.g. rate limits > 0, valid log levels).",
        "estatemap": "app/core/config.py defines Settings with database URLs, Redis parameters, cache TTLs, rate limits, AI provider credentials, and exports a singleton settings object.",
        "code_flow": "App Start -> settings instantiated -> Reads os.environ & .env -> Pydantic validates types -> Singleton imported across modules.",
        "build_snippet": """# Topic Build: Build a typed configuration class with cache TTLs and validation
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AppConfig(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_MAP_TTL_SECONDS: int = Field(default=120, gt=0)
    CACHE_RANKING_TTL_SECONDS: int = Field(default=300, gt=0)
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

config = AppConfig()""",
        "break_it": "Passing an invalid integer string like CACHE_MAP_TTL_SECONDS='two_minutes' causes Pydantic to raise a ValidationError and abort startup immediately.",
        "tradeoffs": "Pydantic-Settings provides compile-time typing and automated validation over fragile, untyped os.environ.get() dictionaries.",
        "system_design": "12-Factor App config separation allows the exact same Docker image to run across local, staging, and production environments with different .env files.",
        "interview_q": "Why is Pydantic-Settings preferred over os.getenv in production backend systems?",
        "interview_a": "Pydantic-Settings automatically parses and validates types, enforces mandatory fields at startup, prevents type-coercion bugs, and supports hierarchical config injection."
    },
    {
        "id": 4, "title": "RFC 7807 Centralized Error Handling & Structured Request ID Logging",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1, 3], "leads_to": [5, 14, 32],
        "files": ["backend/app/core/exceptions.py", "backend/app/core/exception_handlers.py", "backend/app/core/middleware.py"],
        "symbol": "AppException / app_exception_handler / RequestIDMiddleware", "test_cmd": "docker compose exec backend pytest tests/unit/test_exceptions.py",
        "why": "Consistent error contracts prevent leaking raw database stack traces and enable correlated log debugging.",
        "concept": "RFC 7807 Problem Details for HTTP APIs standardizes error JSON responses (type, title, status, detail, instance).",
        "how_it_works": "Custom exception classes inherit from AppException. FastAPI exception handlers intercept exceptions and format structured JSON responses.",
        "estatemap": "app/core/exceptions.py defines EntityNotFoundException, RateLimitExceededException, ValidationException. Middleware injects X-Request-ID into context and response headers.",
        "code_flow": "Incoming Request -> RequestIDMiddleware generates/extracts X-Request-ID -> Route raises AppException -> Exception Handler formats RFC 7807 JSON -> Response returned with X-Request-ID header.",
        "build_snippet": """# Topic Build: Create an RFC 7807 base exception and exception handler
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
    )""",
        "break_it": "Letting raw SQLAlchemy exceptions bubble up unhandled returns HTTP 500 containing internal database table names and connection parameters to the client.",
        "tradeoffs": "RFC 7807 standardized schema over custom error dicts allows API consumers to handle validation errors and business failures uniformly.",
        "system_design": "Propagating X-Request-ID through logs and response headers enables engineers to trace a single request's execution across distributed components with log queries.",
        "interview_q": "How do you handle exceptions and error responses cleanly across a large FastAPI application?",
        "interview_a": "Define a domain exception hierarchy inheriting from a base AppException. Register centralized FastAPI exception handlers that format errors according to RFC 7807 Problem Details."
    },

    # Module 02: REST API Design & Validation (5-7)
    {
        "id": 5, "title": "Request & Response Schema Validation with Pydantic v2",
        "module_id": 2, "module_name": "Module 02: REST API Design & Validation", "importance": STATUS_ESSENTIAL,
        "prereqs": [1, 3, 4], "leads_to": [6, 7, 10, 21, 36],
        "files": ["backend/app/schemas/property.py", "backend/app/schemas/search.py", "backend/app/schemas/auth.py"],
        "symbol": "PropertyResponse / PropertyCreate / PropertyFilterParams", "test_cmd": "docker compose exec backend pytest tests/unit/test_property_schemas.py",
        "why": "Input validation at the API boundary protects domain services and SQL queries from malformed payloads.",
        "concept": "Pydantic v2 core delivers high-throughput serialization and strict schema validation.",
        "how_it_works": "app/schemas/ defines strict BaseModel schemas with Field constraints (e.g. price > 0, latitude [-90, 90]).",
        "estatemap": "app/schemas/ defines PropertyCreate, PropertyUpdate, PropertyResponse models with exact typing and field constraints.",
        "code_flow": "HTTP Request Payload -> FastAPI body parser -> Pydantic model validation -> Clean typed object passed to endpoint -> Return schema serializes output.",
        "build_snippet": """# Topic Build: Create a Pydantic v2 property create schema with coordinate bounds
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
        return v.strip()""",
        "break_it": "Passing latitude > 90 or negative prices returns HTTP 422 Unprocessable Entity with exact error field locations in the response body.",
        "tradeoffs": "Pydantic schemas decouple database model structures from public API contracts, preventing over-fetching and unintended internal column exposure.",
        "system_design": "Validated request schemas serve as the contract for OpenAPI documentation and protect internal services from malformed inputs.",
        "interview_q": "What is the difference between ORM models and Pydantic schemas?",
        "interview_a": "ORM models map to database tables and manage persistence; Pydantic schemas enforce API boundary validation, type coercion, and serialization."
    },
    {
        "id": 6, "title": "Deterministic Pagination, Sorting & Query Parameter Contracts",
        "module_id": 2, "module_name": "Module 02: REST API Design & Validation", "importance": STATUS_ESSENTIAL,
        "prereqs": [5], "leads_to": [7, 10],
        "files": ["backend/app/utils/pagination.py", "backend/app/repositories/property_repository.py"],
        "symbol": "PropertyRepository.list / PropertyRepository._apply_sorting", "test_cmd": "docker compose exec backend pytest tests/integration/test_properties.py",
        "why": "Non-deterministic sorting causes duplicate or missing items across paginated API requests during concurrent database writes.",
        "concept": "Stable sorting requires appending a unique primary key tie-breaker to all ORDER BY clauses.",
        "how_it_works": "PropertyRepository._apply_sorting adds Property.id.desc() as the final sorting clause.",
        "estatemap": "app/utils/pagination.py and PropertyRepository apply LIMIT, OFFSET, and compound ORDER BY clauses with primary key tie-breakers.",
        "code_flow": "GET /api/v1/properties?limit=20&offset=40 -> Query params parsed -> Repository appends ORDER BY price ASC, id DESC -> Database executes indexed fetch -> Paginated list returned.",
        "build_snippet": """# Topic Build: Build a reusable query sorter with primary key tie-breaking
from sqlalchemy import select, asc, desc

def apply_deterministic_sorting(stmt, model_cls, sort_by: str, sort_order: str = "asc"):
    col = getattr(model_cls, sort_by, model_cls.created_at)
    direction = asc if sort_order.lower() == "asc" else desc
    # Primary sort column + mandatory primary key tie-breaker
    return stmt.order_by(direction(col), desc(model_cls.id))""",
        "break_it": "Sorting by price alone causes rows with identical price values to shift position between page 1 and page 2, returning duplicate listings to users.",
        "tradeoffs": "Offset pagination is simple and flexible for moderate datasets; Keyset/Cursor pagination is reserved for large unbounded tables.",
        "system_design": "Pagination bounds database memory consumption and network payload sizes, preventing out-of-memory errors on large tables.",
        "interview_q": "Why is tie-breaking necessary in database pagination?",
        "interview_a": "Without unique tie-breaking, database query planners return rows with identical sort values in arbitrary physical disk order, creating duplicates or missing items across pages."
    },
    {
        "id": 7, "title": "Composable Multi-Facet Filter Query Generation",
        "module_id": 2, "module_name": "Module 02: REST API Design & Validation", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 6], "leads_to": [10, 18],
        "files": ["backend/app/repositories/property_repository.py", "backend/app/schemas/property.py"],
        "symbol": "PropertyRepository._apply_common_filters / PropertyFilterParams", "test_cmd": "docker compose exec backend pytest tests/integration/test_filter_equivalence.py",
        "why": "Hardcoded SQL strings lead to SQL injection vulnerabilities and unmaintainable conditional branching.",
        "concept": "Composable AST query building appends binary filter expressions to the query object only when parameters are present.",
        "how_it_works": "PropertyRepository._apply_common_filters checks filter params and chains .where() conditions cleanly.",
        "estatemap": "PropertyRepository encapsulates filter generation, applying min_price, max_price, bedrooms, property_type, and city conditions.",
        "code_flow": "FilterParams received -> Repository initializes select(Property) -> _apply_common_filters chains active conditions -> Query executed via async session.",
        "build_snippet": """# Topic Build: Implement a composable query filter builder using SQLAlchemy select
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
    return stmt""",
        "break_it": "Chaining filters without matching index coverage on large tables results in full sequential scans and elevated query execution time.",
        "tradeoffs": "Dynamic SQLAlchemy query compilation ensures parameterized safety while supporting arbitrary filter combinations.",
        "system_design": "Composite indexes should align with the most frequent multi-facet filter combinations (e.g. city + property_type + price).",
        "interview_q": "How do you prevent SQL injection in complex dynamic search queries?",
        "interview_a": "Use parameterized query builders like SQLAlchemy where values are passed out-of-band and never concatenated directly as raw SQL strings."
    },

    # Module 03: PostgreSQL & SQLAlchemy 2.0 Async (8-12)
    {
        "id": 8, "title": "Relational Data Modeling, Foreign Keys & Schema Integrity",
        "module_id": 3, "module_name": "Module 03: PostgreSQL & SQLAlchemy 2.0 Async", "importance": STATUS_ESSENTIAL,
        "prereqs": [1, 3], "leads_to": [9, 10, 11, 16],
        "files": ["backend/app/models/property.py", "backend/app/models/user.py", "backend/app/models/poi.py"],
        "symbol": "Property / User / PointOfInterest / Base", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Database constraints provide the final defense line for data integrity even if application bugs occur.",
        "concept": "Relational normalization (3NF) eliminates data redundancy while foreign keys enforce referential integrity.",
        "how_it_works": "app/models/ defines declarative tables with mapped_column, CheckConstraint('price > 0'), and foreign keys.",
        "estatemap": "app/models/property.py, user.py, and poi.py define declarative SQLAlchemy 2.0 models with relationships, cascades, and constraints.",
        "code_flow": "Domain Entity Definition -> Base declarative metadata -> Table definition with foreign keys and check constraints -> Database schema synchronization.",
        "build_snippet": """# Topic Build: Define declarative SQLAlchemy 2.0 models with FK cascades and check constraints
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
    __table_args__ = (CheckConstraint("price > 0", name="chk_price_positive"),)""",
        "break_it": "Inserting a record with price <= 0 triggers a database IntegrityError due to the check constraint, rolling back the transaction.",
        "tradeoffs": "Relational PostgreSQL was chosen over document stores to guarantee strict transactional ACID consistency for real estate listings.",
        "system_design": "Normalized tables prevent update anomalies; foreign keys and check constraints guarantee data consistency at the storage layer.",
        "interview_q": "Why enforce check constraints at the database level when Pydantic already validates inputs?",
        "interview_a": "Defense-in-depth: database constraints protect against direct database updates, migrations, asynchronous background jobs, and multi-service writes."
    },
    {
        "id": 9, "title": "SQLAlchemy 2.0 Async Session Lifecycles & Asyncpg Connection Pooling",
        "module_id": 3, "module_name": "Module 03: PostgreSQL & SQLAlchemy 2.0 Async", "importance": STATUS_ESSENTIAL,
        "prereqs": [2, 8], "leads_to": [10, 13, 18],
        "files": ["backend/app/db/session.py", "backend/app/db/base.py"],
        "symbol": "async_session_factory / create_async_engine / get_db", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Synchronous database drivers block the Python asyncio event loop during I/O operations.",
        "concept": "Async database access avoids blocking the asyncio event loop during PostgreSQL network I/O and allows concurrent requests to make progress while queries are waiting on I/O.",
        "how_it_works": "app/db/session.py initializes create_async_engine and yields AsyncSession via FastAPI Depends(get_db).",
        "estatemap": "app/db/session.py configures connection pool parameters (pool_size=20, max_overflow=10, pool_recycle, pool_pre_ping) and get_db dependency.",
        "code_flow": "HTTP Request -> FastAPI get_db dependency acquires session from pool -> Route executes queries -> Request ends -> get_db commits/closes session back to pool.",
        "build_snippet": """# Topic Build: Configure an async database engine, sessionmaker, and FastAPI get_db generator
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
            raise""",
        "break_it": "Failing to commit or rollback an unclosed session leaves transactions open, exhausting pool connections and timing out subsequent requests.",
        "tradeoffs": "Asyncpg handles non-blocking socket I/O natively, keeping the single-thread event loop responsive across concurrent queries.",
        "system_design": "Connection pooling reuses persistent TCP connections, avoiding expensive TLS/TCP handshakes on every incoming HTTP request.",
        "interview_q": "What happens if an async endpoint calls a synchronous blocking database driver?",
        "interview_a": "It blocks the single asyncio event loop thread, preventing all concurrent requests from making progress until the query finishes."
    },
    {
        "id": 10, "title": "Repository Pattern & Async Database Encapsulation",
        "module_id": 3, "module_name": "Module 03: PostgreSQL & SQLAlchemy 2.0 Async", "importance": STATUS_ESSENTIAL,
        "prereqs": [8, 9], "leads_to": [18, 22, 25],
        "files": ["backend/app/repositories/property_repository.py", "backend/app/repositories/user_repository.py"],
        "symbol": "PropertyRepository / UserRepository", "test_cmd": "docker compose exec backend pytest tests/integration/test_properties.py",
        "why": "Direct SQL queries inside API route handlers make code untestable and violate single-responsibility principles.",
        "concept": "Repository pattern acts as an in-memory collection interface over persistent storage.",
        "how_it_works": "PropertyRepository receives AsyncSession and exposes get_by_id, list, search_radius, and search_bbox methods.",
        "estatemap": "app/repositories/property_repository.py encapsulates all SQL operations for properties, abstracting session execution from service logic.",
        "code_flow": "API Router calls PropertyService -> PropertyService calls PropertyRepository.get_by_id(session, id) -> Repository executes select() -> Returns entity.",
        "build_snippet": """# Topic Build: Implement an async property repository with get_by_id and list operations
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
        return result.scalars().all()""",
        "break_it": "Accessing unloaded async relationships outside the session context raises a MissingGreenlet exception.",
        "tradeoffs": "Repository pattern introduces minor boilerplate but enables straightforward unit testing and centralized query performance optimization.",
        "system_design": "Data access layer encapsulation allows swapping storage engines or optimizing queries without altering business service logic.",
        "interview_q": "Why use the Repository pattern with an ORM?",
        "interview_a": "It isolates data access logic, making unit testing simpler with mocks and query optimization centralized in one file."
    },
    {
        "id": 11, "title": "Schema Migrations with Alembic & Reproducible Database Versioning",
        "module_id": 3, "module_name": "Module 03: PostgreSQL & SQLAlchemy 2.0 Async", "importance": STATUS_IMPORTANT,
        "prereqs": [8, 10], "leads_to": [12, 16],
        "files": ["backend/alembic/env.py", "backend/alembic/versions/2026_09_04_0001-0001_initial_postgis.py"],
        "symbol": "run_migrations_online / Alembic Revisions 0001-0004", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Manual SQL alter scripts lead to environment drift, unrepeatable deployments, and broken production schemas.",
        "concept": "Linear migration DAG tracks applied revisions in the alembic_version table.",
        "how_it_works": "backend/alembic/ manages 4 sequential revisions: PostGIS extension, users table, properties/amenities, and POIs.",
        "estatemap": "backend/alembic/env.py imports Base metadata, configures async connection, and applies versioned migration scripts.",
        "code_flow": "Developer runs alembic upgrade head -> Alembic checks alembic_version table -> Executes missing revision scripts in transaction -> Updates alembic_version.",
        "build_snippet": """# Topic Build: Write an Alembic migration script creating a table and GiST index
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
    op.drop_table('listings')""",
        "break_it": "Adding a non-nullable column without a server default to an existing populated table causes the migration to fail with a NotNullViolation.",
        "tradeoffs": "Alembic integrates directly with SQLAlchemy declarative metadata for automated schema diff detection.",
        "system_design": "Database schema versioning enables reproducible test environments and safe rollback procedures.",
        "interview_q": "How do you handle database migrations with zero downtime?",
        "interview_a": "Use the Expand/Contract pattern: add new nullable columns first, deploy updated code, backfill data, and finally enforce constraints in a subsequent migration."
    },
    {
        "id": 12, "title": "Deterministic Database Seeding & Fixture Management",
        "module_id": 3, "module_name": "Module 03: PostgreSQL & SQLAlchemy 2.0 Async", "importance": STATUS_IMPORTANT,
        "prereqs": [8, 10, 11], "leads_to": [18, 22],
        "files": ["backend/app/db/seed_all.py", "backend/app/db/seed_properties.py", "backend/app/db/seed_pois.py"],
        "symbol": "seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Deterministic seed fixtures ensure that local testing, spatial queries, and demo search flows produce predictable results.",
        "concept": "Idempotent seeding scripts verify existing records before inserting to avoid primary key collisions.",
        "how_it_works": "app/db/seed_all.py is called during FastAPI lifespan startup to seed listings and POIs if tables are empty.",
        "estatemap": "app/db/seed_properties.py and seed_pois.py load structured geographic coordinates, amenities, and price tiers into the database.",
        "code_flow": "Lifespan Startup -> seed_all() checks SELECT count(*) FROM properties -> If 0, inserts curated properties and POIs in a single transaction.",
        "build_snippet": """# Topic Build: Create an idempotent seed function that populates initial properties
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_properties_if_empty(session: AsyncSession, seed_records: list[dict]):
    stmt = select(func.count(Property.id))
    count = (await session.execute(stmt)).scalar()
    if count == 0:
        for item in seed_records:
            prop = Property(**item)
            session.add(prop)
        await session.commit()""",
        "break_it": "Non-deterministic seeding with randomized coordinates causes spatial distance tests and ranking tests to fail intermittently.",
        "tradeoffs": "Hardcoded curated seed fixtures provide immediate out-of-the-box local developer onboarding.",
        "system_design": "Seed fixtures replicate realistic real-world geographic clusters, enabling spatial query testing and ranking calibration.",
        "interview_q": "How do you ensure integration tests run against predictable data?",
        "interview_a": "Idempotent database seeders and deterministic fixtures loaded in test transaction boundaries with rollback on test completion."
    },

    # Module 04: Authentication & Security Boundaries (13-15)
    {
        "id": 13, "title": "Password Hashing with Argon2id & Cryptographic Salting",
        "module_id": 4, "module_name": "Module 04: Authentication & Security Boundaries", "importance": STATUS_ESSENTIAL,
        "prereqs": [3, 8], "leads_to": [14, 15],
        "files": ["backend/app/core/security.py", "backend/app/services/auth_service.py"],
        "symbol": "get_password_hash / verify_password / PasswordHasher", "test_cmd": "docker compose exec backend pytest tests/unit/test_security.py",
        "why": "Storing plaintext or MD5/SHA256 hashed passwords exposes user accounts to rainbow table compromise.",
        "concept": "Argon2id combines data-independent and data-dependent memory access for side-channel and ASIC resistance.",
        "how_it_works": "app/core/security.py implements get_password_hash and verify_password using passlib/argon2.",
        "estatemap": "app/core/security.py uses argon2-cffi to hash passwords with calibrated time cost and memory parameters.",
        "code_flow": "User Registration -> Plaintext Password -> Argon2id generates salt & hash -> Hash stored in users.hashed_password.",
        "build_snippet": """# Topic Build: Implement password hashing and verification using passlib Argon2 context
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_user_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_user_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)""",
        "break_it": "Passing a non-string or None to verify_password raises a TypeError, which if unhandled turns into an uncaught 500 error.",
        "tradeoffs": "Argon2id is computationally heavier than bcrypt but provides superior resistance to dedicated hardware cracking.",
        "system_design": "Memory-hard hashing forces attackers to allocate significant RAM per crack attempt, making parallel attacks economically infeasible.",
        "interview_q": "Why is SHA-256 unsuitable for password storage?",
        "interview_a": "SHA-256 is designed to be fast for data integrity; password hashing requires slow, memory-hard algorithms like Argon2id to defeat brute-force and GPU rainbow table attacks."
    },
    {
        "id": 14, "title": "Stateless JWT Authentication, Token Expiration & Signature Verification",
        "module_id": 4, "module_name": "Module 04: Authentication & Security Boundaries", "importance": STATUS_ESSENTIAL,
        "prereqs": [3, 13], "leads_to": [15, 33],
        "files": ["backend/app/core/security.py", "backend/app/api/v1/auth.py"],
        "symbol": "create_access_token / decode_access_token / TokenSchema", "test_cmd": "docker compose exec backend pytest tests/integration/test_auth.py",
        "why": "Stateless JWTs allow backend API instances to verify user identity without querying a central session database on every request.",
        "concept": "JWT consists of Header, Payload (claims), and HMAC-SHA256 Signature verified via secret key.",
        "how_it_works": "app/core/security.py generates tokens with ACCESS_TOKEN_EXPIRE_MINUTES (60 min) and decodes sub/role claims.",
        "estatemap": "app/core/security.py implements create_access_token and decode_access_token with PyJWT HS256 validation.",
        "code_flow": "POST /api/v1/auth/login -> AuthService verifies password -> create_access_token() signs payload -> Returns access_token -> Client sends Bearer token.",
        "build_snippet": """# Topic Build: Build token generation and decoding helpers with expiration validation
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
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])""",
        "break_it": "Decoding an expired token raises jwt.ExpiredSignatureError; decoding with the wrong secret key raises jwt.InvalidSignatureError.",
        "tradeoffs": "Stateless JWTs eliminate database session lookups but require short TTLs or revocation lists for immediate logout.",
        "system_design": "Stateless tokens allow horizontal scaling of backend servers because any worker node can verify the signature independently.",
        "interview_q": "How do stateless JWTs scale better than session IDs?",
        "interview_a": "The server verifies the cryptographic signature locally using the shared secret key without needing shared session database lookups on every request."
    },
    {
        "id": 15, "title": "Dependency-Based Role Authorization & Resource Ownership Validation",
        "module_id": 4, "module_name": "Module 04: Authentication & Security Boundaries", "importance": STATUS_ESSENTIAL,
        "prereqs": [13, 14], "leads_to": [18, 42],
        "files": ["backend/app/core/dependencies.py", "backend/app/services/property_service.py"],
        "symbol": "get_current_user / get_current_active_user / require_role", "test_cmd": "docker compose exec backend pytest tests/integration/test_auth.py",
        "why": "Prevent Broken Object Level Authorization (BOLA/IDOR) where users modify resources owned by other users.",
        "concept": "FastAPI Depends() injects verified user objects into endpoint parameters before handler execution.",
        "how_it_works": "app/core/dependencies.py extracts Bearer token, fetches user, and PropertyService verifies property.owner_id == user.id.",
        "estatemap": "app/core/dependencies.py provides reusable security dependencies (get_current_user, get_current_active_admin) that parse tokens.",
        "code_flow": "Incoming Request -> Depends(get_current_user) extracts Bearer token -> Validates token signature -> Fetches User entity -> Passes user to route handler.",
        "build_snippet": """# Topic Build: Create a FastAPI get_current_user security dependency
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
    return user""",
        "break_it": "Omitting the Bearer token or supplying a malformed authorization header returns HTTP 403 / 401 before the route handler is invoked.",
        "tradeoffs": "Dependency injection centralizes security checks, preventing boilerplate code duplication across route handlers.",
        "system_design": "Declarative security dependencies ensure authorization rules are enforced consistently across all private API endpoints.",
        "interview_q": "What is an IDOR vulnerability and how do you prevent it?",
        "interview_a": "Insecure Direct Object Reference occurs when an API accepts an object ID without verifying that the requesting user owns that object. Prevent it by checking ownership in the service layer before mutation."
    },

    # Module 05: PostGIS Spatial Search (16-21)
    {
        "id": 16, "title": "Geospatial Coordinates, WGS84 (EPSG:4326) & PostGIS POINT Storage",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [8, 11], "leads_to": [17, 18, 19],
        "files": ["backend/app/models/property.py", "backend/app/models/poi.py"],
        "symbol": "mapped_column(Geometry(geometry_type='POINT', srid=4326)) / idx_properties_location", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Standard SQL numeric columns cannot perform spherical distance calculations or spatial bounding box containment.",
        "concept": "WGS84 (EPSG:4326) defines points on the Earth's ellipsoidal surface using (Longitude, Latitude) coordinates.",
        "how_it_works": "app/models/property.py defines location as Geometry('POINT', srid=4326) with explicit longitude-first ordering.",
        "estatemap": "app/models/property.py and poi.py map location columns using GeoAlchemy2 Geometry with SRID 4326.",
        "code_flow": "Insert Property -> GeoAlchemy2 converts (lon, lat) to WKT (POINT(lon lat)) -> PostgreSQL stores binary geometry representation.",
        "build_snippet": """# Topic Build: Define a GeoAlchemy2 POINT model and instantiate a spatial point
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
    return WKTElement(f"POINT({lon} {lat})", srid=4326)""",
        "break_it": "Swapping latitude and longitude coordinates (putting lat first in WKT) stores the point in the wrong quadrant of the globe.",
        "tradeoffs": "Storing as geometry with runtime geography casting combines fast Cartesian indexing with accurate ellipsoidal distance math.",
        "system_design": "Spatial point storage enables spatial indexing, polygon intersection, and radius filtering natively inside PostgreSQL.",
        "interview_q": "Why does PostGIS use (Longitude, Latitude) ordering instead of (Lat, Lon)?",
        "interview_a": "PostGIS follows standard Cartesian (X, Y) coordinate conventions where Longitude is the horizontal X axis and Latitude is the vertical Y axis."
    },
    {
        "id": 17, "title": "GiST Spatial Indexing & Bounding-Box Search Pruning",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [16], "leads_to": [18, 19, 47],
        "files": ["backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py", "backend/app/models/property.py"],
        "symbol": "spatial_index=True / idx_properties_location (USING gist)", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Without spatial indexes, querying spatial candidates requires sequential scans and per-row mathematical checks.",
        "concept": "GiST (Generalized Search Tree) is an indexing framework. PostGIS geometry commonly uses spatial operator classes based on bounding-box relationships to prune irrelevant candidates. Exact performance depends on dataset size, distribution, selectivity, planner decisions and hardware.",
        "how_it_works": "Alembic revision 0003 creates idx_properties_location USING gist on the location geometry column.",
        "estatemap": "Database schema sets spatial_index=True on Geometry columns, instructing PostgreSQL to create a GiST index.",
        "code_flow": "Spatial Query -> Query Planner evaluates GiST index -> Prunes non-overlapping bounding-box subtrees -> Filters candidate rows -> Verifies exact geometry predicate.",
        "build_snippet": """# Topic Build: Create a GiST index on a PostGIS geometry column using Alembic operations
from alembic import op

def create_gist_spatial_index():
    op.create_index(
        'idx_properties_location',
        'properties',
        ['location'],
        unique=False,
        postgresql_using='gist'
    )""",
        "break_it": "Wrapping the indexed location column in an unindexed function in the WHERE clause prevents the planner from utilizing the GiST index, falling back to Seq Scan.",
        "tradeoffs": "GiST indexes trade slightly higher write/update overhead for candidate pruning during spatial filtering.",
        "system_design": "GiST reduces the candidate search space for selective spatial predicates; verify actual planner behavior using EXPLAIN ANALYZE.",
        "interview_q": "How does a GiST spatial index work internally for PostGIS queries?",
        "interview_a": "GiST builds a hierarchical tree of bounding boxes (similar to an R-Tree). Spatial queries check bounding-box overlap and prune entire subtrees that do not intersect the search envelope."
    },
    {
        "id": 18, "title": "Geodesic Radius Search via ST_DWithin on Runtime Cast Geography",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [16, 17], "leads_to": [20, 24, 25],
        "files": ["backend/app/services/geo_service.py", "backend/app/repositories/property_repository.py"],
        "symbol": "PropertyRepository.search_radius / func.ST_DWithin / func.ST_Distance", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Querying Euclidean distance in degrees on EPSG:4326 causes severe distortion because degrees of longitude shrink away from the equator.",
        "concept": "Casting geometry to geography enables spherical great-circle distance calculations directly in meters.",
        "how_it_works": "PropertyRepository.search_radius casts Property.location to geography and executes ST_DWithin(loc, point, radius_m).",
        "estatemap": "app/repositories/property_repository.py casts location to Geography and applies func.ST_DWithin and func.ST_Distance.",
        "code_flow": "GET /api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=5000 -> Repository constructs ST_DWithin query -> PostGIS index filters bounding box -> Returns properties with distance_m.",
        "build_snippet": """# Topic Build: Construct an async ST_DWithin radius query with distance calculation
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
    return stmt""",
        "break_it": "Calling ST_DWithin on uncast geometry with radius_meters=5000 treats the unit as 5,000 degrees, matching every listing on Earth.",
        "tradeoffs": "ST_DWithin leverages bounding box pruning before evaluating exact ellipsoidal distance math.",
        "system_design": "Geodesic radius search is the fundamental building block for location-based discovery in mobile and map applications.",
        "interview_q": "Why must you cast geometry to geography for ST_DWithin(geom, point, 5000)?",
        "interview_a": "Geometry calculations occur in planar units (degrees in EPSG:4326); casting to geography computes distances in meters along the curved Earth spheroid."
    },
    {
        "id": 19, "title": "Viewport Bounding Box Filtering via ST_MakeEnvelope & GiST Intersects",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [16, 17], "leads_to": [21, 42],
        "files": ["backend/app/services/geo_service.py", "backend/app/api/v1/maps.py", "backend/app/repositories/property_repository.py"],
        "symbol": "PropertyRepository.search_bbox / func.ST_MakeEnvelope / func.ST_Within", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Map-driven discovery requires fetching only the properties currently visible in the user's viewport bounding box.",
        "concept": "ST_MakeEnvelope constructs a polygon envelope that checks bounding-box overlap directly against GiST index nodes.",
        "how_it_works": "GET /api/v1/properties/map takes min_lat, max_lat, min_lon, max_lon and queries PropertyRepository.search_bbox.",
        "estatemap": "app/repositories/property_repository.py builds ST_MakeEnvelope polygon and filters properties with ST_Within.",
        "code_flow": "Map Pan/Zoom -> Frontend sends bounds (min_lat, min_lon, max_lat, max_lon) -> Repository generates ST_MakeEnvelope -> GiST index scans matching box -> Returns visible GeoJSON.",
        "build_snippet": """# Topic Build: Build an ST_MakeEnvelope viewport query for map bounding box search
from sqlalchemy import select
from geoalchemy2.functions import ST_MakeEnvelope, ST_Within

def query_viewport(model, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    # Envelope parameter order: (xmin, ymin, xmax, ymax, srid) -> (min_lon, min_lat, max_lon, max_lat, 4326)
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    return select(model).where(ST_Within(model.location, envelope))""",
        "break_it": "Passing min_lat > max_lat creates an inverted bounding box, returning zero results from the spatial index.",
        "tradeoffs": "Bounding box queries are fast because they evaluate 2D box containment without trigonometric distance math.",
        "system_design": "Viewport filtering prevents clients from downloading points outside the visible screen, bounding payload sizes.",
        "interview_q": "How does a map viewport search query work in PostGIS?",
        "interview_a": "The API constructs a bounding envelope via ST_MakeEnvelope and uses ST_Within to leverage the GiST spatial index efficiently."
    },
    {
        "id": 20, "title": "Points of Interest (POI) Proximity Aggregation & Spatial Intelligence",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_IMPORTANT,
        "prereqs": [16, 18], "leads_to": [25, 27],
        "files": ["backend/app/models/poi.py", "backend/app/services/poi_service.py", "backend/app/repositories/poi_repository.py"],
        "symbol": "POIService.get_location_intelligence / POIRepository.get_nearby_pois", "test_cmd": "docker compose exec backend pytest tests/integration/test_pois.py",
        "why": "Listing evaluation requires neighborhood intelligence (proximity to schools, hospitals, transit hubs).",
        "concept": "Spatial aggregation groups nearby POIs by category and computes nearest facility distances within a target radius.",
        "how_it_works": "POIService.get_location_intelligence queries POIRepository for nearby POIs, categorizes them, and caches the summary with CACHE_POI_TTL_SECONDS (1800s).",
        "estatemap": "app/services/poi_service.py coordinates spatial queries across POI categories and calculates summary counts and nearest distances.",
        "code_flow": "Property ID requested -> POIService fetches property coordinates -> Queries POIRepository for POIs within radius -> Computes count per category & nearest distance -> Returns LocationIntelligenceResponse.",
        "build_snippet": """# Topic Build: Aggregate POIs by category and compute nearest distance
from collections import defaultdict

def aggregate_pois_by_category(poi_distance_tuples: list[tuple]) -> dict:
    categories = defaultdict(lambda: {"count": 0, "nearest_km": None})
    for poi, dist_meters in poi_distance_tuples:
        cat = poi.category
        dist_km = round(dist_meters / 1000.0, 2)
        categories[cat]["count"] += 1
        if categories[cat]["nearest_km"] is None or dist_km < categories[cat]["nearest_km"]:
            categories[cat]["nearest_km"] = dist_km
    return dict(categories)""",
        "break_it": "Executing separate un-indexed spatial queries for each POI category individually produces an N+1 query pattern.",
        "tradeoffs": "Location intelligence is calculated on-demand with Redis caching (TTL=1800s) to balance freshness with query performance.",
        "system_design": "Cached POI category aggregations allow fast real-time score calculation during property discovery.",
        "interview_q": "How do you optimize spatial proximity aggregation for listings?",
        "interview_a": "Pre-index POIs with GiST, query with ST_DWithin radius buffers, and cache aggregate category summaries in Redis."
    },
    {
        "id": 21, "title": "RFC 7946 GeoJSON Serialization & Strict Coordinate Ordering",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_IMPORTANT,
        "prereqs": [5, 16], "leads_to": [42],
        "files": ["backend/app/schemas/geo.py", "backend/app/api/v1/properties.py"],
        "symbol": "PropertyGeoJSONFeature / PropertyGeoJSONFeatureCollection / PointGeometry", "test_cmd": "docker compose exec backend pytest tests/unit/test_geo_schemas.py",
        "why": "Standardized GeoJSON payloads ensure seamless rendering across map libraries (MapLibre, Mapbox, Leaflet, QGIS).",
        "concept": "RFC 7946 specifies that GeoJSON coordinate positions MUST be ordered as [easting, northing] -> [longitude, latitude].",
        "how_it_works": "app/schemas/geo.py defines Pydantic models for GeoJSON Feature, FeatureCollection, and Point geometry serialization.",
        "estatemap": "app/schemas/geo.py defines type-safe Pydantic models enforcing GeoJSON specifications and property attributes.",
        "code_flow": "Database Property entity -> Pydantic validator extracts WKB/WKT coordinates -> Formats into FeatureCollection with [lon, lat] geometry -> Serialized to JSON.",
        "build_snippet": """# Topic Build: Build RFC 7946 GeoJSON Feature and FeatureCollection Pydantic schemas
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
    features: List[GeoJSONFeature]""",
        "break_it": "Emitting [latitude, longitude] order in GeoJSON violates RFC 7946 and causes map clients to plot markers in Antarctica.",
        "tradeoffs": "Serializing directly in Pydantic ensures schema validation without requiring heavy external GIS serialization libraries.",
        "system_design": "Standard GeoJSON schemas allow the backend API to be consumed by any GIS platform, web client, or mobile application.",
        "interview_q": "What is the RFC 7946 coordinate ordering standard?",
        "interview_a": "[Longitude, Latitude, Elevation], representing X (easting) then Y (northing)."
    },

    # Module 06: Location Intelligence & Routing (22-24)
    {
        "id": 22, "title": "Deterministic In-Memory Location Resolver for Metropolitan Hubs",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [16, 21], "leads_to": [23, 24, 39],
        "files": ["backend/app/utils/location_resolver.py", "backend/app/api/v1/search.py"],
        "symbol": "LocationResolver.resolve_destination / KNOWN_LOCATIONS / METRO_BOUNDS", "test_cmd": "docker compose exec backend pytest tests/unit/test_location_resolver.py",
        "why": "Natural language searches contain informal locality names that need deterministic coordinate resolution.",
        "concept": "In-memory alias dictionary and normalized matching resolve known metropolitan hubs (Bengaluru and Chennai) without external network dependencies.",
        "how_it_works": "LocationResolver matches query strings against KNOWN_LOCATIONS registry with metro bounding box validation (Bengaluru and Chennai).",
        "estatemap": "app/utils/location_resolver.py implements string normalization, alias dictionary lookup, and city bounding box verification; returns None for unknown destinations to trigger clarification.",
        "code_flow": "Query string received ('near Electronic City') -> LocationResolver normalizes string -> Matches alias in KNOWN_LOCATIONS -> Returns ResolvedLocation(name, lat, lng).",
        "build_snippet": """# Topic Build: Build an in-memory landmark resolver with exact, word-boundary, and substring matching
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
    cleaned = re.sub(r"[^\\w\\s]", " ", query.lower()).strip()
    cleaned = re.sub(r"\\s+", " ", cleaned)
    if cleaned in LANDMARKS:
        lat, lng, label = LANDMARKS[cleaned]
        return ResolvedLoc(name=label, lat=lat, lng=lng)
    return None""",
        "break_it": "Attempting to geocode arbitrary un-indexed strings without returning None causes false-positive coordinate matches on unrelated user queries.",
        "tradeoffs": "In-memory deterministic resolver avoids third-party geocoding API rate limits, costs, and external network latency.",
        "system_design": "Layered location resolution: check in-memory catalog first; return clarification prompt if destination is unresolved.",
        "interview_q": "Why use an in-memory landmark resolver for domain search?",
        "interview_a": "It provides predictable, fast coordinate resolution for known domain hubs with zero external API costs and no network dependency."
    },
    {
        "id": 23, "title": "External HTTP Client with Async Httpx & OSRM Engine Integration",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [2, 3], "leads_to": [24, 47],
        "files": ["backend/app/services/routing/osrm_provider.py", "backend/app/services/routing/factory.py"],
        "symbol": "OSRMProvider.get_route / RoutingProviderFactory / RoutingProvider", "test_cmd": "docker compose exec backend pytest tests/integration/test_commute.py",
        "why": "Straight-line distance ignores physical road geometry, traffic directionality, and water bodies.",
        "concept": "Async httpx.AsyncClient queries OSRM routing endpoints for driving, walking, and cycling modes.",
        "how_it_works": "OSRMProvider sends coordinate pairs to OSRM /route/v1/{profile}/ and extracts duration (seconds) and distance (meters).",
        "estatemap": "app/services/routing/osrm_provider.py encapsulates async HTTP requests to OSRM with connection timeouts, profile mapping, and response parsing.",
        "code_flow": "Commute request -> OSRMProvider formats coordinate URL -> httpx.AsyncClient executes GET with timeout -> Parses route polyline and duration.",
        "build_snippet": """# Topic Build: Create an async OSRM routing client with timeouts and profile mapping
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
            }""",
        "break_it": "Not setting HTTP timeouts on external routing calls causes backend coroutines to hang if the OSRM server becomes unresponsive.",
        "tradeoffs": "OSRM provides road network routing without commercial API fees, though standard endpoints lack real-time dynamic traffic awareness.",
        "system_design": "External API wrappers must encapsulate timeouts, retries, and fallbacks to prevent cascading system degradation.",
        "interview_q": "How do you safely integrate third-party HTTP services in an async backend?",
        "interview_a": "Use async HTTP clients (httpx) with strict timeouts, connection pooling, and circuit breaker fallbacks."
    },
    {
        "id": 24, "title": "Multi-Modal Commute Calculation & Great-Circle Haversine Fallback",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [18, 22, 23], "leads_to": [25, 30],
        "files": ["backend/app/services/commute_service.py", "backend/app/utils/geo.py"],
        "symbol": "CommuteService.calculate_route / haversine_distance_km", "test_cmd": "docker compose exec backend pytest tests/integration/test_commute.py",
        "why": "Commute duration is a key search criterion; routing provider failures must never crash the search pipeline.",
        "concept": "Haversine formula calculates great-circle distance on a spherical Earth as a robust mathematical fallback.",
        "how_it_works": "CommuteService checks Redis route cache (CACHE_ROUTE_TTL_SECONDS=600s), queries OSRM, and falls back to speed-profile Haversine math on provider failure.",
        "estatemap": "app/services/commute_service.py coordinates multi-property commute calculations, route caching, and Haversine fallback logic.",
        "code_flow": "Properties & Destination passed -> CommuteService checks Redis cache -> Queries routing provider -> If routing fails, applies Haversine fallback -> Returns commute response.",
        "build_snippet": """# Topic Build: Implement Haversine distance and duration estimation fallback
import math

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def estimate_fallback_duration(distance_km: float, speed_kmh: float = 25.0) -> float:
    return round((distance_km / speed_kmh) * 60.0, 1)""",
        "break_it": "Passing negative or zero travel speed in fallback duration calculations causes a ZeroDivisionError.",
        "tradeoffs": "Cached route results combined with mathematical fallbacks ensure commute endpoints remain responsive during external routing outages.",
        "system_design": "Computing commutes across candidate listings requires batching and caching to avoid latency bottlenecks.",
        "interview_q": "What is your fallback strategy if external routing APIs fail?",
        "interview_a": "Gracefully degrade to in-memory Haversine distance with calibrated mode-specific velocity models (e.g. 25 km/h driving, 4 km/h walking)."
    },

    # Module 07: Deterministic Ranking & Business Logic (25-28)
    {
        "id": 25, "title": "6-Factor Mathematical Ranking Engine & Min-Max Score Normalization",
        "module_id": 7, "module_name": "Module 07: Deterministic Ranking & Business Logic", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 18, 24], "leads_to": [26, 27, 28],
        "files": ["backend/app/services/ranking_service.py", "backend/app/utils/ranking.py"],
        "symbol": "RankingService.rank_properties / calculate_price_score / calculate_bedroom_score", "test_cmd": "docker compose exec backend pytest tests/integration/test_ranking.py",
        "why": "Deterministic MCDA ensures transparent, auditable, and reproducible scoring across candidate listings.",
        "concept": "Multi-Criteria Decision Analysis (MCDA) linearly normalizes heterogeneous metrics (INR, sqft, minutes) into comparable [0, 1] scales.",
        "how_it_works": "app/utils/ranking.py implements mathematical scoring functions with user-configurable or preset weight vectors.",
        "estatemap": "app/services/ranking_service.py coordinates scoring calculations across candidate properties and sorts by final composite score; caches results with CACHE_RANKING_TTL_SECONDS (300s).",
        "code_flow": "Filtered properties passed to RankingService -> Evaluates 6 dimension scoring functions -> Multiplies by weight vector -> Sums to composite score -> Returns ranked list.",
        "build_snippet": """# Topic Build: Build a min-max normalizer for price and area scoring
def score_lower_is_better(val: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val: return 1.0
    normalized = 1.0 - (val - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))

def score_higher_is_better(val: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val: return 1.0
    normalized = (val - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))""",
        "break_it": "Failing to handle max_val == min_val causes a ZeroDivisionError when all candidate properties have identical price or area.",
        "tradeoffs": "Deterministic mathematical ranking guarantees identical inputs produce identical rank ordering every time.",
        "system_design": "Separating hard database filters (WHERE price <= max_price) from soft ranking preferences delivers optimal user relevance.",
        "interview_q": "Why use deterministic mathematical ranking over an LLM for search results?",
        "interview_a": "Deterministic scoring is reproducible, computationally efficient, free of token costs, and immune to generative hallucinations."
    },
    {
        "id": 26, "title": "Dynamic Missing-Factor Weight Redistribution & Active Weight Sums",
        "module_id": 7, "module_name": "Module 07: Deterministic Ranking & Business Logic", "importance": STATUS_ESSENTIAL,
        "prereqs": [25], "leads_to": [27, 28],
        "files": ["backend/app/services/ranking_service.py", "backend/app/utils/ranking.py"],
        "symbol": "RankingService._redistribute_weights / active_weight_sum normalization", "test_cmd": "docker compose exec backend pytest tests/unit/test_ranking_scoring.py",
        "why": "If an optional factor (e.g. commute weight = 0.25) is missing, total scores would cap at 0.75, distorting comparisons.",
        "concept": "Active weight renormalization computes W_i' = W_i / sum(W_active), ensuring composite scores always scale to 1.0.",
        "how_it_works": "RankingService._redistribute_weights filters out inactive criteria and divides active weights by active_weight_sum.",
        "estatemap": "app/services/ranking_service.py checks active scoring factors and rescales weight vectors dynamically before scoring.",
        "code_flow": "Ranking query without commute destination -> Commute factor marked inactive -> Active weights summed -> Each active weight divided by sum -> Composite scores sum to 1.0.",
        "build_snippet": """# Topic Build: Implement weight redistribution for missing scoring criteria
def redistribute_active_weights(raw_weights: dict[str, float], active_keys: set[str]) -> dict[str, float]:
    active_sum = sum(w for k, w in raw_weights.items() if k in active_keys)
    if active_sum <= 0:
        equal_weight = 1.0 / max(1, len(active_keys))
        return {k: equal_weight if k in active_keys else 0.0 for k in raw_weights}
    return {k: (w / active_sum if k in active_keys else 0.0) for k, w in raw_weights.items()}""",
        "break_it": "Hardcoding static weights when optional filters are omitted produces skewed scores that do not reflect user priority distributions.",
        "tradeoffs": "Proportional redistribution preserves relative user priority ratios among the remaining active factors.",
        "system_design": "Dynamic weight normalization ensures multi-attribute scoring systems remain statistically valid regardless of missing input dimensions.",
        "interview_q": "How do you handle missing criteria in multi-attribute scoring?",
        "interview_a": "Dynamically rescale active weights so their sum equals 1.0, preserving relative priority ratios."
    },
    {
        "id": 27, "title": "Factual Score Explainability & Human-Readable Score Breakdowns",
        "module_id": 7, "module_name": "Module 07: Deterministic Ranking & Business Logic", "importance": STATUS_IMPORTANT,
        "prereqs": [25, 26], "leads_to": [28, 38],
        "files": ["backend/app/utils/ranking.py", "backend/app/schemas/ranking.py"],
        "symbol": "generate_deterministic_explanations / FactorScoreDetail", "test_cmd": "docker compose exec backend pytest tests/integration/test_ranking.py",
        "why": "Users trust search rankings when the system transparently explains why a listing ranked in a specific position.",
        "concept": "Rule-based template generation derived directly from computed sub-scores guarantees factual explainability.",
        "how_it_works": "app/utils/ranking.py generates FactorScoreDetail arrays attached to every RankedPropertyResponse.",
        "estatemap": "app/utils/ranking.py maps dimension scores and calculated deltas to human-readable factual strings.",
        "code_flow": "Score calculation finishes -> generate_deterministic_explanations() inspects top positive/negative score factors -> Formats string explanations -> Attached to response.",
        "build_snippet": """# Topic Build: Generate template-based factual explanations from factor scores
def generate_factor_explanation(factor_name: str, score: float, raw_val: float) -> str:
    if factor_name == "price" and score >= 0.8:
        return f"Competitively priced at ₹{raw_val:,.0f}"
    if factor_name == "commute" and score >= 0.8:
        return f"Short commute time ({raw_val:.0f} mins)"
    if factor_name == "location" and score >= 0.8:
        return "High density of nearby amenities"
    return f"{factor_name.title()} score: {score:.2f}" """,
        "break_it": "Passing unformatted raw numbers (e.g. 15000000.0 instead of ₹1.5 Cr) reduces explainability and causes client UI formatting bugs.",
        "tradeoffs": "Deterministic explanation generation requires zero LLM tokens and executes in-memory.",
        "system_design": "Exposing structured explainability objects enables client applications to highlight key decision drivers without extra API roundtrips.",
        "interview_q": "How do you provide explainability in recommendation systems?",
        "interview_a": "Expose atomic sub-score breakdowns and template-driven factual reasoning derived directly from scoring metrics."
    },
    {
        "id": 28, "title": "Deterministic Property Comparison Engine & Dimension Winners",
        "module_id": 7, "module_name": "Module 07: Deterministic Ranking & Business Logic", "importance": STATUS_ESSENTIAL,
        "prereqs": [25, 26, 27], "leads_to": [38, 42],
        "files": ["backend/app/services/comparison_service.py", "backend/app/schemas/comparison.py"],
        "symbol": "ComparisonService.compare_properties / ComparisonResult / DimensionWinner", "test_cmd": "docker compose exec backend pytest tests/integration/test_ai_comparison.py",
        "why": "Comparing properties side-by-side requires objective numerical diffs before synthesizing a narrative summary.",
        "concept": "Pairwise and 3-way dimensional comparisons select verified winners for price per sqft, bedroom count, and commute.",
        "how_it_works": "ComparisonService.compare_properties fetches listings, computes metric diffs, determines winners, and packages ComparisonResult.",
        "estatemap": "app/services/comparison_service.py implements structured metric diffing, price per sqft calculation, and winner selection.",
        "code_flow": "POST /api/v1/properties/compare [ids] -> Service fetches properties -> Calculates metric deltas -> Selects dimension winners -> Returns structured ComparisonResult.",
        "build_snippet": """# Topic Build: Build a dimensional winner evaluator for 2-3 properties
def pick_dimension_winner(items: list[dict], metric: str, lower_is_better: bool = False) -> dict:
    if not items: return {}
    comparator = min if lower_is_better else max
    winner = comparator(items, key=lambda x: x.get(metric, 0))
    return {
        "metric": metric,
        "winner_id": winner["id"],
        "winner_value": winner[metric]
    }""",
        "break_it": "Requesting comparison for non-existent property IDs raises an EntityNotFoundException if not validated before processing.",
        "tradeoffs": "Deterministic dimension winners provide hard facts that ground subsequent narrative summaries.",
        "system_design": "Decoupling metric comparison from narrative generation allows caching the deterministic comparison result independently.",
        "interview_q": "How do you structure property comparison in the backend?",
        "interview_a": "Compute deterministic dimensional deltas and metric winners first, then pass those verified facts to the presentation or AI layer."
    },

    # Module 08: Redis In-Memory Caching (29-31)
    {
        "id": 29, "title": "Redis Async Client & Cache-Aside (Lazy Loading) Architecture",
        "module_id": 8, "module_name": "Module 08: Redis In-Memory Caching", "importance": STATUS_ESSENTIAL,
        "prereqs": [2, 3], "leads_to": [30, 31, 32],
        "files": ["backend/app/cache/redis.py", "backend/app/cache/cache_service.py"],
        "symbol": "CacheService.get_json / CacheService.set_json / init_redis", "test_cmd": "docker compose exec backend pytest tests/unit/test_cache_service.py",
        "why": "Repeated spatial and ranking queries consume database CPU; caching identical requests avoids redundant database queries.",
        "concept": "Cache-Aside pattern loads data on-demand, keeping in-memory footprints bounded to active query working sets.",
        "how_it_works": "CacheService wraps redis.asyncio client with JSON serialization and transparent database fallback on cache miss.",
        "estatemap": "app/cache/redis.py manages connection pool; app/cache/cache_service.py provides get_json, set_json, and delete methods with domain TTLs.",
        "code_flow": "Client Request -> CacheService.get_json(key) -> Cache HIT: return cached JSON -> Cache MISS: query DB -> CacheService.set_json(key, data, ttl) -> Return response.",
        "build_snippet": """# Topic Build: Implement a generic Cache-Aside helper around an async fetch function
import json
import redis.asyncio as aioredis
from typing import Callable, Any

async def cached_fetch(redis: aioredis.Redis, key: str, ttl_sec: int, fetch_fn: Callable[[], Any]) -> Any:
    cached = await redis.get(key)
    if cached:
        return json.loads(cached)
    data = await fetch_fn()
    await redis.set(key, json.dumps(data), ex=ttl_sec)
    return data""",
        "break_it": "Storing non-JSON-serializable objects (such as raw SQLAlchemy instances or datetime objects) in Redis without a custom encoder causes a TypeError.",
        "tradeoffs": "Cache-Aside handles cache node restarts gracefully because the database remains the authoritative single source of truth.",
        "system_design": "Caching read-heavy geospatial and ranking responses protects database connection pools and increases read capacity.",
        "interview_q": "How does the Cache-Aside pattern work and what are its failure modes?",
        "interview_a": "The application queries cache first; on miss, loads from DB and writes to cache with TTL. If cache fails, app gracefully falls back to querying the database directly."
    },
    {
        "id": 30, "title": "Canonical Cache Key Design, Coordinate Precision & SHA-256 Hashing",
        "module_id": 8, "module_name": "Module 08: Redis In-Memory Caching", "importance": STATUS_ESSENTIAL,
        "prereqs": [29], "leads_to": [31, 32],
        "files": ["backend/app/cache/cache_keys.py", "backend/app/cache/cache_service.py"],
        "symbol": "CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route", "test_cmd": "docker compose exec backend pytest tests/unit/test_cache_keys.py",
        "why": "Microscopic float precision differences destroy cache hit ratios; coordinate rounding normalizes nearby requests.",
        "concept": "Rounding coordinates to CACHE_COORDINATE_PRECISION (4 decimal places, ~11m precision) collapses GPS drift into canonical cache buckets.",
        "how_it_works": "CacheKeys.normalize_coord rounds floats to 4 decimals; filter dicts are sorted and hashed with SHA-256.",
        "estatemap": "app/cache/cache_keys.py implements key generator functions with version prefixes (estatemap:v1:*) and deterministic hashing.",
        "code_flow": "Parameters received -> CacheKeys formats key: estatemap:v1:map:{min_lat}:{min_lon}:{max_lat}:{max_lon}:{sha256(filters)} -> Canonical key used in Redis lookup.",
        "build_snippet": """# Topic Build: Build a canonical geospatial cache key generator with SHA-256 hashing
import hashlib
import json

def make_geo_cache_key(prefix: str, min_lat: float, min_lon: float, max_lat: float, max_lon: float, params: dict, precision: int = 4) -> str:
    coords = f"{round(min_lat, precision)}:{round(min_lon, precision)}:{round(max_lat, precision)}:{round(max_lon, precision)}"
    param_str = json.dumps(params, sort_keys=True)
    digest = hashlib.sha256(param_str.encode()).hexdigest()[:12]
    return f"estatemap:v1:{prefix}:{coords}:{digest}" """,
        "break_it": "Omitting sort_keys=True when serializing filter dictionaries produces different JSON hashes for identical filter combinations, causing unnecessary cache misses.",
        "tradeoffs": "SHA-256 digests keep Redis key lengths fixed and predictable regardless of complex filter parameter counts.",
        "system_design": "Hierarchical key namespaces simplify monitoring, debugging, and targeted wildcard key invalidation.",
        "interview_q": "How do you design cache keys for geospatial search queries?",
        "interview_a": "Normalize coordinates to fixed precision (e.g. 4 decimals), sort filter parameters deterministically, and hash with version prefixes to guarantee collision-free lookups."
    },
    {
        "id": 31, "title": "Cache Invalidation via Non-Blocking SCAN & TTL-Based Expiration",
        "module_id": 8, "module_name": "Module 08: Redis In-Memory Caching", "importance": STATUS_IMPORTANT,
        "prereqs": [29, 30], "leads_to": [32, 47],
        "files": ["backend/app/cache/cache_service.py", "backend/app/core/config.py"],
        "symbol": "CacheService.delete_pattern / CacheService.delete / CACHE_MAP_TTL_SECONDS", "test_cmd": "docker compose exec backend pytest tests/unit/test_cache_service.py",
        "why": "Using the blocking KEYS * command halts the single-threaded Redis event loop; SCAN iterates cursor-by-cursor safely.",
        "concept": "TTL-based expiration guarantees eventual consistency; mutation hooks trigger active prefix invalidation via SCAN.",
        "how_it_works": "CacheService.delete_pattern uses redis.scan_iter(match=pattern, count=100) to delete matching keys without blocking.",
        "estatemap": "app/cache/cache_service.py implements delete_pattern using async scan_iter and applies configurable TTLs from Settings (Map: 120s, Ranking: 300s, Route: 600s, POI: 1800s).",
        "code_flow": "Property Updated -> PropertyService calls CacheService.delete_pattern('estatemap:v1:map:*') -> redis.scan_iter iterates batches -> Keys deleted -> Next read re-caches fresh data.",
        "build_snippet": """# Topic Build: Implement non-blocking batch cache invalidation using scan_iter
import redis.asyncio as aioredis

async def invalidate_cache_pattern(redis: aioredis.Redis, pattern: str, batch_size: int = 100):
    keys_to_del = []
    async for key in redis.scan_iter(match=pattern, count=batch_size):
        keys_to_del.append(key)
        if len(keys_to_del) >= batch_size:
            await redis.delete(*keys_to_del)
            keys_to_del.clear()
    if keys_to_del:
        await redis.delete(*keys_to_del)""",
        "break_it": "Running KEYS 'estatemap:*' on a production Redis instance blocks all other Redis operations for the duration of the scan.",
        "tradeoffs": "SCAN has O(N) overall complexity across iterations but never blocks the single-threaded Redis event loop.",
        "system_design": "Configuring distinct domain TTLs balances data freshness with database query reduction across fast-changing and slow-changing data.",
        "interview_q": "Why is KEYS * dangerous in production Redis, and what is the alternative?",
        "interview_a": "KEYS * blocks the single-threaded Redis server until all keys are scanned, stalling all traffic. Use SCAN with cursor pagination instead."
    },

    # Module 09: Rate Limiting & Resilience (32-34)
    {
        "id": 32, "title": "Sliding-Window Log Rate Limiting via Redis Sorted Sets (ZSET)",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_ESSENTIAL,
        "prereqs": [4, 29], "leads_to": [33, 34],
        "files": ["backend/app/core/rate_limit.py", "backend/app/core/middleware.py"],
        "symbol": "RateLimiter / redis.pipeline() / ZADD / ZREMRANGEBYSCORE", "test_cmd": "docker compose exec backend pytest tests/integration/test_rate_limiting.py",
        "why": "Fixed window rate limiters allow 2x traffic bursts across window boundaries; sliding windows provide uniform enforcement.",
        "concept": "Redis pipeline reduces network round trips; however, pipeline execution does not make the sliding-window decision fully atomic without Lua or transactional isolation. Concurrent clients may interleave operations.",
        "how_it_works": "RateLimiter executes pipelined ZREMRANGEBYSCORE -> ZCARD -> ZADD -> EXPIRE, rejecting requests exceeding limit with HTTP 429.",
        "estatemap": "app/core/rate_limit.py implements RateLimiter class using async Redis pipelines for sliding-window log tracking; rolls back ZADD on limit breach.",
        "code_flow": "Incoming Request -> RateLimiter executes Redis pipeline: ZREMRANGEBYSCORE(0, now-60) -> ZCARD -> If count >= limit: rollback ZADD & raise RateLimitExceededException -> Else allow request.",
        "build_snippet": """# Topic Build: Implement a sliding-window rate limiter using Redis pipelines
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
    return False, max(0, limit - (count_before + 1))""",
        "break_it": "In high concurrency, multiple requests reading ZCARD before ZADD can cause a slight over-limit race condition unless executed via server-side Lua scripts.",
        "tradeoffs": "Redis ZSET sliding window offers precision and burst protection with minimal memory per active client IP.",
        "system_design": "Rate limiting protects downstream database connection pools and external AI providers from traffic spikes and abuse.",
        "interview_q": "Does a Redis pipeline guarantee atomic rate limiting?",
        "interview_a": "No. A pipeline batches commands to reduce network round trips, but other commands can interleave unless wrapped in MULTI/EXEC or executed via a Lua script."
    },
    {
        "id": 33, "title": "Multi-Tier Endpoint Scopes, HTTP 429 & Retry-After Semantics",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_ESSENTIAL,
        "prereqs": [32], "leads_to": [34, 42],
        "files": ["backend/app/core/rate_limit.py", "backend/app/core/config.py"],
        "symbol": "RateLimiter / RateLimitExceededException / HTTP 429", "test_cmd": "docker compose exec backend pytest tests/integration/test_rate_limiting.py",
        "why": "Compute-heavy AI and ranking endpoints require stricter rate limits than lightweight health and listing endpoints.",
        "concept": "Tiered rate limiting scopes limits by identity (IP or user ID) and endpoint domain; standard HTTP 429 returns Retry-After.",
        "how_it_works": "RateLimiter applies domain configurations (Auth: 10/min, AI: 15/min, Ranked Search: 20/min, Commute: 30/min, Default: 100/min).",
        "estatemap": "app/core/rate_limit.py maps route scopes to Settings limits and raises RateLimitExceededException with calculated Retry-After duration.",
        "code_flow": "Request evaluated -> RateLimiter determines scope limit -> If exceeded, raises RateLimitExceededException -> Formats HTTP 429 with Retry-After header in seconds.",
        "build_snippet": """# Topic Build: Create scoped rate limiter dependencies with Retry-After calculation
from fastapi import Request, HTTPException

def create_scoped_limiter(scope_name: str, limit: int, window_sec: int = 60):
    async def limiter_dependency(request: Request):
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"ratelimit:{scope_name}:{client_ip}"
        # Evaluate limiter...
        # If limited:
        # raise HTTPException(status_code=429, detail="Too Many Requests", headers={"Retry-After": str(window_sec)})
    return limiter_dependency""",
        "break_it": "Omitting the Retry-After header causes client frontends to retry immediately, worsening backend overload.",
        "tradeoffs": "Tiered scoping prevents heavy AI feature usage from starving general browsing and health traffic.",
        "system_design": "Tiered rate limiting protects upstream AI quotas and database resources while keeping read paths responsive.",
        "interview_q": "What headers should a rate-limited API return?",
        "interview_a": "Standard HTTP 429 status code with the RFC Retry-After header indicating seconds to wait, and optional conventional metadata."
    },
    {
        "id": 34, "title": "Fail-Open vs Fail-Closed Resiliency Policies on Redis Degradation",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_IMPORTANT,
        "prereqs": [32, 33], "leads_to": [37, 47],
        "files": ["backend/app/core/rate_limit.py", "backend/app/cache/cache_service.py"],
        "symbol": "RATE_LIMIT_FAIL_OPEN / Redis error handling", "test_cmd": "docker compose exec backend pytest tests/integration/test_redis_degradation.py",
        "why": "An auxiliary Redis outage should not bring down the entire property search application.",
        "concept": "Fail-open policy allows traffic through when rate limiting infrastructure is unreachable, prioritizing availability.",
        "how_it_works": "RateLimiter and CacheService catch Redis errors; if fail_open=True (default), log a warning and let the request proceed.",
        "estatemap": "app/core/rate_limit.py and app/cache/cache_service.py implement try/except RedisError blocks governed by settings.RATE_LIMIT_FAIL_OPEN.",
        "code_flow": "Redis connection drops -> RateLimiter catches RedisError -> Checks fail_open flag -> Logs warning -> Permits request to reach route handler.",
        "build_snippet": """# Topic Build: Implement fail-open/fail-closed error handling around Redis operations
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
        return True # Fail open: permit request""",
        "break_it": "Uncaught Redis connection errors bubbling up to route handlers turn every incoming API call into an HTTP 500.",
        "tradeoffs": "Failing open prioritizes availability over strict rate enforcement; strict security paths (e.g. auth brute-force) can be configured to fail closed.",
        "system_design": "Graceful degradation ensures non-essential auxiliary subsystem failures do not cause catastrophic core business outages.",
        "interview_q": "What is the difference between fail-open and fail-closed in rate limiting?",
        "interview_a": "Fail-open permits requests if the limiter is unreachable (prioritizing availability); fail-closed blocks requests (prioritizing resource protection)."
    },

    # Module 10: Multi-Provider AI Architecture (35-38)
    {
        "id": 35, "title": "Abstract AI Provider Interface & Structural Parity (Ollama & Gemini)",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [3, 5], "leads_to": [36, 37, 38],
        "files": ["backend/app/ai/base.py", "backend/app/ai/ollama_provider.py", "backend/app/ai/gemini_provider.py"],
        "symbol": "AIProvider / OllamaProvider / GeminiProvider / MockAIProvider", "test_cmd": "docker compose exec backend pytest tests/unit/test_cross_provider_parity.py",
        "why": "Coupling domain services to a single commercial LLM vendor creates vendor lock-in and vulnerability to outages.",
        "concept": "Abstract Base Class (ABC) defines the provider contract: parse_search_intent, parse_search_patch, explain_property, explain_comparison.",
        "how_it_works": "app/ai/base.py defines AIProvider ABC; OllamaProvider, GeminiProvider, and MockAIProvider implement the exact same methods.",
        "estatemap": "app/ai/base.py defines the AIProvider contract; concrete adapters implement API calls and return structured Pydantic schemas.",
        "code_flow": "AI Service calls provider method -> Adapter formats vendor-specific prompt -> Sends HTTP request -> Validates response schema -> Returns typed object.",
        "build_snippet": """# Topic Build: Define the abstract AI provider base class and a test mock implementation
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
        return {"raw_query": query, "confidence": 1.0}, 5.0""",
        "break_it": "A provider returning an unvalidated dictionary instead of the standard schema breaks downstream service methods.",
        "tradeoffs": "Unified AI provider contract allows running cost-free local Ollama in development and cloud Gemini in production.",
        "system_design": "Adapter pattern isolates external SDK idiosyncrasies from core application domain logic.",
        "interview_q": "How do you prevent vendor lock-in when integrating LLMs?",
        "interview_a": "Define an abstract provider interface with standardized Pydantic input/output schemas implemented by all provider adapters."
    },
    {
        "id": 36, "title": "Strict LLM Output Validation via Pydantic v2 Schemas",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 35], "leads_to": [37, 38, 39],
        "files": ["backend/app/schemas/ai.py", "backend/app/ai/gemini_provider.py", "backend/app/ai/ollama_provider.py"],
        "symbol": "PropertySearchIntent / AIExplanationResponse / AIOutputValidationException", "test_cmd": "docker compose exec backend pytest tests/unit/test_ai_schemas.py",
        "why": "LLMs can return malformed JSON or out-of-range numerical values.",
        "concept": "Regex JSON extraction followed by strict Pydantic model validation transforms untrusted text into type-safe domain objects.",
        "how_it_works": "Provider implementations extract JSON substrings and validate with PropertySearchIntent.model_validate_json().",
        "estatemap": "app/schemas/ai.py defines PropertySearchIntent and explanation models; providers validate model output and raise AIOutputValidationException on failure.",
        "code_flow": "LLM returns raw text -> Regex extracts JSON block -> Pydantic model_validate() checks types and bounds -> If valid: return object -> If invalid: trigger failover.",
        "build_snippet": """# Topic Build: Build a JSON extraction and Pydantic validation firewall for LLM text output
import re
import json
from pydantic import BaseModel, Field, ValidationError

class ExtractedIntent(BaseModel):
    locality: str | None = None
    max_price: float | None = Field(None, gt=0)
    bedrooms: int | None = Field(None, ge=1, le=10)

def extract_and_validate_intent(raw_llm_text: str) -> ExtractedIntent:
    match = re.search(r"\\{.*?\\}", raw_llm_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return ExtractedIntent.model_validate_json(match.group(0))""",
        "break_it": "Passing raw LLM text directly to json.loads() without regex parsing or Pydantic validation causes syntax errors on markdown code fences.",
        "tradeoffs": "Pydantic validation acts as a resilient firewall between non-deterministic AI generation and deterministic database logic.",
        "system_design": "Schema validation and sanitization are essential defenses against prompt injection and LLM hallucination.",
        "interview_q": "How do you handle non-deterministic LLM responses in production?",
        "interview_a": "Request structured JSON mode, extract with regex, validate against Pydantic schemas, and trigger fallbacks on validation failure."
    },
    {
        "id": 37, "title": "Dynamic Provider Routing, Latency Timeouts & Loop-Bounded Failover",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [35, 36], "leads_to": [38, 39],
        "files": ["backend/app/ai/router.py", "backend/app/services/ai_service.py", "backend/app/ai/routing_policy.py"],
        "symbol": "AIRouter.get_provider / AIService.parse_search_intent / AI_TOTAL_TIMEOUT_SECONDS", "test_cmd": "docker compose exec backend pytest tests/integration/test_ai_failover.py",
        "why": "Local or cloud AI providers can experience timeouts, rate limits, or connectivity issues.",
        "concept": "Sequential loop failover tries configured providers within a global time budget bounded by AI_TOTAL_TIMEOUT_SECONDS (35.0s).",
        "how_it_works": "AIRoutingPolicy selects attempt order; AIService loops over providers with attempt_timeout = min(remaining_budget, prov_timeout) and executes at most once per provider.",
        "estatemap": "app/ai/router.py resolves providers; app/services/ai_service.py iterates providers with asyncio.wait_for and falls back to deterministic rules if all fail.",
        "code_flow": "AI Request -> AIService calculates remaining budget -> Calls Provider 1 with timeout -> On Timeout/Error: logs warning -> Calls Provider 2 with remaining budget -> If all fail: executes deterministic fallback.",
        "build_snippet": """# Topic Build: Build a multi-provider failover loop with global deadline budgeting
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
    return {"fallback": True, "error": str(last_err)}""",
        "break_it": "Not checking remaining time budget before attempting the second provider causes total request duration to exceed API gateway limits.",
        "tradeoffs": "Loop-bounded failover improves service resilience without unbounded execution time.",
        "system_design": "Provider failover and deterministic fallbacks improve resilience when individual AI providers fail.",
        "interview_q": "How do you implement timeout budgets in multi-provider failover chains?",
        "interview_a": "Set a global deadline at request start; for each provider attempt, set timeout to min(remaining_budget, provider_timeout), and fall back if the budget is exhausted."
    },
    {
        "id": 38, "title": "Algorithmic Grounded Fallbacks & Hallucination-Risk Reduction",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_IMPORTANT,
        "prereqs": [27, 28, 36, 37], "leads_to": [39, 41],
        "files": ["backend/app/services/ai_service.py", "backend/app/services/comparison_service.py", "backend/app/utils/price_parser.py"],
        "symbol": "AIService.explain_property fallback / IndianPriceParser / rule_based_v1", "test_cmd": "docker compose exec backend pytest tests/integration/test_ai_endpoints.py",
        "why": "When all AI providers fail, users must still receive valid search results and property explanations.",
        "concept": "When AI providers fail, EstateMap can generate deterministic fallback text from verified backend facts. This reduces dependence on generative output and reduces unsupported-generation risk, but does not justify universal factuality or availability guarantees.",
        "how_it_works": "AIService constructs structured summaries using verified property attributes, POI distances, and commute metrics directly from database records.",
        "estatemap": "app/services/ai_service.py implements deterministic rule-based generators (IndianPriceParser for search, template formatting for property/comparison explanations).",
        "code_flow": "All AI providers fail or timeout -> AIService catches error -> Invokes rule-based fallback generator -> Assembles verified facts into string -> Returns response with fallback_used=True.",
        "build_snippet": """# Topic Build: Build a deterministic property explanation fallback from verified context
def build_factual_explanation_fallback(prop_dict: dict, pois_dict: dict, commute_dict: dict | None) -> str:
    parts = [f"{prop_dict.get('bedrooms', '')} BHK {prop_dict.get('property_type', 'property')} in {prop_dict.get('locality', '')}, {prop_dict.get('city', '')} listed at ₹{prop_dict.get('price_inr', 0):,.0f} ({prop_dict.get('area_sqft', 0):,.0f} sqft)."]
    if pois_dict:
        items = [f"{k.replace('_', ' ')} ({v['nearest_distance_km']} km)" for k, v in pois_dict.items() if v.get('nearest_distance_km')]
        if items: parts.append(f"Nearby amenities include {', '.join(items[:2])}.")
    if commute_dict:
        parts.append(f"Estimated commute to {commute_dict['destination']} is {commute_dict['duration_minutes']} mins ({commute_dict['distance_km']} km).")
    return " ".join(parts)""",
        "break_it": "Returning empty strings or HTTP 500 when AI fails degrades user experience when verified database facts are already available.",
        "tradeoffs": "Deterministic fallbacks are fast and reliable, though less linguistically varied than LLM output.",
        "system_design": "Grounded fallbacks ensure user interfaces remain functional and informative during upstream AI outages.",
        "interview_q": "How do you handle AI provider downtime in production?",
        "interview_a": "Fall back to algorithmic rule-based summaries assembled directly from verified database facts, returning the result with a fallback_used flag."
    },

    # Module 11: Ask-the-Map Conversational Search Orchestration (39-41)
    {
        "id": 39, "title": "Natural Language Search Intent Extraction & Backend Authority Boundary",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 22, 36, 37], "leads_to": [40, 41],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/schemas/conversational_search.py"],
        "symbol": "SearchStatePatch / AskMapRequest / AskMapResponse / SearchOrchestrator", "test_cmd": "docker compose exec backend pytest tests/integration/test_ask_the_map.py",
        "why": "AI models must only extract proposed search intent; the backend retains complete authority over database query execution.",
        "concept": "Backend Authority Boundary: LLM output is strictly an untrusted patch proposal validated before application to canonical state.",
        "how_it_works": "AIService extracts SearchStatePatch from user query; SearchOrchestrator applies the patch, resolves coordinates, and executes queries.",
        "estatemap": "app/schemas/conversational_search.py defines SearchStatePatch; app/services/search_orchestrator.py applies patches and executes PostGIS/ranking queries.",
        "code_flow": "User submits text -> AIService extracts SearchStatePatch -> SearchOrchestrator.apply_patch updates state -> LocationResolver validates destination -> Executes queries.",
        "build_snippet": """# Topic Build: Define the conversational SearchStatePatch schema and validation bounds
from pydantic import BaseModel, Field
from typing import Optional, List

class SearchStatePatch(BaseModel):
    locality: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=1, le=10)
    commute_destination: Optional[str] = None
    clear_fields: List[str] = Field(default_factory=list)""",
        "break_it": "Allowing the LLM to directly generate SQL WHERE clauses exposes the database to prompt injection and syntax errors.",
        "tradeoffs": "Structured intent parsing separates natural language comprehension from secure PostGIS SQL execution.",
        "system_design": "Intent extraction with backend query execution provides AI flexibility while maintaining database security.",
        "interview_q": "How do you prevent prompt injection in conversational database search?",
        "interview_a": "The LLM never writes SQL. It outputs a validated Pydantic patch schema which the backend applies to deterministic query builders."
    },
    {
        "id": 40, "title": "Stateless Conversational Search State Machine & State Reducer",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [39], "leads_to": [41, 42],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/schemas/conversational_search.py"],
        "symbol": "ConversationalSearchState / SearchOrchestrator.apply_patch / AppliedPatchFeedback", "test_cmd": "docker compose exec backend pytest tests/unit/test_search_orchestrator.py",
        "why": "Storing conversational search sessions in server memory breaks horizontal scaling across backend instances.",
        "concept": "Stateless state reducer: New State = Reducer(Old State, Patch), eliminating server-side session stickiness.",
        "how_it_works": "AskMapRequest carries ConversationalSearchState; SearchOrchestrator.apply_patch merges changes and returns updated state in AskMapResponse.",
        "estatemap": "app/schemas/conversational_search.py defines ConversationalSearchState; app/services/search_orchestrator.py apply_patch executes state reduction.",
        "code_flow": "POST /api/v1/search/ask-the-map {message, current_state} -> Orchestrator extracts patch -> apply_patch(current_state, patch) -> Returns (new_state, feedback, results).",
        "build_snippet": """# Topic Build: Build a pure functional state reducer for conversational search filters
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
    return SearchState(**state_dict)""",
        "break_it": "Relying on in-memory server session dictionaries causes state loss when backend instances restart or requests hit different pods.",
        "tradeoffs": "Client-held state simplifies backend scaling at the cost of slightly larger HTTP request payloads.",
        "system_design": "Stateless state machines allow backend API replicas to process any conversation turn without sticky session routing.",
        "interview_q": "How do you design multi-turn conversational search without sticky sessions?",
        "interview_a": "Keep the backend stateless: client passes current search state in the request, backend reducer applies patches and returns the new state."
    },
    {
        "id": 41, "title": "Multi-Turn Criteria Modification, History Merging & Orchestrated Search",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [39, 40], "leads_to": [42, 46],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/services/ranking_service.py"],
        "symbol": "SearchOrchestrator.execute / SearchOrchestrator._build_geojson / AskMapResponse", "test_cmd": "docker compose exec backend pytest tests/integration/test_ask_the_map.py",
        "why": "A conversational assistant must support iterative refinement (e.g. 'under 1.5 Cr', 'now make it 3 BHK') seamlessly.",
        "concept": "SearchOrchestrator coordinates Domain Services (LocationResolver -> PropertyRepository -> RankingService -> ComparisonService).",
        "how_it_works": "SearchOrchestrator.execute coordinates the full pipeline, resolving destinations, applying ranking, and building GeoJSON responses.",
        "estatemap": "app/services/search_orchestrator.py coordinates multi-service execution, handles destination ambiguity, and formats conversational responses.",
        "code_flow": "Turn 1: 'Find 3BHK in Whitefield' -> Sets bedrooms=3, locality=Whitefield -> Turn 2: 'Under 1.5 Cr' -> Merges max_price=15000000 -> Re-executes ranked search.",
        "build_snippet": """# Topic Build: Coordinate multi-turn state merging with domain service execution
async def orchestrate_turn(orchestrator, current_state, patch, user_message):
    new_state, feedback, notes, unresolved = orchestrator.apply_patch(current_state, patch)
    if unresolved:
        return {"needs_clarification": True, "prompt": f"Could you clarify '{unresolved}'?", "state": current_state}
    # Execute database filter and ranking...
    return {"state": new_state, "feedback": feedback, "results": []}""",
        "break_it": "Overwriting previous valid filters when applying a partial patch (e.g. wiping out bedrooms when updating max_price) breaks conversational context.",
        "tradeoffs": "Centralizing orchestration in a dedicated domain service keeps API route handlers clean and testable.",
        "system_design": "Domain service orchestration decouples conversational logic from raw database storage and third-party APIs.",
        "interview_q": "Trace the end-to-end execution of a natural language search query.",
        "interview_a": "1. AI extracts patch; 2. Resolver checks destination; 3. State Reducer updates criteria; 4. PostGIS filters DB; 5. Ranking scores results; 6. Response returned."
    },

    # Module 12: Backend ↔ Frontend API Integration (42)
    {
        "id": 42, "title": "Backend ↔ Frontend API Integration Contract & Data Boundary",
        "module_id": 12, "module_name": "Module 12: Backend ↔ Frontend API Integration", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 14, 21, 33, 40], "leads_to": [46, 48],
        "files": ["backend/app/api/v1/properties.py", "backend/app/api/v1/search.py", "backend/app/api/v1/auth.py"],
        "symbol": "API Router definitions / OpenAPI schemas / CORS middleware", "test_cmd": "docker compose exec backend pytest tests/integration/test_properties.py",
        "why": "Clear API contracts enable frontend and backend teams to develop, test, and mock independently without tight coupling.",
        "concept": "RESTful HTTP endpoints communicate strictly via standard JSON, GeoJSON, Authorization headers, and HTTP status codes.",
        "how_it_works": "FastAPI automatically generates OpenAPI docs (/docs) matching Pydantic schemas and error contracts.",
        "estatemap": "backend/app/api/v1/ defines versioned routers exposing properties, search, commute, ranking, and auth endpoints.",
        "code_flow": "Frontend makes fetch(url, {headers: {Authorization: Bearer token}}) -> FastAPI routes request -> Pydantic serializes response -> Frontend consumes JSON/GeoJSON.",
        "build_snippet": """# Topic Build: Assemble versioned API routers under /api/v1
from fastapi import APIRouter

api_v1_router = APIRouter(prefix="/api/v1")
# Mount sub-routers
# api_v1_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
# api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
# api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])""",
        "break_it": "Changing a response field name in the backend without updating the Pydantic schema causes frontend runtime crashes.",
        "tradeoffs": "Strict JSON/GeoJSON contracts decouple the Python backend from specific frontend frameworks.",
        "system_design": "API contract stability guarantees backward compatibility for existing clients during backend upgrades.",
        "interview_q": "How do you design clean API integration boundaries?",
        "interview_a": "Use versioned REST endpoints (/api/v1), explicit Pydantic response schemas, RFC 7807 error structures, and automated OpenAPI contract generation."
    },

    # Module 13: Backend Testing & Debugging (43-44)
    {
        "id": 43, "title": "Pytest Fundamentals, Async Fixtures & Dependency Overrides",
        "module_id": 13, "module_name": "Module 13: Backend Testing & Debugging", "importance": STATUS_ESSENTIAL,
        "prereqs": [1, 9, 10], "leads_to": [44],
        "files": ["backend/tests/conftest.py", "backend/tests/unit/test_health.py"],
        "symbol": "pytest_asyncio / app.dependency_overrides / async_session fixture", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Automated tests give developers confidence to refactor code without introducing silent regressions.",
        "concept": "Arrange-Act-Assert pattern with isolated test database sessions and mocked third-party dependencies.",
        "how_it_works": "backend/tests/conftest.py initializes test clients, database engines, and clean session fixtures.",
        "estatemap": "tests/conftest.py defines async fixtures for db_session, async_client, test_settings, and mock_ai_provider.",
        "code_flow": "pytest runs -> conftest initializes test database connection -> Injects async_session into test -> Test executes Arrange-Act-Assert -> Session rolled back.",
        "build_snippet": """# Topic Build: Create an async test client fixture with dependency overrides in pytest
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
    app.dependency_overrides.clear()""",
        "break_it": "Sharing mutable state across tests without cleanup causes flaky tests that fail only when run in specific test execution orders.",
        "tradeoffs": "Dependency overrides allow testing authenticated routes and repositories in complete isolation.",
        "system_design": "Fast unit test suites running in seconds encourage continuous test-driven development (TDD).",
        "interview_q": "How do you test authenticated FastAPI routes without making real login calls?",
        "interview_a": "Use app.dependency_overrides[get_current_user] = lambda: mock_user in your test fixture to inject a mock authenticated user directly."
    },
    {
        "id": 44, "title": "Integration Testing of Repositories, Redis, External APIs & Error Paths",
        "module_id": 13, "module_name": "Module 13: Backend Testing & Debugging", "importance": STATUS_IMPORTANT,
        "prereqs": [43], "leads_to": [46],
        "files": ["backend/tests/integration/test_properties.py", "backend/tests/integration/test_rate_limiting.py"],
        "symbol": "pytest integration test suites (288 tests)", "test_cmd": "docker compose exec backend pytest",
        "why": "Unit tests with mocks cannot catch SQL syntax errors, GiST index misconfigurations, or Redis connection bugs.",
        "concept": "Integration tests run against real containerized services (Postgres, Redis) to verify end-to-end component interaction.",
        "how_it_works": "tests/integration/ covers auth, properties, spatial search, commute routing, ranking, AI failover, and rate limiting.",
        "estatemap": "tests/integration/ contains 288 comprehensive integration tests verifying API workflows against real Postgres and Redis.",
        "code_flow": "docker compose exec backend pytest -> Pytest runs 288 tests -> Verifies real DB queries, Redis caching hits/misses, and AI failovers -> 100% pass.",
        "build_snippet": """# Topic Build: Write an integration test verifying spatial property creation and radius search
import pytest

@pytest.mark.asyncio
async def test_create_and_query_radius(test_client, auth_headers):
    payload = {"title": "Test Listing", "price": 9500000, "bedrooms": 3, "latitude": 12.9716, "longitude": 77.5946}
    create_res = await test_client.post("/api/v1/properties", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    
    search_res = await test_client.get("/api/v1/properties/radius?lat=12.9716&lon=77.5946&radius_m=1000")
    assert search_res.status_code == 200
    assert any(p["id"] == create_res.json()["id"] for p in search_res.json()["items"])""",
        "break_it": "Testing only happy paths leaves edge cases (e.g. database disconnect, invalid token format) untested for production.",
        "tradeoffs": "Integration tests are slower than unit tests but provide the highest fidelity proof of system correctness.",
        "system_design": "Automated test suites in CI/CD block regressions from reaching staging and production environments.",
        "interview_q": "What is the difference between unit and integration tests in a FastAPI project?",
        "interview_a": "Unit tests test isolated functions with mocked dependencies; integration tests verify API endpoints against real databases and Redis."
    },

    # Module 14: Docker for Backend Developers (45)
    {
        "id": 45, "title": "Multi-Container Backend Orchestration with Docker Compose",
        "module_id": 14, "module_name": "Module 14: Docker for Backend Developers", "importance": STATUS_IMPORTANT,
        "prereqs": [1, 9, 29], "leads_to": [46],
        "files": ["docker-compose.yml", "backend/Dockerfile", ".env"],
        "symbol": "services: postgres-postgis, redis, backend / healthcheck", "test_cmd": "docker compose ps",
        "why": "Containerization eliminates 'works on my machine' issues by providing identical local and production runtime environments.",
        "concept": "Docker Compose manages container networks, port bindings, persistent volumes, environment files, and healthcheck dependencies.",
        "how_it_works": "docker-compose.yml defines services with depends_on condition: service_healthy ensuring DB is ready before backend boots.",
        "estatemap": "docker-compose.yml coordinates postgres-postgis, redis, and backend containers on a shared bridge network.",
        "code_flow": "docker compose up -> Postgres & Redis boot -> Healthchecks pass -> Backend container boots -> Alembic runs -> FastAPI starts serving traffic.",
        "build_snippet": """# Topic Build: Write a docker-compose.yml service block with PostgreSQL healthcheck
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
#       retries: 5""",
        "break_it": "Backend starting before PostgreSQL is healthy causes initial connection attempts to fail and crash the container.",
        "tradeoffs": "Docker Compose provides lightweight local orchestration without the operational complexity of Kubernetes.",
        "system_design": "Standardized container definitions allow any developer to clone the repo and run the full stack with a single docker compose up command.",
        "interview_q": "Why use service health checks in docker-compose.yml?",
        "interview_a": "To ensure dependent services (like PostgreSQL) are fully initialized and ready to accept connections before the backend starts, preventing startup crashes."
    },

    # Module 15: EstateMap System Design & Architecture Synthesis (46-48)
    {
        "id": 46, "title": "EstateMap Modular Monolith Architecture & Request Lifecycle Synthesis",
        "module_id": 15, "module_name": "Module 15: EstateMap System Design & Architecture Synthesis", "importance": STATUS_ESSENTIAL,
        "prereqs": [4, 10, 15, 21, 28, 31, 34, 38, 41, 42, 44, 45], "leads_to": [47, 48],
        "files": ["backend/app/main.py", "backend/app/services/search_orchestrator.py", "docs/mastery/ARCHITECTURE.md"],
        "symbol": "Request Lifecycle: Middleware -> Router -> Dependency -> Service -> Repository -> PostGIS/Redis -> Pydantic Response", "test_cmd": "docker compose exec backend pytest",
        "why": "Senior engineers must be able to trace and defend the end-to-end lifecycle of any incoming HTTP request across all system layers.",
        "concept": "Clean layered architecture strictly isolates Presentation (FastAPI), Domain (Services), Data Access (Repositories), and Infrastructure (Postgres/Redis).",
        "how_it_works": "Every request traverses RequestID -> CORS -> RateLimiter -> Router -> get_db -> Service Layer -> Repository -> DB/Redis -> Pydantic serialization.",
        "estatemap": "Complete repository codebase adheres to this layered architecture with explicit boundary isolation and dependency injection.",
        "code_flow": "1. Client sends request -> 2. RequestID & CORS middleware -> 3. RateLimiter evaluates ZSET -> 4. Router parses schema -> 5. Service orchestrates business logic -> 6. Repository executes PostGIS query -> 7. Pydantic serializes response.",
        "build_snippet": """# Topic Build: Map the complete 7-layer request pipeline in an architectural blueprint
# Layer 1: ASGI Server (Uvicorn)
# Layer 2: Middleware Pipeline (RequestID, CORS)
# Layer 3: Security & Rate Limiting (RateLimiter dependency, JWT auth)
# Layer 4: API Presentation (FastAPI Router + Pydantic validation)
# Layer 5: Domain Services (SearchOrchestrator, RankingService, CommuteService)
# Layer 6: Data Access (PropertyRepository, POIRepository via AsyncSession)
# Layer 7: Infrastructure Storage (PostgreSQL 16 + PostGIS, Redis 7)""",
        "break_it": "Importing database session objects directly in route handlers bypassing the service layer creates architectural coupling and makes testing difficult.",
        "tradeoffs": "Modular Monolith eliminates network serialization hops while maintaining clean domain module boundaries.",
        "system_design": "Layered modular architecture allows future extraction of isolated high-throughput services if organizational or scaling requirements dictate.",
        "interview_q": "Walk me through the exact request lifecycle of a conversational search query in your system.",
        "interview_a": "1. RequestID middleware tags request; 2. Rate limiter checks ZSET; 3. Router validates schema; 4. AI Service extracts intent patch; 5. Resolver checks destination; 6. State Reducer updates state; 7. PostGIS filters candidates; 8. Ranking scores results; 9. GeoJSON response returned."
    },
    {
        "id": 47, "title": "15 Core Architectural Tradeoffs & Engineering Justifications",
        "module_id": 15, "module_name": "Module 15: EstateMap System Design & Architecture Synthesis", "importance": STATUS_ESSENTIAL,
        "prereqs": [46], "leads_to": [48],
        "files": ["docs/mastery/SYSTEM_DESIGN.md", "backend/app/core/config.py"],
        "symbol": "15 Architectural Decisions: Monolith vs Microservices, PostgreSQL+PostGIS vs Mongo, Redis ZSET vs Token Bucket, etc.", "test_cmd": "python docs/mastery/generator/verify_backend_curriculum.py",
        "why": "Senior engineers are evaluated on their ability to justify architectural tradeoffs with concrete engineering reasoning rather than dogma.",
        "concept": "Engineering is the discipline of tradeoffs: every architectural choice trades simplicity, consistency, latency, cost, and operational overhead.",
        "how_it_works": "SYSTEM_DESIGN.md documents 15 core architectural decisions with What Was Chosen, What Was Rejected, and Why.",
        "estatemap": "EstateMap implements Modular Monolith, PostgreSQL+PostGIS, Asyncpg, Redis Cache-Aside, Redis ZSET rate limiting, MCDA deterministic ranking, and multi-provider AI.",
        "code_flow": "Architecture Review -> Evaluate functional requirements -> Analyze operational cost & latency -> Select technology -> Document rejected alternatives and tradeoffs.",
        "build_snippet": """# Topic Build: Formulate a structured Tradeoff Defense matrix for technical interviews
# Format: [Decision] | [Chosen Tech] | [Rejected Alternative] | [Engineering Justification]
# 1. Architecture: Modular Monolith vs Microservices (Zero network RPC overhead, single deployment)
# 2. Database: PostgreSQL+PostGIS vs MongoDB (Native GiST spatial indexing, ACID referential integrity)
# 3. Driver: Asyncpg vs Psycopg2 (Non-blocking asyncio I/O, event loop concurrency)
# 4. Caching: Redis Cache-Aside vs In-Memory Dict (Shared across worker processes, TTL eviction)
# 5. Ranking: 6-Factor MCDA vs LLM-based (Deterministic, reproducible, fast, zero token cost)""",
        "break_it": "Choosing microservices or distributed event brokers prematurely for a single-developer or early-stage system introduces massive operational overhead without business benefit.",
        "tradeoffs": "Every technology decision in EstateMap is defended with concrete latency, consistency, and operational complexity rationale.",
        "system_design": "System design maturity is demonstrated by selecting the simplest architecture that fulfills all functional and non-functional requirements.",
        "interview_q": "Why did you choose PostgreSQL with PostGIS over MongoDB with Geospatial indexes?",
        "interview_a": "PostgreSQL provides true ACID transactions, relational foreign key constraints for listings/owners, and PostGIS offers advanced geodesic functions (ST_DWithin, ST_MakeEnvelope) backed by GiST indexing."
    },
    {
        "id": 48, "title": "Scaling EstateMap from 10k to 1M Users (Evolutionary Roadmaps)",
        "module_id": 15, "module_name": "Module 15: EstateMap System Design & Architecture Synthesis", "importance": STATUS_IMPORTANT,
        "prereqs": [46, 47], "leads_to": [],
        "files": ["docs/mastery/SYSTEM_DESIGN.md"],
        "symbol": "Evolutionary Scaling: Stage 1 (Single Node) -> Stage 2 (Read Replicas + Redis Cache) -> Stage 3 (Async Task Queues + Sharding)", "test_cmd": "python docs/mastery/generator/verify_backend_curriculum.py",
        "why": "Demonstrate system design maturity by mapping how an architecture evolves systematically as traffic and data volumes grow.",
        "concept": "Evolutionary Architecture: Scale bottlenecks incrementally based on measured constraints (CPU, DB I/O, Cache memory, Network).",
        "how_it_works": "SYSTEM_DESIGN.md details Stage 1 (10k DAU), Stage 2 (100k DAU with Read Replicas & Connection Pooling), and Stage 3 (1M DAU with Geo-partitioning and CDN caching).",
        "estatemap": "EstateMap current architecture represents Stage 1/2 ready foundations with stateless workers and async database access.",
        "code_flow": "Traffic Growth -> Identify bottleneck (DB Read I/O) -> Add Read Replicas -> Add Redis Cache -> Add Async Task Queue -> Add Geographic Partitioning.",
        "build_snippet": """# Topic Build: Design a 3-Stage Evolutionary Scaling Blueprint
# Stage 1 (10k DAU): Single PostgreSQL container, Single Redis, 2 Uvicorn ASGI workers.
# Stage 2 (100k DAU): 1 Primary DB (writes) + 2 Read Replicas (spatial queries), PgBouncer connection pooler, Redis Cluster.
# Stage 3 (1M DAU): Geo-partitioned database clusters by metropolitan region, CDN edge tile caching, Celery/RabbitMQ async commute precomputation.""",
        "break_it": "Attempting to implement geographic sharding and Kafka brokers before reaching traffic scale creates accidental complexity and slows development velocity.",
        "tradeoffs": "Scale incrementally when metrics demand it rather than over-engineering upfront.",
        "system_design": "Horizontal scaling of stateless backend containers combined with read replicas and caching supports orders of magnitude traffic growth.",
        "interview_q": "How would you scale this real estate backend from 10,000 to 1,000,000 daily active users?",
        "interview_a": "1. Deploy stateless ASGI workers behind load balancers; 2. Add PostgreSQL read replicas with PgBouncer; 3. Cache frequent viewport queries in Redis; 4. Precompute POI and commute matrices asynchronously via task queues; 5. Partition databases by metropolitan city."
    }
]

def generate_stories_doc() -> str:
    lines = [
        "# EstateMap AI — 48 Backend Engineering Stories",
        "",
        "> **Role Target:** Python Backend Engineer / Backend System Designer  ",
        "> **Core Focus:** Python 3.12, FastAPI, PostgreSQL 16, PostGIS 3.4, SQLAlchemy 2.0 (Asyncpg), Redis 7, Multi-Provider AI (Ollama + Gemini), Deterministic Ranking, Spatial Indexing & System Design.  ",
        "> **Structure:** 48 Deep Stories across 15 Modules | 37 Essential, 11 Important, 0 Optional.  ",
        "",
        "---",
        ""
    ]
    
    current_mod = None
    for s in STORIES:
        if s["module_name"] != current_mod:
            current_mod = s["module_name"]
            lines.extend([
                f"## {current_mod}",
                ""
            ])
        
        prereqs_str = ", ".join([f"Story {p:02d}" for p in s["prereqs"]]) if s["prereqs"] else "None (Entry Point)"
        leads_to_str = ", ".join([f"Story {l:02d}" for l in s["leads_to"]]) if s["leads_to"] else "Final Synthesis"
        files_str = ", ".join([f"`{f}`" for f in s["files"]])
        
        lines.extend([
            f"### Story {s['id']:02d}: {s['title']} {s['importance']}",
            f"- **Module:** {s['module_name']}",
            f"- **Prerequisites:** {prereqs_str}",
            f"- **Leads To:** {leads_to_str}",
            f"- **Code Truth Files:** {files_str}",
            f"- **Key Symbol(s):** `{s['symbol']}`",
            f"- **Automated Test Command:** `{s['test_cmd']}`",
            "",
            "#### 1. Why This Matters in Production",
            s["why"],
            "",
            "#### 2. Core Engineering Concept",
            s["concept"],
            "",
            "#### 3. How It Works Under the Hood",
            s["how_it_works"],
            "",
            "#### 4. EstateMap Implementation Reality",
            s["estatemap"],
            "",
            "#### 5. Step-by-Step Code Flow",
            s["code_flow"],
            "",
            "#### 6. Build It Yourself (Topic-Specific Exercise)",
            "```python",
            s["build_snippet"],
            "```",
            "",
            "#### 7. Break It & Debug It (Specific Failure Mode)",
            s["break_it"],
            "",
            "#### 8. Architectural Tradeoffs & Rejected Alternatives",
            s["tradeoffs"],
            "",
            "#### 9. System Design & Scalability Angle",
            s["system_design"],
            "",
            "#### 10. Senior Backend Interview Prep",
            f"**Q:** {s['interview_q']}",
            "",
            f"**A:** {s['interview_a']}",
            "",
            "#### 11. Self-Assessment & Mastery Check",
            "- [ ] I can explain this mechanism from memory without looking at notes.",
            "- [ ] I can implement this component in a clean Python file from scratch.",
            "- [ ] I can diagnose and fix the specific failure mode described above.",
            "",
            "---",
            ""
        ])
    return "\n".join(lines)

def compile_all():
    print("Compiling 48 Reconciled Backend Stories...")
    stories_doc = generate_stories_doc()
    with open(os.path.join(MASTERY_DIR, "BACKEND_ENGINEERING_STORIES.md"), "w", encoding="utf-8") as f:
        f.write(stories_doc)
    print("Wrote BACKEND_ENGINEERING_STORIES.md")

if __name__ == "__main__":
    compile_all()

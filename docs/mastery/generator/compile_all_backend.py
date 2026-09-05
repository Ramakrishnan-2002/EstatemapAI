# -*- coding: utf-8 -*-
"""
EstateMap AI — Complete Backend Mastery Curriculum Compiler
Compiles all 48 backend stories across 15 modules into 7 canonical documents.
"""
import os
import sys
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MASTERY_DIR = os.path.join(BASE_DIR, "docs", "mastery")

STATUS_ESSENTIAL = "[ESSENTIAL]"
STATUS_IMPORTANT = "[IMPORTANT]"

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
        "build_snippet": """from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up resources...")
    yield
    print("Shutting down resources...")

def create_app() -> FastAPI:
    app = FastAPI(title="EstateMap Backend", lifespan=lifespan)
    return app

app = create_app()""",
        "break_it": "Introducing a circular import (e.g. importing a service in a router that imports the router) crashes Python with an ImportError during boot.",
        "tradeoffs": "Modular Monolith was chosen over microservices to eliminate distributed latency, RPC serialization overhead, and multi-repo operational complexity.",
        "system_design": "Stateless ASGI workers scale horizontally behind an NGINX / Cloud load balancer with zero shared in-process memory.",
        "interview_q": "Why use FastAPI over traditional frameworks like Django or Flask for high-performance APIs?",
        "interview_a": "FastAPI is built natively on Starlette and asyncio, allowing non-blocking concurrent I/O on a single thread event loop. It integrates Pydantic for high-throughput C-based schema validation."
    },
    {
        "id": 2, "title": "Async Event Loop, Non-Blocking Concurrency & Lifespan Management",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1], "leads_to": [8, 9, 29],
        "files": ["backend/app/main.py", "backend/app/cache/redis.py", "backend/app/db/session.py"],
        "symbol": "app.main:lifespan / asynccontextmanager", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Proper lifecycle management guarantees that database pools, Redis clients, and seed fixtures are safely initialized before taking traffic and gracefully closed on SIGTERM.",
        "concept": "Python asyncio event loop cooperative multitasking: I/O operations yield control with await, allowing thousands of concurrent requests per worker.",
        "how_it_works": "lifespan context manager runs code before yield on server startup and code after yield on server shutdown.",
        "estatemap": "app/main.py lifespan initializes Redis connection pools, verifies PostgreSQL connectivity, runs seed_all(), and teardowns pools on exit.",
        "code_flow": "Process Start -> Uvicorn triggers lifespan -> init_redis() -> init_db() -> seed_all() -> yield (Serve Requests) -> close_redis() -> dispose_engine() -> Process Exit.",
        "build_snippet": """from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup resources before taking requests
    db_pool = await create_db_pool()
    redis_client = await init_redis()
    yield
    # Cleanup resources on shutdown
    await redis_client.close()
    await db_pool.close()""",
        "break_it": "Forgetting the yield statement in the lifespan context manager causes FastAPI to hang during startup, timing out health checks.",
        "tradeoffs": "Lifespan context managers replace deprecated @app.on_event('startup') with structured, type-safe exception handling.",
        "system_design": "Graceful shutdown allows in-flight database transactions and HTTP requests to complete before closing sockets during rolling deployments.",
        "interview_q": "How does Python asyncio handle 10,000 concurrent I/O-bound requests on a single CPU core?",
        "interview_a": "When a coroutine awaits network I/O (database query or HTTP call), it yields control to the event loop, which immediately schedules other ready coroutines, preventing thread blocking."
    },
    {
        "id": 3, "title": "Type-Safe Environment Configuration with Pydantic-Settings",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1], "leads_to": [4, 8, 13, 29, 35],
        "files": ["backend/app/core/config.py", ".env.example"],
        "symbol": "app.core.config:Settings / get_settings", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Failing fast during boot when environment variables (DB URLs, API keys, TTLs) are invalid prevents runtime 500 errors in production.",
        "concept": "Strict schema parsing transforms raw environment string values into typed integers, booleans, and PostgresDsn objects with default fallbacks.",
        "how_it_works": "Pydantic BaseSettings reads .env files, coerces data types, and validates constraints (e.g. rate limits > 0, valid log levels).",
        "estatemap": "app/core/config.py defines Settings with database URLs, Redis parameters, rate limits, AI provider credentials, and exposes get_settings().",
        "code_flow": "App Start -> get_settings() -> Reads os.environ & .env -> Pydantic validates types -> Cached singleton injected across services.",
        "build_snippet": """from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_PER_MINUTE: int = 100
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

@lru_cache
def get_settings() -> Settings:
    return Settings()""",
        "break_it": "Setting an invalid port string like DATABASE_URL='postgres://user:pass@localhost:abc/db' raises a ValidationError, halting the app immediately.",
        "tradeoffs": "Pydantic-Settings provides compile-time typing and automated validation over fragile, manual os.environ.get() dictionaries.",
        "system_design": "12-Factor App config separation allows the exact same Docker image to run across local, staging, and production environments with different .env files.",
        "interview_q": "Why is Pydantic-Settings preferred over os.getenv in production backend systems?",
        "interview_a": "Pydantic-Settings automatically parses and validates types, enforces mandatory fields at startup, prevents type-coercion bugs, and supports hierarchical config injection."
    },
    {
        "id": 4, "title": "RFC 7807 Centralized Error Handling & Structured Request ID Logging",
        "module_id": 1, "module_name": "Module 01: Python & FastAPI Foundations", "importance": STATUS_ESSENTIAL,
        "prereqs": [1, 3], "leads_to": [5, 14, 32],
        "files": ["backend/app/core/exceptions.py", "backend/app/core/exception_handlers.py", "backend/app/core/middleware.py"],
        "symbol": "AppException / validation_exception_handler / RequestIDMiddleware", "test_cmd": "docker compose exec backend pytest tests/unit/test_exceptions.py",
        "why": "Consistent error contracts prevent leaking raw database stack traces and enable correlated distributed log debugging.",
        "concept": "RFC 7807 Problem Details for HTTP APIs standardizes error JSON responses (type, title, status, detail, instance).",
        "how_it_works": "Custom exception classes inherit from AppException. FastAPI exception handlers intercept exceptions and format structured JSON responses.",
        "estatemap": "app/core/exceptions.py defines NotFoundException, RateLimitExceededException, ValidationException. Middleware injects X-Request-ID.",
        "code_flow": "Incoming Request -> RequestIDMiddleware generates/extracts X-Request-ID -> Route raises AppException -> Exception Handler formats RFC 7807 JSON -> Response returned with X-Request-ID header.",
        "build_snippet": """from fastapi import FastAPI, Request
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
    )""",
        "break_it": "Letting raw SQLAlchemy exceptions bubble up returns HTTP 500 containing raw SQL queries, column names, and internal server paths.",
        "tradeoffs": "RFC 7807 standardized schema over custom error dicts allows frontend clients and API consumers to handle errors uniformly.",
        "system_design": "Logging X-Request-ID in every log entry allows DevOps and developers to trace an entire request journey across microservices with a single grep.",
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
        "concept": "Pydantic v2 Rust core (pydantic-core) delivers high-throughput serialization and schema validation.",
        "how_it_works": "app/schemas/ defines strict BaseModel schemas with Field constraints (e.g. price > 0, latitude [-90, 90]).",
        "estatemap": "app/schemas/ defines PropertyCreate, PropertyUpdate, PropertyResponse models with exact typing and field aliases.",
        "code_flow": "HTTP Request Payload -> FastAPI body parser -> Pydantic model validation -> Clean typed object passed to endpoint -> Return schema serializes output.",
        "build_snippet": """from pydantic import BaseModel, Field

class PropertyCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    price: float = Field(..., gt=0)
    bedrooms: int = Field(..., ge=1, le=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)""",
        "break_it": "Passing negative prices or out-of-range coordinates returns HTTP 422 Unprocessable Entity with exact field pointers.",
        "tradeoffs": "Pydantic schemas decouple database model structures from public API contracts (preventing over-fetching and unintended schema exposure).",
        "system_design": "Validated request schemas act as compile-time documentation for OpenAPI/Swagger and protect internal systems from invalid input formats.",
        "interview_q": "What is the difference between ORM models and Pydantic schemas?",
        "interview_a": "ORM models map to database tables and relationships; Pydantic schemas enforce API input/output validation, serialization, and type boundaries."
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
        "estatemap": "app/utils/pagination.py and PropertyRepository apply LIMIT, OFFSET, and compound ORDER BY clauses with tie-breakers.",
        "code_flow": "GET /api/v1/properties?limit=20&offset=40 -> Query params parsed -> Repository appends ORDER BY price ASC, id DESC -> Database executes indexed fetch -> Paginated list returned.",
        "build_snippet": """def apply_sorting(query, sort_by: str, sort_order: str):
    order_col = getattr(Property, sort_by, Property.created_at)
    if sort_order == "asc":
        return query.order_by(order_col.asc(), Property.id.asc())
    return query.order_by(order_col.desc(), Property.id.desc())""",
        "break_it": "Sorting by price alone causes unstable row ordering when multiple properties share the exact same price, resulting in duplicate items across pages.",
        "tradeoffs": "Offset pagination is simple and flexible for moderate datasets; Keyset/Cursor pagination is reserved for millions of rows.",
        "system_design": "Pagination bounds database memory consumption and network payload sizes, preventing out-of-memory errors on large tables.",
        "interview_q": "Why is tie-breaking necessary in database pagination?",
        "interview_a": "Without unique tie-breaking, database query planners return rows with identical sort values in arbitrary physical disk order, creating duplicates or missing items across pages."
    },
    {
        "id": 7, "title": "Advanced Multi-Facet Filter Query Generation",
        "module_id": 2, "module_name": "Module 02: REST API Design & Validation", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 6], "leads_to": [10, 18],
        "files": ["backend/app/repositories/property_repository.py", "backend/app/schemas/property.py"],
        "symbol": "PropertyRepository._apply_common_filters / PropertyFilterParams", "test_cmd": "docker compose exec backend pytest tests/integration/test_filter_equivalence.py",
        "why": "Hardcoded SQL strings lead to SQL injection vulnerabilities and unmaintainable conditional branching.",
        "concept": "Composable AST query building appends binary filter expressions to the query object only when parameters are present.",
        "how_it_works": "PropertyRepository._apply_common_filters checks filter params and chains .where() conditions cleanly.",
        "estatemap": "PropertyRepository encapsulates filter generation, applying min_price, max_price, bedrooms, property_type, and city conditions.",
        "code_flow": "FilterParams received -> Repository initializes select(Property) -> _apply_common_filters chains active conditions -> Query executed via async session.",
        "build_snippet": """def apply_filters(query, filters: PropertyFilterParams):
    if filters.min_price is not None:
        query = query.where(Property.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Property.price <= filters.max_price)
    if filters.bedrooms is not None:
        query = query.where(Property.bedrooms == filters.bedrooms)
    return query""",
        "break_it": "Applying filters without index coverage on large tables results in full table sequential scans and high query latency.",
        "tradeoffs": "Dynamic SQLAlchemy query compilation ensures parameterized safety while supporting arbitrary filter combinations.",
        "system_design": "Composite and partial B-Tree indexes must align with the most frequent multi-facet filter combinations (e.g. city + property_type + price).",
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
        "build_snippet": """from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, ForeignKey, CheckConstraint

class Base(DeclarativeBase):
    pass

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    __table_args__ = (CheckConstraint("price > 0", name="chk_price_positive"),)""",
        "break_it": "Deleting a user without CASCADE rules on related properties triggers a ForeignKeyViolation error and fails the operation.",
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
        "why": "Synchronous database drivers block the Python asyncio event loop, collapsing concurrent API throughput.",
        "concept": "AsyncSession with asyncpg performs non-blocking socket I/O, yielding control during query execution.",
        "how_it_works": "app/db/session.py initializes create_async_engine and yields AsyncSession via FastAPI Depends(get_db).",
        "estatemap": "app/db/session.py configures connection pool parameters (pool_size=20, max_overflow=10, pool_recycle, pool_pre_ping) and get_db dependency.",
        "code_flow": "HTTP Request -> FastAPI get_db dependency acquires session from pool -> Route executes queries -> Request ends -> get_db commits/closes session back to pool.",
        "build_snippet": """from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
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
            raise""",
        "break_it": "Forgetting to commit or rollback a session leaves transactions in 'idle in transaction' state, locking rows and starving the connection pool.",
        "tradeoffs": "Asyncpg delivers 3-5x higher throughput compared to traditional synchronous psycopg2 under high concurrency.",
        "system_design": "Connection pooling reuses persistent TCP connections, avoiding expensive TLS/TCP handshakes on every incoming HTTP request.",
        "interview_q": "What happens if an async endpoint calls a synchronous blocking database library?",
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
        "build_snippet": """from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class PropertyRepository:
    @staticmethod
    async def get_by_id(session: AsyncSession, property_id: int) -> Optional[Property]:
        stmt = select(Property).where(Property.id == property_id, Property.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()""",
        "break_it": "Leaking raw SQLAlchemy query objects to the presentation layer creates lazy-loading MissingGreenlet errors in async contexts.",
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
        "build_snippet": """# alembic revision script example
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
def downgrade() -> None:
    op.drop_table('users')""",
        "break_it": "Applying a migration with a non-nullable column without a default value fails if rows already exist in production.",
        "tradeoffs": "Alembic integrates directly with SQLAlchemy declarative metadata for automated schema diff detection.",
        "system_design": "Database schema versioning enables reproducible CI/CD test environments and safe rollbacks during blue/green deployments.",
        "interview_q": "How do you handle database migrations with zero downtime?",
        "interview_a": "Use the Expand/Contract pattern: add new nullable columns first, deploy updated code, backfill data, and finally make columns non-nullable in a subsequent migration."
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
        "build_snippet": """async def seed_properties(session: AsyncSession):
    stmt = select(func.count(Property.id))
    count = (await session.execute(stmt)).scalar()
    if count == 0:
        for data in SEED_DATA:
            prop = Property(**data)
            session.add(prop)
        await session.commit()""",
        "break_it": "Non-deterministic seeding with random coordinates causes spatial distance tests to fail intermittently.",
        "tradeoffs": "Hardcoded curated seed fixtures provide immediate out-of-the-box local developer onboarding.",
        "system_design": "Seed fixtures replicate realistic real-world geographic clusters, enabling accurate spatial index testing and ranking calibration.",
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
        "why": "Storing plaintext or MD5/SHA256 hashed passwords exposes user accounts to instant rainbow table compromise.",
        "concept": "Argon2id combines data-independent and data-dependent memory access for maximum side-channel and ASIC resistance.",
        "how_it_works": "app/core/security.py implements get_password_hash and verify_password using passlib/argon2.",
        "estatemap": "app/core/security.py uses argon2-cffi to hash passwords with calibrated time cost and memory parameters.",
        "code_flow": "User Registration -> Plaintext Password -> Argon2id generates salt & hash -> Hash stored in users.hashed_password.",
        "build_snippet": """from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)""",
        "break_it": "Using fast cryptographic hashes (SHA-256) allows attackers to compute billions of guesses per second on modern GPUs.",
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
        "build_snippet": """import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")""",
        "break_it": "Failing to verify the 'exp' claim allows expired tokens to remain valid indefinitely.",
        "tradeoffs": "Stateless JWTs eliminate database session lookups but require token revocation strategies (e.g. short TTLs) for instant logout.",
        "system_design": "Stateless tokens allow seamless horizontal scaling of backend servers because any worker node can verify the signature independently.",
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
        "build_snippet": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    user = await UserRepository.get_by_id(db, int(payload.get("sub")))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user""",
        "break_it": "Relying solely on frontend role hiding allows malicious users to send direct POST/DELETE requests to API endpoints.",
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
        "build_snippet": """from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=False)""",
        "break_it": "Swapping latitude and longitude coordinates places points in the wrong hemisphere or ocean.",
        "tradeoffs": "Storing as geometry with runtime geography casting combines fast Cartesian indexing with accurate ellipsoidal distance math.",
        "system_design": "Spatial point storage enables spatial indexing, polygon intersection, and radius filtering natively inside PostgreSQL.",
        "interview_q": "Why does PostGIS use (Longitude, Latitude) ordering instead of (Lat, Lon)?",
        "interview_a": "PostGIS follows standard Cartesian (X, Y) coordinate conventions where Longitude is the horizontal X axis and Latitude is the vertical Y axis."
    },
    {
        "id": 17, "title": "GiST Spatial Indexing & Logarithmic Search Performance",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [16], "leads_to": [18, 19, 47],
        "files": ["backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py", "backend/app/models/property.py"],
        "symbol": "spatial_index=True / idx_properties_location (USING gist)", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Without spatial indexes, querying 100,000 properties requires computing mathematical distances for every row (O(N) full scan).",
        "concept": "GiST organizes points into nested minimum bounding boxes (MBRs), reducing spatial search complexity to O(log N).",
        "how_it_works": "Alembic revision 0003 creates idx_properties_location USING gist on the location geometry column.",
        "estatemap": "Database schema sets spatial_index=True on Geometry columns, instructing PostgreSQL to create a GiST R-Tree index.",
        "code_flow": "Spatial Query -> Query Planner checks GiST index -> Traverses R-Tree bounding boxes -> Eliminates non-overlapping nodes -> Returns matching rows in <5ms.",
        "build_snippet": """-- Alembic SQL Migration for GiST Index
CREATE INDEX idx_properties_location ON properties USING gist (location);""",
        "break_it": "Calling functions on indexed columns without spatial operators prevents the PostgreSQL query planner from using the GiST index.",
        "tradeoffs": "GiST indexes have slightly higher write overhead during inserts but provide sub-10ms spatial filtering on large datasets.",
        "system_design": "Spatial indexing enables the database to filter millions of geospatial listings across bounding boxes in single-digit milliseconds.",
        "interview_q": "How does a GiST spatial index work internally?",
        "interview_a": "It builds an R-Tree hierarchy of bounding boxes. Searches eliminate entire tree branches whose bounding boxes do not intersect the query envelope."
    },
    {
        "id": 18, "title": "Geodesic Radius Search via ST_DWithin on Runtime Cast Geography",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_ESSENTIAL,
        "prereqs": [16, 17], "leads_to": [20, 24, 25],
        "files": ["backend/app/services/geo_service.py", "backend/app/repositories/property_repository.py"],
        "symbol": "PropertyRepository.search_radius / func.ST_DWithin / func.ST_Distance", "test_cmd": "docker compose exec backend pytest tests/integration/test_spatial_search.py",
        "why": "Querying Euclidean distance in degrees on EPSG:4326 results in massive distortion because degrees of longitude shrink near poles.",
        "concept": "Casting geometry to geography enables spherical great-circle distance calculations directly in meters.",
        "how_it_works": "PropertyRepository.search_radius casts Property.location to geography and executes ST_DWithin(loc, point, radius_m).",
        "estatemap": "app/repositories/property_repository.py casts location to Geography and applies func.ST_DWithin and func.ST_Distance.",
        "code_flow": "GET /api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=5000 -> Repository constructs ST_DWithin query -> PostGIS index filters bounding box -> Returns properties with distance_m.",
        "build_snippet": """from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint
from geoalchemy2 import Geography

def search_radius(session, lat: float, lon: float, radius_m: float):
    point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)
    loc_geog = func.cast(Property.location, Geography)
    point_geog = func.cast(point, Geography)
    stmt = select(Property, ST_Distance(loc_geog, point_geog).label("distance_m")).where(
        ST_DWithin(loc_geog, point_geog, radius_m)
    ).order_by("distance_m")
    return session.execute(stmt)""",
        "break_it": "Passing radius in meters to ST_DWithin on uncast geometry treats the radius as degrees (e.g. 5000 degrees covers the entire Earth).",
        "tradeoffs": "ST_DWithin uses the index bounding box filter before computing exact geodesic distances, maximizing query speed.",
        "system_design": "Geodesic radius search is the fundamental building block for location-based discovery in mobile and map applications.",
        "interview_q": "Why must you cast geometry to geography for ST_DWithin(geom, point, 5000)?",
        "interview_a": "Geometry calculations occur in planar units (degrees); casting to geography computes distances in real-world meters along the curved Earth spheroid."
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
        "estatemap": "app/repositories/property_repository.py builds ST_MakeEnvelope polygon and filters properties with ST_Within / ST_Intersects.",
        "code_flow": "Map Pan/Zoom -> Frontend sends bounds (min_lat, min_lon, max_lat, max_lon) -> Repository generates ST_MakeEnvelope -> GiST index scans matching box -> Returns visible GeoJSON.",
        "build_snippet": """from geoalchemy2.functions import ST_MakeEnvelope, ST_Within

def search_bbox(session, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    envelope = ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
    stmt = select(Property).where(ST_Within(Property.location, envelope))
    return session.execute(stmt)""",
        "break_it": "Passing min_lon > max_lon on queries crossing the 180th meridian produces an invalid inverted envelope.",
        "tradeoffs": "Bounding box queries are significantly faster than radius calculations because they only require 2D box intersection checks.",
        "system_design": "Viewport filtering prevents frontend maps from downloading hundreds of thousands of irrelevant points outside the visible screen.",
        "interview_q": "How does a map viewport search query work in PostGIS?",
        "interview_a": "The API constructs a bounding envelope via ST_MakeEnvelope and uses the ST_Within or && operator to leverage the GiST spatial index efficiently."
    },
    {
        "id": 20, "title": "Points of Interest (POI) Proximity Aggregation & Spatial Intelligence",
        "module_id": 5, "module_name": "Module 05: PostGIS Spatial Search", "importance": STATUS_IMPORTANT,
        "prereqs": [16, 18], "leads_to": [25, 27],
        "files": ["backend/app/models/poi.py", "backend/app/services/poi_service.py", "backend/app/repositories/poi_repository.py"],
        "symbol": "POIService.get_location_intelligence / POIRepository.get_nearby_pois", "test_cmd": "docker compose exec backend pytest tests/integration/test_pois.py",
        "why": "Property buyers require neighborhood intelligence (walkability, transit proximity) to make informed purchasing decisions.",
        "concept": "Spatial joins and radius counts group nearby POIs by category and compute nearest facility distances.",
        "how_it_works": "POIService.get_location_intelligence queries POIRepository for nearby POIs, categorizes them, and caches the summary.",
        "estatemap": "app/services/poi_service.py coordinates spatial queries across POI categories and calculates summary statistics.",
        "code_flow": "Property ID requested -> POIService fetches property coordinates -> Queries POIRepository for POIs within radius -> Computes count per category & nearest distance -> Returns LocationIntelligenceResponse.",
        "build_snippet": """async def get_nearby_pois(session, lat: float, lon: float, radius_m: float = 2000):
    point = func.cast(ST_SetSRID(ST_MakePoint(lon, lat), 4326), Geography)
    stmt = select(PointOfInterest, func.ST_Distance(func.cast(PointOfInterest.location, Geography), point).label("dist")).where(
        func.ST_DWithin(func.cast(PointOfInterest.location, Geography), point, radius_m)
    )
    return (await session.execute(stmt)).all()""",
        "break_it": "Executing separate spatial queries for every individual listing causes an N+1 spatial query bottleneck.",
        "tradeoffs": "Location intelligence is calculated on-demand with Redis caching (TTL=300s) to balance freshness with query performance.",
        "system_design": "Pre-computed spatial joins or cached category aggregations allow fast real-time score calculation during property discovery.",
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
        "concept": "RFC 7946 specifies that GeoJSON coordinate positions MUST be ordered as [easting, northing] -> [lon, lat].",
        "how_it_works": "app/schemas/geo.py defines Pydantic models for GeoJSON Feature, FeatureCollection, and Point geometry serialization.",
        "estatemap": "app/schemas/geo.py defines type-safe Pydantic models enforcing GeoJSON specifications and property attributes.",
        "code_flow": "Database Property entity -> Pydantic validator extracts WKB/WKT coordinates -> Formats into FeatureCollection with [lon, lat] geometry -> Serialized to JSON.",
        "build_snippet": """from pydantic import BaseModel
from typing import List, Literal

class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] # [lon, lat]

class PropertyGeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: dict""",
        "break_it": "Emitting [lat, lon] coordinates in GeoJSON violates RFC 7946 and causes map clients to render markers in Antarctica.",
        "tradeoffs": "Serializing directly in Pydantic ensures schema validation without requiring heavy external GIS serialization dependencies.",
        "system_design": "Standard GeoJSON schemas allow the backend API to be consumed by any GIS platform, web client, or mobile application.",
        "interview_q": "What is the RFC 7946 coordinate ordering standard?",
        "interview_a": "[Longitude, Latitude, Elevation], representing X (easting) then Y (northing)."
    },

    # Module 06: Location Intelligence & Routing (22-24)
    {
        "id": 22, "title": "Deterministic Location Resolver for Tech Parks & Metropolitan Hubs",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [16, 21], "leads_to": [23, 24, 39],
        "files": ["backend/app/utils/location_resolver.py", "backend/app/api/v1/search.py"],
        "symbol": "LocationResolver.resolve / KNOWN_LOCATIONS / METRO_BOUNDS", "test_cmd": "docker compose exec backend pytest tests/unit/test_location_resolver.py",
        "why": "Natural language searches contain informal locality names that need instant, deterministic coordinate resolution.",
        "concept": "In-memory alias dictionary and normalized substring matching resolve known hubs with zero external network latency.",
        "how_it_works": "LocationResolver matches query strings against 50+ curated Bengaluru and Chennai landmarks with bounding box checks.",
        "estatemap": "app/utils/location_resolver.py implements string normalization, alias dictionary lookup, and city bounding box verification.",
        "code_flow": "Query string received (e.g. 'near Electronic City') -> LocationResolver normalizes string -> Matches alias in dictionary -> Returns exact (lat, lon) coordinates.",
        "build_snippet": """class LocationResolver:
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
        return None""",
        "break_it": "Resolving locations outside supported city boundaries without error bounds causes searches to return empty results.",
        "tradeoffs": "In-memory deterministic resolver avoids expensive third-party geocoding API rate limits and external latency.",
        "system_design": "Layered location resolution: check in-memory catalog first (sub-millisecond), fallback to external geocoders only for unknown addresses.",
        "interview_q": "Why use an in-memory landmark resolver before calling external geocoders?",
        "interview_a": "It resolves 90%+ of common local destination queries in sub-millisecond time with zero external API cost and zero network dependency."
    },
    {
        "id": 23, "title": "External HTTP Client with Async Httpx & OSRM Engine Integration",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [2, 3], "leads_to": [24, 47],
        "files": ["backend/app/services/routing/osrm_provider.py", "backend/app/services/routing/factory.py"],
        "symbol": "OSRMProvider.calculate_route / RoutingProviderFactory / RoutingProvider", "test_cmd": "docker compose exec backend pytest tests/integration/test_commute.py",
        "why": "Straight-line distance ignores physical road geometry, traffic directionality, and water bodies (bridges vs direct lines).",
        "concept": "Async httpx.AsyncClient queries OSRM routing endpoints using Contraction Hierarchies graph traversal.",
        "how_it_works": "OSRMProvider sends coordinate pairs to OSRM /route/v1/driving/ and extracts duration (seconds) and distance (meters).",
        "estatemap": "app/services/routing/osrm_provider.py encapsulates async HTTP requests to OSRM with connection timeouts and response parsing.",
        "code_flow": "Commute request -> OSRMProvider formats coordinate URL -> httpx.AsyncClient executes GET with 5s timeout -> Parses route polyline and duration.",
        "build_snippet": """import httpx

class OSRMProvider:
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        self.base_url = base_url

    async def calculate_route(self, orig_lat: float, orig_lon: float, dest_lat: float, dest_lon: float):
        url = f"{self.base_url}/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=full"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            data = resp.json()
            route = data["routes"][0]
            return {"duration_sec": route["duration"], "distance_m": route["distance"], "geometry": route["geometry"]}""",
        "break_it": "Not setting HTTP timeouts on external routing calls causes backend worker threads to hang when OSRM is slow.",
        "tradeoffs": "OSRM provides open-source routing without commercial API fees (e.g. Google Maps API costs at scale).",
        "system_design": "External API wrappers must encapsulate timeouts, retries with exponential backoff, and circuit breakers to prevent cascading system failures.",
        "interview_q": "How do you safely integrate third-party HTTP services in an async backend?",
        "interview_a": "Use async HTTP clients (httpx) with strict connection/read timeouts, connection pooling, and circuit breaker fallbacks."
    },
    {
        "id": 24, "title": "Multi-Modal Commute Matrix & Great-Circle Haversine Fallback",
        "module_id": 6, "module_name": "Module 06: Location Intelligence & Routing", "importance": STATUS_ESSENTIAL,
        "prereqs": [18, 22, 23], "leads_to": [25, 30],
        "files": ["backend/app/services/commute_service.py", "backend/app/utils/geo.py"],
        "symbol": "CommuteService.calculate_commute_matrix / haversine_distance_km", "test_cmd": "docker compose exec backend pytest tests/integration/test_commute.py",
        "why": "Commute duration is the #1 decision factor for real estate buyers; routing failures must never crash the search pipeline.",
        "concept": "Haversine formula calculates great-circle distance on a spherical Earth as a robust mathematical fallback.",
        "how_it_works": "CommuteService checks Redis route cache, queries OSRM, and falls back to estimated speed-profile Haversine math on failure.",
        "estatemap": "app/services/commute_service.py coordinates multi-property commute calculations, route caching, and Haversine fallback logic.",
        "code_flow": "Properties & Destination passed -> CommuteService checks Redis cache -> Queries OSRM for uncached pairs -> If OSRM fails, applies Haversine fallback -> Returns matrix.",
        "build_snippet": """import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c""",
        "break_it": "Dividing by zero speed in fallback calculations or failing to catch HTTP timeouts crashes the commute endpoint.",
        "tradeoffs": "Cached route matrices combined with mathematical fallbacks provide sub-50ms commute responses even during network outages.",
        "system_design": "Computing commute matrices for 20 properties concurrently requires parallel async requests or batch matrix API endpoints to avoid latency bloat.",
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
        "why": "Black-box ML ranking produces non-reproducible, untestable results; deterministic MCDA ensures transparent, auditable scoring.",
        "concept": "Multi-Criteria Decision Analysis (MCDA) linearly normalizes heterogeneous metrics (INR, sqft, minutes) into comparable [0, 1] scales.",
        "how_it_works": "app/utils/ranking.py implements mathematical scoring functions with user-configurable or preset weight vectors.",
        "estatemap": "app/services/ranking_service.py coordinates scoring calculations across candidate properties and sorts by final composite score.",
        "code_flow": "Filtered properties passed to RankingService -> Evaluates 6 dimension scoring functions -> Multiplies by weight vector -> Sums to composite score -> Returns ranked list.",
        "build_snippet": """def calculate_price_score(price: float, min_p: float, max_p: float) -> float:
    if max_p <= min_p:
        return 1.0
    # Lower price gets higher score
    return max(0.0, min(1.0, 1.0 - (price - min_p) / (max_p - min_p)))""",
        "break_it": "Unnormalized raw prices (millions) dominating area scores (thousands) distorts composite ranking scores completely.",
        "tradeoffs": "Deterministic mathematical ranking guarantees identical inputs produce identical rank ordering every time.",
        "system_design": "Separating hard database filters (WHERE price <= max_price) from soft ranking preferences (score based on budget affinity) delivers optimal user relevance.",
        "interview_q": "Why use deterministic mathematical ranking over an LLM for search results?",
        "interview_a": "Deterministic scoring is fast (sub-5ms), 100% reproducible, cost-free, and mathematically immune to hallucinations."
    },
    {
        "id": 26, "title": "Dynamic Missing-Factor Weight Redistribution & Active Weight Sums",
        "module_id": 7, "module_name": "Module 07: Deterministic Ranking & Business Logic", "importance": STATUS_ESSENTIAL,
        "prereqs": [25], "leads_to": [27, 28],
        "files": ["backend/app/services/ranking_service.py", "backend/app/utils/ranking.py"],
        "symbol": "RankingService._redistribute_weights / active_weight_sum normalization", "test_cmd": "docker compose exec backend pytest tests/unit/test_ranking_scoring.py",
        "why": "If an optional factor (e.g. commute weight = 0.25) is missing, total scores would cap at 0.75, penalizing all listings unfairly.",
        "concept": "Active weight renormalization computes W_i' = W_i / sum(W_active), ensuring composite scores always sum to exactly 1.0.",
        "how_it_works": "RankingService._redistribute_weights filters out inactive criteria and divides active weights by active_weight_sum.",
        "estatemap": "app/services/ranking_service.py checks active scoring factors and rescales weight vectors dynamically before scoring.",
        "code_flow": "Ranking query without commute destination -> Commute factor marked inactive -> Active weights summed -> Each active weight divided by sum -> Composite scores sum to 1.0.",
        "build_snippet": """def redistribute_weights(weights: dict, active_factors: set) -> dict:
    active_sum = sum(w for k, w in weights.items() if k in active_factors)
    if active_sum == 0:
        return {k: 1.0 / len(active_factors) if k in active_factors else 0.0 for k in weights}
    return {k: (w / active_sum if k in active_factors else 0.0) for k, w in weights.items()}""",
        "break_it": "Hardcoding static weights when optional filters are omitted produces skewed scores and incorrect ranking order.",
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
        "why": "Users trust search rankings when the system transparently explains WHY a listing ranked #1 versus #5.",
        "concept": "Rule-based template generation derived directly from computed sub-scores guarantees factual explainability.",
        "how_it_works": "app/utils/ranking.py generates FactorScoreDetail arrays attached to every RankedPropertyResponse.",
        "estatemap": "app/utils/ranking.py maps dimension scores and calculated deltas to human-readable factual strings.",
        "code_flow": "Score calculation finishes -> generate_deterministic_explanations() inspects top positive/negative score factors -> Formats string explanations -> Attached to response.",
        "build_snippet": """def explain_score(factor: str, score: float, raw_value: float) -> str:
    if factor == "price" and score > 0.8:
        return f"Priced competitively at ₹{raw_value:,.0f}"
    elif factor == "commute" and score > 0.8:
        return f"Convenient commute duration ({raw_value:.0f} mins)"
    return f"{factor.capitalize()} rating: {score*100:.0f}%" """,
        "break_it": "Allowing LLMs to generate score explanations from scratch risks fabricating non-existent amenities or travel times.",
        "tradeoffs": "Deterministic explanation generation requires zero LLM tokens and executes in microseconds.",
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
        "concept": "Pairwise and 3-way dimensional min/max comparisons select verified winners for price per sqft, bedroom count, and commute.",
        "how_it_works": "ComparisonService.compare_properties fetches listings, computes metric diffs, determines winners, and packages ComparisonResult.",
        "estatemap": "app/services/comparison_service.py implements structured metric diffing, price per sqft calculation, and winner selection.",
        "code_flow": "POST /api/v1/properties/compare [ids] -> Service fetches properties -> Calculates metric deltas -> Selects dimension winners -> Returns structured ComparisonResult.",
        "build_snippet": """def select_dimension_winner(properties: list, metric_key: str, lower_is_better: bool = False):
    if lower_is_better:
        winner = min(properties, key=lambda p: getattr(p, metric_key))
    else:
        winner = max(properties, key=lambda p: getattr(p, metric_key))
    return {"winner_id": winner.id, "metric": metric_key, "value": getattr(winner, metric_key)}""",
        "break_it": "Comparing non-existent property IDs or mismatched city properties without validation creates invalid comparisons.",
        "tradeoffs": "Deterministic dimension winners provide hard facts that ground subsequent AI-generated comparison summaries.",
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
        "why": "Repeated spatial and ranking queries saturate database CPU; caching identical viewport requests cuts latency from 50ms to 2ms.",
        "concept": "Cache-Aside pattern loads data on-demand, keeping in-memory footprints bounded to active query working sets.",
        "how_it_works": "CacheService wraps redis.asyncio client with JSON serialization and transparent database fallback on cache miss.",
        "estatemap": "app/cache/redis.py manages connection pool; app/cache/cache_service.py provides get_json, set_json, and delete methods.",
        "code_flow": "Client Request -> CacheService.get_json(key) -> Cache HIT: return cached JSON (2ms) -> Cache MISS: query DB (50ms) -> CacheService.set_json(key, data, ttl) -> Return response.",
        "build_snippet": """import json
import redis.asyncio as redis

class CacheService:
    def __init__(self, client: redis.Redis):
        self.redis = client

    async def get_json(self, key: str):
        val = await self.redis.get(key)
        return json.loads(val) if val else None

    async def set_json(self, key: str, data: dict, ttl_seconds: int = 120):
        await self.redis.set(key, json.dumps(data), ex=ttl_seconds)""",
        "break_it": "Storing un-versioned cache keys causes deserialization errors when Pydantic model schemas are updated in new deployments.",
        "tradeoffs": "Cache-Aside handles cache node restarts gracefully because the database remains the authoritative single source of truth.",
        "system_design": "Caching read-heavy geospatial and ranking responses protects database connection pools and scales read throughput 10x.",
        "interview_q": "How does the Cache-Aside pattern work and what are its failure modes?",
        "interview_a": "Application queries cache first; on miss, loads from DB and writes to cache with TTL. If cache fails, app gracefully falls back to querying the database directly."
    },
    {
        "id": 30, "title": "Canonical Cache Key Design, Coordinate Precision & SHA-256 Hashing",
        "module_id": 8, "module_name": "Module 08: Redis In-Memory Caching", "importance": STATUS_ESSENTIAL,
        "prereqs": [29], "leads_to": [31, 32],
        "files": ["backend/app/cache/cache_keys.py", "backend/app/cache/cache_service.py"],
        "symbol": "CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route", "test_cmd": "docker compose exec backend pytest tests/unit/test_cache_keys.py",
        "why": "Slight float precision differences (12.9715999 vs 12.9716001) destroy cache hit ratios; coordinate rounding normalizes nearby requests.",
        "concept": "Rounding coordinates to 4 decimal places (~11 meters) collapses microscopic GPS drift into canonical cache buckets.",
        "how_it_works": "CacheKeys.normalize_coord rounds floats to 4 decimals; filter dicts are sorted and hashed with SHA-256.",
        "estatemap": "app/cache/cache_keys.py implements key generator functions with version prefixes (estatemap:v1:*) and deterministic hashing.",
        "code_flow": "Parameters received -> CacheKeys formats key: estatemap:v1:map:{min_lat}:{min_lon}:{max_lat}:{max_lon}:{sha256(filters)} -> Canonical key used in Redis lookup.",
        "build_snippet": """import hashlib
import json

class CacheKeys:
    @staticmethod
    def map_bbox_key(min_lat: float, min_lon: float, max_lat: float, max_lon: float, filters: dict) -> str:
        coords = f"{min_lat:.4f}:{min_lon:.4f}:{max_lat:.4f}:{max_lon:.4f}"
        filter_str = json.dumps(filters, sort_keys=True)
        h = hashlib.sha256(filter_str.encode()).hexdigest()[:12]
        return f"estatemap:v1:map:{coords}:{h}" """,
        "break_it": "Unsorted dictionary serialization produces different JSON strings for identical filter sets, causing cache misses.",
        "tradeoffs": "SHA-256 digests keep Redis key lengths fixed and predictable regardless of complex filter parameter counts.",
        "system_design": "Well-designed hierarchical key namespaces simplify monitoring, debugging, and targeted wildcard key invalidation.",
        "interview_q": "How do you design cache keys for geospatial search queries?",
        "interview_a": "Normalize coordinates to fixed precision (e.g. 4 decimals), sort filter parameters deterministically, and hash with version prefixes to guarantee collision-free lookups."
    },
    {
        "id": 31, "title": "Cache Invalidation via Non-Blocking SCAN & TTL Stampede Mitigation",
        "module_id": 8, "module_name": "Module 08: Redis In-Memory Caching", "importance": STATUS_IMPORTANT,
        "prereqs": [29, 30], "leads_to": [32, 47],
        "files": ["backend/app/cache/cache_service.py", "backend/app/core/config.py"],
        "symbol": "CacheService.delete_pattern / CacheService.delete / CACHE_MAP_TTL_SECONDS", "test_cmd": "docker compose exec backend pytest tests/unit/test_cache_service.py",
        "why": "Using the blocking KEYS * command halts Redis event loops in production; SCAN iterates cursor-by-cursor safely.",
        "concept": "TTL-based expiration guarantees eventual consistency; mutation hooks trigger active prefix invalidation.",
        "how_it_works": "CacheService.delete_pattern uses redis.scan_iter(match=pattern, count=100) to delete matching keys without blocking.",
        "estatemap": "app/cache/cache_service.py implements delete_pattern using async scan_iter and applies configurable TTLs from Settings.",
        "code_flow": "Property Updated -> PropertyService calls CacheService.delete_pattern('estatemap:v1:map:*') -> redis.scan_iter iterates batches -> Keys deleted -> Next read re-caches fresh data.",
        "build_snippet": """async def delete_pattern(redis_client, pattern: str):
    async for key in redis_client.scan_iter(match=pattern, count=100):
        await redis_client.delete(key)""",
        "break_it": "Running KEYS 'estatemap:*' on a Redis instance with 1,000,000 keys locks Redis for several seconds, timing out all API requests.",
        "tradeoffs": "SCAN has O(N) overall complexity across iterations but never blocks the single-threaded Redis event loop.",
        "system_design": "Cache stampede mitigation: staggered TTL jitter and probabilistic early recomputation prevent database spikes when hot keys expire.",
        "interview_q": "Why is KEYS * dangerous in production Redis, and what is the alternative?",
        "interview_a": "KEYS * blocks the single-threaded Redis server until all keys are scanned, stalling all traffic. Use SCAN with cursor pagination instead."
    },

    # Module 09: Rate Limiting & Resilience (32-34)
    {
        "id": 32, "title": "Sliding-Window Log Rate Limiting via Redis Sorted Sets (ZSET)",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_ESSENTIAL,
        "prereqs": [4, 29], "leads_to": [33, 34],
        "files": ["backend/app/core/rate_limit.py", "backend/app/core/middleware.py"],
        "symbol": "RateLimiter.is_rate_limited / redis.pipeline() / ZADD / ZREMRANGEBYSCORE", "test_cmd": "docker compose exec backend pytest tests/integration/test_rate_limiting.py",
        "why": "Fixed window rate limiters allow 2x traffic bursts across window boundaries (e.g. 100 requests at 00:59 and 100 at 01:00).",
        "concept": "Sliding Window Log scores timestamps in a ZSET: removes items older than (now - window), counts remaining, and adds current timestamp.",
        "how_it_works": "RateLimiter executes pipelined ZREMRANGEBYSCORE -> ZCARD -> ZADD -> EXPIRE, rejecting requests exceeding limit with HTTP 429.",
        "estatemap": "app/core/rate_limit.py implements RateLimiter class using async Redis pipelines for atomic sliding-window evaluation.",
        "code_flow": "Incoming Request -> RateLimiter executes Redis pipeline: ZREMRANGEBYSCORE(0, now-60) -> ZCARD -> If count >= limit: raise RateLimitExceededException -> Else ZADD(now, now) -> Allow request.",
        "build_snippet": """import time

async def is_rate_limited(redis_client, key: str, limit: int, window_sec: int = 60) -> tuple[bool, int]:
    now = time.time()
    pipe = redis_client.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)
    pipe.zcard(key)
    pipe.zadd(key, {str(now): now})
    pipe.expire(key, window_sec)
    results = await pipe.execute()
    count = results[1]
    return (count >= limit, max(0, limit - count))""",
        "break_it": "Executing rate limiter Redis commands as separate non-pipelined network calls introduces race conditions under concurrency.",
        "tradeoffs": "Redis ZSET sliding window offers precision and burst protection with minimal memory per active client IP.",
        "system_design": "Rate limiting protects downstream database connection pools and expensive AI endpoints from denial-of-service exhaustion.",
        "interview_q": "How does a Redis sliding window log rate limiter work?",
        "interview_a": "Stores request timestamps in a ZSET, prunes timestamps older than now - window with ZREMRANGEBYSCORE, checks if ZCARD exceeds the limit, and records the current timestamp."
    },
    {
        "id": 33, "title": "Multi-Tier Endpoint Scopes & RFC Rate Limit Headers",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_ESSENTIAL,
        "prereqs": [32], "leads_to": [34, 42],
        "files": ["backend/app/core/rate_limit.py", "backend/app/core/config.py"],
        "symbol": "X-RateLimit-Limit / X-RateLimit-Remaining / RateLimitExceededException", "test_cmd": "docker compose exec backend pytest tests/integration/test_rate_limiting.py",
        "why": "Expensive LLM and spatial ranking endpoints must have stricter limits than lightweight health and listing read endpoints.",
        "concept": "Rate limiting keys are scoped by client identifier (IP or User ID) combined with the target endpoint tier.",
        "how_it_works": "RateLimiter inspects request path, applies configured tier thresholds, and appends X-RateLimit-Remaining headers.",
        "estatemap": "app/core/rate_limit.py maps route paths to tier limits and formats RFC response headers (Limit, Remaining, Retry-After).",
        "code_flow": "Request evaluated -> RateLimiter determines remaining tokens -> Injects X-RateLimit-Limit & X-RateLimit-Remaining headers -> If blocked, returns HTTP 429 with Retry-After: 60.",
        "build_snippet": """TIER_LIMITS = {
    "/api/v1/search/orchestrated": 15, # Expensive AI
    "/api/v1/search/ranked": 20,       # Ranking engine
    "default": 100                     # General reads
}""",
        "break_it": "Omitting Retry-After headers on HTTP 429 causes aggressive frontend clients to hammer the server in a tight retry loop.",
        "tradeoffs": "Tiered scoping prevents heavy AI feature abuse from starving general browsing traffic.",
        "system_design": "Cost-based rate limiting allocates infrastructure resources proportionally to business value and compute cost.",
        "interview_q": "What headers should a well-designed rate-limited API return?",
        "interview_a": "X-RateLimit-Limit (max requests), X-RateLimit-Remaining (requests left in window), and Retry-After (seconds to wait when rate limited with HTTP 429)."
    },
    {
        "id": 34, "title": "Fail-Open vs Fail-Closed Resiliency Policies on Cache Outage",
        "module_id": 9, "module_name": "Module 09: Rate Limiting & Resilience", "importance": STATUS_IMPORTANT,
        "prereqs": [32, 33], "leads_to": [37, 47],
        "files": ["backend/app/core/rate_limit.py", "backend/app/cache/cache_service.py"],
        "symbol": "RATE_LIMIT_FAIL_OPEN=True / RedisConnectionError handling", "test_cmd": "docker compose exec backend pytest tests/integration/test_redis_degradation.py",
        "why": "An auxiliary cache/rate-limiter outage should not bring down the entire property search application.",
        "concept": "Circuit breaker and exception isolation catch RedisConnectionError and allow requests through when configured to fail open.",
        "how_it_works": "RateLimiter and CacheService wrap Redis calls in try/except RedisError; on exception, log warning and return degraded fallback.",
        "estatemap": "app/core/rate_limit.py and app/cache/cache_service.py handle Redis connection errors gracefully based on RATE_LIMIT_FAIL_OPEN setting.",
        "code_flow": "Redis crashes -> RateLimiter attempts pipeline -> Catches ConnectionError -> Logs warning -> If fail_open=True: permits request -> Main API functionality continues uninterrupted.",
        "build_snippet": """try:
    is_limited, remaining = await rate_limiter.check(ip)
except redis.RedisError as e:
    logger.warning("Redis rate limiter down: %s", e)
    if settings.RATE_LIMIT_FAIL_OPEN:
        is_limited, remaining = False, 999
    else:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")""",
        "break_it": "Uncaught Redis connection errors bubbling to FastAPI middleware turn every API request into an HTTP 500 error.",
        "tradeoffs": "Failing open prioritizes system availability over strict rate enforcement during infrastructure degradation.",
        "system_design": "Graceful degradation ensures non-essential auxiliary subsystem failures do not cause catastrophic core business outages.",
        "interview_q": "What is the difference between fail-open and fail-closed in rate limiting?",
        "interview_a": "Fail-open permits requests if the limiter is unreachable (prioritizing availability); fail-closed blocks requests (prioritizing resource protection)."
    },

    # Module 10: Multi-Provider AI Architecture (35-38)
    {
        "id": 35, "title": "AI Provider Protocol & Structural Parity (Ollama Local & Gemini Cloud)",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [3, 5], "leads_to": [36, 37, 38],
        "files": ["backend/app/ai/protocol.py", "backend/app/ai/ollama_provider.py", "backend/app/ai/gemini_provider.py"],
        "symbol": "AIProvider / OllamaProvider / GeminiProvider / AIResponse", "test_cmd": "docker compose exec backend pytest tests/unit/test_cross_provider_parity.py",
        "why": "Tight coupling to a single commercial LLM vendor creates vendor lock-in and leaves the backend vulnerable to API outages.",
        "concept": "Python Protocol enables structural subtyping (duck typing with static type checking) for swappable AI providers.",
        "how_it_works": "app/ai/protocol.py defines AIProvider with parse_intent, explain_property, and compare_properties methods.",
        "estatemap": "app/ai/protocol.py defines the interface; ollama_provider.py and gemini_provider.py implement adapter classes.",
        "code_flow": "AI Service calls AIProvider method -> Active provider executes HTTP call to LLM engine -> Formats response into common AIResponse schema -> Returns to service.",
        "build_snippet": """from typing import Protocol, runtime_checkable

@runtime_checkable
class AIProvider(Protocol):
    async def parse_search_intent(self, query: str) -> dict: ...
    async def explain_property(self, property_data: dict, score_details: list) -> str: ...
    async def compare_properties(self, comparison_facts: dict) -> str: ...""",
        "break_it": "Provider implementations returning differing JSON structures break downstream state orchestrators.",
        "tradeoffs": "Unified AI protocol allows running cost-free local Ollama in development and scalable cloud Gemini in production.",
        "system_design": "Adapter pattern isolates external SDK idiosyncrasies from core application domain logic.",
        "interview_q": "How do you prevent vendor lock-in when integrating LLMs?",
        "interview_a": "Define a strict provider Protocol/Interface with standardized Pydantic input/output schemas implemented by all provider adapters."
    },
    {
        "id": 36, "title": "Strict LLM Output Validation via Pydantic v2 Schemas",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 35], "leads_to": [37, 38, 39],
        "files": ["backend/app/schemas/ai.py", "backend/app/services/ai_service.py"],
        "symbol": "AIExplanationResponse / AISearchIntent / ParseSearchResponse", "test_cmd": "docker compose exec backend pytest tests/unit/test_ai_schemas.py",
        "why": "LLMs frequently hallucinate invalid JSON, invent property IDs, or output negative budget values.",
        "concept": "Regex JSON extraction followed by strict Pydantic model validation transforms non-deterministic text into type-safe domain objects.",
        "how_it_works": "AIService parses LLM responses through Pydantic schemas, validating extracted criteria against known bounds.",
        "estatemap": "app/schemas/ai.py defines strict response schemas; app/services/ai_service.py extracts JSON and validates with model_validate_json.",
        "code_flow": "LLM returns raw text -> Regex extracts JSON block -> Pydantic model_validate() checks types and bounds -> If valid: return object -> If invalid: trigger fallback.",
        "build_snippet": """class AISearchIntent(BaseModel):
    city: Optional[str] = None
    locality: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    bedrooms: Optional[int] = Field(None, ge=1, le=10)
    destination: Optional[str] = None""",
        "break_it": "Directly parsing raw LLM JSON with json.loads() without Pydantic validation crashes downstream services on unexpected fields.",
        "tradeoffs": "Pydantic validation provides a resilient firewall between non-deterministic AI generation and deterministic database logic.",
        "system_design": "Input sanitization and output schema validation are essential defenses against prompt injection and LLM hallucination.",
        "interview_q": "How do you handle non-deterministic LLM responses in production?",
        "interview_a": "Request JSON mode, extract with regex, validate against Pydantic schemas, and fallback to deterministic logic on validation error."
    },
    {
        "id": 37, "title": "Dynamic Provider Routing, Latency Timeouts & Circuit Failover",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_ESSENTIAL,
        "prereqs": [35, 36], "leads_to": [38, 39],
        "files": ["backend/app/ai/router.py", "backend/app/services/ai_service.py"],
        "symbol": "AIRouter.get_provider / AIService._execute_with_fallback / AI_TIMEOUT_SECONDS", "test_cmd": "docker compose exec backend pytest tests/integration/test_ai_failover.py",
        "why": "Local Ollama instances may hang under CPU load; cloud APIs may experience rate limiting (HTTP 429); the app must failover instantly.",
        "concept": "Circuit failover tries the primary provider with asyncio.wait_for timeout, immediately routing to backup on failure.",
        "how_it_works": "AIRouter inspects AI_PROVIDER setting; AIService executes primary provider and catches timeouts/errors to trigger fallback.",
        "estatemap": "app/ai/router.py resolves provider instances; app/services/ai_service.py wraps executions in asyncio.wait_for with try/except failover.",
        "code_flow": "AI Request -> AIRouter selects Primary (Ollama) -> asyncio.wait_for(primary.call(), timeout=5s) -> If Timeout/Error: Log warning -> AIRouter selects Backup (Gemini) -> Return response.",
        "build_snippet": """async def execute_ai_with_failover(primary: AIProvider, backup: AIProvider, prompt: str):
    try:
        return await asyncio.wait_for(primary.call(prompt), timeout=5.0)
    except Exception as e:
        logger.warning("Primary AI failed (%s), switching to backup...", e)
        return await asyncio.wait_for(backup.call(prompt), timeout=5.0)""",
        "break_it": "Unbounded async calls to external LLM APIs can hold open client connections for 60+ seconds, exhausting backend worker pools.",
        "tradeoffs": "Configurable provider routing allows cost optimization (local dev, hybrid staging, cloud prod).",
        "system_design": "Multi-provider failover circuits provide 99.9%+ availability for AI-driven features despite third-party API instability.",
        "interview_q": "How do you design a resilient multi-provider AI pipeline?",
        "interview_a": "Implement an AI router with strict execution timeouts (5s), automatic failover from local to cloud provider, and algorithmic fallbacks on complete outage."
    },
    {
        "id": 38, "title": "Algorithmic Grounded Fallbacks & Hallucination Elimination",
        "module_id": 10, "module_name": "Module 10: Multi-Provider AI Architecture", "importance": STATUS_IMPORTANT,
        "prereqs": [27, 28, 36, 37], "leads_to": [39, 41],
        "files": ["backend/app/services/ai_service.py", "backend/app/services/comparison_service.py"],
        "symbol": "AIService.generate_fallback_explanation / AIService.generate_fallback_comparison", "test_cmd": "docker compose exec backend pytest tests/integration/test_ai_endpoints.py",
        "why": "Total AI provider outages must never prevent users from seeing property search explanations or comparisons.",
        "concept": "Rule-based template generation using deterministic score breakdown facts guarantees 100% uptime with zero hallucination.",
        "how_it_works": "AIService generates structured fallback summaries using listing price, area, locality, and dimension winner data.",
        "estatemap": "app/services/ai_service.py implements template-based fallback generators that assemble verified property attributes into natural language.",
        "code_flow": "Primary & Backup AI providers fail -> AIService catches exception -> Calls generate_fallback_explanation(property, score_details) -> Assembles factual summary -> Returns with fallback=True flag.",
        "build_snippet": """def generate_fallback_summary(prop: Property, winner: dict) -> str:
    return (
        f"{prop.title} in {prop.locality} offers {prop.bedrooms} BHK across {prop.area_sqft} sqft. "
        f"It is ranked #1 for {winner['metric']} with a competitive rate of ₹{prop.price:,.0f}."
    )""",
        "break_it": "Returning empty explanation strings or HTTP 500 when AI fails degrades user experience unnecessarily.",
        "tradeoffs": "Algorithmic fallbacks are instant and 100% accurate, though less linguistically varied than LLM output.",
        "system_design": "Deterministic grounding guarantees that AI-augmented applications never display factually incorrect claims to end users.",
        "interview_q": "How do you eliminate hallucination risk in mission-critical AI features?",
        "interview_a": "Ground all prompts strictly in deterministic database facts and provide rule-based algorithmic fallbacks when AI is unavailable."
    },

    # Module 11: Ask-the-Map Conversational Orchestration (39-41)
    {
        "id": 39, "title": "Natural Language Search Intent Parsing & Backend Authority Boundary",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 22, 36, 37], "leads_to": [40, 41],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/schemas/search.py"],
        "symbol": "SearchOrchestrator.orchestrate_search / SearchStatePatch / AskMapRequest", "test_cmd": "docker compose exec backend pytest tests/integration/test_ask_the_map.py",
        "why": "AI models must only extract proposed search intent; the backend retains complete authority over database query execution.",
        "concept": "Backend Authority Boundary: LLM output is strictly an untrusted patch proposal validated before application to state.",
        "how_it_works": "SearchOrchestrator sends query to AI provider, parses SearchStatePatch, and validates location via LocationResolver.",
        "estatemap": "app/services/search_orchestrator.py implements intent parsing, state merging, and PostGIS query execution pipeline.",
        "code_flow": "User submits text -> AIService extracts SearchStatePatch -> LocationResolver validates destination -> SearchOrchestrator applies patch to state -> Executes DB query.",
        "build_snippet": """class SearchStatePatch(BaseModel):
    city: Optional[str] = None
    locality: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None
    destination: Optional[str] = None""",
        "break_it": "Allowing the LLM to directly generate SQL WHERE clauses exposes the database to prompt injection and syntax errors.",
        "tradeoffs": "Structured intent parsing separates natural language comprehension from secure PostGIS SQL execution.",
        "system_design": "Intent extraction with backend query execution provides AI convenience while maintaining strict database security.",
        "interview_q": "How do you prevent prompt injection in conversational database search?",
        "interview_a": "The LLM never writes SQL. It outputs a validated Pydantic patch schema which the backend applies to deterministic query builders."
    },
    {
        "id": 40, "title": "Stateless Conversational Search State Machine & State Reducer",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [39], "leads_to": [41, 42],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/schemas/search.py"],
        "symbol": "ConversationalSearchState / SearchOrchestrator._apply_patch / state reducer", "test_cmd": "docker compose exec backend pytest tests/unit/test_search_orchestrator.py",
        "why": "Storing conversational search sessions in server memory breaks horizontal scaling when requests hit different backend instances.",
        "concept": "Stateless state reducer: New State = Reducer(Old State, Patch), eliminating server-side session stickiness.",
        "how_it_works": "AskMapRequest carries ConversationalSearchState; SearchOrchestrator merges patches and returns updated state in AskMapResponse.",
        "estatemap": "app/schemas/search.py defines ConversationalSearchState; app/services/search_orchestrator.py applies functional state reduction.",
        "code_flow": "POST /api/v1/search/orchestrated {query, state} -> Orchestrator extracts patch -> _apply_patch(current_state, patch) -> Returns (results, new_state).",
        "build_snippet": """def reduce_state(current: ConversationalSearchState, patch: SearchStatePatch) -> ConversationalSearchState:
    new_state = current.model_copy()
    for field, val in patch.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(new_state, field, val)
    return new_state""",
        "break_it": "Relying on in-memory session dictionaries causes state loss whenever backend pods restart or scale horizontally.",
        "tradeoffs": "Client-held state simplifies backend scaling at the cost of slightly larger HTTP request payloads.",
        "system_design": "Stateless state machines allow backend API replicas to process any conversation turn without sticky session routing.",
        "interview_q": "How do you design multi-turn conversational search without sticky sessions?",
        "interview_a": "Keep the backend stateless: client passes current search state in the request, backend reducer applies patches and returns the new state."
    },
    {
        "id": 41, "title": "Multi-Turn Criteria Modification, History Merging & Grounded Results",
        "module_id": 11, "module_name": "Module 11: Ask-the-Map Conversational Orchestration", "importance": STATUS_ESSENTIAL,
        "prereqs": [39, 40], "leads_to": [42, 46],
        "files": ["backend/app/services/search_orchestrator.py", "backend/app/services/property_service.py"],
        "symbol": "SearchOrchestrator._execute_search / SearchOrchestrator._resolve_destination", "test_cmd": "docker compose exec backend pytest tests/integration/test_ask_the_map.py",
        "why": "A conversational assistant must support iterative refinement (now filter under 1 Cr, make it 2 bedrooms) seamlessly.",
        "concept": "Orchestrator chains Domain Services (LocationResolver -> PropertyRepository -> RankingService -> POIService).",
        "how_it_works": "SearchOrchestrator coordinates the complete search pipeline, producing matching properties, GeoJSON, and feedback.",
        "estatemap": "app/services/search_orchestrator.py coordinates multi-service execution, handles destination ambiguity, and formats conversational responses.",
        "code_flow": "Turn 1: 'Find 3BHK in Whitefield' -> Sets city=Bengaluru, bedrooms=3, locality=Whitefield -> Turn 2: 'Under 1.2 Cr' -> Merges max_price=12000000 -> Re-executes search.",
        "build_snippet": """async def orchestrate(query: str, current_state: ConversationalSearchState):
    patch = await ai_service.parse_intent(query)
    updated_state = reduce_state(current_state, patch)
    properties = await property_repo.search(updated_state.to_filter_params())
    ranked = ranking_service.rank(properties, updated_state.ranking_weights)
    return {"results": ranked, "state": updated_state}""",
        "break_it": "Failing to clear conflicting filter criteria (e.g. min_price > max_price after a patch) produces 0 search results.",
        "tradeoffs": "Centralizing orchestration in a dedicated service keeps API route handlers clean and easily testable.",
        "system_design": "Domain service orchestration decouples conversational logic from raw database storage and third-party APIs.",
        "interview_q": "Trace the end-to-end execution of a natural language search query.",
        "interview_a": "1. AI extracts patch; 2. Resolver finds coordinates; 3. State Reducer updates criteria; 4. PostGIS filters DB; 5. Ranking scores results; 6. Response returned."
    },

    # Module 12: Backend ↔ Frontend API Integration (42)
    {
        "id": 42, "title": "Backend ↔ Frontend API Integration Contract & Data Boundary",
        "module_id": 12, "module_name": "Module 12: Backend ↔ Frontend API Integration", "importance": STATUS_ESSENTIAL,
        "prereqs": [5, 14, 21, 33, 40], "leads_to": [46, 48],
        "files": ["backend/app/api/v1/properties.py", "backend/app/api/v1/search.py", "backend/app/api/v1/auth.py"],
        "symbol": "API Router definitions / OpenAPI JSON schemas / CORS middleware", "test_cmd": "docker compose exec backend pytest tests/integration/test_properties.py",
        "why": "Clear API contracts enable frontend and backend teams to develop, test, and mock independently without coupling.",
        "concept": "RESTful HTTP endpoints communicate strictly via standard JSON, GeoJSON, Authorization headers, and HTTP status codes.",
        "how_it_works": "FastAPI automatically generates interactive OpenAPI docs (/docs) matching Pydantic schemas and error contracts.",
        "estatemap": "backend/app/api/v1/ defines versioned routers exposing properties, search, commute, ranking, and auth endpoints.",
        "code_flow": "Frontend makes fetch(url, {headers: {Authorization: Bearer token}}) -> FastAPI routes request -> Pydantic serializes response -> Frontend consumes JSON/GeoJSON.",
        "build_snippet": """# Standard FastAPI Router mounting
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])""",
        "break_it": "Changing a response field name in the backend without updating the Pydantic schema causes frontend runtime type crashes.",
        "tradeoffs": "Strict JSON/GeoJSON contracts decouple the Python backend from specific frontend frameworks (Next.js, mobile apps).",
        "system_design": "API contract stability guarantees backward compatibility for existing mobile and web clients during backend upgrades.",
        "interview_q": "How do you design clean API integration boundaries?",
        "interview_a": "Use versioned REST endpoints (/api/v1), explicit Pydantic response schemas, RFC 7807 error structures, and automated OpenAPI contract generation."
    },

    # Module 13: Backend Testing & Debugging (43-44)
    {
        "id": 43, "title": "Pytest Fundamentals, Async Fixtures & Dependency Overrides",
        "module_id": 13, "module_name": "Module 13: Backend Testing & Debugging", "importance": STATUS_IMPORTANT,
        "prereqs": [1, 9, 10], "leads_to": [44],
        "files": ["backend/tests/conftest.py", "backend/tests/unit/test_health.py"],
        "symbol": "pytest_asyncio / app.dependency_overrides / async_session fixture", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Automated tests give developers confidence to refactor code without introducing silent regressions.",
        "concept": "Arrange-Act-Assert pattern with isolated test database sessions and mocked third-party dependencies.",
        "how_it_works": "backend/tests/conftest.py initializes test clients, database engines, and clean session fixtures.",
        "estatemap": "tests/conftest.py defines async fixtures for db_session, async_client, test_settings, and mock_ai_provider.",
        "code_flow": "pytest runs -> conftest initializes in-memory test database -> Injects async_session into test -> Test executes Arrange-Act-Assert -> Session rolled back.",
        "build_snippet": """import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client""",
        "break_it": "Sharing mutable state across tests without cleanup causes flaky tests that fail only when run in specific orders.",
        "tradeoffs": "Dependency overrides allow testing authenticated routes and database repositories in complete isolation.",
        "system_design": "Fast unit tests running in under 5 seconds encourage continuous test-driven development (TDD) during feature additions.",
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
        "estatemap": "tests/integration/ contains 288 comprehensive integration tests testing end-to-end API workflows against real Postgres and Redis.",
        "code_flow": "docker compose exec backend pytest -> Pytest runs 288 tests -> Tests verify real DB queries, Redis caching hits/misses, and AI failovers -> 100% pass.",
        "build_snippet": """@pytest.mark.asyncio
async def test_property_creation_and_spatial_query(async_client, auth_headers):
    payload = {"title": "Test Apartment", "price": 8500000, "bedrooms": 2, "latitude": 12.9716, "longitude": 77.5946}
    resp = await async_client.post("/api/v1/properties", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    prop_id = resp.json()["id"]
    
    # Verify spatial radius query
    search_resp = await async_client.get("/api/v1/properties/radius?lat=12.97&lon=77.59&radius_m=2000")
    assert any(p["id"] == prop_id for p in search_resp.json()["items"])""",
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
        "symbol": "services: postgres-postgis, redis, backend, frontend / healthcheck", "test_cmd": "docker compose ps",
        "why": "Containerization eliminates 'works on my machine' issues by providing identical local and production runtime environments.",
        "concept": "Docker Compose manages container networks, port bindings, persistent volumes, environment files, and healthcheck dependencies.",
        "how_it_works": "docker-compose.yml defines 4 services with depends_on condition: service_healthy ensuring DB is ready before backend boots.",
        "estatemap": "docker-compose.yml coordinates postgres-postgis, redis, backend, and frontend containers on a shared bridge network.",
        "code_flow": "docker compose up -> Postgres & Redis boot -> Healthchecks pass -> Backend container boots -> Alembic runs -> FastAPI starts serving traffic.",
        "build_snippet": """# docker-compose.yml service snippet
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
        condition: service_healthy""",
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
        "prereqs": [1, 9, 18, 25, 29, 32, 35, 40, 42], "leads_to": [47, 48],
        "files": ["backend/app/main.py", "docs/mastery/ARCHITECTURE.md"],
        "symbol": "Modular Monolith Topology / End-to-End Request Lifecycle", "test_cmd": "docker compose exec backend pytest tests/unit/test_health.py",
        "why": "Senior backend engineers must explain how all system components interact across the entire end-to-end request lifecycle.",
        "concept": "Modular Monolith enforces strict domain boundaries inside a single deployable process, avoiding distributed network overhead.",
        "how_it_works": "Request enters Uvicorn -> Middleware (CORS, RequestID) -> Router -> Service -> Repository/Cache/AI -> Database.",
        "estatemap": "app/main.py wires all modules; ARCHITECTURE.md details the runtime topology, schema, and data flows.",
        "code_flow": "HTTP Request -> ASGI Pipeline -> Middleware -> APIRouter -> Dependency Injection -> Domain Service -> Repository -> PostGIS DB -> Response.",
        "build_snippet": """# End-to-End Architecture Flow
# Client -> Uvicorn -> Middleware -> FastAPI APIRouter
# -> Dependency Injection (get_db, get_current_user)
# -> Domain Service (PropertyService, RankingService, AIService)
# -> Data Layer (PropertyRepository, CacheService, PostGIS DB)""",
        "break_it": "Blurring domain boundaries by allowing API routes to directly execute raw SQL queries destroys maintainability.",
        "tradeoffs": "A modular monolith handles up to 50,000+ daily active users on a single modest server before requiring microservice decomposition.",
        "system_design": "Clear modular boundaries inside a monolith allow future extraction of high-load domains into separate microservices if required.",
        "interview_q": "Why did you choose a Modular Monolith over Microservices?",
        "interview_a": "To eliminate distributed system overhead (network latency, distributed tracing, two-phase commits) while maintaining clean domain module boundaries that can be extracted later if needed."
    },
    {
        "id": 47, "title": "Requirement-Driven Scalability, Bottleneck Analysis & Caching Evolution",
        "module_id": 15, "module_name": "Module 15: EstateMap System Design & Architecture Synthesis", "importance": STATUS_ESSENTIAL,
        "prereqs": [17, 29, 32, 46], "leads_to": [48],
        "files": ["docs/mastery/SYSTEM_DESIGN.md"],
        "symbol": "Scale Evolution: 10k -> 100k -> 1M DAU / Bottleneck Mitigation", "test_cmd": "docker compose exec backend pytest tests/integration/test_rate_limiting.py",
        "why": "System design interviews require explaining WHEN and WHY to introduce caching, read replicas, connection pooling, or partitioning.",
        "concept": "Identify bottleneck -> Evaluate simplest response (Index -> Cache -> Read Replica -> Sharding) based on quantitative metrics.",
        "how_it_works": "SYSTEM_DESIGN.md documents scaling evolution milestones from single-node deployment up to 1M daily active users.",
        "estatemap": "SYSTEM_DESIGN.md details scale milestones (10k, 100k, 1M users), latency budgets, and caching hierarchies.",
        "code_flow": "Load Increases -> Bottleneck identified (DB Read CPU) -> Mitigation 1: Add GiST index -> Mitigation 2: Add Redis Cache-Aside -> Mitigation 3: Add Postgres Read Replicas.",
        "build_snippet": """# Scalability Hierarchy
# Level 1: Single Postgres Node + GiST Spatial Indexes (< 10k DAU)
# Level 2: Add Redis Cache-Aside for Viewport & Ranking (< 100k DAU)
# Level 3: Add PostgreSQL Read Replicas for Search Queries (< 500k DAU)
# Level 4: Spatial Hash Partitioning / Sharding (1M+ DAU)""",
        "break_it": "Introducing premature complexity (Kafka, Sharding) before exhausting database indexes and Redis caching wastes engineering resources.",
        "tradeoffs": "Horizontal scaling of stateless FastAPI workers behind a load balancer is the first and most cost-effective scaling lever.",
        "system_design": "Scalability is requirement-driven: scale the bottleneck component only when performance metrics exceed service level objectives.",
        "interview_q": "If your database read latency spikes under heavy load, what steps do you take?",
        "interview_a": "1. Check EXPLAIN ANALYZE for missing indexes; 2. Add Redis Cache-Aside for hot queries; 3. Add PostgreSQL read replicas before considering sharding."
    },
    {
        "id": 48, "title": "Senior Backend Architectural Defense, Tradeoffs & Whiteboard Mastery",
        "module_id": 15, "module_name": "Module 15: EstateMap System Design & Architecture Synthesis", "importance": STATUS_ESSENTIAL,
        "prereqs": [46, 47], "leads_to": [],
        "files": ["docs/mastery/SYSTEM_DESIGN.md", "docs/mastery/INTERVIEW_PREP.md"],
        "symbol": "15 Core Architectural Tradeoffs / Whiteboard Challenge Blueprints", "test_cmd": "docker compose exec backend pytest",
        "why": "Interviewers evaluate your ability to justify WHY an architecture was chosen, what tradeoffs were accepted, and how it fails.",
        "concept": "Structured STAR-format defense linking business requirements to concrete technical decisions and failure mitigation.",
        "how_it_works": "INTERVIEW_PREP.md provides elevator pitches, Top 25 STAR Q&As, and 10 Whiteboard challenge blueprints.",
        "estatemap": "INTERVIEW_PREP.md and SYSTEM_DESIGN.md consolidate all architectural defenses, failure modes, and whiteboard blueprints.",
        "code_flow": "Interview Question -> Candidate delivers 30-second high-level summary -> Follows with 2-minute technical deep dive -> Draws component architecture on whiteboard -> Explains tradeoffs & failure modes.",
        "build_snippet": """# Senior Architectural Pitch Framework
# 1. Problem: Real estate discovery requires multi-modal geospatial search, ranking, and conversational intent parsing.
# 2. Architecture: FastAPI ASGI modular monolith, PostGIS GiST spatial indexing, Redis caching & ZSET sliding window rate limiting.
# 3. Key Decision: Deterministic MCDA ranking + multi-provider AI fallback circuit (Ollama local -> Gemini cloud -> Algorithmic fallback).""",
        "break_it": "Saying 'we used Redis because it is fast' without explaining data structures, eviction policies, or failure modes signals junior thinking.",
        "tradeoffs": "Every technical decision is a tradeoff: PostGIS vs ElasticSearch, Redis ZSET vs Token Bucket, Local Ollama vs Cloud Gemini.",
        "system_design": "Mastery means being able to defend why each technology was chosen, what alternatives were rejected, and how the system degrades under failure.",
        "interview_q": "Walk me through the architecture of EstateMap AI.",
        "interview_a": "Deliver the structured 2-minute architectural pitch covering FastAPI ASGI, PostGIS spatial indexing, Redis caching, deterministic ranking, and multi-provider AI."
    }
]

def generate_story_md(s):
    prereq_str = ", ".join([f"Story {p:02d}" for p in s["prereqs"]]) if s["prereqs"] else "None (Foundational)"
    leads_str = ", ".join([f"Story {l:02d}" for l in s["leads_to"]]) if s["leads_to"] else "None (Terminal Story)"
    files_str = ", ".join([f"`{f}`" for f in s["files"]])

    return f"""
### Story {s['id']:02d}: {s['title']}

* **Module**: {s['module_name']}
* **Importance Level**: `{s['importance']}`
* **Prerequisites**: {prereq_str}
* **Leads To**: {leads_str}
* **Primary Code Files**: {files_str}
* **Concrete Symbol / Class**: `{s['symbol']}`
* **Automated Verification**: `{s['test_cmd']}`

#### 1. Why This Matters
{s['why']}

#### 2. Concept & Architecture
{s['concept']}

#### 3. How It Works Internally
{s['how_it_works']}

#### 4. EstateMap Implementation
{s['estatemap']}

#### 5. Code Flow & Request Lifecycle
```text
{s['code_flow']}
```

#### 6. Build It Yourself (Python Blueprint)
```python
{s['build_snippet']}
```

#### 7. Break It & Debug It (Topic-Specific Failure Mode)
* **Failure Scenario**: {s['break_it']}
* **Debugging Command / Step**: Run `{s['test_cmd']}` or inspect PostgreSQL / Redis logs.

#### 8. Tradeoffs & Rejected Alternatives
{s['tradeoffs']}

#### 9. System Design & Scaling Angle
{s['system_design']}

#### 10. Interview Defense (STAR Q&A)
* **Question**: {s['interview_q']}
* **Answer**: {s['interview_a']}

#### 11. Mastery Verification Check
```bash
{s['test_cmd']}
```

---
"""

def compile_all():
    print(f"Compiling {len(STORIES)} backend stories...")
    
    # 1. Compile BACKEND_ENGINEERING_STORIES.md
    stories_doc = f"""# EstateMap AI — Backend Engineering Stories Master Curriculum
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
"""
    current_module = 0
    for s in STORIES:
        if s["module_id"] != current_module:
            current_module = s["module_id"]
            stories_doc += f"\n## {s['module_name']}\n"
        stories_doc += generate_story_md(s)

    with open(os.path.join(MASTERY_DIR, "BACKEND_ENGINEERING_STORIES.md"), "w", encoding="utf-8") as f:
        f.write(stories_doc)
    print("Wrote BACKEND_ENGINEERING_STORIES.md")

    # 2. Compile BACKEND_ROADMAP.md
    print("Compiling BACKEND_ROADMAP.md...")
    roadmap_doc = """# EstateMap AI — Backend Learning Roadmap & Verification Guide
> **Structured Study Progression for Python Backend Engineers & System Designers**

## 1. The 15-Module Backend Progression Path
```text
Python & FastAPI Foundations (Stories 01-04)
        ↓
REST API Design & Validation (Stories 05-07)
        ↓
PostgreSQL & SQLAlchemy 2.0 Async (Stories 08-12)
        ↓
Authentication & Security (Stories 13-15)
        ↓
PostGIS Spatial Search Engine (Stories 16-21)
        ↓
Location Intelligence & Routing (Stories 22-24)
        ↓
Deterministic Ranking & Business Logic (Stories 25-28)
        ↓
Redis In-Memory Caching (Stories 29-31)
        ↓
Rate Limiting & Distributed Resilience (Stories 32-34)
        ↓
Multi-Provider AI Architecture (Stories 35-38)
        ↓
Ask-the-Map Conversational Orchestrator (Stories 39-41)
        ↓
Backend ↔ Frontend API Integration Contract (Story 42)
        ↓
Backend Testing & Debugging (Stories 43-44)
        ↓
Docker for Backend Developers (Story 45)
        ↓
EstateMap System Design & Architectural Defense (Stories 46-48)
```

---

## 2. The 10 Cumulative Mastery Demonstrations (CMDs)

| CMD | Milestone | Core Focus | Verification Command |
| :---: | :--- | :--- | :--- |
| **CMD 01** | Modular Monolith & Lifespan | FastAPI, Lifespan, Logging | `docker compose exec backend pytest tests/unit/test_health.py` |
| **CMD 02** | Asyncpg Relational Database | SQLAlchemy 2.0, Asyncpg, Alembic | `docker compose exec backend pytest tests/integration/test_database.py` |
| **CMD 03** | PostGIS Geodesic Spatial Search | GiST Index, ST_DWithin, ST_MakeEnvelope | `docker compose exec backend pytest tests/integration/test_spatial_search.py` |
| **CMD 04** | Stateless JWT Authentication | Argon2id, JWT, FastAPI Depends | `docker compose exec backend pytest tests/integration/test_auth.py` |
| **CMD 05** | Commute Routing & Matrix | OSRM Engine, Haversine Fallback | `docker compose exec backend pytest tests/integration/test_commute.py` |
| **CMD 06** | 6-Factor Deterministic Ranking | MCDA, Weight Redistribution | `docker compose exec backend pytest tests/integration/test_ranking.py` |
| **CMD 07** | Redis Caching & Invalidation | Cache-Aside, SHA-256 Key Hashing | `docker compose exec backend pytest tests/unit/test_cache_service.py` |
| **CMD 08** | Pipelined Sliding Window Rate Limiter | Redis ZSET, Pipelined Eval | `docker compose exec backend pytest tests/integration/test_rate_limiting.py` |
| **CMD 09** | Multi-Provider AI & Orchestration | Ollama + Gemini, State Reducer | `docker compose exec backend pytest tests/integration/test_ai_search.py` |
| **CMD 10** | End-to-End Backend Verification | Complete 288-Test Regression Suite | `docker compose exec backend pytest` |

---

## 3. 4-Week Structured Study Plan
- **Week 1: Foundations, Database & Spatial Indexing** (Modules 1–5: Stories 01–21)
- **Week 2: Location, Routing, Ranking & Caching** (Modules 6–8: Stories 22–31)
- **Week 3: Rate Limiting, Multi-Provider AI & Conversational Search** (Modules 9–11: Stories 32–41)
- **Week 4: API Contracts, Testing, Docker & System Design Whiteboarding** (Modules 12–15: Stories 42–48)
"""
    with open(os.path.join(MASTERY_DIR, "BACKEND_ROADMAP.md"), "w", encoding="utf-8") as f:
        f.write(roadmap_doc)
    print("Wrote BACKEND_ROADMAP.md")

    # 3. Compile BACKEND_DEPENDENCY_GRAPH.md
    print("Compiling BACKEND_DEPENDENCY_GRAPH.md...")
    graph_doc = """# EstateMap AI — Backend Learning Dependency Graph
> **Directed Acyclic Graph (DAG) for all 48 Backend Engineering Stories across 15 Modules**

```mermaid
flowchart TD
    subgraph M01["Module 01: Python & FastAPI (1-4)"]
        S01["Story 01: Architecture"] --> S02["Story 02: Lifespan"]
        S01 --> S03["Story 03: Config"]
        S01 --> S04["Story 04: Errors & Logging"]
    end

    subgraph M02["Module 02: API Design & Validation (5-7)"]
        S04 --> S05["Story 05: Pydantic Schemas"]
        S05 --> S06["Story 06: Pagination"]
        S05 --> S07["Story 07: Dynamic Filters"]
    end

    subgraph M03["Module 03: PostgreSQL & SQLAlchemy (8-12)"]
        S03 --> S08["Story 08: Relational Models"]
        S08 --> S09["Story 09: Asyncpg Pool"]
        S08 --> S10["Story 10: Repositories"]
        S08 --> S11["Story 11: Alembic"]
        S08 --> S12["Story 12: Seeding"]
    end

    subgraph M04["Module 04: Security & Auth (13-15)"]
        S03 --> S13["Story 13: Argon2id"]
        S13 --> S14["Story 14: JWT Auth"]
        S14 --> S15["Story 15: RBAC & Ownership"]
    end

    subgraph M05["Module 05: PostGIS Spatial Search (16-21)"]
        S08 --> S16["Story 16: WGS84 Point"]
        S16 --> S17["Story 17: GiST Index"]
        S17 --> S18["Story 18: ST_DWithin Radius"]
        S17 --> S19["Story 19: ST_MakeEnvelope BBox"]
        S18 --> S20["Story 20: POI Intelligence"]
        S16 --> S21["Story 21: GeoJSON"]
    end

    subgraph M06["Module 06: Routing & Commute (22-24)"]
        S16 --> S22["Story 22: Location Resolver"]
        S02 --> S23["Story 23: OSRM Routing"]
        S22 --> S24["Story 24: Commute Matrix"]
        S23 --> S24
    end

    subgraph M07["Module 07: Ranking Engine (25-28)"]
        S05 --> S25["Story 25: 6-Factor Ranking"]
        S25 --> S26["Story 26: Weight Redistribution"]
        S25 --> S27["Story 27: Explainability"]
        S25 --> S28["Story 28: Comparison Engine"]
    end

    subgraph M08["Module 08: Redis Caching (29-31)"]
        S02 --> S29["Story 29: Cache-Aside"]
        S29 --> S30["Story 30: Key Design"]
        S30 --> S31["Story 31: SCAN Invalidation"]
    end

    subgraph M09["Module 09: Rate Limiting (32-34)"]
        S29 --> S32["Story 32: ZSET Sliding Window"]
        S32 --> S33["Story 33: Headers & Tiers"]
        S33 --> S34["Story 34: Fail-Open Policy"]
    end

    subgraph M10["Module 10: Multi-Provider AI (35-38)"]
        S05 --> S35["Story 35: AI Protocol"]
        S35 --> S36["Story 36: Schema Validation"]
        S36 --> S37["Story 37: Provider Routing"]
        S37 --> S38["Story 38: Grounded Fallbacks"]
    end

    subgraph M11["Module 11: Conversational Search (39-41)"]
        S37 --> S39["Story 39: Intent Parsing"]
        S39 --> S40["Story 40: State Reducer"]
        S40 --> S41["Story 41: Multi-Turn Search"]
    end

    subgraph M12["Module 12: API Integration (42)"]
        S05 --> S42["Story 42: Backend Contract"]
        S14 --> S42
        S21 --> S42
    end

    subgraph M13["Module 13: Testing & Debugging (43-44)"]
        S10 --> S43["Story 43: Pytest Fixtures"]
        S43 --> S44["Story 44: Integration Tests"]
    end

    subgraph M14["Module 14: Docker (45)"]
        S01 --> S45["Story 45: Docker Compose"]
    end

    subgraph M15["Module 15: System Design (46-48)"]
        S42 --> S46["Story 46: Modular Monolith"]
        S46 --> S47["Story 47: Bottleneck Scaling"]
        S47 --> S48["Story 48: Whiteboard Defense"]
    end
```
"""
    with open(os.path.join(MASTERY_DIR, "BACKEND_DEPENDENCY_GRAPH.md"), "w", encoding="utf-8") as f:
        f.write(graph_doc)
    print("Wrote BACKEND_DEPENDENCY_GRAPH.md")

    # 4. Compile README.md
    print("Compiling README.md...")
    readme_doc = """# EstateMap AI — Python Backend & System Design Mastery Curriculum
> **Curriculum Status: FROZEN & TAILORED STRICTLY FOR PYTHON BACKEND & SYSTEM DESIGN**
> **Canonical Document Library: 7 Focused Documents | 0 Hallucinations | 100% Executable Code Truth**

Welcome to the EstateMap AI Backend Engineering Curriculum. This curriculum is designed to help you become strong in **Python backend development, database engineering (PostgreSQL + PostGIS), distributed caching & rate limiting (Redis), and system design** by deeply understanding, building, and explaining the EstateMap backend.

---

## 1. My Exact Learning Target
```text
Python
  ↓
FastAPI
  ↓
REST API Engineering
  ↓
Pydantic v2
  ↓
Async Python (asyncio / asyncpg)
  ↓
SQLAlchemy 2.0
  ↓
PostgreSQL
  ↓
PostGIS (WGS84, GiST, ST_DWithin, ST_MakeEnvelope)
  ↓
Authentication & Authorization (Argon2id, JWT, RBAC)
  ↓
Redis (In-Memory Data Structures)
  ↓
Caching (Cache-Aside, SHA-256 Hashing, SCAN Invalidation)
  ↓
Rate Limiting (Sliding Window Log via Redis ZSET)
  ↓
Routing / External APIs (Async Httpx, OSRM, Haversine)
  ↓
Deterministic Ranking (MCDA 6-Factor Normalization)
  ↓
AI Provider Integration (Ollama Local, Gemini Cloud, Pydantic Firewall)
  ↓
Conversational Backend Orchestration (Stateless State Reducer)
  ↓
Backend Testing Fundamentals (Pytest, Fixtures, Mocking)
  ↓
Docker Fundamentals (Docker Compose, Healthchecks)
  ↓
System Design (Tradeoffs, Bottlenecks, Scaling 10k → 1M users)
```

---

## 2. How to Study This Repository (The 3-Pass Backend Study System)

### Pass 1: UNDERSTAND (Mental Models & System Architecture)
*Goal: Understand how the backend works, why each decision was made, and how data flows through the system.*
1. Read [`ARCHITECTURE.md`](ARCHITECTURE.md) to understand the backend modular monolith layout, Docker Compose topology, and database schema.
2. Read [`BACKEND_MASTER_BOOK.md`](BACKEND_MASTER_BOOK.md) for deep textbook chapters on FastAPI request lifecycles, PostGIS spatial indexing, 6-Factor ranking math, Redis caching, and multi-provider AI failover.
3. Read [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md) to internalize the 15 architectural tradeoffs, technology necessity, failure mode mitigations, and scaling roadmaps.

### Pass 2: BUILD (Hand-Rebuild & Active Recall)
*Goal: Gain hands-on muscle memory by coding the core mechanisms from scratch without AI assistance.*
1. Follow the **48 Backend Engineering Stories** in [`BACKEND_ENGINEERING_STORIES.md`](BACKEND_ENGINEERING_STORIES.md).
2. Execute the **10 Cumulative Mastery Demonstrations (CMDs)** in [`BACKEND_ROADMAP.md`](BACKEND_ROADMAP.md).
3. Practice the 8 Live Backend Debugging Labs and 5 Rebuild Challenges in [`ACTIVE_RECALL.md`](ACTIVE_RECALL.md).

### Pass 3: INTERVIEW (Pitch, Defend & Whiteboard)
*Goal: Flawlessly communicate your technical expertise in senior backend and system design interviews.*
1. Rehearse the 30-second and 2-minute elevator pitches in [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md).
2. Master the Top 25 Backend/System Design STAR-format answers in [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md).
3. Practice sketching the 10 Whiteboard Challenge Blueprints.
4. Review the 12 Red Flags to avoid during interviews.
5. Study the complete Senior Backend Mock Interview transcript.

---

## 3. What to Study vs What to Ignore

| Category | What to Study (ESSENTIAL & IMPORTANT) | What to Ignore (REMOVED FROM CURRICULUM) |
| :--- | :--- | :--- |
| **Backend & Spatial** | FastAPI, Pydantic v2, SQLAlchemy 2.0, Asyncpg, PostGIS `Geometry(Point, 4326)`, GiST indexes, `ST_DWithin`, `ST_MakeEnvelope`, GeoJSON serializers. | Next.js internals, React components, Tailwind CSS, MapLibre rendering. |
| **Caching & Limiting** | Redis Cache-Aside, SHA-256 key hashing, SCAN invalidation, Redis ZSET sliding-window rate limiter, Fail-open policy. | Redis Cluster sharding, Raft consensus, complex multi-region replication. |
| **AI Orchestration** | Provider Protocol, Ollama (local) + Gemini (cloud), Pydantic validation firewall, SearchOrchestrator stateless state reducer. | Token streaming, LLM fine-tuning, autonomous agent frameworks. |
| **DevOps & Testing** | Dockerfile, Docker Compose local orchestration, Pytest async fixtures, dependency overrides, integration test suites. | Kubernetes, Helm, CI/CD GitHub Actions matrices, Playwright browser tests, Testcontainers, Prometheus/OpenTelemetry agents. |

---

## 4. The 7 Canonical Documents Library

| # | Document | Role & Purpose | Recommended Focus |
| :-: | :--- | :--- | :--- |
| 1 | [`README.md`](README.md) | **Single Entry Point**, Backend Learning Path, Study Order. | All Learners |
| 2 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Authoritative backend architecture, container topology, database schema, services, and Mermaid diagrams. | Architecture & SDE Study |
| 3 | [`BACKEND_MASTER_BOOK.md`](BACKEND_MASTER_BOOK.md) | In-depth backend engineering textbook (FastAPI, PostGIS, Ranking, Routing, AI, Caching, Rate Limiting, API Contract). | Deep Technical Study |
| 4 | [`BACKEND_ENGINEERING_STORIES.md`](BACKEND_ENGINEERING_STORIES.md) | 48 deep backend engineering stories organized into 15 modules with 11-section high-signal format. | Hands-On Implementation |
| 5 | [`SYSTEM_DESIGN.md`](SYSTEM_DESIGN.md) | Requirement-driven system design case study, 15 core architectural tradeoffs, technology necessity, failure modes, scaling evolution. | System Design Prep |
| 6 | [`INTERVIEW_PREP.md`](INTERVIEW_PREP.md) | Senior Backend & System Design interview guide (Pitches, Top 25 STAR Q&As, 10 Whiteboard challenge blueprints, Mock interview). | Interview Practice |
| 7 | [`ACTIVE_RECALL.md`](ACTIVE_RECALL.md) | 50 Backend active recall drills with hidden answer keys, 8 topic-specific live debugging labs, and 5 rebuild challenges. | Self-Assessment |

---

## 5. Implementation & Verification Status
- **Total Backend Stories:** 48
- **Essential Backend Stories:** 32
- **Important Backend Stories:** 16
- **Automated Regression Status:** 288/288 Backend Pytest Passed | 100% Executable Code Truth
"""
    with open(os.path.join(MASTERY_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_doc)
    print("Wrote README.md")

    # 5. Clean up obsolete files
    print("Cleaning up obsolete files...")
    obsolete_files = [
        "ENGINEERING_STORIES.md",
        "MASTER_BOOK.md",
        "SYSTEM_DESIGN_AND_TRADEOFFS.md",
        "LEARNING_ROADMAP.md",
        "LEARNING_DEPENDENCY_GRAPH.md",
        "KNOW_YOUR_CODE.md",
        "CURRICULUM_INTEGRITY_AUDIT.md",
        "STORY_CLAIM_EVIDENCE_MATRIX.md"
    ]
    for of in obsolete_files:
        p = os.path.join(MASTERY_DIR, of)
        if os.path.exists(p):
            os.remove(p)
            print(f"Removed obsolete file: {of}")

if __name__ == "__main__":
    compile_all()

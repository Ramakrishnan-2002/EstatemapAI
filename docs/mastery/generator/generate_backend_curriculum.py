# -*- coding: utf-8 -*-
"""
EstateMap AI — Backend-Only Python & System Design Curriculum Generator
Compiles 48 focused backend stories across 15 modules and 7 canonical documents.
"""
import os
import sys
import re
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MASTERY_DIR = os.path.join(BASE_DIR, "docs", "mastery")

STATUS_ESSENTIAL = "[ESSENTIAL]"
STATUS_IMPORTANT = "[IMPORTANT]"

# Complete 48 Backend Stories across 15 Modules
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
        "prereqs": [1, 3], [5, 14, 32],
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
        "prereqs": [1, 3, 4], [6, 7, 10, 21, 36],
        "files": ["backend/app/schemas/property.py", "backend/app/schemas/search.py", "backend/app/schemas/auth.py"],
        "symbol": "PropertyResponse / PropertyCreate / PropertyFilterParams", "test_cmd": "docker compose exec backend pytest tests/unit/test_property_schemas.py",
        "why": "Input validation at the API boundary protects domain services and SQL queries from malformed payloads.",
        "concept": "Pydantic v2 Rust core (pydantic-core) delivers high-throughput serialization and schema validation.",
        "how_it_works": "app/schemas/ defines strict BaseModel schemas with Field constraints (e.g. price > 0, latitude [-90, 90]).",
        "estatemap": "app/schemas/ defines PropertyCreate, PropertyUpdate, PropertyResponse models with exact typing and field aliases.",
        "code_flow": "HTTP Request Payload -> FastAPI body parser -> Pydantic model validation -> Clean typed object passed to endpoint -> Return schema serializes output.",
        "build_snippet": """from pydantic import BaseModel, Field, field_validator

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
        "prereqs": [5], [7, 10],
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
        "prereqs": [5, 6], [10, 18],
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
        "prereqs": [1, 3], [9, 10, 11, 16],
        "files": ["backend/app/models/property.py", "backend/app/models/user.py", "backend/app/models/poi.py"],
        "symbol": "Property / User / PointOfInterest / Base", "test_cmd": "docker compose exec backend pytest tests/integration/test_database.py",
        "why": "Database constraints provide the final defense line for data integrity even if application bugs occur.",
        "concept": "Relational normalization (3NF) eliminates data redundancy while foreign keys enforce referential integrity.",
        "how_it_works": "app/models/ defines declarative tables with mapped_column, CheckConstraint('price > 0'), and foreign keys.",
        "estatemap": "app/models/property.py, user.py, and poi.py define declarative SQLAlchemy 2.0 models with relationships, cascades, and constraints.",
        "code_flow": "Domain Entity Definition -> Base declarative metadata -> Table definition with foreign keys and check constraints -> Database schema synchronization.",
        "build_snippet": """from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey, CheckConstraint

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
        "prereqs": [2, 8], [10, 13, 18],
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
        "prereqs": [8, 9], [18, 22, 25],
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
        "prereqs": [8, 10], [12, 16],
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
        "prereqs": [8, 10, 11], [18, 22],
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
        "prereqs": [3, 8], [14, 15],
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
        "prereqs": [3, 13], [15, 33],
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
        "prereqs": [13, 14], [18, 42],
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
    }
]

# Write out the remaining stories dynamically to avoid file length constraints
def get_all_stories():
    all_stories = list(STORIES)
    # Modules 5 to 15 will be appended
    return all_stories

print(f"Loaded {len(STORIES)} initial stories.")

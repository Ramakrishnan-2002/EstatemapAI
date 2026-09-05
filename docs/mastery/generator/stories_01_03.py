# -*- coding: utf-8 -*-
# Stories 1 to 3

def get_stories():
    return [
        {
            'num': 1,
            'title': 'Python Project Structure & Clean Architecture',
            'points': 2,
            'why_exists': 'Scalable backend applications require clear modular directory boundaries to prevent circular imports, maintain separation of concerns, and allow multi-engineer collaboration without code collisions. Naive single-folder scripts fail when the codebase exceeds 500 lines due to cross-layer coupling.',
            'problem_solved': 'Disorganized Python projects mix HTTP route handling with database SQL and business domain logic in a single file or tangled directories, causing circular dependency crashes on boot and making unit testing impossible without mocking the entire runtime.',
            'prereq_stories': [],
            'prereq_concepts': ['Python 3.12 module system', 'sys.path and import mechanics', 'Clean Architecture layers'],
            'depends_on': [],
            'unlocks': [2, 3, 4],
            'readiness': [
                'Understand Python relative and absolute imports',
                'Familiar with virtual environments and pyproject.toml package definitions',
                'Able to explain the difference between a module and a package'
            ],
            'objectives': [
                'Structure a production FastAPI backend using Clean Architecture (API, Service, Repository, Model, Core)',
                'Configure pyproject.toml and Ruff linting rules to enforce architectural boundaries',
                'Isolate domain entities from database ORM and HTTP transport layers'
            ],
            'concepts': [
                'Modular Monolith: Organizing a single codebase into strictly bounded domain modules',
                'Separation of Concerns: Isolating Transport (FastAPI), Business Logic (Services), and Persistence (SQLAlchemy/Repositories)',
                'Dependency Direction Rule: Source code dependencies must point inward toward high-level policies, never toward low-level details',
                'Circular Import Resolution: Using standard module hierarchies and local imports or Protocols where necessary'
            ],
            'impl': 'EstateMap organizes backend code under backend/app/ with clear functional directories: api/ (v1 route controllers), core/ (settings, security, middleware, custom exceptions), db/ (engine and session lifecycle), models/ (SQLAlchemy declarative ORM entities), repositories/ (data access layer), schemas/ (Pydantic DTO contracts), services/ (domain computation, ranking, routing), cache/ (Redis client and rate limiting), and ai/ (LLM provider orchestration).',
            'files': [
                'backend/app/main.py',
                'backend/pyproject.toml',
                'backend/app/core/config.py',
                'backend/app/api/v1/router.py'
            ],
            'data_flow': 'Client Request -> Uvicorn ASGI Server -> main.py (FastAPI App) -> Middleware Stack (RequestID, RateLimit) -> API Route Handler (api/v1/endpoints/) -> Domain Service (services/) -> Repository Layer (repositories/) -> Database Model (models/) -> PostgreSQL',
            'lab_standalone': '''Create a minimal 3-tier Python project from scratch:
1. Create directories: app/api/, app/services/, app/repositories/, app/models/.
2. Implement an in-memory ItemRepository in repositories/item_repo.py.
3. Implement ItemService in services/item_service.py that depends on ItemRepository.
4. Implement a FastAPI router in api/items.py that instantiates ItemService.
5. Run with Uvicorn and verify zero circular import errors on startup.''',
            'lab_mapping': 'Inspect backend/app/api/v1/endpoints/properties.py and trace how it calls backend/app/services/property_service.py, which in turn queries backend/app/repositories/property_repo.py.',
            'acceptance_criteria': [
                'All application code resides inside backend/app/ with no root-level cross-module leakages.',
                'Importing any service module does not trigger imports of API route controllers.',
                'pyproject.toml defines package dependencies, formatting, and linting rules executed by Ruff without errors.',
                'Running pytest discovers all unit and integration tests under backend/tests/ without setting manual PYTHONPATH hacks.'
            ],
            'evidence': [
                'Run docker exec estatemap-backend ruff check . to verify zero import or boundary violations.',
                'Run docker exec estatemap-backend python -c "import app.main; print(\'Clean imports verified\')".'
            ],
            'outcome_conceptual': 'Mental model of Clean Architecture in Python, understanding how unidirectional dependencies prevent cyclic deadlocks and decouple domain logic from transport protocols.',
            'outcome_impl': 'Ability to scaffold a production-ready, multi-layered Python backend with automated linting, typing, and modular directory boundaries from memory.',
            'outcome_interview': 'Ability to defend why EstateMap chose a Modular Monolith over Microservices and explain exact package boundaries to a senior interviewer.',
            'mistakes': [
                'Importing an API route handler or FastAPI Request object directly inside a database model or repository.',
                'Using wild-card from module import * which pollutes namespaces and obscures dependency cycles.',
                'Hardcoding business logic directly in FastAPI endpoint functions instead of delegating to domain services.'
            ],
            'debug_symptom': 'ImportError: cannot import name X from partially initialized module app.services.property_service (most likely due to a circular import).',
            'debug_investigate': 'Trace the import chain between the two failing modules. Identify where a lower-level module is trying to import a higher-level controller or schema.',
            'debug_goal': 'Refactor the shared data structure or exception into core/ or schemas/, ensuring both modules import from the shared foundation.',
            'tradeoffs': [
                'Modular Monolith vs. Microservices: Chose Modular Monolith to eliminate distributed network latency, deployment overhead, and cross-service transaction complexity while maintaining strict internal module boundaries.',
                'Feature-based directory structure vs Layer-based: Chose Layer-based for EstateMap because cross-cutting spatial algorithms and AI routing span multiple entities.'
            ],
            'prod_current': 'Layer-based modular structure with Ruff linting and type checking in Docker container.',
            'prod_scale': 'Enforce package boundaries using import-linter or Bazel/Pants build systems to forbid cross-layer import violations at compile-time in CI.',
            'q_basic': 'What are the core layers of Clean Architecture and what is the dependency direction rule?',
            'q_impl': 'How does EstateMap structure its backend codebase to prevent circular imports between routers, services, and repositories?',
            'q_tradeoff': 'Why start with a Modular Monolith instead of splitting the Property, Spatial, and AI services into separate microservices?',
            'q_debug': 'If you encounter a circular import error during application startup in Python, what steps do you take to diagnose and resolve it?',
            'q_sysdesign': 'How would you evolve this modular monolith into microservices if team size expanded from 2 to 50 engineers?',
            'ans_framework': 'Structure the answer around: 1) The 4 distinct layers in EstateMap (API, Service, Repository, Model), 2) The Unidirectional Dependency Rule (outer layers know inner layers, inner never know outer), 3) Concrete examples from EstateMap (PropertyService sits between endpoint and DB), 4) The architectural benefit: testability and zero circular import deadlocks.',
            'conn_prev': 'Initial architectural foundation of the EstateMap platform.',
            'conn_next': 'Story 02 builds upon this directory structure to implement the FastAPI application lifecycle and async lifespan context manager.',
            'checklist': [
                'Can explain the role of each directory in backend/app/ without looking at docs',
                'Can describe the Dependency Inversion Principle as applied to Python services and repositories',
                'Can configure pyproject.toml with Ruff rules for strict architectural boundary enforcement',
                'Can diagnose and resolve circular import errors in under 2 minutes'
            ]
        },
        {
            'num': 2,
            'title': 'FastAPI Lifespan & Application Lifecycle',
            'points': 3,
            'why_exists': 'Production web servers must manage initialization (database pools, cache connections, seed verification) and graceful shutdown (closing sockets, flushing buffers) deterministically. Legacy event hooks like @app.on_event are deprecated in modern ASGI.',
            'problem_solved': 'Uninitialized database connection pools crash the first incoming user request; unclosed pools leak socket descriptors and trigger connection exhaustion on server restarts.',
            'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture'],
            'prereq_concepts': ['ASGI specification', 'Python async context managers (@asynccontextmanager)', 'Resource lifecycle management'],
            'depends_on': [1],
            'unlocks': [3, 6, 9, 39],
            'readiness': [
                'Understand async with and the generator yield keyword in context managers',
                'Familiar with how ASGI servers (Uvicorn) invoke application lifespan protocols',
                'Able to explain why connection pooling requires lifecycle hooks'
            ],
            'objectives': [
                'Implement a robust @asynccontextmanager lifespan handler for FastAPI',
                'Initialize Redis connection pools and verify PostgreSQL schema connectivity before accepting HTTP traffic',
                'Execute graceful teardown of connection pools on SIGTERM/SIGINT signals'
            ],
            'concepts': [
                'ASGI Lifespan Protocol: Standardized communication between web servers and application frameworks for startup/shutdown',
                'Fail-Fast Startup: Halting server boot immediately if critical infrastructure (DB/Cache) is unreachable',
                'Graceful Teardown: Draining active requests and closing network sockets cleanly on process termination',
                'Idempotent Seeding: Running data initialization checks during startup without duplicating database records'
            ],
            'impl': 'backend/app/main.py defines lifespan(app: FastAPI) as an @asynccontextmanager. During startup, it logs the boot event, initializes the Redis connection pool (get_redis_client), verifies database schema readiness, and triggers seed_properties() to ensure demo listings exist. On shutdown, it yields control and safely closes Redis and database connections.',
            'files': [
                'backend/app/main.py (lifespan)',
                'backend/app/cache/redis.py (get_redis_client, close_redis_client)',
                'backend/app/db/session.py (engine, async_session_maker)'
            ],
            'data_flow': 'Uvicorn Boot -> Lifespan Context Manager Start -> Initialize Redis Pool -> Check PostgreSQL Readiness -> Run Seed Verification -> Yield Control -> Process Client HTTP Traffic -> SIGTERM Signal -> Lifespan Teardown -> Close Redis Pool -> Dispose DB Engine -> Process Exit',
            'lab_standalone': '''Build a standalone async lifespan test script:
1. Write a minimal FastAPI app with @asynccontextmanager async def lifespan(app: FastAPI).
2. In the startup phase, connect an async Redis client and verify await redis.ping().
3. Yield control to the application.
4. In the finally block, execute await redis.close().
5. Run using Uvicorn programmatically and verify startup and shutdown logs appear in exact sequence.''',
            'lab_mapping': 'Inspect backend/app/main.py lines 25-50 to see the exact lifespan definition and how exceptions during boot prevent the server from accepting traffic.',
            'acceptance_criteria': [
                'FastAPI instance is created with FastAPI(lifespan=lifespan) without any @app.on_event deprecation warnings.',
                'Redis connection pool is pinged and established during startup.',
                'Server boot aborts with a non-zero exit code if PostgreSQL or Redis connection fails.',
                'Sending SIGINT (Ctrl+C) gracefully closes all active Redis and database connections without dangling socket warnings.'
            ],
            'evidence': [
                'View server startup logs: docker logs estatemap-backend | grep -i lifespan.',
                'Verify clean shutdown by restarting the container: docker restart estatemap-backend and checking exit logs.'
            ],
            'outcome_conceptual': 'Complete grasp of the ASGI application lifecycle, understanding the execution timeline before, during, and after request processing.',
            'outcome_impl': 'Ability to write production-grade lifespan managers with health checks, database readiness polling, and socket cleanup from scratch.',
            'outcome_interview': 'Ability to explain the difference between legacy FastAPI event handlers and modern lifespan context managers and explain how connection pooling lifecycle is managed.',
            'mistakes': [
                'Using @app.on_event("startup") which is deprecated in FastAPI >= 0.93.0 and lacks structured error handling.',
                'Failing to wrap cleanup code in a finally block or after the yield, causing leaks if an error occurs during runtime.',
                'Executing blocking synchronous code inside the async lifespan function, freezing the ASGI event loop on boot.'
            ],
            'debug_symptom': 'RuntimeError: Event loop is closed or unclosed client session warnings during server shutdown.',
            'debug_investigate': 'Check if await redis.close() or await engine.dispose() is executed properly after the yield statement in the lifespan handler.',
            'debug_goal': 'Ensure all async resources are awaited and properly closed before the lifespan context exits.',
            'tradeoffs': [
                'Async Lifespan Context Manager vs On-Event Hooks: Lifespan is standardized across ASGI, supports structured exception handling, and shares state via app.state.',
                'Auto-seeding during lifespan vs External migration container: Auto-seeding simplifies local development and demo environments but must be guarded by idempotency in production.'
            ],
            'prod_current': 'Lifespan manages Redis pool lifecycle, DB engine verification, and demo data seeding.',
            'prod_scale': 'In Kubernetes, startup probe checks database connectivity; database seeding is moved to an init-container or CI/CD deployment job.',
            'q_basic': 'What is the ASGI lifespan protocol and how does FastAPI implement it?',
            'q_impl': 'How does EstateMap manage database and Redis connection lifecycle using the @asynccontextmanager?',
            'q_tradeoff': 'What are the risks of running database migrations or seeding inside the application lifespan versus a standalone CI/CD step?',
            'q_debug': 'How do you debug an ASGI application that hangs during boot and never begins accepting HTTP requests?',
            'q_sysdesign': 'How does the application lifecycle interact with Kubernetes Readiness and Liveness probes during rolling deployments?',
            'ans_framework': 'Explain: 1) What ASGI lifespan is (structured startup/shutdown protocol), 2) Why context managers are superior to event hooks (unified try/yield/finally semantics), 3) EstateMap\'s exact implementation (Redis pool + DB check + teardown), 4) The fail-fast principle in containerized deployments.',
            'conn_prev': 'Story 01 defined the directory structure; Story 02 activates the application entrypoint main.py.',
            'conn_next': 'Story 03 implements type-safe configuration management required by the lifespan handler.',
            'checklist': [
                'Can write an @asynccontextmanager lifespan function from scratch without reference',
                'Can explain why @app.on_event is deprecated in modern FastAPI',
                'Can implement proper resource cleanup in the shutdown phase',
                'Can configure startup health checks that follow the fail-fast principle'
            ]
        },
        {
            'num': 3,
            'title': 'Type-Safe Configuration with Pydantic-Settings',
            'points': 2,
            'why_exists': 'Hardcoding configuration constants or reading raw environment variables with os.getenv() leads to silent runtime crashes, security credential leaks, and deployment failures across development, staging, and production environments.',
            'problem_solved': 'Invalid environment variables (e.g. malformed connection URLs, missing JWT secrets, or string ports) cause silent runtime failures deep inside request handlers rather than failing fast during boot.',
            'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture'],
            'prereq_concepts': ['12-Factor App methodology (Config)', 'Pydantic v2 BaseSettings', 'Environment variable parsing and type coercion'],
            'depends_on': [1],
            'unlocks': [2, 4, 7, 14, 39, 52],
            'readiness': [
                'Understand .env file formats and OS environment variables',
                'Familiar with Pydantic type annotations and default values',
                'Able to explain why sensitive credentials must not be committed to Git'
            ],
            'objectives': [
                'Create a centralized, type-safe Settings class using pydantic-settings',
                'Enforce fail-fast startup validation for database URLs, secret keys, and provider configurations',
                'Support seamless overriding of configuration via .env files and Docker environment variables'
            ],
            'concepts': [
                '12-Factor Config Principle: Strict separation of config from code, storing config in environment variables',
                'Fail-Fast Validation: Crashing at startup with clear human-readable error messages if required configuration is invalid',
                'Type Coercion: Automatically casting environment strings to integers, booleans, and structured objects',
                'Settings Singleton Pattern: Caching the settings instance to avoid repeated filesystem reads'
            ],
            'impl': 'backend/app/core/config.py defines Settings(BaseSettings) with typed fields: DATABASE_URL (Postgres DSN), REDIS_URL (Redis DSN), SECRET_KEY (JWT signing string), ROUTING_PROVIDER (OSRM vs Mock), AI_PROVIDER (Ollama vs Gemini), and GEMINI_API_KEY. It utilizes model_config = SettingsConfigDict(env_file=".env", extra="ignore") and exposes a singleton settings = Settings().',
            'files': [
                'backend/app/core/config.py (Settings)',
                '.env.example',
                'backend/app/main.py'
            ],
            'data_flow': 'OS Environment / .env File -> pydantic_settings parses string values -> Validates types & constraints -> Instantiates settings singleton -> Injected across DB, Security, Cache, and AI subsystems at startup',
            'lab_standalone': '''Build a type-safe settings module:
1. Install pydantic-settings.
2. Define a DatabaseSettings class with DB_PORT: int = 5432 and DB_HOST: str.
3. Add a field validator that ensures DB_PORT is between 1 and 65535.
4. Pass invalid environment variables (DB_PORT="not_a_number") and verify Pydantic raises a descriptive ValidationError during import.''',
            'lab_mapping': 'Inspect backend/app/core/config.py and modify DATABASE_URL to an invalid scheme (e.g. mysql://) to observe Pydantic validation behavior.',
            'acceptance_criteria': [
                'All environment variables are validated into strongly-typed attributes on settings.',
                'Missing required variables (like DATABASE_URL) cause immediate startup failure with clear logs.',
                '.env file values are loaded in development while OS environment variables take precedence in Docker/production.',
                'No secret credentials or API keys are hardcoded in source code.'
            ],
            'evidence': [
                'Run docker exec estatemap-backend python -c "from app.core.config import settings; print(settings.DATABASE_URL)".',
                'Verify .env.example contains all required configuration keys without sensitive production values.'
            ],
            'outcome_conceptual': 'Understanding of 12-Factor App configuration principles and how type-safe parsing prevents environment mismatch bugs.',
            'outcome_impl': 'Ability to build declarative, self-validating configuration layers using pydantic-settings from scratch.',
            'outcome_interview': 'Ability to articulate why pydantic-settings is superior to os.getenv() and explain how configuration validation integrates with CI/CD.',
            'mistakes': [
                'Sprinkling os.getenv("VAR_NAME") calls across arbitrary business logic files instead of using a centralized settings object.',
                'Committing .env files containing live secrets to source control.',
                'Allowing default fallback values for production secrets (like JWT SECRET_KEY = "changeme"), creating security vulnerabilities.'
            ],
            'debug_symptom': 'pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings on server startup.',
            'debug_investigate': 'Read the terminal output to identify the exact field name and type expected by Pydantic. Check .env or Docker environment overrides.',
            'debug_goal': 'Supply the required environment variable with the correct type format (e.g. valid URI or integer).',
            'tradeoffs': [
                'Pydantic-Settings vs Raw os.environ / python-dotenv: Pydantic provides type coercion, validation, and editor auto-completion at zero runtime cost after boot.',
                'Single global settings object vs Multiple domain settings: Single global object simplifies dependency injection in small to medium backends.'
            ],
            'prod_current': 'Settings(BaseSettings) singleton loading from environment variables with .env fallback.',
            'prod_scale': 'Integrate with HashiCorp Vault or AWS Secrets Manager by mounting secrets as environment variables or volume files at container launch.',
            'q_basic': 'Why is using pydantic-settings preferred over standard os.getenv() in Python backends?',
            'q_impl': 'How does EstateMap validate configuration at boot time and how are default values specified?',
            'q_tradeoff': 'What are the tradeoffs between validating configuration at startup versus reading environment variables dynamically at runtime?',
            'q_debug': 'If a service fails to start in staging due to a Pydantic ValidationError, how do you isolate whether the issue is a missing variable or a type mismatch?',
            'q_sysdesign': 'How do you manage secret rotation (e.g. database passwords or API keys) in a production microservices environment using 12-factor configuration?',
            'ans_framework': 'Discuss: 1) The 12-Factor App config mandate, 2) Fail-Fast principle (crash early on invalid config rather than during a transaction), 3) Type safety & developer ergonomics (IDE completion, automatic integer parsing), 4) EstateMap implementation details.',
            'conn_prev': 'Story 02 established the application lifecycle; Story 03 supplies validated settings to that lifecycle.',
            'conn_next': 'Story 04 uses Pydantic schemas to validate incoming HTTP request payloads and outgoing responses.',
            'checklist': [
                'Can define a custom BaseSettings class with required and optional fields',
                'Can implement custom field validators for complex configuration strings',
                'Can explain how .env file loading interacts with OS environment precedence',
                'Can defend the fail-fast principle in cloud-native applications'
            ]
        }
    ]

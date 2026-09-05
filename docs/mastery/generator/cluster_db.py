# -*- coding: utf-8 -*-
# Stories 7-13 & 18-20 (Database Modeling, ORM, Migrations, Connection Pooling, CRUD & Filtering)

def get_db_stories():
    stories = []

    # Story 07
    stories.append({
        'num': 7,
        'title': 'PostgreSQL Relational Modeling & Schema Integrity',
        'points': 5,
        'why_exists': 'Application-level validation can be bypassed by manual database edits, buggy scripts, or concurrent transactions. Relational schema constraints in PostgreSQL guarantee ACID consistency and domain integrity at the persistence layer.',
        'problem_solved': 'Corrupted property records (e.g. negative prices, orphan amenities, missing foreign keys, null coordinates) crashing search and ranking queries.',
        'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture', 'Story 03 — Type-Safe Configuration with Pydantic-Settings'],
        'prereq_concepts': ['Relational database design (3NF)', 'ACID transactions', 'Foreign key constraints', 'CHECK constraints', 'PostgreSQL 16 datatypes'],
        'depends_on': [1, 3],
        'unlocks': [8, 9, 10, 11, 21],
        'readiness': [
            'Understand primary keys, foreign keys, and unique indexes in SQL',
            'Familiar with PostgreSQL column types (VARCHAR, INTEGER, NUMERIC, TIMESTAMP, JSONB)',
            'Able to explain why CHECK constraints protect data integrity'
        ],
        'objectives': [
            'Design normalized relational tables (users, properties, property_amenities, pois, user_favorites, interactions)',
            'Enforce database-level CHECK constraints (price > 0, bedrooms >= 0, bathrooms >= 0)',
            'Configure cascading deletes and referential integrity rules across related entities'
        ],
        'concepts': [
            'Declarative Schema Constraints: Enforcing domain invariants at the database engine level rather than relying solely on application code',
            'Referential Integrity: Ensuring foreign keys strictly reference existing parent rows with ON DELETE CASCADE or ON DELETE RESTRICT',
            'Surrogate vs Natural Keys: Using auto-incrementing integer or UUID primary keys for performance and decoupling from mutable business identifiers',
            'JSONB Columns: Storing unstructured or semi-structured feature metadata while maintaining indexing capabilities'
        ],
        'impl': 'EstateMap defines relational schemas in backend/app/models/: Property (id, title, price, bedrooms, bathrooms, square_feet, property_type, location, city, created_at), User (id, email, hashed_password, role, is_active), POI (id, name, category, location, city), and Interaction (id, user_id, property_id, interaction_type, timestamp).',
        'files': [
            'backend/app/models/property.py',
            'backend/app/models/user.py',
            'backend/app/models/poi.py',
            'backend/app/models/interaction.py'
        ],
        'data_flow': 'FastAPI Endpoint -> PropertyService -> Repository -> SQLAlchemy ORM Model -> PostgreSQL 16 Engine -> Schema Constraints Checked (CHECK price > 0, FK user_id) -> Row Inserted / Updated -> Transaction Committed',
        'lab_standalone': '''Build a standalone PostgreSQL schema test:
1. Connect to PostgreSQL using psql or asyncpg.
2. Create table properties with CHECK (price > 0 AND bedrooms >= 1).
3. Attempt to insert a row with price = -500 and verify PostgreSQL rejects with CheckViolationError.
4. Insert a valid row and verify ACID durability.''',
        'lab_mapping': 'Inspect backend/app/models/property.py and examine the column definitions, constraints, and relationships with User and POI.',
        'acceptance_criteria': [
            'All database tables define explicit primary keys, not-null constraints, and sensible defaults.',
            'CHECK constraints reject invalid domain values (e.g. price <= 0) at the SQL level.',
            'Foreign key relationships enforce referential integrity between properties, users, and interactions.',
            'Timestamps (created_at, updated_at) are automatically populated with timezone-aware UTC timestamps.'
        ],
        'evidence': [
            'Inspect database schema: docker exec -it estatemap-postgres psql -U postgres -d estatemap -c "\d properties".',
            'Attempt invalid insert in psql and verify check constraint rejection.'
        ],
        'outcome_conceptual': 'Mastery of relational data modeling, domain invariants, and PostgreSQL schema constraints.',
        'outcome_impl': 'Ability to design and implement robust, normalized PostgreSQL relational schemas from scratch.',
        'outcome_interview': 'Ability to explain why database-level constraints are necessary even when using Pydantic validation at the API boundary.',
        'mistakes': [
            'Relying solely on application-level validation and omitting SQL CHECK and NOT NULL constraints.',
            'Using FLOAT instead of NUMERIC/BIGINT for currency prices, leading to binary floating-point rounding errors.',
            'Creating bidirectional foreign keys that cause circular reference deadlocks during table truncation or deletion.'
        ],
        'debug_symptom': 'psycopg2.errors.CheckViolation: new row for relation "properties" violates check constraint "price_positive".',
        'debug_investigate': 'Check the incoming service payload or migration script to see why a non-positive price or invalid coordinate was passed.',
        'debug_goal': 'Ensure domain services validate inputs before emitting SQL and sanitize bulk ingestion data.',
        'tradeoffs': [
            'PostgreSQL Relational vs MongoDB NoSQL: Relational tables provide ACID guarantees, relational joins, and strict spatial indexing; document databases offer flexible schema but sacrifice relational integrity.',
            'NUMERIC vs BIGINT for prices: NUMERIC allows exact decimals (e.g. cents/paise); BIGINT stores currency in lowest denominator units.'
        ],
        'prod_current': 'PostgreSQL 16 relational tables with declarative constraints and PostGIS spatial columns.',
        'prod_scale': 'Implement table partitioning by city or creation year (declarative range partitioning) when table size exceeds 100 million rows.',
        'q_basic': 'Why are database CHECK constraints important if Pydantic already validates incoming HTTP requests?',
        'q_impl': 'How does EstateMap structure the relationship between Properties, Users, POIs, and Interactions in PostgreSQL?',
        'q_tradeoff': 'What are the tradeoffs between storing property amenities in a normalized join table versus a JSONB column?',
        'q_debug': 'How do you handle a Foreign Key violation error during a high-throughput bulk ingestion pipeline?',
        'q_sysdesign': 'How would you design a database schema to support real estate property listing versioning and audit history at scale?',
        'ans_framework': 'Explain: 1) Defense-in-depth: API validation protects users, DB constraints protect data integrity against all sources, 2) EstateMap relational architecture (Properties, Users, POIs), 3) ACID guarantees, 4) Tradeoffs of JSONB vs relational join tables.',
        'conn_prev': 'Story 01-06 established API transport and logging; Story 07 establishes persistent relational storage.',
        'conn_next': 'Story 08 maps these PostgreSQL relational tables to Python objects using SQLAlchemy 2.0 Declarative Models.',
        'checklist': [
            'Can write raw SQL DDL with primary keys, foreign keys, and CHECK constraints',
            'Can explain why monetary values should never be stored in standard IEEE floating-point columns',
            'Can design a normalized relational schema for real estate discovery',
            'Can explain the difference between ON DELETE CASCADE and ON DELETE SET NULL'
        ]
    })

    # Story 08
    stories.append({
        'num': 8,
        'title': 'SQLAlchemy 2.0 Declarative Models & Repository Pattern',
        'points': 5,
        'why_exists': 'Scattering raw SQL queries across API endpoints creates tight coupling to database dialects, makes refactoring painful, and exposes code to SQL injection risks. The Repository Pattern encapsulates data access behind clean Python abstractions.',
        'problem_solved': 'Direct SQL queries mixed with HTTP handlers duplicate filtering logic, hinder unit testing without live databases, and break separation of concerns.',
        'prereq_stories': ['Story 07 — PostgreSQL Relational Modeling & Schema Integrity'],
        'prereq_concepts': ['SQLAlchemy 2.0 syntax (select, update, delete)', 'Declarative Base & Mapped type annotations', 'Repository Pattern', 'Unit of Work'],
        'depends_on': [7],
        'unlocks': [9, 18, 19, 20],
        'readiness': [
            'Understand Object-Relational Mapping (ORM) concepts',
            'Familiar with Python class inheritance and dataclasses',
            'Able to explain how the Repository pattern abstracts data access'
        ],
        'objectives': [
            'Define modern SQLAlchemy 2.0 declarative models using Mapped[] and mapped_column()',
            'Implement the Repository Pattern with BaseRepository, PropertyRepository, and UserRepository',
            'Decouple domain business logic from database query mechanics'
        ],
        'concepts': [
            'SQLAlchemy 2.0 Style: Moving away from legacy session.query() to explicit 2.0 select() statements with full type hint support',
            'Mapped & mapped_column: Modern type-safe column declarations integrated with Mypy and IDE autocompletion',
            'Repository Pattern: Mediating between the domain service layer and data mapping layers using collection-like interfaces',
            'Base Repository Generic: Creating reusable CRUD methods (get_by_id, list, create, update, delete) via Python generics TypeVar'
        ],
        'impl': 'backend/app/models/base.py defines Base = declarative_base(). backend/app/models/property.py defines class Property(Base) with Mapped columns. backend/app/repositories/base_repo.py implements BaseRepository[ModelType], and backend/app/repositories/property_repo.py implements PropertyRepository with spatial and filter query methods.',
        'files': [
            'backend/app/models/base.py',
            'backend/app/models/property.py',
            'backend/app/repositories/base_repo.py',
            'backend/app/repositories/property_repo.py'
        ],
        'data_flow': 'Domain Service calls property_repo.get_by_id(db, id) -> PropertyRepository executes select(Property).where(Property.id == id) -> SQLAlchemy compiles query to parameterized SQL -> Asyncpg executes against PostgreSQL -> Returns Property entity instance -> Service processes entity',
        'lab_standalone': '''Build a standalone SQLAlchemy 2.0 Repository lab:
1. Define class Item(Base) with id: Mapped[int] and name: Mapped[str].
2. Implement class ItemRepository: async def get(self, session, id) -> Optional[Item].
3. Execute select(Item).where(Item.id == id) using AsyncSession.
4. Test inserting and retrieving items via repository methods.''',
        'lab_mapping': 'Inspect backend/app/repositories/property_repo.py and trace how filter_properties constructs dynamic SQLAlchemy select() queries based on search parameters.',
        'acceptance_criteria': [
            'All database models use modern SQLAlchemy 2.0 Mapped[] type annotations.',
            'No raw SQL string interpolation is used; all queries use parameterized SQLAlchemy select/update constructs.',
            'Repository methods encapsulate all database interaction, keeping domain services free of ORM session management.',
            'BaseRepository provides generic CRUD operations inherited by all entity repositories.'
        ],
        'evidence': [
            'Run docker exec estatemap-backend pytest tests/unit/test_repositories.py.',
            'Check SQLAlchemy query execution logs in DEBUG mode: verify proper parameterized SQL generation.'
        ],
        'outcome_conceptual': 'Deep understanding of modern SQLAlchemy 2.0 architecture, type-safe ORM mapping, and repository design patterns.',
        'outcome_impl': 'Ability to scaffold type-safe SQLAlchemy 2.0 models and generic repository layers in Python from scratch.',
        'outcome_interview': 'Ability to explain why SQLAlchemy 2.0 transitioned to select() and articulate the benefits of the Repository pattern in enterprise backends.',
        'mistakes': [
            'Using legacy SQLAlchemy 1.x session.query(Model) syntax which lacks type inference in modern IDEs.',
            'Instantiating database sessions inside repositories instead of injecting the session from FastAPI dependency injection.',
            'Returning raw SQLAlchemy internal query objects from repositories into API route controllers.'
        ],
        'debug_symptom': 'AttributeError: \'Select\' object has no attribute \'all\' when migrating from SQLAlchemy 1.4 to 2.0.',
        'debug_investigate': 'Check if the code attempted session.query().all() instead of await session.execute(select(...)) and result.scalars().all().',
        'debug_goal': 'Refactor query to modern 2.0 style: result = await db.execute(select(Property)); return result.scalars().all().',
        'tradeoffs': [
            'SQLAlchemy ORM vs Raw SQL / SQLModel: SQLAlchemy 2.0 provides mature migrations, spatial extension support (GeoAlchemy2), and comprehensive relationship mapping.',
            'Repository Pattern vs Active Record: Repository pattern decouples business logic from persistence at the cost of additional boilerplate classes.'
        ],
        'prod_current': 'SQLAlchemy 2.0 declarative models with Generic Async BaseRepository and specialized PropertyRepository.',
        'prod_scale': 'Add read/write query splitting in repositories to route SELECT queries to read replicas and INSERT/UPDATE to the primary database.',
        'q_basic': 'What is the difference between SQLAlchemy 1.4 query syntax and SQLAlchemy 2.0 select syntax?',
        'q_impl': 'How does EstateMap implement the Repository Pattern to isolate database operations from domain services?',
        'q_tradeoff': 'What are the pros and cons of using an ORM like SQLAlchemy versus a lightweight query builder like asyncpg directly?',
        'q_debug': 'How do you prevent the N+1 query problem when loading properties and their associated owner details in SQLAlchemy 2.0?',
        'q_sysdesign': 'How do you design a data access layer that supports both PostgreSQL relational queries and Elasticsearch full-text search transparently?',
        'ans_framework': 'Discuss: 1) The role of the Repository Pattern in Clean Architecture, 2) Modern SQLAlchemy 2.0 type safety with Mapped and mapped_column, 3) Preventing SQL injection via AST query compilation, 4) EstateMap PropertyRepository implementation.',
        'conn_prev': 'Story 07 established PostgreSQL schemas; Story 08 maps those schemas into Python classes via SQLAlchemy 2.0.',
        'conn_next': 'Story 09 connects these declarative models to PostgreSQL using non-blocking asynchronous database drivers (asyncpg).',
        'checklist': [
            'Can write SQLAlchemy 2.0 models using Mapped[] and mapped_column()',
            'Can write select(), update(), and delete() statements using modern 2.0 syntax',
            'Can implement a generic BaseRepository[T] with CRUD methods',
            'Can explain how selectinload and joinedload solve N+1 query problems'
        ]
    })

    # Story 09
    stories.append({
        'num': 9,
        'title': 'Non-Blocking Async Database Access with Asyncpg',
        'points': 5,
        'why_exists': 'Synchronous database drivers (like psycopg2) block the Python asyncio event loop during network I/O, reducing a concurrent web server to handling only one database query at a time per OS thread.',
        'problem_solved': 'High concurrent traffic causes severe latency spikes and connection timeouts because slow database queries freeze the single-threaded asyncio event loop.',
        'prereq_stories': ['Story 02 — FastAPI Lifespan & Application Lifecycle', 'Story 07 — PostgreSQL Relational Modeling & Schema Integrity', 'Story 08 — SQLAlchemy 2.0 Declarative Models & Repository Pattern'],
        'prereq_concepts': ['Python Asyncio event loop', 'Async database drivers (asyncpg)', 'SQLAlchemy AsyncSession & create_async_engine', 'Event loop non-blocking I/O'],
        'depends_on': [2, 7, 8],
        'unlocks': [13, 18, 86],
        'readiness': [
            'Understand async/await execution mechanics in Python',
            'Able to explain why blocking I/O freezes the asyncio event loop',
            'Familiar with PostgreSQL wire protocol communication'
        ],
        'objectives': [
            'Configure create_async_engine with postgresql+asyncpg:// connection strings',
            'Implement async_sessionmaker to generate AsyncSession instances for FastAPI request lifecycle',
            'Execute concurrent database queries asynchronously using asyncio.gather without thread blocking'
        ],
        'concepts': [
            'Asyncpg: High-performance, pure asynchronous PostgreSQL driver written in Cython utilizing native binary protocol',
            'SQLAlchemy Async Engine: Translating ORM queries into async wire protocol packets executed over asyncio streams',
            'Request-Scoped Session Lifecycle: Opening an AsyncSession on request start and committing/rolling back and closing upon request completion',
            'Event Loop Freedom: Yielding execution to concurrent HTTP requests while waiting for PostgreSQL query responses'
        ],
        'impl': 'backend/app/db/session.py configures engine = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True) and async_session_maker = async_sessionmaker(engine, expire_on_commit=False). FastAPI dependency get_db() yields an AsyncSession wrapped in a context manager.',
        'files': [
            'backend/app/db/session.py',
            'backend/app/api/deps.py (get_db)',
            'backend/app/core/config.py'
        ],
        'data_flow': 'FastAPI endpoint requests get_db() -> async_sessionmaker creates AsyncSession -> Passed to PropertyService -> Repository awaits session.execute(query) -> Asyncpg transmits binary query packet over non-blocking socket -> Event loop processes other HTTP requests -> DB responds -> Asyncpg wakes coroutine -> Result returned',
        'lab_standalone': '''Build an async database concurrency benchmark:
1. Connect to PostgreSQL using asyncpg.
2. Launch 100 concurrent queries using asyncio.gather([db.fetch("SELECT pg_sleep(0.1)") for _ in range(100)]).
3. Measure total execution time: verify it finishes in ~150ms rather than 10 seconds (100 * 0.1s).
4. Contrast with synchronous psycopg2 execution.''',
        'lab_mapping': 'Inspect backend/app/db/session.py to see how create_async_engine and async_sessionmaker are configured with connection pooling parameters.',
        'acceptance_criteria': [
            'All database queries in repositories and services use await session.execute() without blocking the event loop.',
            'FastAPI dependency get_db yields an AsyncSession and reliably closes the session in a finally block.',
            'Concurrent API requests execute in parallel without queueing behind slow database queries.',
            'SQLAlchemy connection pool utilizes pool_pre_ping=True to discard stale connections.'
        ],
        'evidence': [
            'Run docker exec estatemap-backend pytest tests/integration/test_db_async.py.',
            'Verify async driver in settings: check DATABASE_URL begins with postgresql+asyncpg://.'
        ],
        'outcome_conceptual': 'Clear mastery of asynchronous database I/O, event loop concurrency, and non-blocking database driver mechanics.',
        'outcome_impl': 'Ability to configure and manage production SQLAlchemy async engines and sessions with asyncpg in FastAPI.',
        'outcome_interview': 'Ability to explain why asyncpg outperforms psycopg2 and how AsyncSession operates under the hood.',
        'mistakes': [
            'Using standard synchronous postgresql:// instead of postgresql+asyncpg:// in DATABASE_URL.',
            'Calling synchronous blocking methods (e.g. time.sleep() or sync ORM operations) inside async endpoints.',
            'Forgetting expire_on_commit=False, causing lazy-load GreenletSpawn errors when accessing model attributes after commit.'
        ],
        'debug_symptom': 'sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been spawned; can not call await_only() here.',
        'debug_investigate': 'Check if an un-eagerly-loaded relationship attribute was accessed outside an active async session context.',
        'debug_goal': 'Use selectinload or joinedload in the initial repository select query, and set expire_on_commit=False on the session maker.',
        'tradeoffs': [
            'Asyncpg vs Psycopg2/3: Asyncpg delivers 3-5x higher throughput under high concurrency in asyncio applications.',
            'Async ORM complexity vs Raw SQL: Async ORM requires careful handling of relationships and greenlets, but provides strong type safety.'
        ],
        'prod_current': 'create_async_engine with asyncpg driver, pool_size=20, and expire_on_commit=False.',
        'prod_scale': 'Deploy PgBouncer in transaction pooling mode in front of PostgreSQL to support 10,000+ client connections without exhausting database RAM.',
        'q_basic': 'Why is an asynchronous driver like asyncpg necessary when using FastAPI with PostgreSQL?',
        'q_impl': 'How does EstateMap configure SQLAlchemy async_sessionmaker and manage session lifecycle with FastAPI dependencies?',
        'q_tradeoff': 'What causes the dreaded MissingGreenlet error in SQLAlchemy async and how do you prevent it?',
        'q_debug': 'How do you detect if a third-party library or legacy function is secretly making blocking synchronous calls inside an async route?',
        'q_sysdesign': 'How do you configure connection pool sizes across 20 horizontally scaled FastAPI application containers sharing a single PostgreSQL primary?',
        'ans_framework': 'Explain: 1) Single-threaded event loop architecture in Python, 2) Why blocking socket I/O kills concurrency, 3) Asyncpg binary wire protocol benefits, 4) EstateMap session lifecycle and expire_on_commit=False configuration.',
        'conn_prev': 'Story 08 defined declarative models; Story 09 connects them asynchronously via asyncpg.',
        'conn_next': 'Story 10 manages database schema evolution across environments using Alembic migrations.',
        'checklist': [
            'Can configure create_async_engine with postgresql+asyncpg:// and connection pooling',
            'Can implement an async get_db dependency yielding an AsyncSession',
            'Can explain the cause and fix for MissingGreenlet exceptions in SQLAlchemy async',
            'Can explain why asyncpg is significantly faster than psycopg2'
        ]
    })

    return stories

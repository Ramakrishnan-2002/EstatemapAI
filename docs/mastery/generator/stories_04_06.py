# -*- coding: utf-8 -*-
# Stories 4 to 6

def get_stories():
    return [
        {
            'num': 4,
            'title': 'API Request/Response Schemas with Pydantic v2',
            'points': 3,
            'why_exists': 'Robust REST APIs require strict input validation to prevent SQL injection, type corruption, and malformed client payloads, alongside deterministic response filtering to prevent accidental data leaks.',
            'problem_solved': 'Accepting unvalidated client JSON leads to database errors, security exploits, and unpredictable response structures that break mobile and web frontend clients.',
            'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture', 'Story 03 — Type-Safe Configuration with Pydantic-Settings'],
            'prereq_concepts': ['HTTP REST semantics', 'Pydantic v2 BaseModel & Field', 'Data Transfer Object (DTO) pattern', 'JSON Schema / OpenAPI 3.0'],
            'depends_on': [1, 3],
            'unlocks': [5, 18, 19, 27, 34, 55],
            'readiness': [
                'Understand Python type annotations (str, int, float, Optional, List)',
                'Familiar with JSON serialization and deserialization',
                'Able to explain the purpose of DTOs in multi-tier architecture'
            ],
            'objectives': [
                'Define declarative Pydantic v2 schemas for API request validation and response serialization',
                'Implement custom @field_validator and @model_validator logic for cross-field consistency',
                'Prevent Data Loss Prevention (DLP) leaks by using response_model filtering to omit sensitive model attributes'
            ],
            'concepts': [
                'Data Transfer Object (DTO): Decoupling internal database models from external public API representations',
                'Automatic OpenAPI Generation: Generating live Swagger documentation from Pydantic type annotations',
                'Strict Mode Validation: Rejecting unexpected data types and extra fields using extra="forbid"',
                'Data Loss Prevention (DLP): Ensuring internal attributes (e.g. hashed_password, internal IDs) are never serialized to clients'
            ],
            'impl': 'backend/app/schemas/ defines domain schemas: property.py (PropertyCreate, PropertyUpdate, PropertyResponse), search.py (RankedSearchRequest, WeightVector, SpatialFilter), auth.py (Token, UserCreate, UserResponse), and comparison.py (ComparisonResponse). Schemas enforce constraints like price > 0, bedrooms >= 1, and coordinate bounds (-90 <= lat <= 90).',
            'files': [
                'backend/app/schemas/property.py',
                'backend/app/schemas/search.py',
                'backend/app/schemas/auth.py',
                'backend/app/api/v1/endpoints/properties.py'
            ],
            'data_flow': 'Client JSON Payload -> FastAPI endpoint signature -> Pydantic Deserialization & Validation -> (Validation Error? Return 422 JSON) -> Validated Schema passed to Domain Service -> Service returns Domain/ORM Model -> Pydantic response_model serializes filtered JSON -> HTTP 200 Response',
            'lab_standalone': '''Build a validated Pydantic schema suite:
1. Create PropertyCreate with title: str, price: float = Field(gt=0), bedrooms: int = Field(ge=1).
2. Add a @field_validator("title") that rejects strings with leading/trailing whitespace.
3. Add a PropertyResponse schema with model_config = ConfigDict(from_attributes=True).
4. Test validating an ORM-like Python object into PropertyResponse and verify serialization.''',
            'lab_mapping': 'Inspect backend/app/schemas/search.py to see how WeightVector validates that weight components sum to a normalized range.',
            'acceptance_criteria': [
                'Invalid API requests (e.g. price: -100 or missing fields) return HTTP 422 with structured field error messages.',
                'All API route handlers specify explicit response_model annotations.',
                'Sensitive database columns (e.g. hashed_password) are never present in any response schema.',
                'Swagger UI at /docs accurately reflects all request/response models and field constraints.'
            ],
            'evidence': [
                'Send invalid POST payload: curl -X POST http://localhost:8000/api/v1/properties -H "Content-Type: application/json" -d "{\\\"price\\\": -10}" -> verify 422 response.',
                'Run docker exec estatemap-backend pytest tests/unit/test_schemas.py.'
            ],
            'outcome_conceptual': 'Deep understanding of boundary validation, schema contracts, and how Pydantic v2 Rust core delivers high-speed serialization.',
            'outcome_impl': 'Ability to construct complex, nested Pydantic schemas with custom validators, ORM compatibility, and field aliases from scratch.',
            'outcome_interview': 'Ability to explain how Pydantic protects against data pollution, enables automatic OpenAPI spec generation, and prevents security leaks.',
            'mistakes': [
                'Reusing the same Pydantic schema for both creation (input) and reading (output), exposing internal or read-only fields.',
                'Using Pydantic v1 syntax (@validator instead of @field_validator, class Config instead of ConfigDict) in Pydantic v2.',
                'Performing heavy database queries inside Pydantic field validators instead of domain services.'
            ],
            'debug_symptom': 'pydantic.errors.ResponseValidationError when an endpoint returns data that does not match the declared response_model.',
            'debug_investigate': 'Check if the ORM model returned by the service has missing attributes or mismatched types compared to the response_model schema.',
            'debug_goal': 'Align the repository query or schema definition, setting from_attributes=True on the response schema.',
            'tradeoffs': [
                'Pydantic v2 vs Marshmallow / Cerberus: Pydantic v2 is compiled in Rust, offering 5-10x faster validation and native integration with FastAPI type hints.',
                'Single schema hierarchy vs Separate Create/Update/Response schemas: Separate schemas increase boilerplate slightly but provide total type safety at API boundaries.'
            ],
            'prod_current': 'Strict Pydantic v2 models with from_attributes=True across all API endpoints.',
            'prod_scale': 'Compile Pydantic schemas to TypeScript types using pydantic-to-typescript to ensure end-to-end type safety between backend and Next.js frontend.',
            'q_basic': 'What is the purpose of Pydantic schemas in FastAPI and how do they differ from database ORM models?',
            'q_impl': 'How does EstateMap use Pydantic from_attributes=True (formerly orm_mode) to serialize SQLAlchemy models?',
            'q_tradeoff': 'Why should you avoid using database ORM models directly in API route handlers without a Pydantic DTO layer?',
            'q_debug': 'How do you diagnose and fix a 422 Unprocessable Entity error returned by FastAPI when sending a complex nested JSON body?',
            'q_sysdesign': 'How do API schemas enforce contract testing and backwards compatibility in a public REST API?',
            'ans_framework': 'Highlight: 1) Boundary validation (never trust client input), 2) DTO pattern separating transport from persistence, 3) Security DLP (filtering internal DB fields), 4) Performance benefits of Pydantic v2 Rust serialization engine.',
            'conn_prev': 'Story 03 defined configuration schemas; Story 04 defines HTTP payload and response schemas.',
            'conn_next': 'Story 05 introduces centralized RFC 7807 error handling to format schema validation failures uniformly.',
            'checklist': [
                'Can write Pydantic v2 models using Field, @field_validator, and @model_validator',
                'Can configure model_config = ConfigDict(from_attributes=True) for ORM serialization',
                'Can explain how FastAPI transforms Pydantic validation errors into HTTP 422 responses',
                'Can design an API schema architecture that prevents sensitive data leaks'
            ]
        },
        {
            'num': 5,
            'title': 'RFC 7807 Centralized Error Handling',
            'points': 3,
            'why_exists': 'Inconsistent error formats across endpoints break frontend client parsers, complicate debugging, and leak internal server stack traces to external clients.',
            'problem_solved': 'Uncaught exceptions return generic HTML 500 pages or unstructured JSON strings, leaving frontend applications unable to display actionable error messages or correlate errors with backend logs.',
            'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture', 'Story 04 — API Request/Response Schemas with Pydantic v2'],
            'prereq_concepts': ['RFC 7807 Problem Details specification', 'FastAPI Exception Handlers', 'Python custom exception hierarchies'],
            'depends_on': [1, 4],
            'unlocks': [6, 14, 18, 58],
            'readiness': [
                'Understand HTTP status code semantics (400, 401, 403, 404, 409, 422, 500)',
                'Familiar with Python try/except and creating custom subclasses of Exception',
                'Able to explain why raw stack traces should never be exposed in production API responses'
            ],
            'objectives': [
                'Implement custom domain exceptions (EntityNotFoundError, AuthenticationError, RateLimitExceededError)',
                'Register global FastAPI exception handlers that conform strictly to the RFC 7807 Problem Details standard',
                'Attach unique correlation request_id values to all error responses for distributed log tracing'
            ],
            'concepts': [
                'RFC 7807 Problem Details: Standardized JSON format (type, title, status, detail, instance) for HTTP API errors',
                'Domain Exception Decoupling: Raising pure business exceptions in services without hardcoding HTTP status codes in domain logic',
                'Global Exception Interception: Centralizing error-to-HTTP mapping in FastAPI exception handler middleware',
                'Information Redaction: Sanitizing internal database and infrastructure error messages before serialization'
            ],
            'impl': 'backend/app/core/exceptions.py defines the domain exception hierarchy (EstateMapError, PropertyNotFoundError, InvalidCoordinatesError, AuthenticationError, RateLimitExceededError). backend/app/core/exception_handlers.py registers global handlers on the FastAPI app, converting these exceptions, Pydantic RequestValidationError, and unhandled Exception into RFC 7807 compliant JSON envelopes containing error_code, message, status_code, and request_id.',
            'files': [
                'backend/app/core/exceptions.py',
                'backend/app/core/exception_handlers.py',
                'backend/app/main.py (register_exception_handlers)'
            ],
            'data_flow': 'Service raises DomainException -> Bubble up through endpoint -> Intercepted by registered FastAPI exception handler -> Extract request_id from request.state -> Format RFC 7807 JSON Envelope -> Return JSONResponse with appropriate HTTP status code',
            'lab_standalone': '''Create an RFC 7807 error handling lab:
1. Define a base AppError(Exception) with status_code: int and error_code: str.
2. Subclass UserNotFoundError(AppError) with status_code=404 and error_code="USER_NOT_FOUND".
3. Write a FastAPI global handler @app.exception_handler(AppError) returning {"type": "about:blank", "title": exc.error_code, "status": exc.status_code, "detail": str(exc), "instance": request.url.path}.
4. Trigger the error from a route and verify standard JSON structure.''',
            'lab_mapping': 'Inspect backend/app/core/exception_handlers.py and observe how validation_exception_handler formats Pydantic validation errors into clean field-by-field messages.',
            'acceptance_criteria': [
                'All error responses returned by the API follow the standardized JSON envelope structure.',
                'Raising a domain exception in a service automatically maps to the correct HTTP status code without manual HTTPException raises in endpoints.',
                'Unhandled 500 errors log full tracebacks to the server log but return a sanitized message to the client.',
                'Every error payload includes a non-empty request_id correlating with server log entries.'
            ],
            'evidence': [
                'Request non-existent property: curl -i http://localhost:8000/api/v1/properties/999999 -> verify JSON envelope with status 404.',
                'Run docker exec estatemap-backend pytest tests/unit/test_exceptions.py.'
            ],
            'outcome_conceptual': 'Clear mental model of centralized error handling and RFC 7807 compliance in modern REST APIs.',
            'outcome_impl': 'Ability to design and implement a complete, decoupled domain exception and global handler architecture in FastAPI from scratch.',
            'outcome_interview': 'Ability to explain how RFC 7807 improves API usability, client resilience, and distributed debugging in production.',
            'mistakes': [
                'Raising fastapi.HTTPException directly inside deep database repository or calculation methods, coupling persistence to HTTP transport.',
                'Letting raw SQL errors (e.g. PostgreSQL foreign key violation) leak directly to the client JSON response.',
                'Returning HTTP 200 with an {"status": "error", "message": "..."} payload (anti-pattern).'
            ],
            'debug_symptom': 'Frontend displays [object Object] or crashes on unexpected HTML 500 error page.',
            'debug_investigate': 'Check if an unhandled Python exception bypassed domain handlers and verify the global Exception catch-all handler is registered in main.py.',
            'debug_goal': 'Register a fallback exception handler for Exception that returns a structured 500 Problem Details envelope.',
            'tradeoffs': [
                'RFC 7807 Problem Details vs Custom JSON error schema: RFC 7807 is an open IETF standard recognized by client SDKs and API gateways.',
                'Domain Exceptions vs FastAPI HTTPException: Domain exceptions decouple business logic from HTTP transport, enabling service reuse in CLI or background workers.'
            ],
            'prod_current': 'Centralized exception handlers registered in main.py producing RFC 7807 compliant responses with request_id correlation.',
            'prod_scale': 'Integrate exception handlers with Sentry or Datadog to automatically capture uncaught exceptions with full stack traces and request context.',
            'q_basic': 'What is the RFC 7807 Problem Details specification and why is it used in REST APIs?',
            'q_impl': 'How does EstateMap handle exceptions across the service and repository layers without coupling them to FastAPI\'s HTTPException?',
            'q_tradeoff': 'Why should domain services raise domain-specific exceptions rather than directly raising HTTP exceptions with status codes?',
            'q_debug': 'How do you trace a production error reported by a frontend user back to the exact backend log line using request correlation IDs?',
            'q_sysdesign': 'How do you design error handling across a distributed microservices architecture so client applications receive consistent error structures?',
            'ans_framework': 'Explain: 1) The problem of fragmented error formats, 2) The RFC 7807 standard (title, status, detail, instance, request_id), 3) EstateMap\'s 2-tier design: pure Python domain exceptions in services + FastAPI exception handlers at the API boundary, 4) Security benefit: zero stack trace leakage.',
            'conn_prev': 'Story 04 established request/response schemas; Story 05 handles schema validation failures and runtime errors.',
            'conn_next': 'Story 06 integrates distributed request IDs into structured logs to make error tracing actionable.',
            'checklist': [
                'Can implement an RFC 7807 compliant error handler in FastAPI',
                'Can design a clean domain exception hierarchy that is completely free of HTTP dependencies',
                'Can configure Pydantic validation error formatting for clear client feedback',
                'Can explain how correlation IDs connect client error responses to backend log files'
            ]
        },
        {
            'num': 6,
            'title': 'Structured Logging & Distributed Request IDs',
            'points': 3,
            'why_exists': 'In multi-user concurrent applications, unstructured plain text logs become an unsearchable mess. Distributed request correlation IDs and structured JSON logging are required to trace single requests across middleware, services, and database queries.',
            'problem_solved': 'When an error occurs under high concurrency, engineers cannot correlate which database query or log message belonged to which client request without tracing a shared unique identifier.',
            'prereq_stories': ['Story 01 — Python Project Structure & Clean Architecture', 'Story 05 — RFC 7807 Centralized Error Handling'],
            'prereq_concepts': ['Structured logging (JSON vs text)', 'ASGI Middleware mechanics', 'ContextVars for async request-scoped context'],
            'depends_on': [1, 5],
            'unlocks': [13, 46, 58, 89],
            'readiness': [
                'Understand Python standard logging module and log levels (DEBUG, INFO, WARNING, ERROR)',
                'Familiar with contextvars.ContextVar for thread-safe/task-safe variable storage in asyncio',
                'Able to explain how middleware intercepts incoming requests and outgoing responses'
            ],
            'objectives': [
                'Implement an ASGI RequestIDMiddleware that generates or propagates X-Request-ID headers',
                'Use contextvars to make request_id accessible anywhere in the async call stack without passing it explicitly',
                'Configure JSON-formatted structured logging with timestamps, log levels, request IDs, and module names'
            ],
            'concepts': [
                'Correlation ID Pattern: Propagating a unique UUID throughout the entire lifecycle of an HTTP request',
                'ContextVars in Asyncio: Managing task-isolated state in concurrent async Python without thread-local race conditions',
                'Structured JSON Logging: Emitting machine-readable JSON logs for ingestion by Elasticsearch, Loki, or Datadog',
                'Middleware Execution Order: Positioning RequestID middleware at the outer edge of the ASGI pipeline'
            ],
            'impl': 'backend/app/core/middleware.py defines RequestIDMiddleware. For every incoming request, it checks for an existing X-Request-ID header or generates a new uuid.uuid4(). It sets this ID in request.state.request_id and a contextvars.ContextVar, appends the header to the outgoing response, and binds it to all logs emitted by backend/app/core/logging.py.',
            'files': [
                'backend/app/core/middleware.py (RequestIDMiddleware)',
                'backend/app/core/logging.py',
                'backend/app/main.py'
            ],
            'data_flow': 'Client Request (with optional X-Request-ID) -> RequestIDMiddleware intercepts -> Assigns UUID -> Sets contextvar -> Request processed by routes/services (all logger calls automatically include request_id) -> Response headers populated with X-Request-ID -> Client receives response',
            'lab_standalone': '''Build an async request-ID tracing pipeline:
1. Create a contextvars.ContextVar("request_id", default=None).
2. Write a custom logging filter RequestIDFilter that injects request_id.get() into every LogRecord.
3. Write a FastAPI middleware that sets the ContextVar on request start.
4. Emit log messages from deep inside a dummy service function and verify the request_id is automatically present in the log output.''',
            'lab_mapping': 'Inspect backend/app/core/middleware.py to see how RequestIDMiddleware interacts with backend/app/core/exception_handlers.py to pass the request ID into error envelopes.',
            'acceptance_criteria': [
                'Every HTTP response contains the X-Request-ID header.',
                'If a client sends an X-Request-ID header, the backend preserves and reuses that identifier.',
                'All log entries emitted during request handling contain the matching request_id.',
                'Request ID is stored in a ContextVar to avoid passing request objects into domain services.'
            ],
            'evidence': [
                'Send request and inspect headers: curl -i http://localhost:8000/api/v1/properties -> check X-Request-ID in response headers.',
                'Check docker logs: docker logs estatemap-backend | grep -i request_id.'
            ],
            'outcome_conceptual': 'Complete mastery of distributed tracing principles, asynchronous context propagation, and structured observability.',
            'outcome_impl': 'Ability to build asynchronous request ID middleware and structured logging pipelines in Python from scratch.',
            'outcome_interview': 'Ability to explain how distributed tracing operates and how contextvars prevents race conditions in concurrent ASGI backends.',
            'mistakes': [
                'Using threading.local() instead of contextvars.ContextVar in an async application, causing request IDs to bleed across concurrent async tasks sharing the same OS thread.',
                'Passing the FastAPI Request object into domain services and repositories just to log the request ID, breaking Clean Architecture layers.',
                'Generating a new UUID when the upstream API gateway or client has already provided a valid X-Request-ID.'
            ],
            'debug_symptom': 'Log lines from concurrent requests show the same request_id or None in async background tasks.',
            'debug_investigate': 'Check if contextvars.ContextVar is properly initialized and verify whether background tasks copy the context via contextvars.copy_context().',
            'debug_goal': 'Ensure ContextVar is set at the entrypoint of every async task.',
            'tradeoffs': [
                'ContextVars vs Explicit Parameter Passing: ContextVars eliminate function signature pollution while maintaining strict async task isolation.',
                'JSON Logs vs Plain Text Logs: JSON logs require a formatter but enable direct filtering and indexing in log aggregators like Loki and CloudWatch.'
            ],
            'prod_current': 'RequestIDMiddleware generates UUIDs, sets ContextVars, and injects X-Request-ID into response headers.',
            'prod_scale': 'Propagate traceparent headers conforming to the W3C TraceContext standard for OpenTelemetry distributed tracing across microservices.',
            'q_basic': 'What is a correlation ID and why is it essential in backend web applications?',
            'q_impl': 'Why must you use contextvars instead of threading.local when storing request-scoped state in FastAPI?',
            'q_tradeoff': 'What are the performance implications of structured JSON logging versus plain text logging in high-throughput systems?',
            'q_debug': 'How do you investigate an intermittent race condition where logs from two different users appear with the same correlation ID?',
            'q_sysdesign': 'How do you propagate distributed trace context across HTTP boundaries, message queues (Kafka/RabbitMQ), and background workers?',
            'ans_framework': 'Structure response around: 1) The observability problem in concurrent systems, 2) The solution: Correlation ID propagated via X-Request-ID header, 3) The Python concurrency model: why contextvars is required for asyncio task isolation, 4) EstateMap\'s middleware implementation and log integration.',
            'conn_prev': 'Story 05 established centralized error handling; Story 06 attaches correlation IDs to those error responses.',
            'conn_next': 'Story 07 transitions from the core foundation layer to relational data modeling in PostgreSQL.',
            'checklist': [
                'Can explain the difference between contextvars and threading.local in Python asyncio',
                'Can write an ASGI middleware that handles header extraction and injection',
                'Can configure a structured JSON logging pipeline in Python',
                'Can trace a request from incoming HTTP header through application logs to client response'
            ]
        }
    ]

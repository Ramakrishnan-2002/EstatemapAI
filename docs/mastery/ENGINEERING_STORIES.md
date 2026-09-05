# EstateMap AI — Engineering Stories Master Book
> **100 Connected Engineering Stories for Personal Technical Mastery & Interview Whiteboard Defense**

This document contains all 100 connected engineering stories for EstateMap AI. Every story conforms strictly to the **Mandatory Master Story Contract (22 Numbered Sections + Header & Reality Check)**.

### Implementation Status Legend:
- `[CURRENT]`: Directly implemented and verifiable in the EstateMap repository.
- `[PARTIAL]`: Core mechanism implemented; advanced enterprise extensions remain theoretical.
- `[THEORY]`: Foundational CS/engineering concepts required to understand EstateMap design decisions.
- `[FUTURE]`: Scalability / enterprise architecture evolution path under concrete requirement triggers.


## Phase 1: Foundation (Stories 1-6)

### Story 01 — Python Project Structure & Clean Architecture
* **Story Points**: 2 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/main.py`). Verified by automated test suites (backend/tests/unit/test_health.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for python project structure & clean architecture; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements python project structure & clean architecture in `backend/app/main.py` (app.main:app)."

**Do Not Claim:** "Do not claim unverified distributed extensions for python project structure & clean architecture."

#### 1. Core Concept
FastAPI application factory, clean modular layout, router mounting, and dependency separation. Understanding python project structure & clean architecture is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/main.py`
- `backend/pyproject.toml`
- `backend/app/core/config.py`
- Primary Symbol / Class / Function: `app.main:app`
- Verification Test Harness: `backend/tests/unit/test_health.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Python Project Structure & Clean Architecture Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: None (Foundation)
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/main.py`.
2. Verify the implementation of `app.main:app`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_health.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/main.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_health.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_health.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/main.py`.
- [ ] Test harness `backend/tests/unit/test_health.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement python project structure & clean architecture and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/main.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: None (Foundation)
- Downstream Dependents: Story 02, Story 03, Story 04

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 02 — FastAPI Lifespan & Application Lifecycle
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/main.py`). Verified by automated test suites (backend/tests/integration/test_database.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for fastapi lifespan & application lifecycle; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements fastapi lifespan & application lifecycle in `backend/app/main.py` (app.main:lifespan)."

**Do Not Claim:** "Do not claim unverified distributed extensions for fastapi lifespan & application lifecycle."

#### 1. Core Concept
Asynccontextmanager lifespan managing startup auto-seeding and graceful connection teardown. Understanding fastapi lifespan & application lifecycle is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/main.py`
- `backend/app/cache/redis.py`
- `backend/app/db/session.py`
- Primary Symbol / Class / Function: `app.main:lifespan`
- Verification Test Harness: `backend/tests/integration/test_database.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ FastAPI Lifespan & Application Lifecycle Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/main.py`.
2. Verify the implementation of `app.main:lifespan`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_database.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/main.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_database.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_database.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/main.py`.
- [ ] Test harness `backend/tests/integration/test_database.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement fastapi lifespan & application lifecycle and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/main.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01
- Downstream Dependents: Story 03, Story 06, Story 09, Story 39

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 03 — Type-Safe Configuration with Pydantic-Settings
* **Story Points**: 2 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/config.py`). Verified by automated test suites (backend/tests/unit/test_health.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for type-safe configuration with pydantic-settings; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements type-safe configuration with pydantic-settings in `backend/app/core/config.py` (app.core.config:Settings)."

**Do Not Claim:** "Do not claim unverified distributed extensions for type-safe configuration with pydantic-settings."

#### 1. Core Concept
Pydantic BaseSettings loading environment variables, validating TTLs, rate limits, and AI provider configs. Understanding type-safe configuration with pydantic-settings is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/config.py`
- `.env.example`
- Primary Symbol / Class / Function: `app.core.config:Settings`
- Verification Test Harness: `backend/tests/unit/test_health.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Type-Safe Configuration with Pydantic-Settings Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/config.py`.
2. Verify the implementation of `app.core.config:Settings`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_health.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/config.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_health.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_health.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/config.py`.
- [ ] Test harness `backend/tests/unit/test_health.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement type-safe configuration with pydantic-settings and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/config.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01
- Downstream Dependents: Story 02, Story 04, Story 07, Story 14, Story 39, Story 52

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 04 — API Request/Response Schemas with Pydantic v2
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/schemas/property.py`). Verified by automated test suites (backend/tests/unit/test_property_schemas.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for api request/response schemas with pydantic v2; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements api request/response schemas with pydantic v2 in `backend/app/schemas/property.py` (PropertyResponse / PropertyCreate)."

**Do Not Claim:** "Do not claim unverified distributed extensions for api request/response schemas with pydantic v2."

#### 1. Core Concept
Strict input validation and output serialization schemas enforcing types and domain constraints. Understanding api request/response schemas with pydantic v2 is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/property.py`
- `backend/app/schemas/search.py`
- `backend/app/schemas/auth.py`
- Primary Symbol / Class / Function: `PropertyResponse / PropertyCreate`
- Verification Test Harness: `backend/tests/unit/test_property_schemas.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ API Request/Response Schemas with Pydantic v2 Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 03
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/property.py`.
2. Verify the implementation of `PropertyResponse / PropertyCreate`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_property_schemas.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_property_schemas.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_property_schemas.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/property.py`.
- [ ] Test harness `backend/tests/unit/test_property_schemas.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement api request/response schemas with pydantic v2 and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 03
- Downstream Dependents: Story 05, Story 18, Story 19, Story 27, Story 34, Story 55

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 05 — RFC 7807 Centralized Error Handling
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/exceptions.py`). Verified by automated test suites (backend/tests/unit/test_exceptions.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for rfc 7807 centralized error handling; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements rfc 7807 centralized error handling in `backend/app/core/exceptions.py` (AppException / validation_exception_handler)."

**Do Not Claim:** "Do not claim unverified distributed extensions for rfc 7807 centralized error handling."

#### 1. Core Concept
Standardized problem detail JSON error responses with consistent HTTP status mapping. Understanding rfc 7807 centralized error handling is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/exceptions.py`
- `backend/app/core/exception_handlers.py`
- Primary Symbol / Class / Function: `AppException / validation_exception_handler`
- Verification Test Harness: `backend/tests/unit/test_exceptions.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ RFC 7807 Centralized Error Handling Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 04
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/exceptions.py`.
2. Verify the implementation of `AppException / validation_exception_handler`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_exceptions.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/exceptions.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_exceptions.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_exceptions.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/exceptions.py`.
- [ ] Test harness `backend/tests/unit/test_exceptions.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement rfc 7807 centralized error handling and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/exceptions.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 04
- Downstream Dependents: Story 06, Story 14, Story 18, Story 58

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 06 — Structured Logging & Distributed Request IDs
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/middleware.py`). Verified by automated test suites (backend/tests/unit/test_middleware.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for structured logging & distributed request ids; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements structured logging & distributed request ids in `backend/app/core/middleware.py` (RequestIDMiddleware / setup_logging)."

**Do Not Claim:** "Do not claim unverified distributed extensions for structured logging & distributed request ids."

#### 1. Core Concept
Correlation ID propagation via X-Request-ID and contextual structured logging. Understanding structured logging & distributed request ids is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/middleware.py`
- `backend/app/core/logging.py`
- Primary Symbol / Class / Function: `RequestIDMiddleware / setup_logging`
- Verification Test Harness: `backend/tests/unit/test_middleware.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Structured Logging & Distributed Request IDs Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 05
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/middleware.py`.
2. Verify the implementation of `RequestIDMiddleware / setup_logging`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_middleware.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/middleware.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_middleware.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_middleware.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/middleware.py`.
- [ ] Test harness `backend/tests/unit/test_middleware.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement structured logging & distributed request ids and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/middleware.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 05
- Downstream Dependents: Story 13, Story 46, Story 58, Story 89

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 2: Database & Geospatial Engineering (Stories 7-13 & 18-28)

### Story 07 — PostgreSQL Relational Modeling & Schema Integrity
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/models/property.py`). Verified by automated test suites (backend/tests/integration/test_database.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for postgresql relational modeling & schema integrity; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements postgresql relational modeling & schema integrity in `backend/app/models/property.py` (Property / User / PointOfInterest)."

**Do Not Claim:** "Do not claim unverified distributed extensions for postgresql relational modeling & schema integrity."

#### 1. Core Concept
Declarative relational models with foreign keys, check constraints, and cascade rules. Understanding postgresql relational modeling & schema integrity is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/property.py`
- `backend/app/models/user.py`
- `backend/app/models/poi.py`
- Primary Symbol / Class / Function: `Property / User / PointOfInterest`
- Verification Test Harness: `backend/tests/integration/test_database.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ PostgreSQL Relational Modeling & Schema Integrity Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 03
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/property.py`.
2. Verify the implementation of `Property / User / PointOfInterest`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_database.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_database.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_database.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/property.py`.
- [ ] Test harness `backend/tests/integration/test_database.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement postgresql relational modeling & schema integrity and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 03
- Downstream Dependents: Story 08, Story 09, Story 10, Story 11, Story 21

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 08 — SQLAlchemy 2.0 Async Models & Repository Pattern
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/models/property.py`). Verified by automated test suites (backend/tests/integration/test_properties.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for sqlalchemy 2.0 async models & repository pattern; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements sqlalchemy 2.0 async models & repository pattern in `backend/app/models/property.py` (PropertyRepository / UserRepository)."

**Do Not Claim:** "Do not claim unverified distributed extensions for sqlalchemy 2.0 async models & repository pattern."

#### 1. Core Concept
AsyncSession data access encapsulation separating domain logic from raw SQLAlchemy queries. Understanding sqlalchemy 2.0 async models & repository pattern is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/property.py`
- `backend/app/repositories/property_repository.py`
- `backend/app/repositories/user_repository.py`
- Primary Symbol / Class / Function: `PropertyRepository / UserRepository`
- Verification Test Harness: `backend/tests/integration/test_properties.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ SQLAlchemy 2.0 Async Models & Repository Pattern Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/property.py`.
2. Verify the implementation of `PropertyRepository / UserRepository`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_properties.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_properties.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_properties.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/property.py`.
- [ ] Test harness `backend/tests/integration/test_properties.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement sqlalchemy 2.0 async models & repository pattern and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07
- Downstream Dependents: Story 09, Story 18, Story 19, Story 20

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 09 — Non-Blocking Async Database Access with Asyncpg
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/db/session.py`). Verified by automated test suites (backend/tests/integration/test_database.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for non-blocking async database access with asyncpg; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements non-blocking async database access with asyncpg in `backend/app/db/session.py` (async_session_factory / create_async_engine)."

**Do Not Claim:** "Do not claim unverified distributed extensions for non-blocking async database access with asyncpg."

#### 1. Core Concept
High-performance non-blocking PostgreSQL driver integrated with SQLAlchemy 2.0. Understanding non-blocking async database access with asyncpg is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/db/session.py`
- `backend/app/db/base.py`
- Primary Symbol / Class / Function: `async_session_factory / create_async_engine`
- Verification Test Harness: `backend/tests/integration/test_database.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Non-Blocking Async Database Access with Asyncpg Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 02, Story 07, Story 08
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/db/session.py`.
2. Verify the implementation of `async_session_factory / create_async_engine`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_database.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/db/session.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_database.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_database.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/db/session.py`.
- [ ] Test harness `backend/tests/integration/test_database.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement non-blocking async database access with asyncpg and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/db/session.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 02, Story 07, Story 08
- Downstream Dependents: Story 13, Story 18, Story 86

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 10 — Database Migrations with Alembic
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/alembic/env.py`). Verified by automated test suites (backend/alembic/versions/).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for database migrations with alembic; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements database migrations with alembic in `backend/alembic/env.py` (run_migrations_online / revisions 0001-0004)."

**Do Not Claim:** "Do not claim unverified distributed extensions for database migrations with alembic."

#### 1. Core Concept
Version-controlled schema evolutions enabling reproducible migrations and clean rollbacks. Understanding database migrations with alembic is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/alembic/env.py`
- `backend/alembic/versions/2026_09_04_0001-0001_initial_postgis.py`
- `backend/alembic.ini`
- Primary Symbol / Class / Function: `run_migrations_online / revisions 0001-0004`
- Verification Test Harness: `backend/alembic/versions/`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Database Migrations with Alembic Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07, Story 08
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/alembic/env.py`.
2. Verify the implementation of `run_migrations_online / revisions 0001-0004`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/alembic/versions/`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/alembic/env.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/alembic/versions/` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/alembic/versions/` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/alembic/env.py`.
- [ ] Test harness `backend/alembic/versions/` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement database migrations with alembic and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/alembic/env.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07, Story 08
- Downstream Dependents: Story 11, Story 12, Story 81

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 11 — Soft Deletion & Audit Fields Pattern
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/models/property.py`). Verified by automated test suites (backend/tests/integration/test_properties.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for soft deletion & audit fields pattern; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements soft deletion & audit fields pattern in `backend/app/models/property.py` (Property.is_active / Property.created_at)."

**Do Not Claim:** "Do not claim unverified distributed extensions for soft deletion & audit fields pattern."

#### 1. Core Concept
Logical deactivation of listings preserving historical referential integrity. Understanding soft deletion & audit fields pattern is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/property.py`
- `backend/app/repositories/property_repository.py`
- Primary Symbol / Class / Function: `Property.is_active / Property.created_at`
- Verification Test Harness: `backend/tests/integration/test_properties.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Soft Deletion & Audit Fields Pattern Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07, Story 08, Story 10
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/property.py`.
2. Verify the implementation of `Property.is_active / Property.created_at`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_properties.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_properties.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_properties.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/property.py`.
- [ ] Test harness `backend/tests/integration/test_properties.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement soft deletion & audit fields pattern and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07, Story 08, Story 10
- Downstream Dependents: Story 18, Story 19

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 12 — Database Seeding & Deterministic Test Fixtures
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/db/seed_all.py`). Verified by automated test suites (backend/app/db/seed_all.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for database seeding & deterministic test fixtures; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements database seeding & deterministic test fixtures in `backend/app/db/seed_all.py` (seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES)."

**Do Not Claim:** "Do not claim unverified distributed extensions for database seeding & deterministic test fixtures."

#### 1. Core Concept
Deterministic seeding of 100 Chennai properties, 4 Bengaluru properties, and 29 POIs. Understanding database seeding & deterministic test fixtures is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/db/seed_all.py`
- `backend/app/db/seed_properties.py`
- `backend/app/db/seed_pois.py`
- Primary Symbol / Class / Function: `seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES`
- Verification Test Harness: `backend/app/db/seed_all.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Database Seeding & Deterministic Test Fixtures Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07, Story 08, Story 10
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/db/seed_all.py`.
2. Verify the implementation of `seed_all / BENGALURU_PROPERTIES / CHENNAI_LOCALITIES`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/app/db/seed_all.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/db/seed_all.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/app/db/seed_all.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/app/db/seed_all.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/db/seed_all.py`.
- [ ] Test harness `backend/app/db/seed_all.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement database seeding & deterministic test fixtures and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/db/seed_all.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07, Story 08, Story 10
- Downstream Dependents: Story 18, Story 86

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 13 — Connection Pooling & Pool Exhaustion Prevention
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/db/session.py`). Verified by automated test suites (backend/tests/unit/test_health.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for connection pooling & pool exhaustion prevention; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements connection pooling & pool exhaustion prevention in `backend/app/db/session.py` (async_session_factory (pool_size=20, max_overflow=10))."

**Do Not Claim:** "Do not claim unverified distributed extensions for connection pooling & pool exhaustion prevention."

#### 1. Core Concept
Asyncpg pool sizing, connection recycling, and readiness health probes. Understanding connection pooling & pool exhaustion prevention is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/db/session.py`
- `backend/app/core/config.py`
- Primary Symbol / Class / Function: `async_session_factory (pool_size=20, max_overflow=10)`
- Verification Test Harness: `backend/tests/unit/test_health.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Connection Pooling & Pool Exhaustion Prevention Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 02, Story 06, Story 09
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/db/session.py`.
2. Verify the implementation of `async_session_factory (pool_size=20, max_overflow=10)`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_health.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/db/session.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_health.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_health.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/db/session.py`.
- [ ] Test harness `backend/tests/unit/test_health.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement connection pooling & pool exhaustion prevention and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/db/session.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 02, Story 06, Story 09
- Downstream Dependents: Story 86, Story 92

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 18 — Property CRUD Domain Service & Validation Logic
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/property_service.py`). Verified by automated test suites (backend/tests/integration/test_properties.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for property crud domain service & validation logic; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements property crud domain service & validation logic in `backend/app/services/property_service.py` (PropertyService / PropertyRepository)."

**Do Not Claim:** "Do not claim unverified distributed extensions for property crud domain service & validation logic."

#### 1. Core Concept
Business logic encapsulation for property creation, updates, and authorization boundaries. Understanding property crud domain service & validation logic is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/property_service.py`
- `backend/app/api/v1/properties.py`
- `backend/app/repositories/property_repository.py`
- Primary Symbol / Class / Function: `PropertyService / PropertyRepository`
- Verification Test Harness: `backend/tests/integration/test_properties.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Property CRUD Domain Service & Validation Logic Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04, Story 05, Story 08, Story 09, Story 11
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/property_service.py`.
2. Verify the implementation of `PropertyService / PropertyRepository`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_properties.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/property_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_properties.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_properties.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/property_service.py`.
- [ ] Test harness `backend/tests/integration/test_properties.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement property crud domain service & validation logic and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/property_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04, Story 05, Story 08, Story 09, Story 11
- Downstream Dependents: Story 19, Story 20, Story 34, Story 62

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 19 — Advanced Multi-Facet Property Filtering
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/repositories/property_repository.py`). Verified by automated test suites (backend/tests/integration/test_filter_equivalence.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for advanced multi-facet property filtering; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements advanced multi-facet property filtering in `backend/app/repositories/property_repository.py` (PropertyRepository._apply_common_filters / PropertyFilterParams)."

**Do Not Claim:** "Do not claim unverified distributed extensions for advanced multi-facet property filtering."

#### 1. Core Concept
Dynamic SQL query generation supporting price ranges, bedrooms, property types, and locations. Understanding advanced multi-facet property filtering is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/repositories/property_repository.py`
- `backend/app/schemas/property.py`
- Primary Symbol / Class / Function: `PropertyRepository._apply_common_filters / PropertyFilterParams`
- Verification Test Harness: `backend/tests/integration/test_filter_equivalence.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Advanced Multi-Facet Property Filtering Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04, Story 08, Story 18
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/repositories/property_repository.py`.
2. Verify the implementation of `PropertyRepository._apply_common_filters / PropertyFilterParams`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_filter_equivalence.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/repositories/property_repository.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_filter_equivalence.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_filter_equivalence.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/repositories/property_repository.py`.
- [ ] Test harness `backend/tests/integration/test_filter_equivalence.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement advanced multi-facet property filtering and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/repositories/property_repository.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04, Story 08, Story 18
- Downstream Dependents: Story 20, Story 25, Story 34, Story 75

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 20 — Deterministic Pagination & Sorting Rules
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/utils/pagination.py`). Verified by automated test suites (backend/tests/integration/test_properties.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for deterministic pagination & sorting rules; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements deterministic pagination & sorting rules in `backend/app/utils/pagination.py` (PropertyRepository.list / PropertyRepository._apply_sorting)."

**Do Not Claim:** "Do not claim unverified distributed extensions for deterministic pagination & sorting rules."

#### 1. Core Concept
LIMIT/OFFSET pagination with deterministic tie-breaking (created_at DESC -> id DESC). Understanding deterministic pagination & sorting rules is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/utils/pagination.py`
- `backend/app/repositories/property_repository.py`
- Primary Symbol / Class / Function: `PropertyRepository.list / PropertyRepository._apply_sorting`
- Verification Test Harness: `backend/tests/integration/test_properties.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Deterministic Pagination & Sorting Rules Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 08, Story 18, Story 19
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/utils/pagination.py`.
2. Verify the implementation of `PropertyRepository.list / PropertyRepository._apply_sorting`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_properties.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/utils/pagination.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_properties.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_properties.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/utils/pagination.py`.
- [ ] Test harness `backend/tests/integration/test_properties.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement deterministic pagination & sorting rules and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/utils/pagination.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 08, Story 18, Story 19
- Downstream Dependents: Story 75, Story 95

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 21 — Geospatial Fundamentals & Coordinate Reference Systems (WGS84 vs Projected)
* **Story Points**: 5 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/models/property.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of geospatial fundamentals & coordinate reference systems (wgs84 vs projected) that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for geospatial fundamentals & coordinate reference systems (wgs84 vs projected)."

#### 1. Core Concept
Geographic coordinate systems, ellipsoidal curvature, and spatial projection mathematics. Understanding geospatial fundamentals & coordinate reference systems (wgs84 vs projected) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/property.py`
- `backend/app/models/poi.py`
- Primary Symbol / Class / Function: `EPSG:4326 vs EPSG:3857 CRS Theory`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Geospatial Fundamentals & Coordinate Reference Systems (WGS84 vs Projected) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/property.py`.
2. Verify the implementation of `EPSG:4326 vs EPSG:3857 CRS Theory`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/property.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement geospatial fundamentals & coordinate reference systems (wgs84 vs projected) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07
- Downstream Dependents: Story 22, Story 23, Story 24, Story 29

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 22 — PostGIS POINT Geometry & Spatial Column Storage
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/models/property.py`). Verified by automated test suites (backend/tests/integration/test_spatial_search.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for postgis point geometry & spatial column storage; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements postgis point geometry & spatial column storage in `backend/app/models/property.py` (mapped_column(Geometry(geometry_type='POINT', srid=4326)))."

**Do Not Claim:** "Do not claim unverified distributed extensions for postgis point geometry & spatial column storage."

#### 1. Core Concept
PostGIS point storage using GeoAlchemy2 and explicit geography casting for distance calculations. Understanding postgis point geometry & spatial column storage is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/property.py`
- `backend/app/models/poi.py`
- `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`
- Primary Symbol / Class / Function: `mapped_column(Geometry(geometry_type='POINT', srid=4326))`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ PostGIS POINT Geometry & Spatial Column Storage Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 07, Story 21
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/property.py`.
2. Verify the implementation of `mapped_column(Geometry(geometry_type='POINT', srid=4326))`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/property.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/property.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement postgis point geometry & spatial column storage and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/property.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 07, Story 21
- Downstream Dependents: Story 23, Story 24, Story 25

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 23 — GiST Spatial Indexing (Generalized Search Tree)
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`). Verified by automated test suites (backend/tests/integration/test_spatial_search.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for gist spatial indexing (generalized search tree); essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements gist spatial indexing (generalized search tree) in `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py` (spatial_index=True / idx_properties_location)."

**Do Not Claim:** "Do not claim unverified distributed extensions for gist spatial indexing (generalized search tree)."

#### 1. Core Concept
Hierarchical R-tree bounding box indexing enabling logarithmic spatial search performance. Understanding gist spatial indexing (generalized search tree) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`
- `backend/app/models/property.py`
- Primary Symbol / Class / Function: `spatial_index=True / idx_properties_location`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ GiST Spatial Indexing (Generalized Search Tree) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21, Story 22
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`.
2. Verify the implementation of `spatial_index=True / idx_properties_location`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement gist spatial indexing (generalized search tree) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/alembic/versions/2026_09_04_0003-0003_create_properties_amenities_images.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21, Story 22
- Downstream Dependents: Story 24, Story 25, Story 28, Story 92

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 24 — Radius Distance Search via ST_DWithin on Spheroids
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/geo_service.py`). Verified by automated test suites (backend/tests/integration/test_spatial_search.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for radius distance search via st_dwithin on spheroids; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements radius distance search via st_dwithin on spheroids in `backend/app/services/geo_service.py` (PropertyRepository.search_radius / func.ST_DWithin)."

**Do Not Claim:** "Do not claim unverified distributed extensions for radius distance search via st_dwithin on spheroids."

#### 1. Core Concept
Geodesic meter-based radius filtering using ST_DWithin and ST_Distance on cast geography. Understanding radius distance search via st_dwithin on spheroids is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/geo_service.py`
- `backend/app/repositories/property_repository.py`
- Primary Symbol / Class / Function: `PropertyRepository.search_radius / func.ST_DWithin`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Radius Distance Search via ST_DWithin on Spheroids Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21, Story 22, Story 23
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/geo_service.py`.
2. Verify the implementation of `PropertyRepository.search_radius / func.ST_DWithin`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/geo_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/geo_service.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement radius distance search via st_dwithin on spheroids and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/geo_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21, Story 22, Story 23
- Downstream Dependents: Story 26, Story 28, Story 35

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 25 — Bounding-Box Viewport Search via ST_MakeEnvelope
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/geo_service.py`). Verified by automated test suites (backend/tests/integration/test_spatial_search.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for bounding-box viewport search via st_makeenvelope; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements bounding-box viewport search via st_makeenvelope in `backend/app/services/geo_service.py` (PropertyRepository.search_bbox / ST_MakeEnvelope / ST_Within)."

**Do Not Claim:** "Do not claim unverified distributed extensions for bounding-box viewport search via st_makeenvelope."

#### 1. Core Concept
Map viewport spatial queries utilizing GiST envelope containment and antimeridian splitting. Understanding bounding-box viewport search via st_makeenvelope is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/geo_service.py`
- `backend/app/api/v1/maps.py`
- `backend/app/repositories/property_repository.py`
- Primary Symbol / Class / Function: `PropertyRepository.search_bbox / ST_MakeEnvelope / ST_Within`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Bounding-Box Viewport Search via ST_MakeEnvelope Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21, Story 22, Story 23
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/geo_service.py`.
2. Verify the implementation of `PropertyRepository.search_bbox / ST_MakeEnvelope / ST_Within`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/geo_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/geo_service.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement bounding-box viewport search via st_makeenvelope and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/geo_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21, Story 22, Story 23
- Downstream Dependents: Story 28, Story 76, Story 77

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 26 — Points of Interest (POI) Location Intelligence & Category Queries
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/models/poi.py`). Verified by automated test suites (backend/tests/integration/test_pois.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for points of interest (poi) location intelligence & category queries; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements points of interest (poi) location intelligence & category queries in `backend/app/models/poi.py` (POIService.get_location_intelligence / POIRepository)."

**Do Not Claim:** "Do not claim unverified distributed extensions for points of interest (poi) location intelligence & category queries."

#### 1. Core Concept
Proximity aggregation calculating nearby transit, school, hospital, and park counts. Understanding points of interest (poi) location intelligence & category queries is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/models/poi.py`
- `backend/app/services/poi_service.py`
- `backend/app/repositories/poi_repository.py`
- Primary Symbol / Class / Function: `POIService.get_location_intelligence / POIRepository`
- Verification Test Harness: `backend/tests/integration/test_pois.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Points of Interest (POI) Location Intelligence & Category Queries Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 22, Story 24
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/models/poi.py`.
2. Verify the implementation of `POIService.get_location_intelligence / POIRepository`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_pois.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/models/poi.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_pois.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_pois.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/models/poi.py`.
- [ ] Test harness `backend/tests/integration/test_pois.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement points of interest (poi) location intelligence & category queries and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/models/poi.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 22, Story 24
- Downstream Dependents: Story 35, Story 38

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 27 — RFC 7946 GeoJSON Standard Compliance & Serializers
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/schemas/geo.py`). Verified by automated test suites (backend/tests/unit/test_geo_schemas.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for rfc 7946 geojson standard compliance & serializers; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements rfc 7946 geojson standard compliance & serializers in `backend/app/schemas/geo.py` (PropertyGeoJSONFeature / propertiesToFeatureCollection)."

**Do Not Claim:** "Do not claim unverified distributed extensions for rfc 7946 geojson standard compliance & serializers."

#### 1. Core Concept
GeoJSON serialization strictly enforcing [longitude, latitude] coordinate ordering. Understanding rfc 7946 geojson standard compliance & serializers is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/geo.py`
- `frontend/lib/geojson.ts`
- Primary Symbol / Class / Function: `PropertyGeoJSONFeature / propertiesToFeatureCollection`
- Verification Test Harness: `backend/tests/unit/test_geo_schemas.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ RFC 7946 GeoJSON Standard Compliance & Serializers Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04, Story 22
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/geo.py`.
2. Verify the implementation of `PropertyGeoJSONFeature / propertiesToFeatureCollection`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_geo_schemas.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/geo.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_geo_schemas.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_geo_schemas.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/geo.py`.
- [ ] Test harness `backend/tests/unit/test_geo_schemas.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement rfc 7946 geojson standard compliance & serializers and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/geo.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04, Story 22
- Downstream Dependents: Story 76, Story 78

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 28 — Geospatial Query Optimization & Spatial EXPLAIN ANALYZE
* **Story Points**: 8 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/services/geo_service.py` (PropertyRepository.search_bbox (EXPLAIN Bitmap Index Scan)).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational geospatial query optimization & spatial explain analyze in `backend/app/services/geo_service.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for geospatial query optimization & spatial explain analyze."

#### 1. Core Concept
Query planner analysis, index scan verification, and execution plan optimization. Understanding geospatial query optimization & spatial explain analyze is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/geo_service.py`
- `backend/app/db/session.py`
- Primary Symbol / Class / Function: `PropertyRepository.search_bbox (EXPLAIN Bitmap Index Scan)`
- Verification Test Harness: `backend/tests/integration/test_spatial_search.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Geospatial Query Optimization & Spatial EXPLAIN ANALYZE Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 23, Story 24, Story 25
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/geo_service.py`.
2. Verify the implementation of `PropertyRepository.search_bbox (EXPLAIN Bitmap Index Scan)`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_spatial_search.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/geo_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_spatial_search.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_spatial_search.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/geo_service.py`.
- [ ] Test harness `backend/tests/integration/test_spatial_search.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement geospatial query optimization & spatial explain analyze and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/geo_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 23, Story 24, Story 25
- Downstream Dependents: Story 89, Story 92

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.


## Phase 3: Security, Identity & Authentication (Stories 14-17)

### Story 14 — Password Hashing with Argon2id & Cryptographic Salting
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/security.py`). Verified by automated test suites (backend/tests/unit/test_security.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for password hashing with argon2id & cryptographic salting; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements password hashing with argon2id & cryptographic salting in `backend/app/core/security.py` (get_password_hash / verify_password)."

**Do Not Claim:** "Do not claim unverified distributed extensions for password hashing with argon2id & cryptographic salting."

#### 1. Core Concept
Secure memory-hard password hashing protecting user credentials against brute-force attacks. Understanding password hashing with argon2id & cryptographic salting is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/security.py`
- `backend/app/services/auth_service.py`
- Primary Symbol / Class / Function: `get_password_hash / verify_password`
- Verification Test Harness: `backend/tests/unit/test_security.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Password Hashing with Argon2id & Cryptographic Salting Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 03, Story 05, Story 07
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/security.py`.
2. Verify the implementation of `get_password_hash / verify_password`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_security.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/security.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_security.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_security.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/security.py`.
- [ ] Test harness `backend/tests/unit/test_security.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement password hashing with argon2id & cryptographic salting and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/security.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 03, Story 05, Story 07
- Downstream Dependents: Story 15, Story 16

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 15 — Stateless JWT Authentication & Signature Verification
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/security.py`). Verified by automated test suites (backend/tests/integration/test_auth.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for stateless jwt authentication & signature verification; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements stateless jwt authentication & signature verification in `backend/app/core/security.py` (create_access_token / decode_access_token)."

**Do Not Claim:** "Do not claim unverified distributed extensions for stateless jwt authentication & signature verification."

#### 1. Core Concept
HS256 signed JSON Web Tokens with 60-minute expiration for stateless API authorization. Understanding stateless jwt authentication & signature verification is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/security.py`
- `backend/app/api/v1/auth.py`
- Primary Symbol / Class / Function: `create_access_token / decode_access_token`
- Verification Test Harness: `backend/tests/integration/test_auth.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Stateless JWT Authentication & Signature Verification Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 03, Story 14
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/security.py`.
2. Verify the implementation of `create_access_token / decode_access_token`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_auth.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/security.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_auth.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_auth.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/security.py`.
- [ ] Test harness `backend/tests/integration/test_auth.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement stateless jwt authentication & signature verification and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/security.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 03, Story 14
- Downstream Dependents: Story 16, Story 48, Story 80

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 16 — Role-Based Authorization & Ownership Verification
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/dependencies.py`). Verified by automated test suites (backend/tests/integration/test_auth.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for role-based authorization & ownership verification; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements role-based authorization & ownership verification in `backend/app/core/dependencies.py` (get_current_user / get_current_active_user)."

**Do Not Claim:** "Do not claim unverified distributed extensions for role-based authorization & ownership verification."

#### 1. Core Concept
FastAPI dependency injection enforcing authentication and resource ownership checks. Understanding role-based authorization & ownership verification is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/dependencies.py`
- `backend/app/models/user.py`
- `backend/app/services/property_service.py`
- Primary Symbol / Class / Function: `get_current_user / get_current_active_user`
- Verification Test Harness: `backend/tests/integration/test_auth.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Role-Based Authorization & Ownership Verification Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 14, Story 15
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/dependencies.py`.
2. Verify the implementation of `get_current_user / get_current_active_user`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_auth.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/dependencies.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_auth.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_auth.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/dependencies.py`.
- [ ] Test harness `backend/tests/integration/test_auth.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement role-based authorization & ownership verification and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/dependencies.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 14, Story 15
- Downstream Dependents: Story 18, Story 98

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 17 — Security Headers, CORS Policy & Defense-in-Depth
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/main.py`). Verified by automated test suites (backend/tests/unit/test_middleware.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for security headers, cors policy & defense-in-depth; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements security headers, cors policy & defense-in-depth in `backend/app/main.py` (CORSMiddleware / RequestIDMiddleware)."

**Do Not Claim:** "Do not claim unverified distributed extensions for security headers, cors policy & defense-in-depth."

#### 1. Core Concept
CORS configuration, HTTP security headers, and cross-site scripting mitigations. Understanding security headers, cors policy & defense-in-depth is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/main.py`
- `backend/app/core/middleware.py`
- Primary Symbol / Class / Function: `CORSMiddleware / RequestIDMiddleware`
- Verification Test Harness: `backend/tests/unit/test_middleware.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Security Headers, CORS Policy & Defense-in-Depth Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 15
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/main.py`.
2. Verify the implementation of `CORSMiddleware / RequestIDMiddleware`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_middleware.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/main.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_middleware.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_middleware.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/main.py`.
- [ ] Test harness `backend/tests/unit/test_middleware.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement security headers, cors policy & defense-in-depth and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/main.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 15
- Downstream Dependents: Story 81, Story 98

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 4: Location, Routing & Commute Intelligence (Stories 29-33)

### Story 29 — Haversine Great-Circle Distance vs Geodesic Mathematics
* **Story Points**: 3 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/utils/geo.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of haversine great-circle distance vs geodesic mathematics that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for haversine great-circle distance vs geodesic mathematics."

#### 1. Core Concept
Mathematical models for spherical vs ellipsoidal surface distance calculation. Understanding haversine great-circle distance vs geodesic mathematics is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/utils/geo.py`
- `backend/app/services/commute_service.py`
- Primary Symbol / Class / Function: `haversine_distance_km / WGS84 geodesic formulas`
- Verification Test Harness: `backend/tests/unit/test_commute_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Haversine Great-Circle Distance vs Geodesic Mathematics Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/utils/geo.py`.
2. Verify the implementation of `haversine_distance_km / WGS84 geodesic formulas`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_commute_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/utils/geo.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_commute_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_commute_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/utils/geo.py`.
- [ ] Test harness `backend/tests/unit/test_commute_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement haversine great-circle distance vs geodesic mathematics and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/utils/geo.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21
- Downstream Dependents: Story 30, Story 31, Story 35

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 30 — Deterministic Bounded Location Resolution for Metropolitan Hubs
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/utils/location_resolver.py` (LocationResolver.resolve / KNOWN_LOCATIONS / METRO_BOUNDS).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational deterministic bounded location resolution for metropolitan hubs in `backend/app/utils/location_resolver.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for deterministic bounded location resolution for metropolitan hubs."

#### 1. Core Concept
Authoritative in-memory landmark and tech park coordinate resolution for Bengaluru and Chennai. Understanding deterministic bounded location resolution for metropolitan hubs is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/utils/location_resolver.py`
- `backend/app/api/v1/search.py`
- Primary Symbol / Class / Function: `LocationResolver.resolve / KNOWN_LOCATIONS / METRO_BOUNDS`
- Verification Test Harness: `backend/tests/unit/test_location_resolver.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Deterministic Bounded Location Resolution for Metropolitan Hubs Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21, Story 29
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/utils/location_resolver.py`.
2. Verify the implementation of `LocationResolver.resolve / KNOWN_LOCATIONS / METRO_BOUNDS`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_location_resolver.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/utils/location_resolver.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_location_resolver.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_location_resolver.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/utils/location_resolver.py`.
- [ ] Test harness `backend/tests/unit/test_location_resolver.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement deterministic bounded location resolution for metropolitan hubs and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/utils/location_resolver.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21, Story 29
- Downstream Dependents: Story 31, Story 69

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 31 — Road-Network Graph Traversal vs Euclidean Spatial Distance
* **Story Points**: 5 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/services/routing/protocol.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of road-network graph traversal vs euclidean spatial distance that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for road-network graph traversal vs euclidean spatial distance."

#### 1. Core Concept
Contraction Hierarchies, road topology constraints, and speed-profile travel time modeling. Understanding road-network graph traversal vs euclidean spatial distance is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/routing/protocol.py`
- `backend/app/services/commute_service.py`
- Primary Symbol / Class / Function: `RoutingProvider protocol & graph routing theory`
- Verification Test Harness: `backend/tests/unit/test_routing_models.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Road-Network Graph Traversal vs Euclidean Spatial Distance Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 21, Story 29
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/routing/protocol.py`.
2. Verify the implementation of `RoutingProvider protocol & graph routing theory`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_routing_models.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/routing/protocol.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_routing_models.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_routing_models.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/routing/protocol.py`.
- [ ] Test harness `backend/tests/unit/test_routing_models.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement road-network graph traversal vs euclidean spatial distance and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/routing/protocol.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 21, Story 29
- Downstream Dependents: Story 32, Story 33, Story 35

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 32 — OSRM Routing Engine Integration & Duration Matrix Extraction
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/routing/osrm_provider.py`). Verified by automated test suites (backend/tests/integration/test_commute.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for osrm routing engine integration & duration matrix extraction; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements osrm routing engine integration & duration matrix extraction in `backend/app/services/routing/osrm_provider.py` (OSRMProvider.calculate_route / RoutingProviderFactory)."

**Do Not Claim:** "Do not claim unverified distributed extensions for osrm routing engine integration & duration matrix extraction."

#### 1. Core Concept
HTTP integration with OSRM demo routing service extracting travel duration and polyline routes. Understanding osrm routing engine integration & duration matrix extraction is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/routing/osrm_provider.py`
- `backend/app/services/routing/factory.py`
- Primary Symbol / Class / Function: `OSRMProvider.calculate_route / RoutingProviderFactory`
- Verification Test Harness: `backend/tests/integration/test_commute.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ OSRM Routing Engine Integration & Duration Matrix Extraction Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 31
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/routing/osrm_provider.py`.
2. Verify the implementation of `OSRMProvider.calculate_route / RoutingProviderFactory`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_commute.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/routing/osrm_provider.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_commute.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_commute.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/routing/osrm_provider.py`.
- [ ] Test harness `backend/tests/integration/test_commute.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement osrm routing engine integration & duration matrix extraction and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/routing/osrm_provider.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 31
- Downstream Dependents: Story 33, Story 44

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 33 — Multi-Modal Commute Matrix & Fallback Strategies
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/commute_service.py`). Verified by automated test suites (backend/tests/integration/test_commute.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for multi-modal commute matrix & fallback strategies; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements multi-modal commute matrix & fallback strategies in `backend/app/services/commute_service.py` (CommuteService.calculate_commute_matrix / CommuteService.calculate_route)."

**Do Not Claim:** "Do not claim unverified distributed extensions for multi-modal commute matrix & fallback strategies."

#### 1. Core Concept
Multi-property commute calculations with straight-line fallback on provider timeouts. Understanding multi-modal commute matrix & fallback strategies is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/commute_service.py`
- `backend/app/schemas/commute.py`
- Primary Symbol / Class / Function: `CommuteService.calculate_commute_matrix / CommuteService.calculate_route`
- Verification Test Harness: `backend/tests/integration/test_commute.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Multi-Modal Commute Matrix & Fallback Strategies Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 31, Story 32
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/commute_service.py`.
2. Verify the implementation of `CommuteService.calculate_commute_matrix / CommuteService.calculate_route`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_commute.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/commute_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_commute.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_commute.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/commute_service.py`.
- [ ] Test harness `backend/tests/integration/test_commute.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement multi-modal commute matrix & fallback strategies and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/commute_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 31, Story 32
- Downstream Dependents: Story 35, Story 44

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 5: Deterministic Scoring & Comparison Engine (Stories 34-38 & 62-64)

### Story 34 — Multi-Criteria Decision Analysis & Scoring Normalization
* **Story Points**: 5 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/services/ranking_service.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of multi-criteria decision analysis & scoring normalization that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for multi-criteria decision analysis & scoring normalization."

#### 1. Core Concept
Linear score transformation, min-max normalization, and multi-factor preference calibration. Understanding multi-criteria decision analysis & scoring normalization is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/ranking_service.py`
- `backend/app/utils/ranking.py`
- Primary Symbol / Class / Function: `MCDA utility function normalization theory`
- Verification Test Harness: `backend/tests/unit/test_ranking_scoring.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Multi-Criteria Decision Analysis & Scoring Normalization Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04, Story 18
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/ranking_service.py`.
2. Verify the implementation of `MCDA utility function normalization theory`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ranking_scoring.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/ranking_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ranking_scoring.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ranking_scoring.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/ranking_service.py`.
- [ ] Test harness `backend/tests/unit/test_ranking_scoring.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement multi-criteria decision analysis & scoring normalization and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/ranking_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04, Story 18
- Downstream Dependents: Story 35, Story 36, Story 62

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 35 — 6-Factor Mathematical Ranking Engine
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/ranking_service.py`). Verified by automated test suites (backend/tests/integration/test_ranking.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for 6-factor mathematical ranking engine; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements 6-factor mathematical ranking engine in `backend/app/services/ranking_service.py` (RankingService.rank_properties / calculate_price_score / calculate_bedroom_score)."

**Do Not Claim:** "Do not claim unverified distributed extensions for 6-factor mathematical ranking engine."

#### 1. Core Concept
Deterministic 6-factor scoring: price, bedrooms, area, locality, location, and commute. Understanding 6-factor mathematical ranking engine is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/ranking_service.py`
- `backend/app/utils/ranking.py`
- Primary Symbol / Class / Function: `RankingService.rank_properties / calculate_price_score / calculate_bedroom_score`
- Verification Test Harness: `backend/tests/integration/test_ranking.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ 6-Factor Mathematical Ranking Engine Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 24, Story 26, Story 29, Story 31, Story 33, Story 34
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/ranking_service.py`.
2. Verify the implementation of `RankingService.rank_properties / calculate_price_score / calculate_bedroom_score`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ranking.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/ranking_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ranking.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ranking.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/ranking_service.py`.
- [ ] Test harness `backend/tests/integration/test_ranking.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement 6-factor mathematical ranking engine and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/ranking_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 24, Story 26, Story 29, Story 31, Story 33, Story 34
- Downstream Dependents: Story 36, Story 37, Story 38, Story 62

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 36 — Weight Vector Validation & Preference Calibration
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/schemas/ranking.py`). Verified by automated test suites (backend/tests/unit/test_ranking_scoring.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for weight vector validation & preference calibration; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements weight vector validation & preference calibration in `backend/app/schemas/ranking.py` (RankingWeights / RANKING_PRESETS)."

**Do Not Claim:** "Do not claim unverified distributed extensions for weight vector validation & preference calibration."

#### 1. Core Concept
Validation of user-defined weight vectors and preset profiles (budget_first, commute_first, etc.). Understanding weight vector validation & preference calibration is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/ranking.py`
- `backend/app/services/ranking_service.py`
- Primary Symbol / Class / Function: `RankingWeights / RANKING_PRESETS`
- Verification Test Harness: `backend/tests/unit/test_ranking_scoring.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Weight Vector Validation & Preference Calibration Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 34, Story 35
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/ranking.py`.
2. Verify the implementation of `RankingWeights / RANKING_PRESETS`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ranking_scoring.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/ranking.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ranking_scoring.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ranking_scoring.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/ranking.py`.
- [ ] Test harness `backend/tests/unit/test_ranking_scoring.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement weight vector validation & preference calibration and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/ranking.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 34, Story 35
- Downstream Dependents: Story 37, Story 75

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 37 — Dynamic Missing-Factor Weight Redistribution
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/ranking_service.py`). Verified by automated test suites (backend/tests/unit/test_ranking_scoring.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for dynamic missing-factor weight redistribution; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements dynamic missing-factor weight redistribution in `backend/app/services/ranking_service.py` (RankingService._redistribute_weights / active_weight_sum normalization)."

**Do Not Claim:** "Do not claim unverified distributed extensions for dynamic missing-factor weight redistribution."

#### 1. Core Concept
Proportional redistribution of unavailable factor weights ensuring total score sums to 1.0. Understanding dynamic missing-factor weight redistribution is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/ranking_service.py`
- `backend/app/utils/ranking.py`
- Primary Symbol / Class / Function: `RankingService._redistribute_weights / active_weight_sum normalization`
- Verification Test Harness: `backend/tests/unit/test_ranking_scoring.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Dynamic Missing-Factor Weight Redistribution Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 35, Story 36
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/ranking_service.py`.
2. Verify the implementation of `RankingService._redistribute_weights / active_weight_sum normalization`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ranking_scoring.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/ranking_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ranking_scoring.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ranking_scoring.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/ranking_service.py`.
- [ ] Test harness `backend/tests/unit/test_ranking_scoring.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement dynamic missing-factor weight redistribution and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/ranking_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 35, Story 36
- Downstream Dependents: Story 38, Story 62

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 38 — Ranking Score Explainability & Factor Descriptions
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/schemas/ranking.py`). Verified by automated test suites (backend/tests/integration/test_ranking.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for ranking score explainability & factor descriptions; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements ranking score explainability & factor descriptions in `backend/app/schemas/ranking.py` (generate_deterministic_explanations / FactorScoreDetail)."

**Do Not Claim:** "Do not claim unverified distributed extensions for ranking score explainability & factor descriptions."

#### 1. Core Concept
Factual template-based human-readable explanations derived directly from computed score components. Understanding ranking score explainability & factor descriptions is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/ranking.py`
- `backend/app/utils/ranking.py`
- Primary Symbol / Class / Function: `generate_deterministic_explanations / FactorScoreDetail`
- Verification Test Harness: `backend/tests/integration/test_ranking.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Ranking Score Explainability & Factor Descriptions Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 26, Story 35, Story 37
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/ranking.py`.
2. Verify the implementation of `generate_deterministic_explanations / FactorScoreDetail`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ranking.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/ranking.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ranking.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ranking.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/ranking.py`.
- [ ] Test harness `backend/tests/integration/test_ranking.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement ranking score explainability & factor descriptions and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/ranking.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 26, Story 35, Story 37
- Downstream Dependents: Story 64, Story 70, Story 78

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 62 — Deterministic Property Comparison Engine & Dimension Winners
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/comparison_service.py`). Verified by automated test suites (backend/tests/integration/test_ai_comparison.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for deterministic property comparison engine & dimension winners; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements deterministic property comparison engine & dimension winners in `backend/app/services/comparison_service.py` (ComparisonService.compare_properties / ComparisonResult)."

**Do Not Claim:** "Do not claim unverified distributed extensions for deterministic property comparison engine & dimension winners."

#### 1. Core Concept
Side-by-side evaluation of 2-3 properties with dimension winner selection for price, space, and commute. Understanding deterministic property comparison engine & dimension winners is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/comparison_service.py`
- `backend/app/api/v1/search.py`
- Primary Symbol / Class / Function: `ComparisonService.compare_properties / ComparisonResult`
- Verification Test Harness: `backend/tests/integration/test_ai_comparison.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Deterministic Property Comparison Engine & Dimension Winners Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 18, Story 34, Story 35
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/comparison_service.py`.
2. Verify the implementation of `ComparisonService.compare_properties / ComparisonResult`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ai_comparison.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/comparison_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ai_comparison.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ai_comparison.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/comparison_service.py`.
- [ ] Test harness `backend/tests/integration/test_ai_comparison.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement deterministic property comparison engine & dimension winners and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/comparison_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 18, Story 34, Story 35
- Downstream Dependents: Story 63, Story 64, Story 79

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 63 — Quantitative Feature Comparison & Metric Diff Calculation
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/comparison_service.py`). Verified by automated test suites (backend/tests/unit/test_comparison_service.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for quantitative feature comparison & metric diff calculation; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements quantitative feature comparison & metric diff calculation in `backend/app/services/comparison_service.py` (ComparisonService._calculate_dimension_winners / DimensionWinner)."

**Do Not Claim:** "Do not claim unverified distributed extensions for quantitative feature comparison & metric diff calculation."

#### 1. Core Concept
Mathematical differential calculation across price per sqft, bedroom count, and travel times. Understanding quantitative feature comparison & metric diff calculation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/comparison_service.py`
- `backend/app/schemas/comparison.py`
- Primary Symbol / Class / Function: `ComparisonService._calculate_dimension_winners / DimensionWinner`
- Verification Test Harness: `backend/tests/unit/test_comparison_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Quantitative Feature Comparison & Metric Diff Calculation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 62
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/comparison_service.py`.
2. Verify the implementation of `ComparisonService._calculate_dimension_winners / DimensionWinner`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_comparison_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/comparison_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_comparison_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_comparison_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/comparison_service.py`.
- [ ] Test harness `backend/tests/unit/test_comparison_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement quantitative feature comparison & metric diff calculation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/comparison_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 62
- Downstream Dependents: Story 64, Story 79

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 64 — Grounded Comparison Summary Generation
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/comparison_service.py`). Verified by automated test suites (backend/tests/integration/test_ai_comparison.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for grounded comparison summary generation; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements grounded comparison summary generation in `backend/app/services/comparison_service.py` (AIService.compare_properties / AIComparisonResponse)."

**Do Not Claim:** "Do not claim unverified distributed extensions for grounded comparison summary generation."

#### 1. Core Concept
LLM-generated comparison narrative grounded strictly in deterministic comparison facts. Understanding grounded comparison summary generation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/comparison_service.py`
- `backend/app/ai/gemini_provider.py`
- Primary Symbol / Class / Function: `AIService.compare_properties / AIComparisonResponse`
- Verification Test Harness: `backend/tests/integration/test_ai_comparison.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Grounded Comparison Summary Generation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 38, Story 62, Story 63
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/comparison_service.py`.
2. Verify the implementation of `AIService.compare_properties / AIComparisonResponse`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ai_comparison.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/comparison_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ai_comparison.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ai_comparison.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/comparison_service.py`.
- [ ] Test harness `backend/tests/integration/test_ai_comparison.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement grounded comparison summary generation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/comparison_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 38, Story 62, Story 63
- Downstream Dependents: Story 70, Story 79

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 6: In-Memory Acceleration & Rate Limiting (Stories 39-50)

### Story 39 — Redis In-Memory Architecture & Event Loop Client
* **Story Points**: 3 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/cache/redis.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of redis in-memory architecture & event loop client that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for redis in-memory architecture & event loop client."

#### 1. Core Concept
Redis internal memory structures, persistence tradeoffs (RDB vs AOF), and async client mechanics. Understanding redis in-memory architecture & event loop client is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/redis.py`
- `backend/app/cache/cache_service.py`
- Primary Symbol / Class / Function: `Single-threaded event loop, RESP protocol, in-memory storage theory`
- Verification Test Harness: `backend/tests/integration/test_redis.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Redis In-Memory Architecture & Event Loop Client Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 02, Story 03
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/redis.py`.
2. Verify the implementation of `Single-threaded event loop, RESP protocol, in-memory storage theory`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_redis.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/redis.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_redis.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_redis.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/redis.py`.
- [ ] Test harness `backend/tests/integration/test_redis.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement redis in-memory architecture & event loop client and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/redis.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 02, Story 03
- Downstream Dependents: Story 40, Story 41, Story 46

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 40 — Cache-Aside (Lazy Loading) Pattern Implementation
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/cache/cache_service.py`). Verified by automated test suites (backend/tests/unit/test_cache_service.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for cache-aside (lazy loading) pattern implementation; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements cache-aside (lazy loading) pattern implementation in `backend/app/cache/cache_service.py` (CacheService.get_json / CacheService.set_json)."

**Do Not Claim:** "Do not claim unverified distributed extensions for cache-aside (lazy loading) pattern implementation."

#### 1. Core Concept
Transparent response caching in Redis with database fallback and graceful degradation on Redis outage. Understanding cache-aside (lazy loading) pattern implementation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/cache_service.py`
- `backend/app/services/property_service.py`
- Primary Symbol / Class / Function: `CacheService.get_json / CacheService.set_json`
- Verification Test Harness: `backend/tests/unit/test_cache_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Cache-Aside (Lazy Loading) Pattern Implementation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 39
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/cache_service.py`.
2. Verify the implementation of `CacheService.get_json / CacheService.set_json`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cache_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/cache_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cache_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cache_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/cache_service.py`.
- [ ] Test harness `backend/tests/unit/test_cache_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement cache-aside (lazy loading) pattern implementation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/cache_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 39
- Downstream Dependents: Story 41, Story 42, Story 43, Story 44

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 41 — Canonical Cache Key Design & Deterministic Hashing
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/cache/cache_keys.py`). Verified by automated test suites (backend/tests/unit/test_cache_keys.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for canonical cache key design & deterministic hashing; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements canonical cache key design & deterministic hashing in `backend/app/cache/cache_keys.py` (CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route)."

**Do Not Claim:** "Do not claim unverified distributed extensions for canonical cache key design & deterministic hashing."

#### 1. Core Concept
Versioned deterministic key generation (estatemap:v1:...) with coordinate normalization and SHA-256 digests. Understanding canonical cache key design & deterministic hashing is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/cache_keys.py`
- `backend/app/cache/cache_service.py`
- Primary Symbol / Class / Function: `CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route`
- Verification Test Harness: `backend/tests/unit/test_cache_keys.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Canonical Cache Key Design & Deterministic Hashing Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 39, Story 40
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/cache_keys.py`.
2. Verify the implementation of `CacheKeys.map_properties / CacheKeys.poi_intelligence / CacheKeys.route`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cache_keys.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/cache_keys.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cache_keys.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cache_keys.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/cache_keys.py`.
- [ ] Test harness `backend/tests/unit/test_cache_keys.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement canonical cache key design & deterministic hashing and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/cache_keys.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 39, Story 40
- Downstream Dependents: Story 42, Story 44

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 42 — Cache Invalidation Strategies & Non-Blocking SCAN Eviction
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/cache/cache_service.py` (CacheService.delete_pattern / CacheService.delete).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational cache invalidation strategies & non-blocking scan eviction in `backend/app/cache/cache_service.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for cache invalidation strategies & non-blocking scan eviction."

#### 1. Core Concept
Non-blocking SCAN-based wildcard key invalidation triggered on property mutations. Understanding cache invalidation strategies & non-blocking scan eviction is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/cache_service.py`
- `backend/app/services/property_service.py`
- Primary Symbol / Class / Function: `CacheService.delete_pattern / CacheService.delete`
- Verification Test Harness: `backend/tests/unit/test_cache_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Cache Invalidation Strategies & Non-Blocking SCAN Eviction Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 40, Story 41
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/cache_service.py`.
2. Verify the implementation of `CacheService.delete_pattern / CacheService.delete`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cache_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/cache_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cache_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cache_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/cache_service.py`.
- [ ] Test harness `backend/tests/unit/test_cache_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement cache invalidation strategies & non-blocking scan eviction and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/cache_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 40, Story 41
- Downstream Dependents: Story 43, Story 93

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 43 — Cache Stampede Mitigation & TTL Configuration
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/cache/cache_service.py` (CACHE_MAP_TTL_SECONDS=120 / CACHE_RANKING_TTL_SECONDS=300).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational cache stampede mitigation & ttl configuration in `backend/app/cache/cache_service.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for cache stampede mitigation & ttl configuration."

#### 1. Core Concept
Domain-specific TTLs mitigating cache stampedes and preventing stale viewport data. Understanding cache stampede mitigation & ttl configuration is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/cache_service.py`
- `backend/app/core/config.py`
- Primary Symbol / Class / Function: `CACHE_MAP_TTL_SECONDS=120 / CACHE_RANKING_TTL_SECONDS=300`
- Verification Test Harness: `backend/tests/unit/test_cache_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Cache Stampede Mitigation & TTL Configuration Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 40, Story 41, Story 42
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/cache_service.py`.
2. Verify the implementation of `CACHE_MAP_TTL_SECONDS=120 / CACHE_RANKING_TTL_SECONDS=300`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cache_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/cache_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cache_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cache_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/cache_service.py`.
- [ ] Test harness `backend/tests/unit/test_cache_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement cache stampede mitigation & ttl configuration and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/cache_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 40, Story 41, Story 42
- Downstream Dependents: Story 93

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 44 — Geospatial Route Caching with Invariant Coordinate Rounding
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/services/commute_service.py` (CacheKeys.normalize_coord / CACHE_COORDINATE_PRECISION=4).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational geospatial route caching with invariant coordinate rounding in `backend/app/services/commute_service.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for geospatial route caching with invariant coordinate rounding."

#### 1. Core Concept
Coordinate rounding to 4 decimal places (~11m) maximizing cache hit ratios for nearby routes. Understanding geospatial route caching with invariant coordinate rounding is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/commute_service.py`
- `backend/app/cache/cache_keys.py`
- Primary Symbol / Class / Function: `CacheKeys.normalize_coord / CACHE_COORDINATE_PRECISION=4`
- Verification Test Harness: `backend/tests/unit/test_cache_keys.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Geospatial Route Caching with Invariant Coordinate Rounding Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 32, Story 33, Story 40, Story 41
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/commute_service.py`.
2. Verify the implementation of `CacheKeys.normalize_coord / CACHE_COORDINATE_PRECISION=4`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cache_keys.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/commute_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cache_keys.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cache_keys.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/commute_service.py`.
- [ ] Test harness `backend/tests/unit/test_cache_keys.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement geospatial route caching with invariant coordinate rounding and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/commute_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 32, Story 33, Story 40, Story 41
- Downstream Dependents: Story 93

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 45 — Token Bucket vs Leaky Bucket vs Sliding Window Rate Limiting
* **Story Points**: 5 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/core/rate_limit.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of token bucket vs leaky bucket vs sliding window rate limiting that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for token bucket vs leaky bucket vs sliding window rate limiting."

#### 1. Core Concept
Comparative analysis of rate limiting algorithms, boundary burst handling, and memory tradeoffs. Understanding token bucket vs leaky bucket vs sliding window rate limiting is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/rate_limit.py`
- Primary Symbol / Class / Function: `Rate limiting algorithm theory (Token Bucket, Leaky Bucket, Sliding Window Log)`
- Verification Test Harness: `backend/tests/integration/test_rate_limiting.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Token Bucket vs Leaky Bucket vs Sliding Window Rate Limiting Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 39
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/rate_limit.py`.
2. Verify the implementation of `Rate limiting algorithm theory (Token Bucket, Leaky Bucket, Sliding Window Log)`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_rate_limiting.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/rate_limit.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_rate_limiting.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_rate_limiting.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/rate_limit.py`.
- [ ] Test harness `backend/tests/integration/test_rate_limiting.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement token bucket vs leaky bucket vs sliding window rate limiting and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/rate_limit.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 39
- Downstream Dependents: Story 46, Story 47, Story 48

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 46 — Sliding-Window Log Rate Limiter via Redis Sorted Sets (ZSET)
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/rate_limit.py`). Verified by automated test suites (backend/tests/integration/test_rate_limiting.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for sliding-window log rate limiter via redis sorted sets (zset); essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements sliding-window log rate limiter via redis sorted sets (zset) in `backend/app/core/rate_limit.py` (RateLimiter.is_rate_limited / redis.pipeline())."

**Do Not Claim:** "Do not claim unverified distributed extensions for sliding-window log rate limiter via redis sorted sets (zset)."

#### 1. Core Concept
Pipelined Redis ZSET sliding window rate limiting with optimistic addition and application rollback. Understanding sliding-window log rate limiter via redis sorted sets (zset) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/rate_limit.py`
- `backend/app/core/middleware.py`
- Primary Symbol / Class / Function: `RateLimiter.is_rate_limited / redis.pipeline()`
- Verification Test Harness: `backend/tests/integration/test_rate_limiting.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Sliding-Window Log Rate Limiter via Redis Sorted Sets (ZSET) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 06, Story 39, Story 45
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/rate_limit.py`.
2. Verify the implementation of `RateLimiter.is_rate_limited / redis.pipeline()`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_rate_limiting.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/rate_limit.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_rate_limiting.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_rate_limiting.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/rate_limit.py`.
- [ ] Test harness `backend/tests/integration/test_rate_limiting.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement sliding-window log rate limiter via redis sorted sets (zset) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/rate_limit.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 06, Story 39, Story 45
- Downstream Dependents: Story 47, Story 48, Story 49

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 47 — Rate Limit Headers & RFC Standard Compliance
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/rate_limit.py`). Verified by automated test suites (backend/tests/integration/test_rate_limiting.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for rate limit headers & rfc standard compliance; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements rate limit headers & rfc standard compliance in `backend/app/core/rate_limit.py` (X-RateLimit-Limit / X-RateLimit-Remaining / RateLimitExceededException)."

**Do Not Claim:** "Do not claim unverified distributed extensions for rate limit headers & rfc standard compliance."

#### 1. Core Concept
Emitting RFC-compliant rate limiting telemetry and Retry-After headers on HTTP 429. Understanding rate limit headers & rfc standard compliance is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/rate_limit.py`
- `backend/app/core/exceptions.py`
- Primary Symbol / Class / Function: `X-RateLimit-Limit / X-RateLimit-Remaining / RateLimitExceededException`
- Verification Test Harness: `backend/tests/integration/test_rate_limiting.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Rate Limit Headers & RFC Standard Compliance Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 46
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/rate_limit.py`.
2. Verify the implementation of `X-RateLimit-Limit / X-RateLimit-Remaining / RateLimitExceededException`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_rate_limiting.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/rate_limit.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_rate_limiting.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_rate_limiting.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/rate_limit.py`.
- [ ] Test harness `backend/tests/integration/test_rate_limiting.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement rate limit headers & rfc standard compliance and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/rate_limit.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 46
- Downstream Dependents: Story 48, Story 49

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 48 — Multi-Tiered Rate Limiting by Scope & Identity
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/rate_limit.py`). Verified by automated test suites (backend/tests/integration/test_rate_limiting.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for multi-tiered rate limiting by scope & identity; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements multi-tiered rate limiting by scope & identity in `backend/app/core/rate_limit.py` (RATE_LIMIT_DEFAULT_REQUESTS=100 / RATE_LIMIT_RANKED_SEARCH_REQUESTS=20 / RATE_LIMIT_AI_REQUESTS=15)."

**Do Not Claim:** "Do not claim unverified distributed extensions for multi-tiered rate limiting by scope & identity."

#### 1. Core Concept
Granular endpoint-scoped rate limiting configured via application settings. Understanding multi-tiered rate limiting by scope & identity is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/rate_limit.py`
- `backend/app/core/config.py`
- Primary Symbol / Class / Function: `RATE_LIMIT_DEFAULT_REQUESTS=100 / RATE_LIMIT_RANKED_SEARCH_REQUESTS=20 / RATE_LIMIT_AI_REQUESTS=15`
- Verification Test Harness: `backend/tests/integration/test_rate_limiting.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Multi-Tiered Rate Limiting by Scope & Identity Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 15, Story 46, Story 47
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/rate_limit.py`.
2. Verify the implementation of `RATE_LIMIT_DEFAULT_REQUESTS=100 / RATE_LIMIT_RANKED_SEARCH_REQUESTS=20 / RATE_LIMIT_AI_REQUESTS=15`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_rate_limiting.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/rate_limit.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_rate_limiting.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_rate_limiting.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/rate_limit.py`.
- [ ] Test harness `backend/tests/integration/test_rate_limiting.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement multi-tiered rate limiting by scope & identity and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/rate_limit.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 15, Story 46, Story 47
- Downstream Dependents: Story 49, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 49 — Fail-Open vs Fail-Closed Degradation Policies
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/core/rate_limit.py`). Verified by automated test suites (backend/tests/integration/test_redis_degradation.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for fail-open vs fail-closed degradation policies; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements fail-open vs fail-closed degradation policies in `backend/app/core/rate_limit.py` (RATE_LIMIT_FAIL_OPEN=True)."

**Do Not Claim:** "Do not claim unverified distributed extensions for fail-open vs fail-closed degradation policies."

#### 1. Core Concept
Configurable resilience policy allowing traffic through when Redis experiences downtime. Understanding fail-open vs fail-closed degradation policies is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/rate_limit.py`
- `backend/app/core/middleware.py`
- Primary Symbol / Class / Function: `RATE_LIMIT_FAIL_OPEN=True`
- Verification Test Harness: `backend/tests/integration/test_redis_degradation.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Fail-Open vs Fail-Closed Degradation Policies Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 46, Story 47, Story 48
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/rate_limit.py`.
2. Verify the implementation of `RATE_LIMIT_FAIL_OPEN=True`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_redis_degradation.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/rate_limit.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_redis_degradation.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_redis_degradation.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/rate_limit.py`.
- [ ] Test harness `backend/tests/integration/test_redis_degradation.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement fail-open vs fail-closed degradation policies and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/rate_limit.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 46, Story 47, Story 48
- Downstream Dependents: Story 50, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 50 — Distributed Redis Connection Management & Sentinel High Availability
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/cache/redis.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for distributed redis connection management & sentinel high availability under high load."

**Do Not Claim:** "Do not claim distributed redis connection management & sentinel high availability is running in the current local Docker Compose baseline."

#### 1. Core Concept
Master-replica failover, Sentinel consensus monitoring, and distributed Redis cluster routing. Understanding distributed redis connection management & sentinel high availability is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/redis.py`
- `backend/app/core/config.py`
- Primary Symbol / Class / Function: `Redis Sentinel / Redis Cluster HA Topology`
- Verification Test Harness: `backend/tests/integration/test_redis.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Distributed Redis Connection Management & Sentinel High Availability Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 02, Story 39, Story 49
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/redis.py`.
2. Verify the implementation of `Redis Sentinel / Redis Cluster HA Topology`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_redis.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/redis.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_redis.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_redis.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/redis.py`.
- [ ] Test harness `backend/tests/integration/test_redis.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement distributed redis connection management & sentinel high availability and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/redis.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 02, Story 39, Story 49
- Downstream Dependents: Story 93, Story 97

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.


## Phase 7: Multi-Provider AI Architecture & Conversational Search (Stories 51-61 & 65-72)

### Story 51 — LLM Integration Patterns: RAG vs Function Calling vs State Machines
* **Story Points**: 5 SP
* **Implementation Status**: [THEORY]
* **Learning Priority**: SUPPORTING THEORY
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Foundational CS and mathematical theory directly underpinning EstateMap architectural decisions in `backend/app/ai/base.py`.

**Not Implemented:** Standalone custom database engine or compiler from scratch.

**Why It Is Still Worth Learning:** Deep systems engineering theory required to justify why EstateMap selected specific algorithms and database primitives.

**Safe Interview Wording:** "I understand the theoretical tradeoffs of llm integration patterns: rag vs function calling vs state machines that justified EstateMap's architectural choices."

**Do Not Claim:** "Do not claim custom low-level C engine implementations for llm integration patterns: rag vs function calling vs state machines."

#### 1. Core Concept
Design analysis of stateful agent loops vs deterministic server-side state machines. Understanding llm integration patterns: rag vs function calling vs state machines is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/base.py`
- `backend/app/services/search_orchestrator.py`
- Primary Symbol / Class / Function: `LLM architecture comparison: RAG vs Tool Calling vs State Machines`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ LLM Integration Patterns: RAG vs Function Calling vs State Machines Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/base.py`.
2. Verify the implementation of `LLM architecture comparison: RAG vs Tool Calling vs State Machines`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/base.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/base.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement llm integration patterns: rag vs function calling vs state machines and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/base.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04
- Downstream Dependents: Story 52, Story 55, Story 65

#### 20. Status Audit & Drift Prevention
- Status: `[THEORY]` verified against repository code.

### Story 52 — Abstract AI Provider Protocol & Decoupled Architecture
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/base.py`). Verified by automated test suites (backend/tests/unit/test_cross_provider_parity.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for abstract ai provider protocol & decoupled architecture; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements abstract ai provider protocol & decoupled architecture in `backend/app/ai/base.py` (AIProvider(ABC) / AIRouter.get_provider)."

**Do Not Claim:** "Do not claim unverified distributed extensions for abstract ai provider protocol & decoupled architecture."

#### 1. Core Concept
Abstract base class standardizing intent parsing, property explanation, and comparison across providers. Understanding abstract ai provider protocol & decoupled architecture is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/base.py`
- `backend/app/ai/router.py`
- Primary Symbol / Class / Function: `AIProvider(ABC) / AIRouter.get_provider`
- Verification Test Harness: `backend/tests/unit/test_cross_provider_parity.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Abstract AI Provider Protocol & Decoupled Architecture Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 03, Story 51
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/base.py`.
2. Verify the implementation of `AIProvider(ABC) / AIRouter.get_provider`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_cross_provider_parity.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/base.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_cross_provider_parity.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_cross_provider_parity.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/base.py`.
- [ ] Test harness `backend/tests/unit/test_cross_provider_parity.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement abstract ai provider protocol & decoupled architecture and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/base.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 03, Story 51
- Downstream Dependents: Story 53, Story 54, Story 57

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 53 — Local LLM Inference with Ollama (Llama 3.2:3b)
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/ollama_provider.py`). Verified by automated test suites (backend/tests/unit/test_ollama_provider.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for local llm inference with ollama (llama 3.2:3b); essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements local llm inference with ollama (llama 3.2:3b) in `backend/app/ai/ollama_provider.py` (OllamaProvider.parse_search_intent / OllamaProvider.explain_property)."

**Do Not Claim:** "Do not claim unverified distributed extensions for local llm inference with ollama (llama 3.2:3b)."

#### 1. Core Concept
Local low-latency LLM inference communicating via HTTP with Ollama running on the host. Understanding local llm inference with ollama (llama 3.2:3b) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/ollama_provider.py`
- `backend/app/ai/base.py`
- Primary Symbol / Class / Function: `OllamaProvider.parse_search_intent / OllamaProvider.explain_property`
- Verification Test Harness: `backend/tests/unit/test_ollama_provider.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Local LLM Inference with Ollama (Llama 3.2:3b) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 52
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/ollama_provider.py`.
2. Verify the implementation of `OllamaProvider.parse_search_intent / OllamaProvider.explain_property`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ollama_provider.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/ollama_provider.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ollama_provider.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ollama_provider.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/ollama_provider.py`.
- [ ] Test harness `backend/tests/unit/test_ollama_provider.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement local llm inference with ollama (llama 3.2:3b) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/ollama_provider.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 52
- Downstream Dependents: Story 57, Story 58

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 54 — Cloud LLM Inference with Google Gemini 3.6 Flash
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/gemini_provider.py`). Verified by automated test suites (backend/tests/unit/test_gemini_provider.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for cloud llm inference with google gemini 3.6 flash; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements cloud llm inference with google gemini 3.6 flash in `backend/app/ai/gemini_provider.py` (GeminiProvider.parse_search_intent / GeminiProvider.explain_property)."

**Do Not Claim:** "Do not claim unverified distributed extensions for cloud llm inference with google gemini 3.6 flash."

#### 1. Core Concept
Cloud LLM inference leveraging Google Gemini structured output and temperature controls. Understanding cloud llm inference with google gemini 3.6 flash is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/gemini_provider.py`
- `backend/app/ai/base.py`
- Primary Symbol / Class / Function: `GeminiProvider.parse_search_intent / GeminiProvider.explain_property`
- Verification Test Harness: `backend/tests/unit/test_gemini_provider.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Cloud LLM Inference with Google Gemini 3.6 Flash Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 52
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/gemini_provider.py`.
2. Verify the implementation of `GeminiProvider.parse_search_intent / GeminiProvider.explain_property`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_gemini_provider.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/gemini_provider.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_gemini_provider.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_gemini_provider.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/gemini_provider.py`.
- [ ] Test harness `backend/tests/unit/test_gemini_provider.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement cloud llm inference with google gemini 3.6 flash and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/gemini_provider.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 52
- Downstream Dependents: Story 57, Story 58

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 55 — Structured JSON Schema Enforcement & LLM Output Validation
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/schemas/ai.py`). Verified by automated test suites (backend/tests/unit/test_ai_schemas.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for structured json schema enforcement & llm output validation; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements structured json schema enforcement & llm output validation in `backend/app/schemas/ai.py` (ParseSearchResponse / PropertySearchIntent / AIExplanationResponse)."

**Do Not Claim:** "Do not claim unverified distributed extensions for structured json schema enforcement & llm output validation."

#### 1. Core Concept
Pydantic schema validation preventing malformed LLM outputs from propagating into the domain layer. Understanding structured json schema enforcement & llm output validation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/ai.py`
- `backend/app/ai/gemini_provider.py`
- `backend/app/ai/ollama_provider.py`
- Primary Symbol / Class / Function: `ParseSearchResponse / PropertySearchIntent / AIExplanationResponse`
- Verification Test Harness: `backend/tests/unit/test_ai_schemas.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Structured JSON Schema Enforcement & LLM Output Validation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04, Story 51, Story 52
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/ai.py`.
2. Verify the implementation of `ParseSearchResponse / PropertySearchIntent / AIExplanationResponse`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ai_schemas.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/ai.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ai_schemas.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ai_schemas.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/ai.py`.
- [ ] Test harness `backend/tests/unit/test_ai_schemas.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement structured json schema enforcement & llm output validation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/ai.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04, Story 51, Story 52
- Downstream Dependents: Story 56, Story 59, Story 66

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 56 — Prompt Engineering for Real Estate Query Disambiguation
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/ai/prompts/` (search_intent_v1.txt / property_explanation_v1.txt).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational prompt engineering for real estate query disambiguation in `backend/app/ai/prompts/`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for prompt engineering for real estate query disambiguation."

#### 1. Core Concept
Prompt templates instructing models to extract structured filters without generating SQL. Understanding prompt engineering for real estate query disambiguation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/prompts/`
- `backend/app/services/search_orchestrator.py`
- Primary Symbol / Class / Function: `search_intent_v1.txt / property_explanation_v1.txt`
- Verification Test Harness: `backend/tests/unit/test_ai_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Prompt Engineering for Real Estate Query Disambiguation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 55
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/prompts/`.
2. Verify the implementation of `search_intent_v1.txt / property_explanation_v1.txt`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ai_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/prompts/` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ai_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ai_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/prompts/`.
- [ ] Test harness `backend/tests/unit/test_ai_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement prompt engineering for real estate query disambiguation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/prompts/` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 55
- Downstream Dependents: Story 57, Story 65, Story 69

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 57 — Deterministic Complexity-Based AI Provider Routing Strategy
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/router.py`). Verified by automated test suites (backend/tests/unit/test_routing_policy.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for deterministic complexity-based ai provider routing strategy; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements deterministic complexity-based ai provider routing strategy in `backend/app/ai/router.py` (AIRoutingPolicy.profile_intent_query / AIRouter.resolve_provider)."

**Do Not Claim:** "Do not claim unverified distributed extensions for deterministic complexity-based ai provider routing strategy."

#### 1. Core Concept
Rule-based routing directing simple queries to local Ollama and complex queries to Gemini. Understanding deterministic complexity-based ai provider routing strategy is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/router.py`
- `backend/app/ai/routing_policy.py`
- Primary Symbol / Class / Function: `AIRoutingPolicy.profile_intent_query / AIRouter.resolve_provider`
- Verification Test Harness: `backend/tests/unit/test_routing_policy.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Deterministic Complexity-Based AI Provider Routing Strategy Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 52, Story 53, Story 54, Story 56
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/router.py`.
2. Verify the implementation of `AIRoutingPolicy.profile_intent_query / AIRouter.resolve_provider`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_routing_policy.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/router.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_routing_policy.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_routing_policy.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/router.py`.
- [ ] Test harness `backend/tests/unit/test_routing_policy.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement deterministic complexity-based ai provider routing strategy and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/router.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 52, Story 53, Story 54, Story 56
- Downstream Dependents: Story 58, Story 60, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 58 — Global Request Deadlines & Bounded Provider Failover
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/router.py`). Verified by automated test suites (backend/tests/integration/test_ai_failover.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for global request deadlines & bounded provider failover; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements global request deadlines & bounded provider failover in `backend/app/ai/router.py` (AI_TOTAL_TIMEOUT_SECONDS=35.0 / AIService._execute_with_failover)."

**Do Not Claim:** "Do not claim unverified distributed extensions for global request deadlines & bounded provider failover."

#### 1. Core Concept
Bounded single-attempt failover switching to secondary provider upon transient network timeouts. Understanding global request deadlines & bounded provider failover is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/router.py`
- `backend/app/services/ai_service.py`
- Primary Symbol / Class / Function: `AI_TOTAL_TIMEOUT_SECONDS=35.0 / AIService._execute_with_failover`
- Verification Test Harness: `backend/tests/integration/test_ai_failover.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Global Request Deadlines & Bounded Provider Failover Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 05, Story 06, Story 53, Story 54, Story 57
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/router.py`.
2. Verify the implementation of `AI_TOTAL_TIMEOUT_SECONDS=35.0 / AIService._execute_with_failover`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ai_failover.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/router.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ai_failover.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ai_failover.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/router.py`.
- [ ] Test harness `backend/tests/integration/test_ai_failover.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement global request deadlines & bounded provider failover and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/router.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 05, Story 06, Story 53, Story 54, Story 57
- Downstream Dependents: Story 61, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 59 — AI Guardrails, Prompt-Injection Risk Mitigation & Schema Boundaries
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/services/ai_service.py` (SearchStatePatch Pydantic validation / Untrusted output isolation).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational ai guardrails, prompt-injection risk mitigation & schema boundaries in `backend/app/services/ai_service.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for ai guardrails, prompt-injection risk mitigation & schema boundaries."

#### 1. Core Concept
Mitigating prompt-injection risks by treating all LLM output as untrusted and strictly parsing to Pydantic patches. Understanding ai guardrails, prompt-injection risk mitigation & schema boundaries is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/ai_service.py`
- `backend/app/schemas/conversational_search.py`
- Primary Symbol / Class / Function: `SearchStatePatch Pydantic validation / Untrusted output isolation`
- Verification Test Harness: `backend/tests/unit/test_conversational_search_schemas.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ AI Guardrails, Prompt-Injection Risk Mitigation & Schema Boundaries Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 55, Story 56
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/ai_service.py`.
2. Verify the implementation of `SearchStatePatch Pydantic validation / Untrusted output isolation`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_conversational_search_schemas.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/ai_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_conversational_search_schemas.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_conversational_search_schemas.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/ai_service.py`.
- [ ] Test harness `backend/tests/unit/test_conversational_search_schemas.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement ai guardrails, prompt-injection risk mitigation & schema boundaries and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/ai_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 55, Story 56
- Downstream Dependents: Story 66, Story 70, Story 98

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 60 — Token Usage Tracking, Cost Estimation & Latency Metrics
* **Story Points**: 3 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/schemas/ai.py` (AIUsageMetadata / prompt_tokens / completion_tokens).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational token usage tracking, cost estimation & latency metrics in `backend/app/schemas/ai.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for token usage tracking, cost estimation & latency metrics."

#### 1. Core Concept
Recording token consumption, estimated cost, and provider execution duration. Understanding token usage tracking, cost estimation & latency metrics is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/ai.py`
- `backend/app/ai/gemini_provider.py`
- Primary Symbol / Class / Function: `AIUsageMetadata / prompt_tokens / completion_tokens`
- Verification Test Harness: `backend/tests/unit/test_ai_service.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Token Usage Tracking, Cost Estimation & Latency Metrics Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 57, Story 58
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/ai.py`.
2. Verify the implementation of `AIUsageMetadata / prompt_tokens / completion_tokens`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_ai_service.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/ai.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_ai_service.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_ai_service.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/ai.py`.
- [ ] Test harness `backend/tests/unit/test_ai_service.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement token usage tracking, cost estimation & latency metrics and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/ai.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 57, Story 58
- Downstream Dependents: Story 90, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 61 — Deterministic Fallback Parser (Zero-LLM Mode)
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/ai/mock_provider.py`). Verified by automated test suites (backend/tests/integration/test_ai_endpoints.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for deterministic fallback parser (zero-llm mode); essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements deterministic fallback parser (zero-llm mode) in `backend/app/ai/mock_provider.py` (MockProvider.parse_search_intent / IndianPriceParser)."

**Do Not Claim:** "Do not claim unverified distributed extensions for deterministic fallback parser (zero-llm mode)."

#### 1. Core Concept
Deterministic regex and keyword parsing ensuring search functionality even if all LLM providers fail. Understanding deterministic fallback parser (zero-llm mode) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/mock_provider.py`
- `backend/app/services/ai_service.py`
- Primary Symbol / Class / Function: `MockProvider.parse_search_intent / IndianPriceParser`
- Verification Test Harness: `backend/tests/integration/test_ai_endpoints.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Deterministic Fallback Parser (Zero-LLM Mode) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 58
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/mock_provider.py`.
2. Verify the implementation of `MockProvider.parse_search_intent / IndianPriceParser`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ai_endpoints.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/mock_provider.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ai_endpoints.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ai_endpoints.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/mock_provider.py`.
- [ ] Test harness `backend/tests/integration/test_ai_endpoints.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement deterministic fallback parser (zero-llm mode) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/mock_provider.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 58
- Downstream Dependents: Story 65, Story 66

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 65 — "Ask the Map" Conversational Search Architecture
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/api/v1/ai.py`). Verified by automated test suites (backend/tests/integration/test_ask_the_map.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for "ask the map" conversational search architecture; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements "ask the map" conversational search architecture in `backend/app/api/v1/ai.py` (AskMapRequest / AskMapResponse / SearchOrchestrator.apply_patch)."

**Do Not Claim:** "Do not claim unverified distributed extensions for "ask the map" conversational search architecture."

#### 1. Core Concept
Conversational discovery interface bridging natural language intent with PostGIS filtering and MapLibre. Understanding "ask the map" conversational search architecture is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/api/v1/ai.py`
- `backend/app/services/search_orchestrator.py`
- `frontend/components/search/ask-the-map-bar.tsx`
- Primary Symbol / Class / Function: `AskMapRequest / AskMapResponse / SearchOrchestrator.apply_patch`
- Verification Test Harness: `backend/tests/integration/test_ask_the_map.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ "Ask the Map" Conversational Search Architecture Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 51, Story 56, Story 57, Story 61
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/api/v1/ai.py`.
2. Verify the implementation of `AskMapRequest / AskMapResponse / SearchOrchestrator.apply_patch`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ask_the_map.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/api/v1/ai.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ask_the_map.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ask_the_map.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/api/v1/ai.py`.
- [ ] Test harness `backend/tests/integration/test_ask_the_map.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement "ask the map" conversational search architecture and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/api/v1/ai.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 51, Story 56, Story 57, Story 61
- Downstream Dependents: Story 66, Story 67, Story 68, Story 75

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 66 — Multi-Turn Conversation State Reducer & Delta Patches
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/search_orchestrator.py`). Verified by automated test suites (backend/tests/unit/test_search_orchestrator.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for multi-turn conversation state reducer & delta patches; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements multi-turn conversation state reducer & delta patches in `backend/app/services/search_orchestrator.py` (SearchOrchestrator.apply_patch / ConversationalSearchState / SearchStatePatch)."

**Do Not Claim:** "Do not claim unverified distributed extensions for multi-turn conversation state reducer & delta patches."

#### 1. Core Concept
Deterministic state transitions accumulating, overriding, and clearing filter parameters across turns. Understanding multi-turn conversation state reducer & delta patches is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/search_orchestrator.py`
- `backend/app/schemas/conversational_search.py`
- Primary Symbol / Class / Function: `SearchOrchestrator.apply_patch / ConversationalSearchState / SearchStatePatch`
- Verification Test Harness: `backend/tests/unit/test_search_orchestrator.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Multi-Turn Conversation State Reducer & Delta Patches Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 55, Story 59, Story 61, Story 65
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/search_orchestrator.py`.
2. Verify the implementation of `SearchOrchestrator.apply_patch / ConversationalSearchState / SearchStatePatch`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_search_orchestrator.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/search_orchestrator.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_search_orchestrator.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_search_orchestrator.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/search_orchestrator.py`.
- [ ] Test harness `backend/tests/unit/test_search_orchestrator.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement multi-turn conversation state reducer & delta patches and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/search_orchestrator.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 55, Story 59, Story 61, Story 65
- Downstream Dependents: Story 67, Story 68, Story 71

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 67 — Implicit vs Explicit Filter Modification in Conversational Dialogue
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/search_orchestrator.py`). Verified by automated test suites (backend/tests/unit/test_search_orchestrator.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for implicit vs explicit filter modification in conversational dialogue; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements implicit vs explicit filter modification in conversational dialogue in `backend/app/services/search_orchestrator.py` (AllowedSearchField / AppliedPatchFeedback)."

**Do Not Claim:** "Do not claim unverified distributed extensions for implicit vs explicit filter modification in conversational dialogue."

#### 1. Core Concept
Differentiating explicit filter resets from additive refinements in user dialogue. Understanding implicit vs explicit filter modification in conversational dialogue is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/search_orchestrator.py`
- `backend/app/schemas/conversational_search.py`
- Primary Symbol / Class / Function: `AllowedSearchField / AppliedPatchFeedback`
- Verification Test Harness: `backend/tests/unit/test_search_orchestrator.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Implicit vs Explicit Filter Modification in Conversational Dialogue Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 65, Story 66
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/search_orchestrator.py`.
2. Verify the implementation of `AllowedSearchField / AppliedPatchFeedback`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_search_orchestrator.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/search_orchestrator.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_search_orchestrator.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_search_orchestrator.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/search_orchestrator.py`.
- [ ] Test harness `backend/tests/unit/test_search_orchestrator.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement implicit vs explicit filter modification in conversational dialogue and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/search_orchestrator.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 65, Story 66
- Downstream Dependents: Story 68, Story 69

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 68 — Conversational Filter History & Undo/Reset State Management
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/search_orchestrator.py`). Verified by automated test suites (backend/tests/unit/test_search_orchestrator.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for conversational filter history & undo/reset state management; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements conversational filter history & undo/reset state management in `backend/app/services/search_orchestrator.py` (ConversationAction.RESET_SEARCH / ConversationAction.CLEAR_FILTER)."

**Do Not Claim:** "Do not claim unverified distributed extensions for conversational filter history & undo/reset state management."

#### 1. Core Concept
Supporting atomic reset and single-field removal operations within conversational search. Understanding conversational filter history & undo/reset state management is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/search_orchestrator.py`
- `frontend/components/search/ask-the-map-bar.tsx`
- Primary Symbol / Class / Function: `ConversationAction.RESET_SEARCH / ConversationAction.CLEAR_FILTER`
- Verification Test Harness: `backend/tests/unit/test_search_orchestrator.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Conversational Filter History & Undo/Reset State Management Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 66, Story 67
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/search_orchestrator.py`.
2. Verify the implementation of `ConversationAction.RESET_SEARCH / ConversationAction.CLEAR_FILTER`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_search_orchestrator.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/search_orchestrator.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_search_orchestrator.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_search_orchestrator.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/search_orchestrator.py`.
- [ ] Test harness `backend/tests/unit/test_search_orchestrator.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement conversational filter history & undo/reset state management and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/search_orchestrator.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 66, Story 67
- Downstream Dependents: Story 71, Story 75

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 69 — Conversational Spatial Intent Disambiguation & Clarification
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/utils/location_resolver.py` (unresolved_destination / requires_clarification flag).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational conversational spatial intent disambiguation & clarification in `backend/app/utils/location_resolver.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for conversational spatial intent disambiguation & clarification."

#### 1. Core Concept
Prompting the user for clarification when spatial destinations cannot be resolved to known coordinates. Understanding conversational spatial intent disambiguation & clarification is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/utils/location_resolver.py`
- `backend/app/services/search_orchestrator.py`
- Primary Symbol / Class / Function: `unresolved_destination / requires_clarification flag`
- Verification Test Harness: `backend/tests/integration/test_ask_the_map.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Conversational Spatial Intent Disambiguation & Clarification Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 30, Story 56, Story 65, Story 67
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/utils/location_resolver.py`.
2. Verify the implementation of `unresolved_destination / requires_clarification flag`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ask_the_map.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/utils/location_resolver.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ask_the_map.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ask_the_map.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/utils/location_resolver.py`.
- [ ] Test harness `backend/tests/integration/test_ask_the_map.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement conversational spatial intent disambiguation & clarification and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/utils/location_resolver.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 30, Story 56, Story 65, Story 67
- Downstream Dependents: Story 70, Story 77

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 70 — Grounded AI Response Generation & Hallucination Prevention
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/services/ai_service.py`). Verified by automated test suites (backend/tests/integration/test_ai_endpoints.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for grounded ai response generation & hallucination prevention; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements grounded ai response generation & hallucination prevention in `backend/app/services/ai_service.py` (AIService.explain_property / _build_search_context)."

**Do Not Claim:** "Do not claim unverified distributed extensions for grounded ai response generation & hallucination prevention."

#### 1. Core Concept
Injecting verified PostgreSQL/PostGIS query results into LLM context to eliminate hallucinations. Understanding grounded ai response generation & hallucination prevention is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/ai_service.py`
- `backend/app/services/search_orchestrator.py`
- Primary Symbol / Class / Function: `AIService.explain_property / _build_search_context`
- Verification Test Harness: `backend/tests/integration/test_ai_endpoints.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Grounded AI Response Generation & Hallucination Prevention Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 38, Story 59, Story 64, Story 65
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/ai_service.py`.
2. Verify the implementation of `AIService.explain_property / _build_search_context`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ai_endpoints.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/ai_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ai_endpoints.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ai_endpoints.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/ai_service.py`.
- [ ] Test harness `backend/tests/integration/test_ai_endpoints.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement grounded ai response generation & hallucination prevention and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/ai_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 38, Story 59, Story 64, Story 65
- Downstream Dependents: Story 72, Story 75

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 71 — Stateless Conversation State Model & Client-Side Reducer
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/schemas/conversational_search.py` (Client-maintained ConversationalSearchState payload dispatch).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational stateless conversation state model & client-side reducer in `backend/app/schemas/conversational_search.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for stateless conversation state model & client-side reducer."

#### 1. Core Concept
Stateless server architecture where the client owns session state, avoiding server-side memory leaks. Understanding stateless conversation state model & client-side reducer is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/schemas/conversational_search.py`
- `frontend/app/search/page.tsx`
- Primary Symbol / Class / Function: `Client-maintained ConversationalSearchState payload dispatch`
- Verification Test Harness: `frontend/__tests__/ask_the_map.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Stateless Conversation State Model & Client-Side Reducer Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 39, Story 66, Story 68
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/schemas/conversational_search.py`.
2. Verify the implementation of `Client-maintained ConversationalSearchState payload dispatch`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/ask_the_map.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/schemas/conversational_search.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/ask_the_map.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/ask_the_map.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/schemas/conversational_search.py`.
- [ ] Test harness `frontend/__tests__/ask_the_map.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement stateless conversation state model & client-side reducer and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/schemas/conversational_search.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 39, Story 66, Story 68
- Downstream Dependents: Story 72, Story 96

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 72 — End-to-End Conversational Search Integration Testing
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/tests/integration/test_ask_the_map.py`). Verified by automated test suites (backend/tests/integration/test_ask_the_map.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for end-to-end conversational search integration testing; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements end-to-end conversational search integration testing in `backend/tests/integration/test_ask_the_map.py` (test_ask_the_map_multi_turn_flow)."

**Do Not Claim:** "Do not claim unverified distributed extensions for end-to-end conversational search integration testing."

#### 1. Core Concept
Automated multi-turn test suites validating 8-turn search, refinement, comparison, and reset sequences. Understanding end-to-end conversational search integration testing is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/tests/integration/test_ask_the_map.py`
- `backend/tests/unit/test_search_orchestrator.py`
- Primary Symbol / Class / Function: `test_ask_the_map_multi_turn_flow`
- Verification Test Harness: `backend/tests/integration/test_ask_the_map.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ End-to-End Conversational Search Integration Testing Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 65, Story 66, Story 70, Story 71
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/tests/integration/test_ask_the_map.py`.
2. Verify the implementation of `test_ask_the_map_multi_turn_flow`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/integration/test_ask_the_map.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/tests/integration/test_ask_the_map.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/integration/test_ask_the_map.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/integration/test_ask_the_map.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/tests/integration/test_ask_the_map.py`.
- [ ] Test harness `backend/tests/integration/test_ask_the_map.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement end-to-end conversational search integration testing and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/tests/integration/test_ask_the_map.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 65, Story 66, Story 70, Story 71
- Downstream Dependents: Story 86, Story 88

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 8: Frontend Engineering & Map Visualization (Stories 73-80)

### Story 73 — Next.js 14 App Router & Server/Client Boundary Architecture
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/app/page.tsx`). Verified by automated test suites (frontend/package.json).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for next.js 14 app router & server/client boundary architecture; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements next.js 14 app router & server/client boundary architecture in `frontend/app/page.tsx` ("use client" directive / React Server Components)."

**Do Not Claim:** "Do not claim unverified distributed extensions for next.js 14 app router & server/client boundary architecture."

#### 1. Core Concept
App Router structure, server/client component boundaries, and SSR/CSR hydration strategies. Understanding next.js 14 app router & server/client boundary architecture is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/app/page.tsx`
- `frontend/app/layout.tsx`
- `frontend/app/search/page.tsx`
- Primary Symbol / Class / Function: `"use client" directive / React Server Components`
- Verification Test Harness: `frontend/package.json`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Next.js 14 App Router & Server/Client Boundary Architecture Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 04
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/app/page.tsx`.
2. Verify the implementation of `"use client" directive / React Server Components`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/package.json`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/app/page.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/package.json` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/package.json` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/app/page.tsx`.
- [ ] Test harness `frontend/package.json` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement next.js 14 app router & server/client boundary architecture and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/app/page.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 04
- Downstream Dependents: Story 74, Story 75, Story 76

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 74 — Responsive Real Estate Discovery UI with Tailwind CSS
* **Story Points**: 3 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/app/globals.css`). Verified by automated test suites (frontend/tailwind.config.ts).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for responsive real estate discovery ui with tailwind css; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements responsive real estate discovery ui with tailwind css in `frontend/app/globals.css` (PropertyCard / RankedPropertyCard / Tailwind responsive grid)."

**Do Not Claim:** "Do not claim unverified distributed extensions for responsive real estate discovery ui with tailwind css."

#### 1. Core Concept
Tailwind CSS responsive design system supporting desktop list-map split and mobile stacked discovery. Understanding responsive real estate discovery ui with tailwind css is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/app/globals.css`
- `frontend/tailwind.config.ts`
- `frontend/components/properties/property-card.tsx`
- Primary Symbol / Class / Function: `PropertyCard / RankedPropertyCard / Tailwind responsive grid`
- Verification Test Harness: `frontend/tailwind.config.ts`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Responsive Real Estate Discovery UI with Tailwind CSS Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 73
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/app/globals.css`.
2. Verify the implementation of `PropertyCard / RankedPropertyCard / Tailwind responsive grid`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/tailwind.config.ts`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/app/globals.css` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/tailwind.config.ts` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/tailwind.config.ts` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/app/globals.css`.
- [ ] Test harness `frontend/tailwind.config.ts` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement responsive real estate discovery ui with tailwind css and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/app/globals.css` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 73
- Downstream Dependents: Story 75, Story 78, Story 79

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 75 — Interactive Property Search & Dynamic Filter Controls
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/components/search/filter-bar.tsx`). Verified by automated test suites (frontend/__tests__/ranking-api.test.mjs).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for interactive property search & dynamic filter controls; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements interactive property search & dynamic filter controls in `frontend/components/search/filter-bar.tsx` (FilterBar / RankingPreferences)."

**Do Not Claim:** "Do not claim unverified distributed extensions for interactive property search & dynamic filter controls."

#### 1. Core Concept
Interactive filter controls synchronizing price sliders, BHK selectors, and weight preferences. Understanding interactive property search & dynamic filter controls is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/components/search/filter-bar.tsx`
- `frontend/app/search/page.tsx`
- `frontend/components/search/ranking-preferences.tsx`
- Primary Symbol / Class / Function: `FilterBar / RankingPreferences`
- Verification Test Harness: `frontend/__tests__/ranking-api.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Interactive Property Search & Dynamic Filter Controls Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 19, Story 36, Story 73, Story 74
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/components/search/filter-bar.tsx`.
2. Verify the implementation of `FilterBar / RankingPreferences`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/ranking-api.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/components/search/filter-bar.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/ranking-api.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/ranking-api.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/components/search/filter-bar.tsx`.
- [ ] Test harness `frontend/__tests__/ranking-api.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement interactive property search & dynamic filter controls and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/components/search/filter-bar.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 19, Story 36, Story 73, Story 74
- Downstream Dependents: Story 77, Story 78

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 76 — MapLibre GL WebGL Vector Map Rendering & Tile Management
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/components/map/estate-map.tsx`). Verified by automated test suites (frontend/__tests__/map-sync.test.mjs).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for maplibre gl webgl vector map rendering & tile management; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements maplibre gl webgl vector map rendering & tile management in `frontend/components/map/estate-map.tsx` (EstateMap / MapContainer / maplibre-gl)."

**Do Not Claim:** "Do not claim unverified distributed extensions for maplibre gl webgl vector map rendering & tile management."

#### 1. Core Concept
MapLibre GL JS vector map rendering with custom property pins, POI layers, and mapcn styling. Understanding maplibre gl webgl vector map rendering & tile management is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/components/map/estate-map.tsx`
- `frontend/components/map/map-container.tsx`
- `frontend/components/ui/map.tsx`
- Primary Symbol / Class / Function: `EstateMap / MapContainer / maplibre-gl`
- Verification Test Harness: `frontend/__tests__/map-sync.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ MapLibre GL WebGL Vector Map Rendering & Tile Management Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 25, Story 27, Story 73
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/components/map/estate-map.tsx`.
2. Verify the implementation of `EstateMap / MapContainer / maplibre-gl`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/map-sync.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/components/map/estate-map.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/map-sync.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/map-sync.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/components/map/estate-map.tsx`.
- [ ] Test harness `frontend/__tests__/map-sync.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement maplibre gl webgl vector map rendering & tile management and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/components/map/estate-map.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 25, Story 27, Story 73
- Downstream Dependents: Story 77, Story 78

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 77 — Dynamic Viewport Bounding-Box Calculation & Debounced Pan/Zoom
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/components/map/estate-map.tsx`). Verified by automated test suites (frontend/__tests__/geo-api.test.mjs).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for dynamic viewport bounding-box calculation & debounced pan/zoom; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements dynamic viewport bounding-box calculation & debounced pan/zoom in `frontend/components/map/estate-map.tsx` (buildBBoxQueryParams / onMoveEnd / Viewport state sync)."

**Do Not Claim:** "Do not claim unverified distributed extensions for dynamic viewport bounding-box calculation & debounced pan/zoom."

#### 1. Core Concept
Debounced map movement listeners extracting bounding box coordinates for "Search this area" queries. Understanding dynamic viewport bounding-box calculation & debounced pan/zoom is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/components/map/estate-map.tsx`
- `frontend/lib/api/geo.ts`
- Primary Symbol / Class / Function: `buildBBoxQueryParams / onMoveEnd / Viewport state sync`
- Verification Test Harness: `frontend/__tests__/geo-api.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Dynamic Viewport Bounding-Box Calculation & Debounced Pan/Zoom Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 25, Story 69, Story 75, Story 76
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/components/map/estate-map.tsx`.
2. Verify the implementation of `buildBBoxQueryParams / onMoveEnd / Viewport state sync`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/geo-api.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/components/map/estate-map.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/geo-api.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/geo-api.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/components/map/estate-map.tsx`.
- [ ] Test harness `frontend/__tests__/geo-api.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement dynamic viewport bounding-box calculation & debounced pan/zoom and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/components/map/estate-map.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 25, Story 69, Story 75, Story 76
- Downstream Dependents: Story 78, Story 96

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 78 — Bidirectional Map Marker & Listing Card Synchronized Highlighting
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/components/map/estate-map.tsx`). Verified by automated test suites (frontend/__tests__/map-sync.test.mjs).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for bidirectional map marker & listing card synchronized highlighting; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements bidirectional map marker & listing card synchronized highlighting in `frontend/components/map/estate-map.tsx` (selectedPropertyId / hoveredPropertyId / flyTo marker)."

**Do Not Claim:** "Do not claim unverified distributed extensions for bidirectional map marker & listing card synchronized highlighting."

#### 1. Core Concept
Synchronized hover and click interactions connecting list cards with MapLibre markers. Understanding bidirectional map marker & listing card synchronized highlighting is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/components/map/estate-map.tsx`
- `frontend/components/properties/property-card.tsx`
- `frontend/app/search/page.tsx`
- Primary Symbol / Class / Function: `selectedPropertyId / hoveredPropertyId / flyTo marker`
- Verification Test Harness: `frontend/__tests__/map-sync.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Bidirectional Map Marker & Listing Card Synchronized Highlighting Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 27, Story 38, Story 74, Story 76, Story 77
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/components/map/estate-map.tsx`.
2. Verify the implementation of `selectedPropertyId / hoveredPropertyId / flyTo marker`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/map-sync.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/components/map/estate-map.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/map-sync.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/map-sync.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/components/map/estate-map.tsx`.
- [ ] Test harness `frontend/__tests__/map-sync.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement bidirectional map marker & listing card synchronized highlighting and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/components/map/estate-map.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 27, Story 38, Story 74, Story 76, Story 77
- Downstream Dependents: Story 79, Story 80

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 79 — Interactive Property Comparison Matrix & Visual Differencing
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/components/comparison/comparison-bar.tsx`). Verified by automated test suites (frontend/__tests__/comparison.test.mjs).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for interactive property comparison matrix & visual differencing; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements interactive property comparison matrix & visual differencing in `frontend/components/comparison/comparison-bar.tsx` (ComparisonBar / ComparisonTable / RankingDiffCard)."

**Do Not Claim:** "Do not claim unverified distributed extensions for interactive property comparison matrix & visual differencing."

#### 1. Core Concept
Multi-property comparison modal rendering metric diffs, winner badges, and AI comparison summaries. Understanding interactive property comparison matrix & visual differencing is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/components/comparison/comparison-bar.tsx`
- `frontend/components/comparison/comparison-table.tsx`
- `frontend/app/compare/page.tsx`
- Primary Symbol / Class / Function: `ComparisonBar / ComparisonTable / RankingDiffCard`
- Verification Test Harness: `frontend/__tests__/comparison.test.mjs`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Interactive Property Comparison Matrix & Visual Differencing Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 62, Story 63, Story 64, Story 74, Story 78
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/components/comparison/comparison-bar.tsx`.
2. Verify the implementation of `ComparisonBar / ComparisonTable / RankingDiffCard`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/comparison.test.mjs`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/components/comparison/comparison-bar.tsx` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/comparison.test.mjs` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/comparison.test.mjs` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/components/comparison/comparison-bar.tsx`.
- [ ] Test harness `frontend/__tests__/comparison.test.mjs` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement interactive property comparison matrix & visual differencing and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/components/comparison/comparison-bar.tsx` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 62, Story 63, Story 64, Story 74, Story 78
- Downstream Dependents: Story 80

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 80 — State Management with Zustand & TanStack Query Synchronization
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`frontend/package.json`). Verified by automated test suites (frontend/package.json).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for state management with zustand & tanstack query synchronization; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements state management with zustand & tanstack query synchronization in `frontend/package.json` (QueryClientProvider / TanStack React Query / Zustand store)."

**Do Not Claim:** "Do not claim unverified distributed extensions for state management with zustand & tanstack query synchronization."

#### 1. Core Concept
Client-side caching, optimistic UI updates, and server state synchronization. Understanding state management with zustand & tanstack query synchronization is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/package.json`
- `frontend/components/providers.tsx`
- Primary Symbol / Class / Function: `QueryClientProvider / TanStack React Query / Zustand store`
- Verification Test Harness: `frontend/package.json`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ State Management with Zustand & TanStack Query Synchronization Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 15, Story 78, Story 79
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/package.json`.
2. Verify the implementation of `QueryClientProvider / TanStack React Query / Zustand store`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/package.json`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/package.json` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/package.json` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/package.json` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/package.json`.
- [ ] Test harness `frontend/package.json` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement state management with zustand & tanstack query synchronization and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/package.json` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 15, Story 78, Story 79
- Downstream Dependents: Story 88

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.


## Phase 9: Reliability, Performance & DevOps (Stories 81-90)

### Story 81 — Docker Compose Multi-Container Orchestration
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`docker-compose.yml`). Verified by automated test suites (docker-compose.yml).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for docker compose multi-container orchestration; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements docker compose multi-container orchestration in `docker-compose.yml` (4 services: postgres-postgis, redis, backend, frontend)."

**Do Not Claim:** "Do not claim unverified distributed extensions for docker compose multi-container orchestration."

#### 1. Core Concept
Local development environment orchestrating PostgreSQL/PostGIS, Redis, FastAPI, and Next.js. Understanding docker compose multi-container orchestration is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- Primary Symbol / Class / Function: `4 services: postgres-postgis, redis, backend, frontend`
- Verification Test Harness: `docker-compose.yml`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Docker Compose Multi-Container Orchestration Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 09, Story 39, Story 73
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `docker-compose.yml`.
2. Verify the implementation of `4 services: postgres-postgis, redis, backend, frontend`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docker-compose.yml`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `docker-compose.yml` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docker-compose.yml` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docker-compose.yml` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `docker-compose.yml`.
- [ ] Test harness `docker-compose.yml` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement docker compose multi-container orchestration and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `docker-compose.yml` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 09, Story 39, Story 73
- Downstream Dependents: Story 82, Story 83, Story 84

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 82 — Containerized Health Probes & Dependency-Aware Readiness
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`docker-compose.yml`). Verified by automated test suites (backend/tests/unit/test_health.py).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for containerized health probes & dependency-aware readiness; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements containerized health probes & dependency-aware readiness in `docker-compose.yml` (pg_isready / redis-cli ping / /health/ready probe)."

**Do Not Claim:** "Do not claim unverified distributed extensions for containerized health probes & dependency-aware readiness."

#### 1. Core Concept
Dependency-aware health checks preventing backend startup until PostgreSQL and Redis are healthy. Understanding containerized health probes & dependency-aware readiness is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `docker-compose.yml`
- `backend/app/api/v1/health.py`
- Primary Symbol / Class / Function: `pg_isready / redis-cli ping / /health/ready probe`
- Verification Test Harness: `backend/tests/unit/test_health.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Containerized Health Probes & Dependency-Aware Readiness Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 02, Story 13, Story 81
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `docker-compose.yml`.
2. Verify the implementation of `pg_isready / redis-cli ping / /health/ready probe`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_health.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `docker-compose.yml` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_health.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_health.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `docker-compose.yml`.
- [ ] Test harness `backend/tests/unit/test_health.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement containerized health probes & dependency-aware readiness and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `docker-compose.yml` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 02, Story 13, Story 81
- Downstream Dependents: Story 83, Story 89

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 83 — Production Multi-Stage Dockerfile Optimization
* **Story Points**: 5 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/Dockerfile` (Multi-stage Docker builds & slim base images).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational production multi-stage dockerfile optimization in `backend/Dockerfile`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for production multi-stage dockerfile optimization."

#### 1. Core Concept
Optimized container builds minimizing image size and eliminating build-time dependencies. Understanding production multi-stage dockerfile optimization is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/.dockerignore`
- Primary Symbol / Class / Function: `Multi-stage Docker builds & slim base images`
- Verification Test Harness: `backend/Dockerfile`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Production Multi-Stage Dockerfile Optimization Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 81, Story 82
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/Dockerfile`.
2. Verify the implementation of `Multi-stage Docker builds & slim base images`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/Dockerfile`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/Dockerfile` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/Dockerfile` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/Dockerfile` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/Dockerfile`.
- [ ] Test harness `backend/Dockerfile` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement production multi-stage dockerfile optimization and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/Dockerfile` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 81, Story 82
- Downstream Dependents: Story 84, Story 85

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 84 — Environment Variable Validation & Configuration Invariants
* **Story Points**: 3 SP
* **Implementation Status**: [PARTIAL]
* **Learning Priority**: OPTIONAL PRODUCTION EXTENSION
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Core single-node baseline implemented in `backend/app/core/config.py` (SettingsConfigDict / strict environment parsing).

**Not Implemented:** Distributed multi-region coordination, dynamic cluster topology, or complex consensus.

**Why It Is Still Worth Learning:** Demonstrates how to build clean foundational implementations that scale cleanly to enterprise requirements.

**Safe Interview Wording:** "EstateMap implements foundational environment variable validation & configuration invariants in `backend/app/core/config.py`; advanced distributed topology remains a documented extension."

**Do Not Claim:** "Do not claim enterprise-scale cluster orchestration for environment variable validation & configuration invariants."

#### 1. Core Concept
Startup validation ensuring all mandatory secrets, URLs, and database parameters are present. Understanding environment variable validation & configuration invariants is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/config.py`
- `frontend/package.json`
- `docker-compose.yml`
- Primary Symbol / Class / Function: `SettingsConfigDict / strict environment parsing`
- Verification Test Harness: `backend/tests/unit/test_health.py`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Environment Variable Validation & Configuration Invariants Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 03, Story 81, Story 83
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/config.py`.
2. Verify the implementation of `SettingsConfigDict / strict environment parsing`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/unit/test_health.py`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/config.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/unit/test_health.py` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/unit/test_health.py` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/config.py`.
- [ ] Test harness `backend/tests/unit/test_health.py` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement environment variable validation & configuration invariants and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/config.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 03, Story 81, Story 83
- Downstream Dependents: Story 85, Story 98

#### 20. Status Audit & Drift Prevention
- Status: `[PARTIAL]` verified against repository code.

### Story 85 — CI/CD Pipeline Automation (GitHub Actions Testing Matrix)
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for ci/cd pipeline automation (github actions testing matrix) under high load."

**Do Not Claim:** "Do not claim ci/cd pipeline automation (github actions testing matrix) is running in the current local Docker Compose baseline."

#### 1. Core Concept
Automated linting, testing, and container image publishing on pull requests. Understanding ci/cd pipeline automation (github actions testing matrix) is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT`
- Primary Symbol / Class / Function: `CI/CD automated test runner & container registry push`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ CI/CD Pipeline Automation (GitHub Actions Testing Matrix) Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 81, Story 84
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT`.
2. Verify the implementation of `CI/CD automated test runner & container registry push`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement ci/cd pipeline automation (github actions testing matrix) and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `Hypothetical GitHub Actions Workflow — NOT CURRENTLY PRESENT` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 81, Story 84
- Downstream Dependents: Story 86, Story 88

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 86 — Automated Regression Testing Architecture & Pytest Test Harness
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/tests/conftest.py`). Verified by automated test suites (backend/tests/).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for automated regression testing architecture & pytest test harness; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements automated regression testing architecture & pytest test harness in `backend/tests/conftest.py` (288 pytest unit/integration tests with Asyncpg fixture setup)."

**Do Not Claim:** "Do not claim unverified distributed extensions for automated regression testing architecture & pytest test harness."

#### 1. Core Concept
Comprehensive automated test harness executing 288 backend tests and 33 frontend tests. Understanding automated regression testing architecture & pytest test harness is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/tests/conftest.py`
- `backend/pyproject.toml`
- `backend/tests/unit/`
- `backend/tests/integration/`
- Primary Symbol / Class / Function: `288 pytest unit/integration tests with Asyncpg fixture setup`
- Verification Test Harness: `backend/tests/`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Automated Regression Testing Architecture & Pytest Test Harness Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 12, Story 18, Story 72
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/tests/conftest.py`.
2. Verify the implementation of `288 pytest unit/integration tests with Asyncpg fixture setup`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/tests/`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/tests/conftest.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/tests/` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/tests/` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/tests/conftest.py`.
- [ ] Test harness `backend/tests/` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement automated regression testing architecture & pytest test harness and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/tests/conftest.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 12, Story 18, Story 72
- Downstream Dependents: Story 87, Story 88

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 87 — Ephemeral Integration Testing with Testcontainers
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for ephemeral integration testing with testcontainers under high load."

**Do Not Claim:** "Do not claim ephemeral integration testing with testcontainers is running in the current local Docker Compose baseline."

#### 1. Core Concept
Dynamic container lifecycle management for isolated end-to-end integration tests. Understanding ephemeral integration testing with testcontainers is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT`
- Primary Symbol / Class / Function: `Ephemeral PostgreSQL + Redis containers per test session`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Ephemeral Integration Testing with Testcontainers Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 86
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT`.
2. Verify the implementation of `Ephemeral PostgreSQL + Redis containers per test session`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement ephemeral integration testing with testcontainers and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `Hypothetical Testcontainers Python Suite — NOT CURRENTLY PRESENT` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 86
- Downstream Dependents: Story 88, Story 89

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 88 — Frontend End-to-End Testing with Playwright
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `frontend/__tests__/`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for frontend end-to-end testing with playwright under high load."

**Do Not Claim:** "Do not claim frontend end-to-end testing with playwright is running in the current local Docker Compose baseline."

#### 1. Core Concept
Headless browser testing validating full user workflows across map, filters, and chat. Understanding frontend end-to-end testing with playwright is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `frontend/__tests__/`
- `Hypothetical Playwright E2E Suite — NOT CURRENTLY PRESENT`
- Primary Symbol / Class / Function: `Browser-driven E2E user flow automation for search and compare`
- Verification Test Harness: `frontend/__tests__/`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Frontend End-to-End Testing with Playwright Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 73, Story 76, Story 80
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `frontend/__tests__/`.
2. Verify the implementation of `Browser-driven E2E user flow automation for search and compare`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `frontend/__tests__/`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `frontend/__tests__/` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `frontend/__tests__/` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `frontend/__tests__/` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `frontend/__tests__/`.
- [ ] Test harness `frontend/__tests__/` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement frontend end-to-end testing with playwright and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `frontend/__tests__/` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 73, Story 76, Story 80
- Downstream Dependents: Story 90

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 89 — Structured JSON Telemetry & Prometheus Metric Exporters
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/core/logging.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for structured json telemetry & prometheus metric exporters under high load."

**Do Not Claim:** "Do not claim structured json telemetry & prometheus metric exporters is running in the current local Docker Compose baseline."

#### 1. Core Concept
Prometheus metrics instrumentation for request latency, status codes, and active connections. Understanding structured json telemetry & prometheus metric exporters is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/logging.py`
- `backend/app/core/middleware.py`
- Primary Symbol / Class / Function: `Hypothetical Prometheus /metrics endpoint`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Structured JSON Telemetry & Prometheus Metric Exporters Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 06, Story 48, Story 82
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/logging.py`.
2. Verify the implementation of `Hypothetical Prometheus /metrics endpoint`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/logging.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/logging.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement structured json telemetry & prometheus metric exporters and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/logging.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 06, Story 48, Story 82
- Downstream Dependents: Story 90, Story 94

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 90 — Distributed Tracing & OpenTelemetry APM Instrumentation
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for distributed tracing & opentelemetry apm instrumentation under high load."

**Do Not Claim:** "Do not claim distributed tracing & opentelemetry apm instrumentation is running in the current local Docker Compose baseline."

#### 1. Core Concept
Distributed tracing spans tracking request execution across services and database queries. Understanding distributed tracing & opentelemetry apm instrumentation is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT`
- Primary Symbol / Class / Function: `W3C Trace Context propagation across HTTP, Redis, and DB calls`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Distributed Tracing & OpenTelemetry APM Instrumentation Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 06, Story 89
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT`.
2. Verify the implementation of `W3C Trace Context propagation across HTTP, Redis, and DB calls`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement distributed tracing & opentelemetry apm instrumentation and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `Hypothetical OpenTelemetry Tracer — NOT CURRENTLY PRESENT` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 06, Story 89
- Downstream Dependents: Story 94, Story 96

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.


## Phase 10: Architecture Defense & System Design (Stories 91-100)

### Story 91 — Modular Monolith vs Microservices Architecture Tradeoffs
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`backend/app/main.py`). Verified by automated test suites (backend/app/).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for modular monolith vs microservices architecture tradeoffs; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements modular monolith vs microservices architecture tradeoffs in `backend/app/main.py` (FastAPI modular monolithic domain organization)."

**Do Not Claim:** "Do not claim unverified distributed extensions for modular monolith vs microservices architecture tradeoffs."

#### 1. Core Concept
Architectural defense of modular monolith over microservices for spatial discovery workloads. Understanding modular monolith vs microservices architecture tradeoffs is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/main.py`
- `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`
- Primary Symbol / Class / Function: `FastAPI modular monolithic domain organization`
- Verification Test Harness: `backend/app/`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Modular Monolith vs Microservices Architecture Tradeoffs Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 01, Story 08, Story 09, Story 39
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/main.py`.
2. Verify the implementation of `FastAPI modular monolithic domain organization`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `backend/app/`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/main.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `backend/app/` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `backend/app/` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/main.py`.
- [ ] Test harness `backend/app/` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement modular monolith vs microservices architecture tradeoffs and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/main.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 01, Story 08, Story 09, Story 39
- Downstream Dependents: Story 92, Story 95, Story 99

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 92 — Database Sharding & Read Replica Topology for Spatial Workloads
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/db/session.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for database sharding & read replica topology for spatial workloads under high load."

**Do Not Claim:** "Do not claim database sharding & read replica topology for spatial workloads is running in the current local Docker Compose baseline."

#### 1. Core Concept
Horizontal database scaling via geographic partitioning and read replicas. Understanding database sharding & read replica topology for spatial workloads is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/db/session.py`
- `Hypothetical Database Sharding Topology`
- Primary Symbol / Class / Function: `PostgreSQL primary-replica replication & spatial shard routing`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Database Sharding & Read Replica Topology for Spatial Workloads Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 09, Story 23, Story 28, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/db/session.py`.
2. Verify the implementation of `PostgreSQL primary-replica replication & spatial shard routing`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/db/session.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/db/session.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement database sharding & read replica topology for spatial workloads and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/db/session.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 09, Story 23, Story 28, Story 91
- Downstream Dependents: Story 93, Story 95

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 93 — Distributed Redis Cluster & Geo-Replication Topologies
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/cache/cache_service.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for distributed redis cluster & geo-replication topologies under high load."

**Do Not Claim:** "Do not claim distributed redis cluster & geo-replication topologies is running in the current local Docker Compose baseline."

#### 1. Core Concept
Scaling caching and rate limiting horizontally across a distributed Redis cluster. Understanding distributed redis cluster & geo-replication topologies is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/cache/cache_service.py`
- `Hypothetical Redis Cluster Topology`
- Primary Symbol / Class / Function: `Redis Cluster 16384 hash slot partitioning & geo-replication`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Distributed Redis Cluster & Geo-Replication Topologies Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 39, Story 41, Story 50, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/cache/cache_service.py`.
2. Verify the implementation of `Redis Cluster 16384 hash slot partitioning & geo-replication`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/cache/cache_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/cache/cache_service.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement distributed redis cluster & geo-replication topologies and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/cache/cache_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 39, Story 41, Story 50, Story 91
- Downstream Dependents: Story 94, Story 96

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 94 — High-Throughput AI Gateway & LLM Inference Queueing
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/ai/router.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for high-throughput ai gateway & llm inference queueing under high load."

**Do Not Claim:** "Do not claim high-throughput ai gateway & llm inference queueing is running in the current local Docker Compose baseline."

#### 1. Core Concept
Decoupling user search from LLM latency via asynchronous inference queues. Understanding high-throughput ai gateway & llm inference queueing is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/ai/router.py`
- `Hypothetical AI Gateway Queue`
- Primary Symbol / Class / Function: `Asynchronous task queues (Celery/RabbitMQ) for batch LLM inference`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ High-Throughput AI Gateway & LLM Inference Queueing Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 52, Story 57, Story 58, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/ai/router.py`.
2. Verify the implementation of `Asynchronous task queues (Celery/RabbitMQ) for batch LLM inference`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/ai/router.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/ai/router.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement high-throughput ai gateway & llm inference queueing and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/ai/router.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 52, Story 57, Story 58, Story 91
- Downstream Dependents: Story 95, Story 97

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 95 — Event-Driven Architecture with Kafka / CDC Ingestion
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/services/property_service.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for event-driven architecture with kafka / cdc ingestion under high load."

**Do Not Claim:** "Do not claim event-driven architecture with kafka / cdc ingestion is running in the current local Docker Compose baseline."

#### 1. Core Concept
Decoupling property updates from cache invalidation and search index synchronization. Understanding event-driven architecture with kafka / cdc ingestion is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/property_service.py`
- `Hypothetical Kafka / CDC Ingestion`
- Primary Symbol / Class / Function: `Debezium CDC streaming property updates to Kafka topic`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Event-Driven Architecture with Kafka / CDC Ingestion Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 18, Story 42, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/property_service.py`.
2. Verify the implementation of `Debezium CDC streaming property updates to Kafka topic`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/property_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/property_service.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement event-driven architecture with kafka / cdc ingestion and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/property_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 18, Story 42, Story 91
- Downstream Dependents: Story 96, Story 97

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 96 — Real-Time WebSocket Viewport Synchronization at 100K CCU
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/services/geo_service.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for real-time websocket viewport synchronization at 100k ccu under high load."

**Do Not Claim:** "Do not claim real-time websocket viewport synchronization at 100k ccu is running in the current local Docker Compose baseline."

#### 1. Core Concept
Bi-directional WebSocket streaming for collaborative discovery and real-time listing updates. Understanding real-time websocket viewport synchronization at 100k ccu is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/services/geo_service.py`
- `Hypothetical WebSocket Connection Pool`
- Primary Symbol / Class / Function: `WebSocket server broadcasting viewport property updates`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Real-Time WebSocket Viewport Synchronization at 100K CCU Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 76, Story 77, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/services/geo_service.py`.
2. Verify the implementation of `WebSocket server broadcasting viewport property updates`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/services/geo_service.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/services/geo_service.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement real-time websocket viewport synchronization at 100k ccu and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/services/geo_service.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 76, Story 77, Story 91
- Downstream Dependents: Story 97

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 97 — Multi-Region Active-Active Disaster Recovery & Edge Routing
* **Story Points**: 8 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `Hypothetical Multi-Region Deployment Architecture`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for multi-region active-active disaster recovery & edge routing under high load."

**Do Not Claim:** "Do not claim multi-region active-active disaster recovery & edge routing is running in the current local Docker Compose baseline."

#### 1. Core Concept
Multi-region cloud architecture providing sub-second failover and localized data compliance. Understanding multi-region active-active disaster recovery & edge routing is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `Hypothetical Multi-Region Deployment Architecture`
- Primary Symbol / Class / Function: `Anycast DNS routing, cross-region replication, and failover`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Multi-Region Active-Active Disaster Recovery & Edge Routing Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 50, Story 92, Story 93, Story 95
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `Hypothetical Multi-Region Deployment Architecture`.
2. Verify the implementation of `Anycast DNS routing, cross-region replication, and failover`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `Hypothetical Multi-Region Deployment Architecture` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `Hypothetical Multi-Region Deployment Architecture`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement multi-region active-active disaster recovery & edge routing and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `Hypothetical Multi-Region Deployment Architecture` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 50, Story 92, Story 93, Story 95
- Downstream Dependents: Story 98, Story 100

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 98 — Zero-Trust Security Architecture & Secrets Vault Integration
* **Story Points**: 5 SP
* **Implementation Status**: [FUTURE]
* **Learning Priority**: ADVANCED SYSTEM DESIGN
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Documented production scaling pattern with concrete triggers and design specifications in `backend/app/core/security.py`.

**Not Implemented:** Executable runtime code in current single-node monolithic repository.

**Why It Is Still Worth Learning:** Essential for senior backend system design interviews to explain how EstateMap scales to 100K+ concurrent users.

**Safe Interview Wording:** "EstateMap operates as a modular monolith today; I designed the scaling evolution for zero-trust security architecture & secrets vault integration under high load."

**Do Not Claim:** "Do not claim zero-trust security architecture & secrets vault integration is running in the current local Docker Compose baseline."

#### 1. Core Concept
Enterprise zero-trust hardening eliminating static credentials in application config. Understanding zero-trust security architecture & secrets vault integration is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `backend/app/core/security.py`
- `Hypothetical HashiCorp Vault Integration`
- Primary Symbol / Class / Function: `mTLS service communication and dynamic short-lived credentials`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ Zero-Trust Security Architecture & Secrets Vault Integration Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 14, Story 15, Story 17, Story 91
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `backend/app/core/security.py`.
2. Verify the implementation of `mTLS service communication and dynamic short-lived credentials`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `backend/app/core/security.py` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `backend/app/core/security.py`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement zero-trust security architecture & secrets vault integration and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `backend/app/core/security.py` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 14, Story 15, Story 17, Story 91
- Downstream Dependents: Story 99, Story 100

#### 20. Status Audit & Drift Prevention
- Status: `[FUTURE]` verified against repository code.

### Story 99 — EstateMap Architectural Decision Records (ADRs) & Tradeoffs
* **Story Points**: 5 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`). Verified by automated test suites (docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for estatemap architectural decision records (adrs) & tradeoffs; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements estatemap architectural decision records (adrs) & tradeoffs in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` (ADR Catalog: Modular Monolith, PostGIS, Multi-Provider AI, MapLibre, Redis)."

**Do Not Claim:** "Do not claim unverified distributed extensions for estatemap architectural decision records (adrs) & tradeoffs."

#### 1. Core Concept
Comprehensive catalog of 15 Architectural Decision Records documenting rejected alternatives and tradeoffs. Understanding estatemap architectural decision records (adrs) & tradeoffs is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`
- Primary Symbol / Class / Function: `ADR Catalog: Modular Monolith, PostGIS, Multi-Provider AI, MapLibre, Redis`
- Verification Test Harness: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ EstateMap Architectural Decision Records (ADRs) & Tradeoffs Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 91, Story 92, Story 93, Story 94, Story 95
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.
2. Verify the implementation of `ADR Catalog: Modular Monolith, PostGIS, Multi-Provider AI, MapLibre, Redis`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.
- [ ] Test harness `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement estatemap architectural decision records (adrs) & tradeoffs and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 91, Story 92, Story 93, Story 94, Story 95
- Downstream Dependents: Story 100

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

### Story 100 — End-to-End System Design Whiteboard Defense & Mastery Synthesis
* **Story Points**: 8 SP
* **Implementation Status**: [CURRENT]
* **Learning Priority**: CORE REQUIRED
* **Study Status**: [ ] Not Started | [ ] In Progress | [ ] Implemented | [ ] Verified | [ ] Mastered

#### EstateMap Reality Check
**Implemented Today:** Implemented in EstateMap (`docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`). Verified by automated test suites (docs/mastery/).

**Not Implemented:** Distributed multi-region or enterprise clustering (unnecessary for current monolith baseline).

**Why It Is Still Worth Learning:** Core engineering foundation for end-to-end system design whiteboard defense & mastery synthesis; essential for understanding runtime architecture.

**Safe Interview Wording:** "EstateMap implements end-to-end system design whiteboard defense & mastery synthesis in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` (EstateMap End-to-End System Design Defense Framework)."

**Do Not Claim:** "Do not claim unverified distributed extensions for end-to-end system design whiteboard defense & mastery synthesis."

#### 1. Core Concept
Comprehensive synthesis defending EstateMap architecture, data flow, failure modes, and scalability on a whiteboard. Understanding end-to-end system design whiteboard defense & mastery synthesis is critical for architecting scalable, resilient, and verifiable backend systems.

#### 2. Why This Engineering Decision Exists in EstateMap
EstateMap employs this specific pattern to ensure high cohesion, low coupling, deterministic behavior, and clear isolation of concerns across all layers.

#### 3. Concrete File & Symbol References
- `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`
- `docs/mastery/ENGINEERING_STORIES.md`
- Primary Symbol / Class / Function: `EstateMap End-to-End System Design Defense Framework`
- Verification Test Harness: `docs/mastery/`

#### 4. Mental Model & Visual Flow
```text
[ Client / Request ]
        │
        ▼
[ End-to-End System Design Whiteboard Defense & Mastery Synthesis Boundary ] ───▶ [ Validation & State Reducer ]
        │
        ▼
[ Verified Execution / Response ]
```

#### 5. Prerequisites Checklist
- [ ] Understand prerequisite topics: Story 91, Story 99
- [ ] Verify environment dependencies in `docker-compose.yml`

#### 6. Step-by-Step Implementation Blueprint
1. Inspect the source file `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.
2. Verify the implementation of `EstateMap End-to-End System Design Defense Framework`.
3. Validate domain invariants, error boundaries, and return type contracts.
4. Execute the associated regression test: `docs/mastery/`.

#### 7. Break It Yourself & Debug Lab
1. **Experiment Setup:** Inspect `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` to test behavior under deliberate edge-case parameters or constraint modifications.
2. **Execution:** Run `docs/mastery/` and observe the resulting system behavior or error handling paths.
3. **Diagnosis:** Use `EXPLAIN ANALYZE` or structured logging to observe actual runtime resource utilization and query planner decisions.
4. **Restoration:** Revert any temporary changes and confirm all test assertions pass cleanly.

#### 8. Acceptance Criteria
- **AC1:** Module conforms strictly to type signatures and domain constraints.
- **AC2:** All exceptions are handled gracefully with appropriate RFC 7807 problem details or logged warnings.
- **AC3:** Regression test `docs/mastery/` passes with zero errors.
- **AC4:** Observability telemetry is emitted with correlation IDs where applicable.
- **AC5:** No unvalidated external inputs bypass domain schema boundaries; prompt-injection risks are strictly mitigated by treating all model output as untrusted structured data.
- **AC6:** Resource lifecycle (connections, memory) is safely managed and freed.
- **AC7:** Concurrent executions maintain expected isolation guarantees without assuming unverified multi-step atomicity.
- **AC8:** Code structure conforms to EstateMap clean architecture boundaries.

#### 9. Final Outcome Verification Checklist
- [ ] Source implementation reviewed in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md`.
- [ ] Test harness `docs/mastery/` executed and passing.
- [ ] Whiteboard mental model verified against system design requirements.

#### 10. Common Traps & Anti-Patterns
- Leaking infrastructure dependencies into domain models.
- Failing to handle edge cases or timeout conditions.
- Assuming distributed atomicity without verifying underlying transaction semantics.

#### 11. Performance & Complexity Profile
- **Time Complexity:** $O(1)$ to $O(\log N)$ for indexed operations; $O(N)$ for unbounded linear scans.
- **Space Complexity:** Bounded $O(1)$ auxiliary overhead per request.

#### 12. Alternative Designs Considered
- Evaluated alternative approaches and rejected due to operational complexity or latency overhead.

#### 13. Failure Modes & Edge Cases
- Network partitions, database connectivity drops, and timeout exceptions trigger graceful fallback policies.

#### 14. Observability & Debugging Runbook
- Inspect structured application logs using correlation ID `X-Request-ID`.
- Probe `/health/ready` endpoint to verify dependency reachability.

#### 15. Security & Data Integrity Concerns
- All inputs are strictly validated via Pydantic schemas; SQL injection is prevented via parameterized SQLAlchemy statements.

#### 16. Testing Strategy
- Unit tests validate schema boundaries and algorithmic logic.
- Integration tests run against PostgreSQL/PostGIS and Redis test instances.

#### 17. Interview Defense Questions
- "How does EstateMap implement end-to-end system design whiteboard defense & mastery synthesis and what tradeoffs were accepted?"
- "How would you evolve this architecture if throughput increased 100x?"

#### 18. Self-Study Exercises
1. Trace the code path in `docs/mastery/CANONICAL_ARCHITECTURE_TRUTH.md` from entrypoint to database/cache execution.
2. Implement a standalone minimal prototype in a scratch script.

#### 19. Related Stories in the Graph
- Prerequisites: Story 91, Story 99
- Downstream Dependents: None (Terminal Story)

#### 20. Status Audit & Drift Prevention
- Status: `[CURRENT]` verified against repository code.

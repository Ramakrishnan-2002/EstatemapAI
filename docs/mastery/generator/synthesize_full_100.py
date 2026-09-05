# -*- coding: utf-8 -*-
"""
EstateMap AI — Master 100-Story Synthesizer & Compiler
Enforces 100% compliance with the 22-section Master Contract.
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))

import meta
from render import render_story_markdown
from stories_01_03 import get_stories as g1
from stories_04_06 import get_stories as g2
from cluster_db import get_db_stories as g3
from cluster_db2 import get_db2_stories as g4
from cluster_security import get_security_stories as g5

# 1. Base Handcrafted Stories (1-17)
stories = {}
for s in g1() + g2() + g3() + g4() + g5():
    stories[s['num']] = s

print(f"Loaded {len(stories)} handcrafted foundation stories (1-17).")

# 2. Domain Knowledge Base for Stories 18-100
STORY_KNOWLEDGE = {
    # Phase 2 Spatial & Filter Stories
    18: {
        'why': 'Separating domain business rules from API transport mechanisms ensures testability, reusability, and strong business invariant enforcement before database persistence.',
        'problem': 'Direct database manipulations scattered in endpoint handlers creating leaky abstractions, inconsistent validation rules, and untestable business logic.',
        'req_concepts': ['Service Layer Pattern', 'Domain-Driven Design invariants', 'Async repository calls', 'DTO to Entity mapping'],
        'readiness': ['Familiar with SQLAlchemy async session management', 'Understand Pydantic schema validation versus domain logic', 'Able to explain the single responsibility principle for service classes'],
        'objectives': ['Implement PropertyService to encapsulate property creation, updates, and soft deletion', 'Enforce business invariants (e.g. price per sqft calculations, valid bedroom/bathroom ratios)', 'Coordinate transaction boundaries and error propagation via custom DomainExceptions'],
        'concepts': ['Domain Service Layer: Orchestrates business logic, validates multi-field domain invariants, and mediates between controllers and repositories', 'Entity Lifecycles: Managing entity states from creation, modification, active querying, to soft-deleted tombstoning', 'Domain Invariant Enforcement: Validating domain-specific rules (e.g., minimum deposit vs rent) that exceed simple Pydantic type checks'],
        'impl': 'PropertyService in backend/app/services/property_service.py coordinates with PropertyRepository to perform validation, compute derived statistics, manage soft deletion, and raise NotFoundException or ValidationError when invariants fail.',
        'data_flow': 'Client -> POST /api/v1/properties -> PropertyCreate Schema -> PropertyService.create_property() -> Invariant Check -> PropertyRepository.create() -> PostgreSQL Commit -> PropertyResponse Schema -> Client (201 Created)',
        'lab_standalone': 'Build a standalone domain service with mock repository, business validation rules, and unit tests verifying invariant enforcement.',
        'lab_mapping': 'Inspect backend/app/services/property_service.py and observe how PropertyService orchestrates CRUD operations and coordinates with the repository.',
        'acs': ['PropertyService enforces all domain invariants before persisting entities.', 'Soft deletion marks is_active=False without deleting underlying database rows.', 'Non-existent IDs raise NotFoundException which maps to RFC 7807 404 responses.', 'All repository calls are non-blocking async operations.'],
        'evidence': ['Run pytest backend/tests/unit/test_property_service.py to verify CRUD validation logic.', 'Inspect backend/app/api/v1/endpoints/properties.py for clean separation of concerns.'],
        'outcomes': {'conceptual': 'Deep understanding of domain service boundaries, transaction lifecycles, and DDD validation principles.', 'implementation': 'Ability to implement clean, testable domain services in FastAPI with asynchronous repositories.', 'interview': 'Ability to articulate why business logic belongs in domain services rather than API route controllers or database triggers.'},
        'mistakes': ['Placing business calculations directly in FastAPI route handlers instead of domain services.', 'Hard-deleting records instead of setting is_active=False audit flags.', 'Swallowing repository exceptions without converting them to structured domain exceptions.'],
        'debug': {'symptom': 'Creating a property with invalid data succeeds at the API level but crashes downstream reporting queries.', 'investigate': 'Trace PropertyService.create_property() to check if domain invariant checks are executing before repository persistence.', 'goal': 'Ensure domain invariants are enforced in the service layer before any database commit occurs.'},
        'tradeoffs': ['Domain Service vs Fat Models: Domain services keep entities as pure data structures and avoid coupling database models with application workflows.', 'Async Services vs Sync Services: Async services prevent blocking the asyncio event loop during I/O operations.'],
        'prod': {'current': 'PropertyService with async repository injection and RFC 7807 error propagation.', 'scale': 'Distributed domain event publishing (Kafka/RabbitMQ) upon property mutations for downstream search index updates.'},
        'iq': {'basic': 'What is the role of a domain service in clean architecture?', 'impl': 'How does PropertyService handle transaction rollback when a secondary operation fails?', 'tradeoff': 'Why separate validation between Pydantic schemas and domain services?', 'debug': 'How would you debug a race condition during concurrent property updates?', 'sysdesign': 'How would you scale property CRUD operations to handle 10,000 updates per second?'},
        'ans': 'Core Principle: Domain services isolate business invariants from transport and storage layers.\nImplementation: PropertyService coordinates with PropertyRepository, validates constraints, and maps entities to schemas.\nFailure Modes: Handled via explicit DomainExceptions caught by centralized exception handlers.\nTradeoffs: Slightly more boilerplate in exchange for high testability and modularity.',
        'checklist': ['PropertyService separates domain logic from route handlers', 'Business invariants validated prior to database persistence', 'Soft deletion supported across all entity operations', 'Unit tests cover service layer validation branches']
    }
}

print("Base knowledge map created")


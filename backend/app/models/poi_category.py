"""
POI Category vocabulary for EstateMap AI.

Design decision: Python StrEnum rather than a database table.
A DB table would be appropriate if:
  - categories are user-managed at runtime
  - categories change frequently
  - categories carry rich metadata (icons, descriptions, translations)

At the current project stage none of those requirements exist.
StrEnum provides:
  - compile-time validation in Python
  - automatic OpenAPI enum values for API consumers
  - consistent serialization (string values) in Pydantic
  - easy frontend type generation

If categories need to become dynamic in a future phase, migrate
to a `poi_categories` table and replace this enum with a FK
reference.

Included categories — chosen because each has clear real-estate
relevance and can be demonstrated with deterministic seed data:
  hospital    — healthcare access, important for families and elderly
  school      — education proximity, strong influence on residential value
  transit     — metro/bus stops, commute feasibility indicator
  supermarket — daily convenience, walkability signal
  park        — green space, lifestyle quality indicator
  pharmacy    — healthcare adjacency, companion to hospital category
  bank        — financial services access
"""

from enum import StrEnum


class POICategory(StrEnum):
    """Controlled vocabulary for Point of Interest categories."""

    HOSPITAL = "hospital"
    SCHOOL = "school"
    TRANSIT = "transit"
    SUPERMARKET = "supermarket"
    PARK = "park"
    PHARMACY = "pharmacy"
    BANK = "bank"

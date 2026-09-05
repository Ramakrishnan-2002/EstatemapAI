"""
SQLAlchemy ORM model for Points of Interest (POIs).

Each POI represents a geographic place relevant to real-estate decisions.
The canonical geographic representation is a PostGIS GEOMETRY(POINT, 4326)
column — latitude and longitude scalar columns are NOT stored because
the PostGIS point is the single source of geographic truth.

Spatial index
─────────────
A GiST index on `location` enables:
  - ST_DWithin(poi.location::geography, origin::geography, radius_m)
  - ST_Distance(poi.location::geography, origin::geography)

without sequential scans. The index is created in the Alembic migration
(migration 0004) rather than relying on SQLAlchemy auto-index to keep
migration files fully authoritative.

Relationship to Property
────────────────────────
There is no foreign-key relationship between `pois` and `properties`.
Geographic proximity is computed dynamically via PostGIS. Storing
persistent property↔POI associations would introduce stale-data risk
whenever POI coordinates are corrected.

is_active lifecycle
───────────────────
`is_active=True` marks the POI as part of the live dataset.
Setting `is_active=False` logically deactivates a POI without
destroying historical records. All search endpoints filter to
active POIs by default.
"""

from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.poi_category import POICategory


class PointOfInterest(Base):
    """
    SQLAlchemy Point of Interest model.
    Stores geographic places relevant to property location intelligence.
    """

    __tablename__ = "pois"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core identity
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Category is stored as a VARCHAR constrained to POICategory values.
    # Using a CheckConstraint in the migration provides DB-level integrity
    # without the overhead of a separate category table.
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Optional subdivision within a category (e.g. "government", "private" for hospitals)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # PostGIS canonical location (WGS84 / SRID 4326).
    # GiST index defined in __table_args__ and Alembic migration.
    location = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
        nullable=False,
    )

    # Address information
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    locality: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Lifecycle flag — inactive POIs are excluded from search by default
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

    # Spatial GiST index — must match migration index name
    __table_args__ = (
        Index(
            "idx_pois_location_gist",
            "location",
            postgresql_using="gist",
        ),
        Index("ix_pois_category_active", "category", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<PointOfInterest id={self.id} name={self.name!r} category={self.category}>"

    @property
    def category_enum(self) -> POICategory | None:
        """Return the category as a typed POICategory enum value."""
        try:
            return POICategory(self.category)
        except ValueError:
            return None

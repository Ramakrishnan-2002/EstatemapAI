"""Create pois table with PostGIS spatial index

Revision ID: 0004_create_pois
Revises: 0003_create_properties
Create Date: 2026-09-04 17:20:00.000000

POI table design notes:
- `location` uses GEOMETRY(POINT, 4326) — same SRID convention as `properties.location`.
- GiST spatial index (idx_pois_location_gist) enables efficient ST_DWithin / ST_Distance
  queries without sequential scans. Write/storage cost is acceptable for a dataset of
  millions of POIs; far more critical at tens of millions (clustering strategies needed then).
- Composite B-tree index (ix_pois_category_active) covers the most common filtered query
  pattern: WHERE category = ? AND is_active = true, then spatial filtering narrows further.
- CHECK constraint on `category` enforces DB-level integrity matching POICategory enum.
- No FK to `properties` — distances are computed dynamically.
"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_create_pois"
down_revision: str | None = "0003_create_properties"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Allowed category values — must stay in sync with POICategory enum
VALID_CATEGORIES = (
    "hospital",
    "school",
    "transit",
    "supermarket",
    "park",
    "pharmacy",
    "bank",
)


def upgrade() -> None:
    # Create pois table
    op.create_table(
        "pois",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=True),
        # PostGIS Point — WGS84 / SRID 4326
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("locality", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        # DB-level category integrity
        sa.CheckConstraint(
            f"category IN ({', '.join(repr(c) for c in VALID_CATEGORIES)})",
            name="chk_pois_valid_category",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Standard B-tree indexes
    op.create_index(op.f("ix_pois_name"), "pois", ["name"], unique=False)
    op.create_index(op.f("ix_pois_city"), "pois", ["city"], unique=False)
    op.create_index(op.f("ix_pois_locality"), "pois", ["locality"], unique=False)
    op.create_index(op.f("ix_pois_category"), "pois", ["category"], unique=False)
    op.create_index(op.f("ix_pois_is_active"), "pois", ["is_active"], unique=False)

    # Composite index for the most common filtered query:
    # WHERE category = ? AND is_active = true
    op.create_index(
        "ix_pois_category_active",
        "pois",
        ["category", "is_active"],
        unique=False,
    )

    # GiST spatial index on location
    # Enables: ST_DWithin(pois.location::geography, ..., radius_m) with index scan
    # Query patterns: nearby POI search, property proximity, bbox map queries
    # Write cost: slightly slower INSERT/UPDATE on pois (acceptable for infrequent writes)
    # Storage: ~50-100 bytes per entry overhead (acceptable)
    op.create_index(
        "idx_pois_location_gist",
        "pois",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("idx_pois_location_gist", table_name="pois", postgresql_using="gist")
    op.drop_index("ix_pois_category_active", table_name="pois")
    op.drop_index(op.f("ix_pois_is_active"), table_name="pois")
    op.drop_index(op.f("ix_pois_category"), table_name="pois")
    op.drop_index(op.f("ix_pois_locality"), table_name="pois")
    op.drop_index(op.f("ix_pois_city"), table_name="pois")
    op.drop_index(op.f("ix_pois_name"), table_name="pois")
    op.drop_table("pois")

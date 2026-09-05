"""create properties amenities and images tables

Revision ID: 0003_create_properties
Revises: 0002_create_users_table
Create Date: 2026-09-04 15:35:00.000000

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_create_properties"
down_revision: str | None = "0002_create_users_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create amenities table
    op.create_table(
        "amenities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_amenities_name"), "amenities", ["name"], unique=True)

    # 2. Create properties table with PostGIS Geometry column and constraints
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("property_type", sa.String(length=50), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=True),
        sa.Column("bathrooms", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("area_sqft", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("locality", sa.String(length=100), nullable=False),
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
        sa.Column(
            "status",
            sa.String(length=30),
            server_default="active",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("price >= 0", name="chk_properties_price_positive"),
        sa.CheckConstraint("area_sqft > 0", name="chk_properties_area_positive"),
        sa.CheckConstraint(
            "bedrooms IS NULL OR bedrooms >= 0",
            name="chk_properties_bedrooms_non_negative",
        ),
        sa.CheckConstraint(
            "bathrooms IS NULL OR bathrooms >= 0",
            name="chk_properties_bathrooms_non_negative",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_properties_owner_id"), "properties", ["owner_id"], unique=False)
    op.create_index(op.f("ix_properties_price"), "properties", ["price"], unique=False)
    op.create_index(
        op.f("ix_properties_property_type"), "properties", ["property_type"], unique=False
    )
    op.create_index(op.f("ix_properties_bedrooms"), "properties", ["bedrooms"], unique=False)
    op.create_index(op.f("ix_properties_city"), "properties", ["city"], unique=False)
    op.create_index(op.f("ix_properties_locality"), "properties", ["locality"], unique=False)
    op.create_index(op.f("ix_properties_status"), "properties", ["status"], unique=False)
    op.create_index(op.f("ix_properties_created_at"), "properties", ["created_at"], unique=False)
    op.create_index("ix_properties_city_locality", "properties", ["city", "locality"], unique=False)
    op.create_index(
        "ix_properties_status_created", "properties", ["status", "created_at"], unique=False
    )

    # Spatial GiST index on location
    op.create_index(
        "idx_properties_location_gist",
        "properties",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )

    # 3. Create property_amenities junction table
    op.create_table(
        "property_amenities",
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("amenity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["amenity_id"], ["amenities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("property_id", "amenity_id"),
    )

    # 4. Create property_images table
    op.create_table(
        "property_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=False),
        sa.Column("display_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_property_images_property_id"),
        "property_images",
        ["property_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_property_images_property_id"), table_name="property_images")
    op.drop_table("property_images")
    op.drop_table("property_amenities")
    op.drop_index("idx_properties_location_gist", table_name="properties", postgresql_using="gist")
    op.drop_index("ix_properties_status_created", table_name="properties")
    op.drop_index("ix_properties_city_locality", table_name="properties")
    op.drop_index(op.f("ix_properties_created_at"), table_name="properties")
    op.drop_index(op.f("ix_properties_status"), table_name="properties")
    op.drop_index(op.f("ix_properties_locality"), table_name="properties")
    op.drop_index(op.f("ix_properties_city"), table_name="properties")
    op.drop_index(op.f("ix_properties_bedrooms"), table_name="properties")
    op.drop_index(op.f("ix_properties_property_type"), table_name="properties")
    op.drop_index(op.f("ix_properties_price"), table_name="properties")
    op.drop_index(op.f("ix_properties_owner_id"), table_name="properties")
    op.drop_table("properties")
    op.drop_index(op.f("ix_amenities_name"), table_name="amenities")
    op.drop_table("amenities")

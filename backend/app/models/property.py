from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.amenity import property_amenities

if TYPE_CHECKING:
    from app.models.amenity import Amenity
    from app.models.property_image import PropertyImage
    from app.models.user import User


class Property(Base):
    """
    SQLAlchemy Property model representing real estate listings in EstateMap AI.
    Contains canonical PostGIS POINT location with spatial indexing.
    """

    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, index=True)
    property_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # e.g., apartment, villa, independent_house, plot, commercial
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    bathrooms: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    area_sqft: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    locality: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # PostGIS Canonical Spatial Location (WGS84 / SRID 4326)
    location = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30), default="active", nullable=False, index=True
    )  # active, inactive, sold, rented, draft

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="properties")
    images: Mapped[list["PropertyImage"]] = relationship(
        "PropertyImage",
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImage.display_order",
        lazy="selectin",
    )
    amenities: Mapped[list["Amenity"]] = relationship(
        "Amenity",
        secondary=property_amenities,
        back_populates="properties",
        lazy="selectin",
    )

    # Constraints & Indexes
    __table_args__ = (
        CheckConstraint("price >= 0", name="chk_properties_price_positive"),
        CheckConstraint("area_sqft > 0", name="chk_properties_area_positive"),
        CheckConstraint(
            "bedrooms IS NULL OR bedrooms >= 0", name="chk_properties_bedrooms_non_negative"
        ),
        CheckConstraint(
            "bathrooms IS NULL OR bathrooms >= 0", name="chk_properties_bathrooms_non_negative"
        ),
        Index("ix_properties_city_locality", "city", "locality"),
        Index("ix_properties_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Property id={self.id} title={self.title} price={self.price} city={self.city}>"

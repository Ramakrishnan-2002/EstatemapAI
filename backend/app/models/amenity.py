from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.property import Property

# Association Table for Property <-> Amenity many-to-many relationship
property_amenities = Table(
    "property_amenities",
    Base.metadata,
    Column(
        "property_id",
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "amenity_id",
        Integer,
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class Amenity(Base):
    """
    SQLAlchemy Amenity model representing property features (e.g., Lift, Swimming Pool, 24/7 Security).
    """

    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # e.g., security, leisure, basic
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Many-to-many relationship with Property
    properties: Mapped[list["Property"]] = relationship(
        "Property",
        secondary=property_amenities,
        back_populates="amenities",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Amenity id={self.id} name={self.name} category={self.category}>"

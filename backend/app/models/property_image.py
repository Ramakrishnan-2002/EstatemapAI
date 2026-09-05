from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.property import Property


class PropertyImage(Base):
    """
    SQLAlchemy PropertyImage model representing URLs of property photos/media.
    """

    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("properties.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Many-to-one relationship back to Property
    property: Mapped["Property"] = relationship("Property", back_populates="images")

    def __repr__(self) -> str:
        return f"<PropertyImage id={self.id} property_id={self.property_id} order={self.display_order}>"

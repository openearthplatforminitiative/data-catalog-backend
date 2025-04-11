import uuid
from typing import List

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for category"
    )
    title: Mapped[str] = mapped_column(String, nullable=True, doc="title")
    abstract: Mapped[str] = mapped_column(String, nullable=True, doc="abstract")
    icon: Mapped[str] = mapped_column(String, nullable=True, doc="mui icon")

    # Relations
    resources: Mapped[List["Resource"]] = relationship(secondary="resource_category", back_populates="categories")

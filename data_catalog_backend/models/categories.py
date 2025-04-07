import uuid
from typing import List

from sqlalchemy import UUID, Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Categories(Base):
    __tablename__ = 'categories'
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for category"
    )
    title: Mapped[str] = mapped_column(String, nullable=True, doc="title")
    abstract: Mapped[str] = mapped_column(String, nullable=True, doc="abstract")

    # Relations
    resources: Mapped[List["ResourceCategory"]] = relationship(back_populates="categories")

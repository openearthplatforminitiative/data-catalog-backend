import uuid
from datetime import datetime
from typing import List

from sqlalchemy import UUID, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.models.resource_category import ResourceCategory

from data_catalog_backend.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for category",
    )
    title: Mapped[str] = mapped_column(String, nullable=True, doc="title", unique=True)
    abstract: Mapped[str] = mapped_column(String, nullable=True, doc="abstract")
    icon: Mapped[str] = mapped_column(String, nullable=True, doc="mui icon")
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=func.now(), doc="updated at"
    )

    # Relations
    resources: Mapped[List["ResourceCategory"]] = relationship(
        "ResourceCategory", back_populates="category"
    )

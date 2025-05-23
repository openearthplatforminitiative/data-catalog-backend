import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class License(Base):
    __tablename__ = "licenses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for License",
    )
    name: Mapped[str] = mapped_column(String, nullable=False, doc="Name", unique=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    # Relations
    resources: Mapped[List["Resource"]] = relationship(
        "Resource", back_populates="license"
    )

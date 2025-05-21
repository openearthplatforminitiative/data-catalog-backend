import uuid
from datetime import datetime
from typing import List

from sqlalchemy import UUID, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for provider",
    )
    name: Mapped[str] = mapped_column(String, doc="Name", unique=True)
    short_name: Mapped[str] = mapped_column(
        String, doc="Short unique name", unique=True
    )
    provider_url: Mapped[str] = mapped_column(String, doc="URL to providers website")
    description: Mapped[str] = mapped_column(String, doc="Description")
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    # Relations
    resources: Mapped[List["ResourceProvider"]] = relationship(
        "ResourceProvider", back_populates="provider"
    )

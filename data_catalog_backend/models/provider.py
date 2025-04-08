import uuid
from typing import List

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Provider(Base):
    __tablename__ = 'providers'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for provider"
    )
    name: Mapped[str] = mapped_column(String, nullable=True, doc="name")
    provider_url: Mapped[str] = mapped_column(String, nullable=True, doc="provider url")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")

    # Relations
    resources: Mapped[List["Resource"]] = relationship("Resource", secondary="resource_provider", back_populates="providers")
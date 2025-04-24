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
    name: Mapped[str] = mapped_column(String, nullable=True, doc="Name", unique=True)
    short_name: Mapped[str] = mapped_column(String, nullable=True, doc="Short unique name", unique=True)
    provider_url: Mapped[str] = mapped_column(String, nullable=True, doc="URL to providers website")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="Description")

    # Relations
    resources: Mapped[List["ResourceProvider"]] = relationship("ResourceProvider", back_populates="provider")
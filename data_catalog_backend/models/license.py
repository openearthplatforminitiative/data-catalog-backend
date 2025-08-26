import uuid
from typing import Optional, List

from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base
from data_catalog_backend.models import AuditFieldsMixin


class License(AuditFieldsMixin, Base):
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

    # Relations
    resources: Mapped[List["Resource"]] = relationship(
        "Resource", back_populates="license"
    )

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.models import AuditFieldsMixin
from data_catalog_backend.database import Base


class ResourceProvider(AuditFieldsMixin, Base):
    __tablename__ = "resource_provider"

    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("providers.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String, default=False)

    resource: Mapped["Resource"] = relationship("Resource", back_populates="providers")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="resources")

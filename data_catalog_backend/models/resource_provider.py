import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class ResourceProvider(Base):
    __tablename__ = "resource_provider"

    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("providers.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String, default=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    resource: Mapped["Resource"] = relationship("Resource", back_populates="providers")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="resources")

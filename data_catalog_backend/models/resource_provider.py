import uuid

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base

class ResourceProvider(Base):
    __tablename__ = "resource_provider"

    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"), primary_key=True)
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("providers.id"), primary_key=True)
    role: Mapped[str] = mapped_column(str, default=False)

    provider: Mapped["Resource"] = relationship("Resource", back_populates="resource_provider")
    category: Mapped["Category"] = relationship("Category", back_populates="resource_provider")
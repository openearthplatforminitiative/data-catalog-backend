import uuid
from datetime import datetime
from typing import List

from sqlalchemy import UUID, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class CodeExamples(Base):
    __tablename__ = "code_examples"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for code",
    )
    title: Mapped[str] = mapped_column(String, nullable=False, doc="name")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, default=func.now(), doc="updated at"
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=True
    )
    # Relations
    code: Mapped[List["Code"]] = relationship(back_populates="code_examples")
    resource: Mapped["Resource"] = relationship(back_populates="code_examples")

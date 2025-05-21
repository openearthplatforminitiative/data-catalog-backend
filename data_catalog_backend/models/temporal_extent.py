import uuid
from typing import Optional
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, Date, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class TemporalExtent(Base):
    __tablename__ = "temporalextents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for temporal extent",
    )
    start_date: Mapped[Date] = mapped_column(Date, nullable=False, doc="start date")
    end_date: Mapped[Optional[Date]] = mapped_column(
        Date, nullable=True, doc="end date"
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=False
    )

    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="temporal_extent")

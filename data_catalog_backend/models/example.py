import uuid
from datetime import datetime

from sqlalchemy import UUID, ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Examples(Base):
    __tablename__ = "examples"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Resource",
    )
    title: Mapped[str] = mapped_column(String, doc="title of example")
    type: Mapped[str] = mapped_column(String, doc="type of examples")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    example_url: Mapped[str] = mapped_column(String, doc="link to example")
    favicon_url: Mapped[str] = mapped_column(
        String, nullable=True, doc="link to favicon"
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"))
    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="examples")

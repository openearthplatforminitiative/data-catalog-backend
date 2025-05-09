import uuid
from typing import List

from sqlalchemy import UUID, ForeignKey, String
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
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=True
    )
    # Relations
    code: Mapped[List["Code"]] = relationship(back_populates="code_examples")
    resource: Mapped["Resource"] = relationship(back_populates="code_examples")

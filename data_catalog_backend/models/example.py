import uuid

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class Examples(Base):
    __tablename__ = 'examples'
    example_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Resource"
    )
    type: Mapped[str] = mapped_column(String, nullable=True, doc="type of examples")
    description: Mapped[str] = mapped_column(String, nullable=True, doc="description")
    example_url: Mapped[str] = mapped_column(String, nullable=True, doc="link to example")
    favicon_url: Mapped[str] = mapped_column(String, nullable=True, doc="link to favicon")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=True)

    #Relations
    resource: Mapped["Resource"] = relationship(back_populates='examples')
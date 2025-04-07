import uuid

from sqlalchemy import UUID, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class TemporalExtent(Base):
    __tablename__ = 'temporalextents'

    temporal_extent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for temporal extent"
    )
    start_date: Mapped[Date] = mapped_column(Date, nullable=False, doc="start date")
    end_date: Mapped[Date] = mapped_column(Date, nullable=False, doc="end date")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=False)

    #Relations
    resource: Mapped["Resource"] = relationship(back_populates="temporal_extent")
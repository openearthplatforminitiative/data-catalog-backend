import uuid

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base


class ResourceCategory(Base):
    __tablename__ = 'resource_category'
    has_resources_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for relation between resources and category"
    )
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('categories.category_id'))
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'))
    categories: Mapped["Categories"] = relationship()
    resources: Mapped["Resource"] = relationship()
import uuid

from sqlalchemy import ForeignKey, Boolean, Index
from sqlalchemy.orm import mapped_column, Mapped, relationship

from data_catalog_backend.database import Base

class ResourceCategory(Base):
    __tablename__ = "resource_category"

    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"), primary_key=True)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), primary_key=True)
    is_main_category: Mapped[bool] = mapped_column(Boolean, default=False)

    resource: Mapped["Resource"] = relationship("Resource", back_populates="resource_categories")
    category: Mapped["Category"] = relationship("Category", back_populates="resource_categories")

    __table_args__ = (
        Index(
            'only_one_main_category_per_resource',
            'resource_id',
            unique=True,
            postgresql_where=(is_main_category == True)
        ),
    )
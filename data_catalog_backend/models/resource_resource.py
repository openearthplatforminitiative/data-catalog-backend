import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.database import Base


class ResourceResource(Base):
    __tablename__ = "resource_resource"

    based_on: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )
    used_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), primary_key=True
    )

    based_on_resource: Mapped["Resource"] = relationship(
        "Resource", foreign_keys=[based_on], back_populates="used_by"
    )
    used_by_resource: Mapped["Resource"] = relationship(
        "Resource", foreign_keys=[used_by], back_populates="based_on"
    )

import uuid
from datetime import datetime
from typing import List

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import String, UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base
from data_catalog_backend.models.spatial_extent_geometry_relation import (
    spatial_extent_geometry_relation,
)


class Geometry(Base):
    __tablename__ = "geometries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Geometry",
    )
    name: Mapped[str] = mapped_column(
        String, nullable=False, doc="Unique name for Geometry", unique=True
    )
    geometry: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326),
        nullable=False,
        doc="geometry value",
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
    spatial_extents: Mapped[List["SpatialExtent"]] = relationship(
        "SpatialExtent",
        secondary=spatial_extent_geometry_relation,
        back_populates="geometries",
    )

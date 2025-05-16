import uuid
from typing import Optional, List

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import String, UUID
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
    geometry: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326),
        nullable=False,
        doc="geometry value",
    )

    # Relations
    spatial_extents: Mapped[List["SpatialExtent"]] = relationship(
        "SpatialExtent",
        secondary=spatial_extent_geometry_relation,
        back_populates="geometries",
    )

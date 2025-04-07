import uuid
from typing import Optional
from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry.geo import mapping, shape
from pydantic import ValidationError
from sqlalchemy import UUID, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from data_catalog_backend.database import Base
from enum import StrEnum as PyStrEnum


class SpatialExtentRequestType(PyStrEnum):
    Region = "REGION"
    Global = "GLOBAL"
    NonSpatial = "NON_SPATIAL"

class SpatialExtentType(PyStrEnum):
    Region = "REGION"
    Global = "GLOBAL"

class SpatialExtent(Base):
    __tablename__ = 'spatial_extents'

    spatial_extent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Spatial extent"
    )
    type: Mapped[str] = mapped_column(String, nullable=False, doc="type")
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="region")
    details: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="details")
    geometry: Mapped[Optional[WKBElement]] = mapped_column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True, doc="geometry value")
    spatial_resolution: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="region")
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.resource_id'), nullable=False)

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="spatial_extent")


    # WKBElement to GeoJSON
    @property
    def geom(self):
        if isinstance(self.geometry, WKBElement):
            return mapping(to_shape(self.geometry))
        return None

    # GeoJSON to WKBElement
    @geom.setter
    def geom(self, new_value):
        try:
            # Convert GeoJSON-like dictionary to a Shapely geometry object
            if new_value is not None:
                shapely_geometry = shape(new_value.model_dump())

                # Convert Shapely geometry to WKBElement
                self.geometry = from_shape(shapely_geometry, srid=4326)
        except (ValidationError, ValueError) as e:
            raise ValueError("Invalid geometry value.") from e
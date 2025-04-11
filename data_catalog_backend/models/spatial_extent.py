import logging
import uuid
from typing import Optional, List
from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape, from_shape
from geojson_pydantic import Feature
from shapely.geometry.geo import mapping, shape
from pydantic import ValidationError
from sqlalchemy import UUID, String, ForeignKey, select, case
from sqlalchemy.ext.hybrid import hybrid_method
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

    id: Mapped[uuid.UUID] = mapped_column(
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
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('resources.id'), nullable=False)

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="spatial_extent")


    # WKBElement to GeoJSON
    @property
    def geom(self) -> Optional[List[Feature]]:
        if isinstance(self.geometry, WKBElement):
            geojson = mapping(to_shape(self.geometry))
            if geojson.get("type") == "GeometryCollection":
                return [
                    Feature(geometry=g, properties={}, type="Feature")
                    for g in geojson.get("geometries", [])
                ]
            return [Feature(geometry=geojson, properties={}, type="Feature")]
        return None

    # GeoJSON to WKBElement
    @geom.setter
    def geom(self, new_value):
        from shapely.geometry import GeometryCollection

        try:
            if new_value is not None:
                geometries = [
                    shape(g.geometry if hasattr(g, "geometry") else g["geometry"])
                    if (hasattr(g, "type") and g.type == "Feature") or (isinstance(g, dict) and g.get("type") == "Feature")
                    else shape(g)
                    for g in new_value
                ]
                shapely_geometry = GeometryCollection(geometries)

                self.geometry = from_shape(shapely_geometry, srid=4326)
        except (ValidationError, ValueError, TypeError, AttributeError) as e:
            raise ValueError("Invalid geometry value.") from e
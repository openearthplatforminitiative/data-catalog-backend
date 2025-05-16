import uuid
from typing import Optional, List
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape, from_shape
from geojson_pydantic import Feature
from shapely.geometry.geo import mapping, shape
from pydantic import ValidationError
from sqlalchemy import UUID, String, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from data_catalog_backend.database import Base
from enum import StrEnum as PyStrEnum

from data_catalog_backend.models.spatial_extent_geometry_relation import (
    spatial_extent_geometry_relation,
)
from data_catalog_backend.models.geometry import Geometry


class SpatialExtentRequestType(PyStrEnum):
    Region = "REGION"
    Global = "GLOBAL"
    NonSpatial = "NON_SPATIAL"


class SpatialExtentType(PyStrEnum):
    Region = "REGION"
    Global = "GLOBAL"


class SpatialExtent(Base):
    __tablename__ = "spatial_extents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier for Spatial extent",
    )
    type: Mapped[str] = mapped_column(String, nullable=False, doc="type")
    region: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="region")
    details: Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="details")
    spatial_resolution: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, doc="region"
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id"), nullable=False
    )

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="spatial_extent")
    geometries: Mapped[List["Geometry"]] = relationship(
        "Geometry",
        secondary=spatial_extent_geometry_relation,
        back_populates="spatial_extents",
    )

    geometry: Mapped[Optional[WKBElement]] = column_property(
        select(func.ST_Union(Geometry.geometry))
        .select_from(Geometry)
        .join(
            spatial_extent_geometry_relation,
            spatial_extent_geometry_relation.c.geometry_id == Geometry.id,
        )
        .where(spatial_extent_geometry_relation.c.spatial_extent_id == id)
        .correlate_except(Geometry)
        .scalar_subquery()
    )

    # WKBElement to GeoJSON
    @property
    def geom(self) -> Optional[List[Feature]]:
        if not isinstance(self.geometry, WKBElement):
            return None

        shapely_geom = to_shape(self.geometry)
        geojson = mapping(shapely_geom)

        if geojson.get("type") == "GeometryCollection":
            return [
                Feature(geometry=g, properties={}, type="Feature")
                for g in geojson.get("geometries", [])
            ]
        return [Feature(geometry=geojson, properties={}, type="Feature")]

    # GeoJSON to WKBElement
    @geom.setter
    def geom(self, new_value):
        from shapely.geometry import GeometryCollection

        try:
            if new_value is not None:
                geometries = [
                    (
                        shape(g.geometry if hasattr(g, "geometry") else g["geometry"])
                        if (hasattr(g, "type") and g.type == "Feature")
                        or (isinstance(g, dict) and g.get("type") == "Feature")
                        else shape(g)
                    )
                    for g in new_value
                ]
                shapely_geometry = GeometryCollection(geometries)

                self.geometry = from_shape(shapely_geometry, srid=4326)
        except (ValidationError, ValueError, TypeError, AttributeError) as e:
            raise ValueError("Invalid geometry value.") from e

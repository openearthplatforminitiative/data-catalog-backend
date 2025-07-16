import uuid
from datetime import datetime
from enum import StrEnum as PyStrEnum
from typing import Optional, List

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from geojson_pydantic import FeatureCollection, Feature
from shapely.geometry.geo import mapping
from sqlalchemy import UUID, String, ForeignKey, select, func, DateTime
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property,
    deferred,
)

from data_catalog_backend.database import Base
from data_catalog_backend.models.geometry import Geometry
from data_catalog_backend.models.spatial_extent_geometry_relation import (
    spatial_extent_geometry_relation,
)


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
        ForeignKey("resources.id", ondelete="CASCADE"), nullable=False
    )

    # Relations
    resource: Mapped["Resource"] = relationship(back_populates="spatial_extent")
    geometries: Mapped[List["Geometry"]] = relationship(
        "Geometry",
        secondary=spatial_extent_geometry_relation,
        back_populates="spatial_extents",
        lazy="noload",
        cascade="save-update",
    )

    geometry: Mapped[Optional[WKBElement]] = deferred(
        column_property(
            select(func.ST_Union(func.ST_MakeValid(Geometry.geometry)))
            .select_from(Geometry)
            .join(
                spatial_extent_geometry_relation,
                spatial_extent_geometry_relation.c.geometry_id == Geometry.id,
            )
            .where(spatial_extent_geometry_relation.c.spatial_extent_id == id)
            .correlate_except(Geometry)
            .scalar_subquery()
        )
    )

    created_by: Mapped[str] = mapped_column(String, nullable=False, doc="created by")
    updated_by: Mapped[str] = mapped_column(String, nullable=True, doc="updated by")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), doc="updated at"
    )

    # WKBElement to GeoJSON
    @property
    def geom(self) -> Optional[FeatureCollection]:
        if not isinstance(self.geometry, WKBElement):
            return None

        shapely_geom = to_shape(self.geometry)
        geojson = mapping(shapely_geom)

        if geojson.get("type") == "GeometryCollection":
            features = [
                Feature(geometry=g, properties={}, type="Feature")
                for g in geojson.get("geometries", [])
            ]
        else:
            features = [Feature(geometry=geojson, properties={}, type="Feature")]

        return FeatureCollection(type="FeatureCollection", features=features)

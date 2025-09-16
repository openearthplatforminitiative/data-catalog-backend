import uuid
from typing import List, Optional

from geoalchemy2 import Geometry as Geo, WKBElement
from geoalchemy2.shape import to_shape
from geojson_pydantic import FeatureCollection, Feature
from shapely.geometry import mapping
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data_catalog_backend.database import Base
from data_catalog_backend.models import AuditFieldsMixin
from data_catalog_backend.models.spatial_extent_geometry_relation import (
    spatial_extent_geometry_relation,
)


class Geometry(AuditFieldsMixin, Base):
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
        Geo(geometry_type="GEOMETRY", srid=4326),
        nullable=False,
        doc="geometry value",
    )

    bb_geometry: Mapped[WKBElement] = mapped_column(
        Geo(geometry_type="POLYGON", srid=4326),
        nullable=False,
        doc="bounding box of the geometry",
        default="ST_Envelope(geometry)",
        onupdate="ST_Envelope(geometry)",
    )

    # Relations
    spatial_extents: Mapped[List["SpatialExtent"]] = relationship(
        "SpatialExtent",
        secondary=spatial_extent_geometry_relation,
        back_populates="geometries",
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

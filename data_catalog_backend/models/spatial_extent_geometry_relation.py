from sqlalchemy import Table, ForeignKey, Column

from data_catalog_backend.database import Base

spatial_extent_geometry_relation = Table(
    "spatial_extent_geometry_relation",
    Base.metadata,
    Column(
        "spatial_extent_id",
        ForeignKey("spatial_extents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "geometry_id", ForeignKey("geometries.id", ondelete="CASCADE"), primary_key=True
    ),
)

import uuid
from typing import Optional

from geojson_pydantic import FeatureCollection
from pydantic import Field, AliasChoices

from data_catalog_backend.schemas.basemodel import BaseModel, AuditFieldsMixins


class GeometryRequest(BaseModel):
    name: str = Field(description="Unique name for geometry")
    geometry: FeatureCollection = Field(description="GeoJSON FeatureCollection")


class GeometryResponse(AuditFieldsMixins):
    id: uuid.UUID
    name: str = Field(description="Unique name for geometry")
    geometry: Optional[FeatureCollection] = Field(
        None,
        description="GeoJSON FeatureCollection",
        validation_alias=AliasChoices("geom", "geometry"),
    )


class UpdateGeometryRequest(BaseModel):
    name: Optional[str] = Field(description="Unique name for geometry")
    geometry: Optional[FeatureCollection] = Field(
        description="GeoJSON FeatureCollection"
    )

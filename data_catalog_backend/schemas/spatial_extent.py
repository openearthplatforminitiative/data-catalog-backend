
from typing import Optional
import uuid
from pydantic import  Field
from geojson_pydantic.geometries import Geometry

from data_catalog_backend.models.resource_types import SpatialExtentType
from data_catalog_backend.schemas.basemodel import BaseModel

class SpatialExtentRequest(BaseModel):
    type: SpatialExtentType
    region: Optional[str] = None
    details: Optional[str] = Field(None, description="addition information about the region")
    geometry: Optional[Geometry] = None
    spatial_resolution: Optional[str] = Field(None, description="description of the resolution of the data. ex: 5mx5m")

class SpatialExtentResponse(BaseModel):
    spatial_extent_id: uuid.UUID
    type: SpatialExtentType
    region: Optional[str] = None
    details: Optional[str] = Field(None, description="addition information about the region")
    geometry: Optional[Geometry] = None
    spatial_resolution: Optional[str] = Field(None, description="description of the resolution of the data. ex: 5mx5m")
from typing import Optional, List
import uuid

from geojson_pydantic import Feature
from pydantic import Field

from data_catalog_backend.models import SpatialExtentType
from data_catalog_backend.schemas.basemodel import BaseModel


class SpatialExtentRequest(BaseModel):
    type: SpatialExtentType
    region: Optional[str] = None
    details: Optional[str] = Field(
        None, description="addition information about the region"
    )
    geometries: Optional[List[str]] = None
    spatial_resolution: Optional[str] = Field(
        None, description="description of the resolution of the data. ex: 5mx5m"
    )


class SpatialExtentResponse(BaseModel):
    id: uuid.UUID
    type: SpatialExtentType
    region: Optional[str] = None
    details: Optional[str] = Field(
        None, description="addition information about the region"
    )
    geometry: Optional[List[Feature]] = None
    spatial_resolution: Optional[str] = Field(
        None, description="description of the resolution of the data. ex: 5mx5m"
    )

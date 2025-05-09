import uuid
from typing import Optional, List

from geojson_pydantic import Feature
from pydantic import Field

from data_catalog_backend.models import ResourceType, SpatialExtentRequestType
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class ResourceQueryRequest(BaseModel):
    types: Optional[List[ResourceType]] = None
    features: Optional[List[Feature]] = None
    spatial: Optional[List[SpatialExtentRequestType]] = None
    categories: Optional[List[uuid.UUID]] = None
    providers: Optional[List[uuid.UUID]] = None
    tags: Optional[List[str]] = None


class ResourceQuerySpatialResponse(ResourceSummaryResponse):
    covers_some: Optional[bool] = Field(
        default=None, description="if the resource covers some of the spatial extent"
    )
    covers_all: Optional[bool] = Field(
        default=None, description="if the resource covers all of the spatial extent"
    )
    intersects_some: Optional[bool] = Field(
        default=None,
        description="if the resource intersects some of the spatial extent",
    )
    intersects_all: Optional[bool] = Field(
        default=None, description="if the resource intersects all of the spatial extent"
    )


class ResourceQueryResponse(BaseModel):
    current_page: int
    total_pages: int
    data: List[ResourceQuerySpatialResponse]

import uuid
from typing import Optional

from pydantic import Field

from data_catalog_backend.models import ResourceType, SpatialExtentType
from data_catalog_backend.schemas.basemodel import BaseModel


class ResourceSummaryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Description of the resource")
    type: ResourceType
    icon: Optional[str] = Field(default=None, description="Icon of the resource")
    has_spatial_extent: bool = Field(
        description="True if the resource has a spatial extent, False otherwise"
    )
    spatial_extent_type: Optional[SpatialExtentType] = Field(
        default=None,
        description="If the resource has a spatial extent, the type of the spatial extent",
    )

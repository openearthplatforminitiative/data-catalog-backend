import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field
from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class ResourceCategoryResponse(BaseModel):
    resource: ResourceSummaryResponse = Field(description="Resource")


class CategoryResponse(AuditFieldsMixins):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: Optional[str] = Field(description="MUI icon of the category")
    resources: List[ResourceCategoryResponse] = Field(
        description="list of resources in the category"
    )


class CategoryRequest(BaseModel):
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")


class UpdateCategoryRequest(BaseModel):
    title: Optional[str] = Field(default=None, description="title of the category")
    abstract: Optional[str] = Field(
        default=None, description="short description of the category"
    )
    icon: Optional[str] = Field(default=None, description="MUI icon of the category")


class CategorySummaryResponse(AuditFieldsMixins):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: Optional[str] = Field(default=None, description="MUI icon of the category")

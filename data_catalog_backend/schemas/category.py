import uuid
from typing import List, Optional

from pydantic import Field
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class ResourceCategoryResponse(BaseModel):
    resource: ResourceSummaryResponse = Field(description="Resource")


class CategoryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")
    resources: List[ResourceCategoryResponse] = Field(
        description="list of resources in the category"
    )
    created_by: Optional[str] = Field(
        description="email of the user who created the data"
    )


class CategoryRequest(BaseModel):
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")
    created_by: Optional[str] = Field(
        description="email of the user who created the data"
    )


class UpdateCategoryRequest(BaseModel):
    title: Optional[str] = Field(description="title of the category")
    abstract: Optional[str] = Field(description="short description of the category")
    icon: Optional[str] = Field(description="MUI icon of the category")
    created_by: Optional[str] = Field(
        description="email of the user who created the data"
    )


class CategorySummaryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")
    created_by: Optional[str] = Field(
        description="email of the user who created the data"
    )

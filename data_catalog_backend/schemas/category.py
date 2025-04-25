import uuid
from typing import List

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
    resources: List[ResourceCategoryResponse] = Field(description="list of resources in the category")

class CategoryRequest(BaseModel):
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")

class CategorySummaryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")

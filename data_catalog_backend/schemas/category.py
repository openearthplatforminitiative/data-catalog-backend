import uuid
from typing import List

from pydantic import Field
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class CategoryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")
    resources: List[ResourceSummaryResponse] = Field(description="list of resources in the category")

class CategoryRequest(BaseModel):
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")

class CategoriesResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
    icon: str = Field(description="MUI icon of the category")

class CategoryGetRequest(BaseModel):
    id: uuid.UUID
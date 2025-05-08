import datetime
import uuid
from typing import List, Optional

from pydantic import Field, conlist

from data_catalog_backend.models import ResourceType
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.category import CategorySummaryResponse
from data_catalog_backend.schemas.code import CodeExampleRequest, CodeExampleResponse
from data_catalog_backend.schemas.example import ExampleResponse, ExampleRequest
from data_catalog_backend.schemas.license import LicenseResponse
from data_catalog_backend.schemas.provider import ProviderSummaryResponse
from data_catalog_backend.schemas.spatial_extent import (
    SpatialExtentRequest,
    SpatialExtentResponse,
)


class ResourceCategoryResponse(BaseModel):
    category: CategorySummaryResponse = Field(description="Category")
    is_main_category: bool = Field(description="Role of the provider")


class ResourceProviderResponse(BaseModel):
    provider: ProviderSummaryResponse = Field(description="List of providers")
    role: str = Field(description="Role of the provider")


class ResourceRequest(BaseModel):
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    html_content: Optional[str] = Field(
        description="Extended description of the resource"
    )
    resource_url: Optional[str] = Field(
        default=None, nullable=True, description="link to github"
    )
    documentation_url: str = Field(description="link to openAPI specification")
    git_url: Optional[str] = Field(
        default=None, nullable=True, description="link to github"
    )
    openapi_url: Optional[str] = Field(
        default=None, nullable=True, description="link to openAPI specification"
    )
    maintenance_and_update_frequency: str = Field(
        description="Description of how often this resource is being updated"
    )
    release_date: Optional[datetime.date] = Field(
        default=None, nullable=True, description="Date the resource was released"
    )
    spatial_extent: Optional[List[SpatialExtentRequest]] = Field(
        default=None, nullable=True, description="spatial extent"
    )
    contact: Optional[str] = Field(
        default=None, nullable=True, description="contact information"
    )
    keywords: List[str]
    version: Optional[str] = Field(
        default=None, nullable=True, description="The version of this resource"
    )
    type: ResourceType
    main_category: str = Field(description="Main category of the resource")
    additional_categories: Optional[List[str]] = Field(
        default=None, nullable=True, description="List of relevant categories"
    )
    code_examples: Optional[List[CodeExampleRequest]] = Field(
        default=None, nullable=True, description="Code examples"
    )
    license: str = Field(description="License of the resource")
    providers: conlist(str, min_length=1) = Field(description="List of providers")
    examples: Optional[List[ExampleRequest]] = Field(
        default=None, nullable=True, description="examples of the resource"
    )


class ResourceRelationRequest(BaseModel):
    used_by: str = Field(description="The resource it belongs to")
    based_on: str = Field(description="The resource it is based on")


class ResourceRelationResponse(BaseModel):
    used_by: uuid.UUID = Field(description="The resource it belongs to")
    based_on: uuid.UUID = Field(description="The resource it is based on")


class ResourceResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    icon: str = Field(description="Icon of the resource")
    html_content: Optional[str] = Field(
        description="Extended description of the resource"
    )
    resource_url: Optional[str] = Field(
        default=None, nullable=True, description="link to github"
    )
    documentation_url: Optional[str] = Field(
        description="link to openAPI specification"
    )
    git_url: Optional[str] = Field(
        default=None, nullable=True, description="link to github"
    )
    openapi_url: Optional[str] = Field(
        default=None, nullable=True, description="link to openAPI specification"
    )
    maintenance_and_update_frequency: Optional[str] = Field(
        description="Description of how often this resource is being updated"
    )
    release_date: Optional[datetime.date] = Field(
        default=None, nullable=True, description="Date the resource was released"
    )
    spatial_extent: Optional[List[SpatialExtentResponse]] = Field(
        default=None, nullable=True, description="spatial extent"
    )
    contact: Optional[str] = Field(
        default=None, nullable=True, description="contact information"
    )
    keywords: List[str] = Field(description="keywords")
    version: Optional[str] = Field(
        default=None, nullable=True, description="The version of this resource"
    )
    type: ResourceType = Field(description="Type of the resource")
    categories: List[ResourceCategoryResponse] = Field(
        default=None, nullable=True, description="List of categories"
    )
    code_examples: Optional[List[CodeExampleResponse]] = Field(
        default=None, nullable=True, description="Code examples"
    )
    license: LicenseResponse = Field(description="License of the resource")
    providers: List[ResourceProviderResponse] = Field(description="List of providers")
    examples: Optional[List[ExampleResponse]] = Field(
        default=None, nullable=True, description="examples of the resource"
    )

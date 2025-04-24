import datetime
import uuid
from typing import List, Optional

from pydantic import Field

from data_catalog_backend.models import ResourceType
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.category import CategorySummaryResponse
from data_catalog_backend.schemas.code import CodeExampleRequest, CodeExampleResponse
from data_catalog_backend.schemas.example import ExampleResponse, ExampleRequest
from data_catalog_backend.schemas.license import LicenseResponse
from data_catalog_backend.schemas.provider import ProviderResponse
from data_catalog_backend.schemas.spatial_extent import SpatialExtentRequest, SpatialExtentResponse

class ResourceRequest(BaseModel):
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    html_content: Optional[str] = Field(description="Extended description of the resource")
    resource_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    documentation_url: str = Field(description="link to openAPI specification")
    git_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    openapi_url: Optional[str] = Field(default=None, nullable=True, description="link to openAPI specification")
    maintenance_and_update_frequency: str = Field(description="Description of how often this resource is being updated")
    release_date: Optional[datetime.date] = Field(default=None, nullable=True, description="Date the resource was released")
    spatial_extent: Optional[List[SpatialExtentRequest]] = Field(default=None, nullable=True, description="spatial extent")
    contact: Optional[str] = Field(default=None, nullable=True, description="contact information")
    keywords: List[str]
    version: Optional[str] = Field(default=None, nullable=True, description="The version of this resource")
    type: ResourceType
    main_category: str = Field(description="Main category of the resource")
    additional_categories: Optional[List[str]] = Field(default=None, nullable=True, description="List of relevant categories")
    code_examples: Optional[List[CodeExampleRequest]] = Field(default=None, nullable=True, description="Code examples")
    license: str = Field(description="License of the resource")
    providers: List[str] = Field(description="List of providers")
    examples: Optional[List[ExampleRequest]] = Field(default=None, nullable=True, description="examples of the resource")

class ResourceResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    icon: str = Field(description="Icon of the resource")
    html_content: Optional[str] = Field(description="Extended description of the resource")
    resource_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    documentation_url: Optional[str] = Field(description="link to openAPI specification")
    git_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    openapi_url: Optional[str] = Field(default=None, nullable=True, description="link to openAPI specification")
    maintenance_and_update_frequency: Optional[str] = Field(description="Description of how often this resource is being updated")
    release_date: Optional[datetime.date] = Field(default=None, nullable=True, description="Date the resource was released")
    spatial_extent: Optional[List[SpatialExtentResponse]] = Field(default=None, nullable=True, description="spatial extent")
    contact: Optional[str] = Field(default=None, nullable=True, description="contact information")
    keywords: List[str] = Field(description="keywords")
    version: Optional[str] = Field(default=None, nullable=True, description="The version of this resource")
    type: ResourceType = Field(description="Type of the resource")
    categories: List[CategorySummaryResponse] = Field(default=None, nullable=True, description="List of categories")
    code_examples: Optional[List[CodeExampleResponse]] = Field(default=None, nullable=True, description="Code examples")
    license: LicenseResponse = Field(description="License of the resource")
    providers: List[ProviderResponse] = Field(description="List of providers")
    examples: Optional[List[ExampleResponse]] = Field(default=None, nullable=True, description="examples of the resource")
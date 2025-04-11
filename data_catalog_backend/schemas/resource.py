import datetime
import uuid
from typing import List, Optional, Union

from geojson_pydantic import Feature
from pydantic import Field, PastDate, HttpUrl

from data_catalog_backend.models import ResourceType, SpatialExtentRequestType
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.category import CategoryGetRequest
from data_catalog_backend.schemas.code import CodeExampleRequest, CodeExampleResponse
from data_catalog_backend.schemas.example import ExampleResponse, ExampleRequest
from data_catalog_backend.schemas.license import LicenseRequest, LicenseResponse, LicenseGetRequest
from data_catalog_backend.schemas.provider import ProviderGetRequest, ProviderRequest, ProviderResponse
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse
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
    categories: Optional[List[CategoryGetRequest]] = Field(description="List of relevant categories")
    code_examples: Optional[List[CodeExampleRequest]] = Field(default=None, nullable=True, description="Code examples")
    license: Union[LicenseGetRequest, LicenseRequest]
    providers: List[Union[ProviderGetRequest, ProviderRequest]]
    examples: Optional[List[ExampleRequest]] = Field(default=None, nullable=True, description="examples of the resource")

class ResourcesRequest(BaseModel):
    types: Optional[List[ResourceType]] = None
    features: Optional[List[Feature]] = None
    spatial: Optional[List[SpatialExtentRequestType]] = None
    categories: Optional[List[uuid.UUID]] = None
    providers: Optional[List[uuid.UUID]] = None
    tags: Optional[List[str]] = None

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
    main_category: CategoryGetRequest = Field(description="Main category of the resource")
    categories: List[CategoryGetRequest] = Field(default=None, nullable=True, description="List of categories")
    code_examples: Optional[List[CodeExampleResponse]] = Field(default=None, nullable=True, description="Code examples")
    license: Union[LicenseGetRequest, LicenseResponse] = Field(description="License of the resource")
    providers: List[Union[ProviderGetRequest, ProviderResponse]] = Field(description="List of providers")
    examples: Optional[List[ExampleResponse]] = Field(default=None, nullable=True, description="examples of the resource")

class ExtraResponse(ResourceSummaryResponse):
    covers_some: Optional[bool] = Field(default=None, description="if the resource covers some of the spatial extent")
    covers_all: Optional[bool] = Field(default=None, description="if the resource covers all of the spatial extent")
    intersects_some: Optional[bool] = Field(default=None, description="if the resource intersects some of the spatial extent")
    intersects_all: Optional[bool] = Field(default=None, description="if the resource intersects all of the spatial extent")

class ResourcesResponse(BaseModel):
    current_page: int
    total_pages: int
    resources: List[ExtraResponse]
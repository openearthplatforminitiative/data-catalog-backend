import datetime
import uuid
from typing import List, Optional, Union

from geojson_pydantic import Feature
from pydantic import Field, PastDate, HttpUrl

from data_catalog_backend.models import ResourceType, SpatialExtentRequestType
from data_catalog_backend.schemas.basemodel import BaseModel
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
    maintenance_and_update_frequency: str = Field(description="Description of how often this resource is being updated")
    release_date: Optional[datetime.date] = Field(default=None, nullable=True, description="Date the resource was released")
    spatial_extent: List[SpatialExtentRequest] = Field(description="spatial extent")
    contact: Optional[str] = Field(default=None, nullable=True, description="contact information")
    keywords: List[str]
    version: Optional[str] = Field(default=None, nullable=True, description="The version of this resource")
    type: ResourceType
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

class ResourcesResponse(ResourceSummaryResponse):
    html_content: Optional[str] = None
    resource_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = Field(None, description="link to openAPI specification")
    git_url: Optional[HttpUrl] = Field(None, description="link to github")
    maintenance_and_update_frequency: str = Field(description="Description of how often this resource is being updated")
    release_date: PastDate
    spatial_extent: List[SpatialExtentResponse] = Field(..., description="spatial extent of the resource")
    contact: Optional[str] = Field(description="contact information")
    keywords: Optional[List[str]]
    version: Optional[str] = Field(description="The version of this resource")
    providers: List[ProviderResponse] = Field(description="List of providers")
    code_examples: Optional[List[CodeExampleResponse]] = Field(description="Code examples")
    license: LicenseResponse
    examples: Optional[List[ExampleResponse]] = Field(description="examples of the resource")

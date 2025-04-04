
import uuid
from typing import List, Optional
from pydantic import Field, PastDate, HttpUrl
from data_catalog_backend.models.resource_types import ResourceType
from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.code import CodeExampleRequest, CodeExampleResponse
from data_catalog_backend.schemas.example import ExampleResponse, ExampleRequest
from data_catalog_backend.schemas.license import LicenseRequest, LicenseResponse
from data_catalog_backend.schemas.spatial_extent import SpatialExtentRequest, SpatialExtentResponse


class ResourceSummeryResponse(BaseModel):
    resource_id: uuid.UUID 
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    type: ResourceType

class ResourceRequest(BaseModel):
    title: str = Field(description="Title of the resource")
    abstract: str = Field(description="Short description of the resource")
    html_content: Optional[str] = Field(description="Extended description of the resource")
    resource_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    documentation_url: str = Field(description="link to openAPI specification")
    git_url: Optional[str] = Field(default=None, nullable=True, description="link to github")
    maintenance_and_update_frequency: str = Field(description="Description of how often this resource is being updated")
    release_date: PastDate
    spatial_extent: List[SpatialExtentRequest] = Field(description="spatial extent")
    contact: str = Field(description="contact information")
    keywords: List[str]
    version: str = Field(description="The version of this resource")
    type: ResourceType
    codeexamples: Optional[List[CodeExampleRequest]] = Field(description="Code examples")
    license: LicenseRequest
    examples: Optional[List[ExampleRequest]] = Field(description="examples of the resource")

class ResourcesResponse(ResourceSummeryResponse):
    html_content: Optional[str] = None
    resource_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = Field(None, description="link to openAPI specification")
    git_url: Optional[HttpUrl] = Field(None, description="link to github")
    maintenance_and_update_frequency: str = Field(description="Description of how often this resource is being updated")
    release_date: PastDate
    spatial_extent: List[SpatialExtentResponse] = Field(..., description="spatial extent of the resource")
    contact: str = Field(description="contact information")
    keywords: Optional[List[str]]
    version: Optional[str] = Field(description="The version of this resource")
    codeexamples: Optional[List[CodeExampleResponse]] = Field(description="Code examples")
    license: LicenseResponse
    examples: Optional[List[ExampleResponse]] = Field(description="examples of the resource")

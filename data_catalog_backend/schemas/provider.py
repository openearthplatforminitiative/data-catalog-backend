from typing import List
import uuid

from pydantic import Field, HttpUrl

from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class ResourceProviderResponse(BaseModel):
    resource: ResourceSummaryResponse = Field(description="List of providers")


class ProviderRequest(BaseModel):
    name: str = Field(description="name of provider")
    short_name: str = Field(description="short name of provider")
    provider_url: str = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")


class ProviderSummaryResponse(BaseModel):
    id: uuid.UUID
    name: str = Field(description="name of provider")
    short_name: str = Field(description="short name of provider")
    provider_url: str = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")


class ProviderResponse(ProviderSummaryResponse):
    resources: List[ResourceProviderResponse]

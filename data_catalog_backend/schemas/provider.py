from typing import List
import uuid

from pydantic import Field, HttpUrl

from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class ProviderRequest(BaseModel):
    name: str = Field(description="name of provider")
    provider_url: str = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")

class ProviderResponse(BaseModel):
    id: uuid.UUID
    name: str = Field(description="name of provider")
    provider_url: HttpUrl = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")
    resources: List[ResourceSummaryResponse]

class ProviderGetRequest(BaseModel):
    id: uuid.UUID
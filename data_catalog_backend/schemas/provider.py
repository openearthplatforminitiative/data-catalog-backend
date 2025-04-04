from typing import List
import uuid

from pydantic import Field, HttpUrl

from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.resources import ResourceSummeryResponse

class ProviderRequest(BaseModel):
    name: str = Field(description="name of provider")
    provider_url: str = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")
    resources: List[ResourceSummeryResponse]

class ProviderResponse(BaseModel):
    provider_id: uuid.UUID
    name: str = Field(description="name of provider")
    provider_url: HttpUrl = Field(description="url to the providers website")
    description: str = Field(description="description of the provider")
    resources: List[ResourceSummeryResponse]
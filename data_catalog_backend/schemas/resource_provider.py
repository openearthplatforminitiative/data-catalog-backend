from pydantic import Field

from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.provider import ProviderSummaryResponse


class ResourceProviderResponse(BaseModel):
    provider: ProviderSummaryResponse = Field(description="List of providers")
    role: str = Field(description="Role of the provider")

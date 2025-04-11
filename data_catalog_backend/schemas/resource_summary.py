import uuid

from pydantic import Field

from data_catalog_backend.models import ResourceType
from data_catalog_backend.schemas.basemodel import BaseModel


class ResourceSummaryResponse(BaseModel):
    id: uuid.UUID
    title: str = Field(description="Title of the resource")
    type: ResourceType

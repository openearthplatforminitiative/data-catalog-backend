import uuid
from typing import Optional

from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)


class ExampleResponse(AuditFieldsMixins):
    id: uuid.UUID
    title: str = None
    type: str = None
    description: Optional[str] = None
    example_url: str = None
    favicon_url: Optional[str] = None


class ExampleRequest(BaseModel):
    title: str = None
    type: str = None
    description: Optional[str] = None
    example_url: str = None
    favicon_url: Optional[str] = None


class UpdateExampleRequest(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    example_url: Optional[str] = None
    favicon_url: Optional[str] = None

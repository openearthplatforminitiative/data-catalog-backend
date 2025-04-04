import uuid
from typing import Optional

from data_catalog_backend.schemas.basemodel import BaseModel


class ExampleResponse(BaseModel):
    example_id: uuid.UUID
    type: Optional[str] = None
    description: Optional[str] = None
    example_url: Optional[str] = None
    favicon_url: Optional[str] = None

class ExampleRequest(BaseModel):
    type: Optional[str] = None
    description: Optional[str]  = None
    example_url: Optional[str] = None
    favicon_url: Optional[str] = None


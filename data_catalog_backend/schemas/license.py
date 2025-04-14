from typing import Optional
import uuid

from data_catalog_backend.schemas.basemodel import BaseModel

class LicenseRequest(BaseModel):
    name: str
    url: str
    description: str

class LicenseResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: Optional[str]
    description: Optional[str]
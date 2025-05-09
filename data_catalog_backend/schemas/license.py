from typing import Optional
import uuid

from data_catalog_backend.schemas.basemodel import BaseModel


class LicenseRequest(BaseModel):
    name: str
    url: str


class LicenseResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: Optional[str]

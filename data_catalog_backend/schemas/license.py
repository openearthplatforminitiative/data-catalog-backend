from typing import Optional
import uuid

from data_catalog_backend.schemas.basemodel import BaseModel


class LicenseRequest(BaseModel):
    name: str
    url: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class LicenseResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: Optional[str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class UpdateLicenseRequest(BaseModel):
    id: uuid.UUID

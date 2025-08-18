from typing import Optional
import uuid

from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)


class LicenseRequest(BaseModel):
    name: str
    url: str


class LicenseResponse(AuditFieldsMixins):
    id: uuid.UUID
    name: str
    url: Optional[str]


class UpdateLicenseRequest(BaseModel):
    id: uuid.UUID

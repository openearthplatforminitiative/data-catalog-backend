from typing import Optional, List
import uuid

from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)
from data_catalog_backend.schemas.resource_summary import ResourceSummaryResponse


class LicenseRequest(BaseModel):
    name: str
    url: str


class LicenseResponse(AuditFieldsMixins):
    id: uuid.UUID
    name: str
    url: Optional[str]
    resources: List[ResourceSummaryResponse]


class UpdateLicenseRequest(BaseModel):
    id: uuid.UUID

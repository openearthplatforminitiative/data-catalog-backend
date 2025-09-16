import uuid
from datetime import date
from typing import Optional

from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)


class TemporalExtentRequest(BaseModel):
    start_date: date
    end_date: Optional[date] = None


class TemporalExtentResponse(AuditFieldsMixins):
    id: uuid.UUID
    start_date: date
    end_date: Optional[date] = None

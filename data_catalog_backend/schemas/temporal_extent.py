import uuid
from typing import Optional

from pydantic import PastDate
from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)


class TemporalExtentRequest(BaseModel):
    start_date: PastDate
    end_date: Optional[PastDate] = None


class TemporalExtentResponse(AuditFieldsMixins):
    id: uuid.UUID
    start_date: PastDate
    end_date: Optional[PastDate] = None

import uuid
from typing import Optional

from pydantic import PastDate
from data_catalog_backend.schemas.basemodel import BaseModel


class TemporalExtentRequest(BaseModel):
    start_date: PastDate
    end_date: Optional[PastDate]


class TemporalExtentResponse(BaseModel):
    id: uuid.UUID
    start_date: PastDate
    end_date: Optional[PastDate]

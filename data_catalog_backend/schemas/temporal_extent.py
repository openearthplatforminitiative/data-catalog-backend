import uuid

from pydantic import FutureDate, PastDate
from data_catalog_backend.schemas.basemodel import BaseModel

class TemporalExtentResponse(BaseModel):
    temporal_id: uuid.UUID
    start_date: PastDate
    end_date: FutureDate
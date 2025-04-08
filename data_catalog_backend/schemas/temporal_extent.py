import uuid

from pydantic import PastDate
from data_catalog_backend.schemas.basemodel import BaseModel

class TemporalExtentResponse(BaseModel):
    id: uuid.UUID
    start_date: PastDate
    end_date: PastDate
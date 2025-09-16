import abc
from datetime import datetime
from typing import Optional

from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel, abc.ABC):
    class Config:
        from_attributes = True


class AuditFieldsMixins(BaseModel):
    created_by: str = Field(description="email of the user who created the data")
    created_at: datetime = Field(description="date when the category was created")
    updated_by: Optional[str] = Field(
        default=None, description="email of the user who updated the data"
    )
    updated_at: Optional[datetime] = Field(
        default=None, description="date when the category was updated"
    )

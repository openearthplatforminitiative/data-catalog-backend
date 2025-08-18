import uuid
from typing import List, Optional

from data_catalog_backend.models import CodeType
from data_catalog_backend.schemas.basemodel import (
    BaseModel,
    AuditFieldsMixins,
)


class CodeResponse(BaseModel):
    id: uuid.UUID
    language: CodeType
    source: str
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CodeRequest(BaseModel):
    language: CodeType
    source: str


class UpdateCodeRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    language: Optional[CodeType] = None
    source: Optional[str] = None


class CodeExampleResponse(AuditFieldsMixins):
    id: uuid.UUID
    title: str
    description: str
    code: Optional[List[CodeResponse]] = None


class CodeExampleRequest(BaseModel):
    title: str
    description: str
    code: List[CodeRequest]


class UpdateCodeExampleRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    code: Optional[List[UpdateCodeRequest]] = None

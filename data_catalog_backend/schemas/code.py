import uuid
from email.policy import default
from typing import List, Optional

from data_catalog_backend.models import CodeType
from data_catalog_backend.schemas.basemodel import BaseModel


class CodeResponse(BaseModel):
    id: uuid.UUID
    language: CodeType
    source: str
    created_by: Optional[str] = None


class CodeRequest(BaseModel):
    language: CodeType
    source: str
    created_by: Optional[str] = None


class UpdateCodeRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    language: Optional[CodeType] = None
    source: Optional[str] = None
    updated_by: Optional[str] = None
    created_by: Optional[str] = None


class UpdateCodeRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    language: Optional[CodeType]
    source: Optional[str]
    created_by: Optional[str] = None


class CodeExampleResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    code: Optional[List[CodeResponse]]
    created_by: Optional[str] = None


class CodeExampleRequest(BaseModel):
    title: str
    description: str
    code: List[CodeRequest]
    created_by: Optional[str] = None


class UpdateCodeExampleRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    code: Optional[List[UpdateCodeRequest]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

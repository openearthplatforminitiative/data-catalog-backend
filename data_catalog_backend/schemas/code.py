import uuid
from email.policy import default
from typing import List, Optional

from data_catalog_backend.models import CodeType
from data_catalog_backend.schemas.basemodel import BaseModel


class CodeResponse(BaseModel):
    id: uuid.UUID
    language: CodeType
    source: str


class CodeRequest(BaseModel):
    language: CodeType
    source: str


class UpdateCodeRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    language: Optional[CodeType]
    source: Optional[str]


class CodeExampleResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    code: Optional[List[CodeResponse]]


class CodeExampleRequest(BaseModel):
    title: str
    description: str
    code: List[CodeRequest]


class UpdateCodeExampleRequest(BaseModel):
    id: Optional[uuid.UUID] = None
    title: Optional[str]
    description: Optional[str]
    code: Optional[List[UpdateCodeRequest]]

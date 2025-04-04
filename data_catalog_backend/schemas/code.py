import uuid
from typing import List, Optional

from data_catalog_backend.models.resource_types import CodeType
from data_catalog_backend.schemas.basemodel import BaseModel


class CodeResponse(BaseModel):
    code_id: uuid.UUID
    language: CodeType
    source: str

class CodeRequest(BaseModel):
    language: CodeType
    source: str

class CodeExampleResponse(BaseModel):
    examples_id: uuid.UUID
    title: str
    description: str
    code: Optional[List[CodeResponse]]

class CodeExampleRequest(BaseModel):
    title: str
    description: str
    code: Optional[List[CodeRequest]]
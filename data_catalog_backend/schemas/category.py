import uuid

from pydantic import Field
from data_catalog_backend.schemas.basemodel import BaseModel

class CategoryResponse(BaseModel): 
    category_id: uuid.UUID
    title: str = Field(description="title of the category")
    abstract: str = Field(description="short description of the category")
from pydantic import Field

from data_catalog_backend.schemas.basemodel import BaseModel
from data_catalog_backend.schemas.category import CategorySummaryResponse


class ResourceCategoryResponse(BaseModel):
    category: CategorySummaryResponse = Field(description="Category")
    is_main_category: bool = Field(description="Role of the provider")

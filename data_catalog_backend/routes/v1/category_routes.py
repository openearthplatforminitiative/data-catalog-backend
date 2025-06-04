import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_category_service
from data_catalog_backend.routes.admin.authentication import dummy_user
from data_catalog_backend.schemas.category import (
    CategoryResponse,
    UpdateCategoryRequest,
    CategoryRequest,
)
from data_catalog_backend.services.category_service import CategoryService

router = APIRouter(prefix="/categories")


@router.get(
    "/",
    summary="Get all categories",
    description="Returns all categories in our system",
    response_model=List[CategoryResponse],
    response_model_exclude_none=True,
    tags=["categories"],
)
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> List[CategoryResponse]:
    try:
        logging.info("Fetching all categories")
        categories = service.get_categories()
        converted = [CategoryResponse.model_validate(cat) for cat in categories]
        return converted
    except Exception as e:
        logging.error(f"Error fetching categories: {e}")
        raise e


@router.get(
    "/{category_id}",
    description="Returns specific category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["categories"],
)
async def get_category(
    category_id: uuid.UUID, service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    try:
        category = service.get_category(category_id)
        converted = CategoryResponse.model_validate(category)
        return converted
    except Exception as e:
        logging.error(f"Error getting category {category_id}: {e}")
        raise e

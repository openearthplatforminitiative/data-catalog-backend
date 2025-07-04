import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_category_service
from data_catalog_backend.schemas.category import (
    CategoryResponse,
    UpdateCategoryRequest,
    CategorySummaryResponse
)
from data_catalog_backend.services.category_service import CategoryService

router = APIRouter(prefix="/categories")


@router.get(
    "/",
    summary="Get all categories",
    description="Returns all categories in our system",
    response_model=List[CategorySummaryResponse],
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
    category_id: uuid.UUID,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        category = category_service.get_category(category_id)
        converted = CategoryResponse.model_validate(category)
        return converted
    except Exception as e:
        logging.error(f"Error getting category {category_id}: {e}")
        raise e


@router.post(
    "/categories",
    description="Create a new category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["categories"],
)
async def create_category(
    category: CategoryResponse,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return service.create_category(category)


@router.put(
    "/{category_id}",
    description="Update an existing category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["categories"],
)
async def update_category(
    category: UpdateCategoryRequest,
    category_id: uuid.UUID,
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    return service.update_category(category, category_id)

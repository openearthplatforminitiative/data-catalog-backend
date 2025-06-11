import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_category_service
from data_catalog_backend.schemas.category import (
    CategoryResponse,
    CategorySummaryResponse,
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
    category_service: CategoryService = Depends(get_category_service),
) -> List[CategorySummaryResponse]:
    categories = category_service.get_categories()
    converted = [
        CategorySummaryResponse.model_validate(category) for category in categories
    ]
    return converted


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
    category = category_service.get_category(category_id)
    converted = CategoryResponse.model_validate(category)
    return converted

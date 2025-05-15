import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_category_service
from data_catalog_backend.schemas.category import CategoryResponse
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
    return service.get_categories()


@router.get(
    "/{id}",
    description="Returns specific category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["categories"],
)
async def get_category(
    id: uuid.UUID, service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    return service.get_category(id)

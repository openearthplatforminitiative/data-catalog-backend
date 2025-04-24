import logging
import uuid
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_category_service
from data_catalog_backend.schemas.category import CategoryResponse, CategoryRequest
from data_catalog_backend.services.category_service import CategoryService

router = APIRouter()


@router.post(
    "/category",
    summary="Add a category to the database",
    tags=["admin"],
    response_model=CategoryResponse,
)
async def add_category(
    category_req: CategoryRequest,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        created = category_service.create_category(category_req)
        converted = CategoryResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
    raise HTTPException(status_code=500, detail="Unknown error")


@router.get(
    "/categories",
    summary="Get all categories",
    description="Returns all categories in our system",
    response_model=List[CategoryResponse],
    response_model_exclude_none=True,
)
async def get_categories(
    service: CategoryService = Depends(get_category_service),
) -> List[CategoryResponse]:
    logging.info("Getting categories")
    return service.get_categories()


@router.get(
    "/categories/{id}",
    description="Returns specific category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
)
async def get_category(
    id: uuid.UUID, service: CategoryService = Depends(get_category_service)
) -> CategoryResponse:
    logging.info("getting category")
    return service.get_category(id)

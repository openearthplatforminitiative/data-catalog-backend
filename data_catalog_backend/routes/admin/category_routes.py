import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_category_service,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import CategoryResponse, CategoryRequest
from data_catalog_backend.services.category_service import CategoryService

router = APIRouter(prefix="/categories")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a category to the database",
    tags=["admin"],
    response_model=CategoryResponse,
)
async def add_category(
    category_req: CategoryRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is adding a category")
        created = category_service.create_category(category_req, current_user)
        converted = CategoryResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{category_id}",
    description="Delete a category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def delete_category(
    category_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    deleted_category = service.delete_category(category_id, current_user)
    if not deleted_category:
        raise HTTPException(status_code=404, detail="Category not found")
    if deleted_category.resources and len(deleted_category.resources) > 0:
        raise HTTPException(
            status_code=400, detail="Cannot delete category with existing resources"
        )
    converted = CategoryResponse.model_validate(deleted_category)
    return converted

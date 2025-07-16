import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_category_service,
)
from data_catalog_backend.models import Category
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.category import (
    CategoryResponse,
    CategoryRequest,
    UpdateCategoryRequest,
)
from data_catalog_backend.services.category_service import CategoryService

router = APIRouter(prefix="/categories")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    status_code=201,
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
        category_data = category_req.model_dump()
        category = Category(**category_data)
        created = category_service.create_category(category, current_user)
        converted = CategoryResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{category_id}",
    status_code=200,
    description="Update an existing category",
    response_model=CategoryResponse,
    response_model_exclude_none=True,
    tags=["admin"],
)
async def update_category(
    category_req: UpdateCategoryRequest,
    category_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is updating a category")
        category_data = category_req.model_dump()
        category = Category(**category_data)
        updated_category = category_service.update_category(
            category, category_id, current_user
        )
        converted = CategoryResponse.model_validate(updated_category)
        return converted
    except ValueError as e:
        logger.error(f"Value error while updating category: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{category_id}",
    status_code=204,
    description="Delete a category",
    response_model_exclude_none=True,
    tags=["admin"],
)
async def delete_category(
    category_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    category_service: CategoryService = Depends(get_category_service),
):
    try:
        logging.info(f"Deleting category with id {category_id}")
        category_service.delete_category(category_id, current_user)
    except ValueError as ve:
        logger.error(
            f"Validation error while deleting category with ID: {category_id} - {str(ve)}"
        )
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Error deleting category: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

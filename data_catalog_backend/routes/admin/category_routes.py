import logging
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
        created = category_service.create_category(category_req)
        converted = CategoryResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

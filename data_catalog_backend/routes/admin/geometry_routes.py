import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import (
    get_geometry_service,
)
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.geometry import GeometryRequest
from data_catalog_backend.services.geometry_service import GeometryService

router = APIRouter(prefix="/geometries")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a geometry to the database",
    tags=["admin"],
)
async def add_geometry(
    geometry_req: GeometryRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    geometry_service: GeometryService = Depends(get_geometry_service),
) -> None:
    try:
        logger.info(f"User {current_user.email} is adding a geometry")
        geometry_service.create_geometry(geometry_req)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

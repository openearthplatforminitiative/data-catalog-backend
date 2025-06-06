import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.routes.admin.authentication import authenticate_user
from data_catalog_backend.schemas.User import User
from data_catalog_backend.schemas.license import LicenseResponse, LicenseRequest
from data_catalog_backend.services.license_service import LicenseService

router = APIRouter(prefix="/licenses")
logger = logging.getLogger(__name__)


@router.post(
    "/",
    summary="Add a license to the database",
    tags=["admin"],
    response_model=LicenseResponse,
)
async def add_license(
    license_req: LicenseRequest,
    current_user: Annotated[User, Depends(authenticate_user)],
    license_service: LicenseService = Depends(get_license_service),
) -> LicenseResponse:
    try:
        logger.info(f"User {current_user.preferred_username} is adding a license")
        created = license_service.create_license(license_req, current_user)
        converted = LicenseResponse.model_validate(created)
        return converted
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{licence_id}",
    status_code=204,
    description="Delete a license",
    response_model=LicenseResponse,
    response_model_exclude_none=True,
    tags=["licenses"],
)
async def delete_license(
    license_id: uuid.UUID,
    current_user: Annotated[User, Depends(authenticate_user)],
    service: LicenseService = Depends(get_license_service),
):
    try:
        logging.info(f"Deleting license with id {license_id}")
        service.delete_license(license_id, current_user)
    except Exception as e:
        logger.error(f"Error deleting license: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    return

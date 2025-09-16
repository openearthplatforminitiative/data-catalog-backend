import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.schemas.license import LicenseResponse
from data_catalog_backend.services.license_service import LicenseService

router = APIRouter(prefix="/licenses")


@router.get(
    "/",
    summary="Get all licenses",
    description="Returns all licenses in our system",
    response_model=List[LicenseResponse],
    response_model_exclude_none=True,
    tags=["licenses"],
)
async def get_licenses(
    license_service: LicenseService = Depends(get_license_service),
) -> List[LicenseResponse]:
    logging.info("Getting licenses")
    licences = license_service.get_licenses()
    converted = [LicenseResponse.model_validate(lic) for lic in licences]
    return converted


@router.get(
    "/{license_id}",
    summary="Get license by ID",
    description="Returns a license by its ID",
    response_model=LicenseResponse,
    response_model_exclude_none=True,
    tags=["licenses"],
)
async def get_license_by_id(
    license_id: uuid.UUID,
    license_service: LicenseService = Depends(get_license_service),
) -> LicenseResponse | None:
    logging.info(f"Getting license with ID: {license_id}")
    license = license_service.get_license(license_id)
    if license is None:
        return None
    converted = LicenseResponse.model_validate(license)
    return converted

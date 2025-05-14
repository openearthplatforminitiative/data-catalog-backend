import logging
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.schemas.license import LicenseResponse
from data_catalog_backend.services.license_service import LicenseService

router = APIRouter()


@router.get(
    "/licenses",
    summary="Get all licenses",
    description="Returns all licenses in our system",
    response_model=List[LicenseResponse],
    response_model_exclude_none=True,
    tags=["licenses"],
)
async def get_licenses(
    service: LicenseService = Depends(get_license_service),
) -> List[LicenseResponse]:
    logging.info("Getting licenses")
    return service.get_licenses()

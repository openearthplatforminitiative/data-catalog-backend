import logging
from http.client import HTTPException
from typing import List

from fastapi import APIRouter, Depends

from data_catalog_backend.dependencies import get_license_service
from data_catalog_backend.schemas.license import LicenseResponse, LicenseRequest
from data_catalog_backend.services.license_service import LicenseService

router = APIRouter()


@router.post(
    "/license",
    summary="Add a license to the database",
    tags=["admin"],
    response_model=LicenseResponse,
)
async def add_license(
    license_req: LicenseRequest,
    license_service: LicenseService = Depends(get_license_service),
) -> LicenseResponse:
    try:
        created = license_service.create_license(license_req)
        converted = LicenseResponse.model_validate(created)
        return converted
    except Exception as e:
        logging.error(e)
    raise HTTPException(status_code=500, detail="Unknown error")


@router.get(
    "/licenses",
    summary="Get all licenses",
    description="Returns all licenses in our system",
    response_model=List[LicenseResponse],
    response_model_exclude_none=True,
)
async def get_licenses(
    service: LicenseService = Depends(get_license_service),
) -> List[LicenseResponse]:
    logging.info("Getting licenses")
    return service.get_licenses()
